#!/usr/bin/env python3
"""Bounded, payload-free analysis of Codex/Claude logs and T3 activity exports."""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import hashlib
import html
import json
import math
from pathlib import Path

SCHEMA = 'tool_flow.analysis.v1'


def instant(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be an ISO string')
    result = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timestamps must include a timezone')
    return result.timestamp()


def percentile(values, fraction):
    return values[max(0, math.ceil(len(values) * fraction) - 1)] if values else None


def intervals_union(intervals):
    end, total = None, 0.0
    for a, b in sorted(intervals):
        total += max(0, b - max(a, end if end is not None else a))
        end = b if end is None else max(end, b)
    return total


def native_events(item):
    """Adapters return tool identities and times, never argument/output content."""
    timestamp = item.get('timestamp')
    if item.get('type') == 'response_item':
        p = item.get('payload', {})
        if not isinstance(p, dict):
            return
        kind = p.get('type')
        if kind in ('function_call', 'custom_tool_call'):
            yield 'call', p.get('call_id'), p.get('name', 'unknown'), timestamp
        elif kind in ('function_call_output', 'custom_tool_call_output'):
            yield 'result', p.get('call_id'), None, timestamp
    # Claude JSONL uses message.content blocks and tool_use_id on tool results.
    elif item.get('type') in ('assistant', 'user'):
        message = item.get('message', {})
        if not isinstance(message, dict):
            return
        blocks = message.get('content', [])
        if not isinstance(blocks, list):
            return
        for block in blocks:
            if not isinstance(block, dict):
                continue
            if block.get('type') == 'tool_use':
                yield 'call', block.get('id'), block.get('name', 'unknown'), timestamp
            elif block.get('type') == 'tool_result':
                yield 'result', block.get('tool_use_id'), None, timestamp


def summarize_logs(paths, *, before=None, max_bytes=1024**3, max_line_bytes=32*1024**2,
                   max_calls=200000):
    cutoff = instant(before) if before else None
    pending, seen, results, counts = {}, set(), set(), collections.Counter()
    samples, intervals, sources = collections.defaultdict(list), [], []
    anomalies = collections.Counter()
    compactions = 0
    consumed = 0
    for ordinal, path in enumerate(paths):
        path = Path(path)
        size = path.stat().st_size
        if size > max_bytes - consumed:
            raise ValueError('declared aggregate input-byte limit exceeded')
        digest = hashlib.sha256()
        read_bytes = 0
        # An explicit session id permits split log files, without merging child ids.
        session = f'input-{ordinal + 1}'
        with path.open('rb') as stream:
            while read_bytes < size:
                raw = stream.readline(min(max_line_bytes + 1, size - read_bytes))
                if not raw:
                    break
                if len(raw) > max_line_bytes:
                    raise ValueError('input line exceeds declared line-byte limit')
                read_bytes += len(raw)
                digest.update(raw)
                if not raw.endswith(b'\n'):
                    anomalies['incomplete_tail_lines'] += 1
                    continue
                try:
                    item = json.loads(raw)
                except (ValueError, UnicodeError):
                    anomalies['invalid_json_lines'] += 1
                    continue
                if not isinstance(item, dict):
                    anomalies['nonobject_lines'] += 1
                    continue
                if ((item.get('type') in ('session_meta', 'response_item') and not isinstance(item.get('payload', {}), dict))
                    or (item.get('type') in ('assistant', 'user') and not isinstance(item.get('message', {}), dict))):
                    anomalies['invalid_event_shapes'] += 1
                    continue
                if item.get('type') == 'session_meta':
                    candidate_session = item.get('payload', {}).get('id', session)
                    if not isinstance(candidate_session, str) or not candidate_session:
                        anomalies['invalid_session_identities'] += 1
                        continue
                    session = candidate_session
                try:
                    event_time = instant(item['timestamp']) if item.get('timestamp') else None
                except (ValueError, TypeError):
                    anomalies['invalid_timestamps'] += 1
                    continue
                if cutoff is not None and event_time is not None and event_time > cutoff:
                    continue
                if item.get('type') in ('compacted', 'compaction'):
                    compactions += 1
                for kind, ident, name, timestamp in native_events(item):
                    if not isinstance(ident, str) or not ident or event_time is None or (kind == 'call' and not isinstance(name, str)):
                        anomalies['missing_identity_or_time'] += 1
                        continue
                    key = (session, ident)
                    if kind == 'call':
                        if key in seen:
                            anomalies['duplicate_calls'] += 1
                            continue
                        if len(seen) >= max_calls:
                            raise ValueError('declared call limit exceeded')
                        seen.add(key)
                        counts[name] += 1
                        pending[key] = (event_time, name)
                    elif key in results:
                        anomalies['duplicate_results'] += 1
                    elif key not in pending:
                        anomalies['unmatched_results'] += 1
                    else:
                        start, name = pending.pop(key)
                        results.add(key)
                        if event_time < start:
                            anomalies['negative_intervals'] += 1
                            continue
                        samples[name].append(event_time - start)
                        intervals.append((start, event_time))
        consumed += read_bytes
        sources.append(dict(label=f'input-{ordinal + 1}', prefix_bytes=read_bytes,
                            sha256=digest.hexdigest()))
    groups = {}
    for name, count in sorted(counts.items()):
        values = sorted(samples[name])
        groups[name] = dict(calls=count, paired=len(values),
                            median_s=percentile(values, .5), p95_s=percentile(values, .95),
                            max_s=max(values) if values else None,
                            summed_round_trip_s=math.fsum(values))
    return dict(schema=SCHEMA, sources=sources, before=before, groups=groups,
                total_calls=sum(counts.values()), paired_results=sum(map(len, samples.values())),
                unpaired_calls=len(pending), anomalies=dict(anomalies), compactions=compactions,
                covered_round_trip_union_s=intervals_union(intervals),
                scope='Explicit input sessions only. Outer exec batches may yield or contain nested tools. '
                      'Waits are intentional waiting. Sum of round trips is not elapsed project time. '
                      'Inference, nested-tool attribution, billing and scientific validity are not inferred.',
                payloads_emitted=False)


def summarize_activity(path, max_bytes=128*1024**2):
    if Path(path).stat().st_size > max_bytes:
        raise ValueError('activity-byte limit exceeded')
    with Path(path).open('rb') as stream:
        raw = stream.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError('activity-byte limit exceeded during read')
    data = json.loads(raw)
    if not isinstance(data, (dict, list)):
        raise ValueError('activity object or items array required')
    items = data if isinstance(data, list) else data.get('items', [])
    if not isinstance(items, list):
        raise ValueError('activity items must be an array')
    types, statuses = collections.Counter(), collections.Counter()
    positions, duplicates, truncated, missing = set(), 0, 0, 0
    for ordinal, row in enumerate(items):
        if not isinstance(row, dict):
            raise ValueError('activity item must be an object')
        if (not isinstance(row.get('type', 'unknown'), str) or not isinstance(row.get('status', 'unknown'), str)
                or not (row.get('sourceThreadId') is None or isinstance(row.get('sourceThreadId'), str))):
            raise ValueError('invalid activity identity/type/status')
        if type(row.get('position')) is not int:
            missing += 1
            key = ('unidentified', ordinal)
        else:
            key = ('positioned', row.get('sourceThreadId'), row['position'])
        if key in positions:
            duplicates += 1
            continue
        positions.add(key)
        types[row.get('type', 'unknown')] += 1
        statuses[row.get('status', 'unknown')] += 1
        truncated += bool(row.get('textTruncated'))
    return dict(items=len(positions), types=dict(types), statuses=dict(statuses),
                duplicate_positions=duplicates, missing_position_items=missing, truncated_summaries=truncated,
                scope='App event summaries; event counts are not raw API calls or error rates.')


def render(report):
    rows = ''.join('<tr><th>'+html.escape(name)+'</th>'+''.join(
        '<td>'+html.escape(str(g[key] if g[key] is not None else 'unknown'))+'</td>'
        for key in ('calls', 'median_s', 'p95_s', 'summed_round_trip_s'))+'</tr>'
        for name, g in report['groups'].items())
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tool Flow</title><style>body{margin:0;font:14px/1.6 system-ui;color:var(--foreground,#172033);background:transparent}h2{font-size:20px}table{border-collapse:collapse;width:100%;font-size:12px}th,td{border-bottom:1px solid var(--border,#ddd);padding:8px;text-align:left;overflow-wrap:anywhere}.table{overflow:auto}p{max-width:76ch}details{margin:18px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h2>Tool-call evidence</h2><p>'''+str(report['total_calls'])+''' calls; '''+str(report['paired_results'])+''' paired results. Payload content is omitted.</p><div class="table"><table><thead><tr><th>Tool</th><th>Calls</th><th>Median s</th><th>p95 s</th><th>Σ round trips s</th></tr></thead><tbody>'''+rows+'''</tbody></table></div><p>'''+html.escape(report['scope'])+'''</p><details><summary>Evidence and limitations</summary><pre>'''+html.escape(json.dumps(report,indent=2))+'''</pre></details></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', action='append', type=Path, default=[])
    parser.add_argument('--activity', type=Path)
    parser.add_argument('--before')
    parser.add_argument('--max-bytes', type=int, default=1024**3)
    parser.add_argument('--max-calls', type=int, default=200000)
    parser.add_argument('--json', type=Path)
    parser.add_argument('--html', type=Path)
    args = parser.parse_args()
    if not args.log and not args.activity:
        parser.error('supply explicit --log or --activity inputs')
    if args.max_bytes <= 0 or args.max_calls <= 0:
        parser.error('resource limits must be positive')
    try:
        report = summarize_logs(args.log, before=args.before, max_bytes=args.max_bytes,
                                max_calls=args.max_calls)
        if args.activity:
            report['activity'] = summarize_activity(args.activity, args.max_bytes)
        serialized = json.dumps(report, indent=2, allow_nan=False)+'\n'
        for path, text in ((args.json, serialized), (args.html, render(report))):
            if path:
                with path.open('x', encoding='utf-8') as stream:
                    stream.write(text)
        if not args.json:
            print(serialized, end='')
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps(dict(status='unsupported_or_invalid_input', error=str(error))))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
