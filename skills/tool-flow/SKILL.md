---
name: tool-flow
description: Audit agent tool-call histories and experiment workflows to find repeated failures, excess coordination, context churn, and slow feedback. Use for requests to analyze tool usage or improve an agent's execution loop; ordinary application profiling uses its own tools.
---

# Tool Flow

Make agent work produce useful, accepted evidence with less rework. Distinguish
slow computation from repeated authoring, tool failures, waiting and handoffs.
Keep the user's outcome and required checks intact.

## Inspect the actual work

Identify the requested outcome, representative session/time range, available
logs, resource limits and completion criterion. Use known project/session paths
or app search; do not search whole home directories for logs. A stopped campaign
stays stopped unless the user asks to resume it. An audit does not authorize
replaying spent experiments, changing services or messaging other sessions.

Prefer the app's thread-read/search tools for finding context and current state.
Read a bounded timeline and recover truncated items only when they affect the
finding. Batch independent reads, filter results before returning them to the
model, and keep mutations and dependent operations sequential.

For tool timing, use explicit local log files when available:

```bash
python3 scripts/analyze.py --log /path/to/session.jsonl \
  --before 2026-01-01T12:00:00Z --json analysis.json --html report.html
```

Paths are relative to this skill's directory. The helper streams Codex and Claude
JSONL, pairs call/result identities, bounds input bytes/calls, deduplicates within
session identity and omits payloads. Pass additional `--log` paths deliberately;
child calls are a separate scope, not automatically included. Use `--activity`
for a T3 items-array export when only event summaries are available. Outputs
must be fresh. The helper does not contact a service or execute logged commands.

Read [log interpretation](references/log-interpretation.md) before attributing
latency, failures, cost or speedup. Read [experiment contracts](references/experiment-contracts.md)
when producer/auditor or partial-result mismatches cause rework.

## Find the mechanism

Connect each finding to a source event or measured interval. Check whether a
nonzero result means a real tool error, an expected diff/no-match, or a valid
negative experiment. Separate observation validity, scientific outcome and
adoption. A Boolean false is not missing data; missing and not-yet-entered stages
need explicit semantics.

Keep two clocks: selection to useful evidence, and selection to accepted evidence.
Use absolute boundary events for elapsed time. Keep CPU, aggregate worker time,
waiting and attention separate. Missing shares remain unknown. Outer execution
batches may yield before their nested process completes; do not infer kernel or
physics latency from their round trips.

Use the options lens to decide where an intervention matters: N is independent
work behind stable contracts; K is feasible materially different trials; T is time
to a trustworthy decision; sigma is the named consequential uncertainty. This is
not a calibrated score. If available, Option Flow can guide broader architecture
or experiment choices; this skill does not require it.

## Improve the loop

Choose the smallest intervention that removes demonstrated rework. Common cases:
use a manifest instead of guessed paths; keep a compact current record with
history links; test result contracts before expensive work; reuse lifecycle code;
review changed hashes and assumptions; send one complete review packet instead
of repeated partial handoffs. Do not add reviewers or a framework just to make
an audit look thorough. Use delegation only when the user or repository workflow
authorizes it, with a bounded task and a concrete result.

Compare equivalent workloads and acceptance criteria. Include setup, failures,
serialization, reviews and delivery when claiming a faster loop. A GPU or Rust
implementation needs a measured compute bottleneck, sufficient independent work,
and a parity check; faster kernels do not establish faster accepted delivery.
Document numerical changes explicitly. Preserve reference implementations and
frozen results; new backends need their own qualification.

Return the finding, evidence, intervention, verification, cost, unknowns and
adoption decision. Generate a report only when it improves review; use the app's
HTML preview/render tools when available. Keep raw logs and private routing out
of published packages. Stop when the requested improvement is delivered or an
explicit external prerequisite remains.
