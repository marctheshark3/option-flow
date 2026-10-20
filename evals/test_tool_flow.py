"""Synthetic controls for timing, identity, limits and payload omission."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).parents[1]/'skills/tool-flow/scripts/analyze.py'
spec=importlib.util.spec_from_file_location('analyze',SCRIPT)
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


def item(seconds,kind,ident,name='exec'):
    p=dict(type=kind,call_id=ident)
    if kind.endswith('call'):p.update(name=name,arguments='DO_NOT_EMIT_TOKEN_OR_COMMAND')
    return dict(timestamp=f'2026-01-01T00:00:{seconds:02d}Z',type='response_item',payload=p)


class ToolFlowTests(unittest.TestCase):
    def analyze(self,rows,**options):
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'input.jsonl'
            p.write_text(''.join(json.dumps(x)+'\n'for x in rows))
            return a.summarize_logs([p],**options)

    def test_overlap_is_not_summed_elapsed_and_payload_is_absent(self):
        report=self.analyze([item(0,'function_call','a'),item(1,'function_call','b'),item(3,'function_call_output','a'),item(4,'function_call_output','b')])
        self.assertEqual(report['groups']['exec']['summed_round_trip_s'],6)
        self.assertEqual(report['covered_round_trip_union_s'],4)
        self.assertNotIn('DO_NOT_EMIT',json.dumps(report))

    def test_duplicates_and_missing_results(self):
        report=self.analyze([item(0,'function_call','a'),item(0,'function_call','a'),item(2,'function_call_output','a'),item(3,'function_call_output','a'),item(4,'function_call','b')])
        self.assertEqual(report['total_calls'],2)
        self.assertEqual(report['unpaired_calls'],1)
        self.assertEqual(report['anomalies'],dict(duplicate_calls=1,duplicate_results=1))

    def test_cutoff_keeps_unpaired_call_honest(self):
        report=self.analyze([item(0,'function_call','a'),item(2,'function_call_output','a')],before='2026-01-01T00:00:01Z')
        self.assertEqual(report['unpaired_calls'],1)
        self.assertEqual(report['paired_results'],0)

    def test_separate_files_do_not_collide(self):
        with tempfile.TemporaryDirectory()as directory:
            paths=[]
            for n in range(2):
                p=Path(directory)/str(n);p.write_text(json.dumps(item(0,'function_call','same'))+'\n'+json.dumps(item(2,'function_call_output','same'))+'\n');paths.append(p)
            self.assertEqual(a.summarize_logs(paths)['total_calls'],2)

    def test_split_codex_sessions_deduplicate_explicit_identity(self):
        with tempfile.TemporaryDirectory()as directory:
            paths=[]
            for n in range(2):
                p=Path(directory)/str(n);p.write_text(json.dumps(dict(type='session_meta',payload=dict(id='shared'))) +'\n'+json.dumps(item(0,'function_call','same'))+'\n'+json.dumps(item(2,'function_call_output','same'))+'\n');paths.append(p)
            report=a.summarize_logs(paths)
            self.assertEqual(report['total_calls'],1)
            self.assertEqual(report['anomalies']['duplicate_calls'],1)

    def test_unknown_and_negative_time_are_not_zero_measurements(self):
        rows=[item(2,'function_call','a'),item(1,'function_call_output','a')]
        report=self.analyze(rows)
        self.assertEqual(report['anomalies']['negative_intervals'],1)
        self.assertIsNone(report['groups']['exec']['median_s'])

    def test_claude_adapter(self):
        rows=[dict(type='assistant',timestamp='2026-01-01T00:00:00Z',message=dict(content=[dict(type='tool_use',id='x',name='Bash',input=dict(command='DO_NOT_EMIT'))])),dict(type='user',timestamp='2026-01-01T00:00:02Z',message=dict(content=[dict(type='tool_result',tool_use_id='x',content='DO_NOT_EMIT')]))]
        report=self.analyze(rows)
        self.assertEqual(report['groups']['Bash']['median_s'],2)
        self.assertNotIn('DO_NOT_EMIT',json.dumps(report))

    def test_resource_limits_refuse_instead_of_partial_success(self):
        with self.assertRaises(ValueError):self.analyze([item(0,'function_call','a')],max_bytes=10)
        with self.assertRaises(ValueError):self.analyze([item(0,'function_call','a'),item(1,'function_call','b')],max_calls=1)

    def test_activity_dedup_and_no_latency_inference(self):
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'items.json';p.write_text(json.dumps([dict(position=1,type='command_execution',status='failed',text='diff changed'),dict(position=1,type='command_execution',status='failed')]))
            report=a.summarize_activity(p)
            self.assertEqual(report['items'],1)
            self.assertEqual(report['duplicate_positions'],1)
            self.assertNotIn('median',json.dumps(report))

    def test_numeric_timestamp_is_an_anomaly_not_crash(self):
        event=item(0,'function_call','a');event['timestamp']=123
        report=self.analyze([event])
        self.assertEqual(report['anomalies']['invalid_timestamps'],1)

    def test_missing_activity_identities_do_not_collapse(self):
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'items.json';p.write_text(json.dumps([dict(type='one'),dict(type='two')]))
            report=a.summarize_activity(p)
            self.assertEqual(report['items'],2)
            self.assertEqual(report['missing_position_items'],2)
            self.assertEqual(report['duplicate_positions'],0)

    def test_growing_activity_cannot_exceed_read_bound(self):
        from unittest.mock import patch
        import io
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'items.json';p.write_text('[]')
            with patch.object(Path,'open',return_value=io.BytesIO(b'['+b' '*10000+b']')):
                with self.assertRaises(ValueError):a.summarize_activity(p,max_bytes=4)

    def test_null_event_shapes_are_counted_without_crashing(self):
        rows=[dict(type='response_item',payload=None),dict(type='assistant',message=None),dict(type='session_meta',payload=None)]
        report=self.analyze(rows)
        self.assertEqual(report['anomalies']['invalid_event_shapes'],3)

    def test_nonstring_call_identity_is_not_a_dictionary_key(self):
        event=item(0,'function_call',{'invalid':True})
        report=self.analyze([event])
        self.assertEqual(report['anomalies']['missing_identity_or_time'],1)

    def test_positioned_identity_cannot_collide_with_missing_position(self):
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'items.json';p.write_text(json.dumps([dict(type='one'),dict(type='two',sourceThreadId='unidentified',position=0)]))
            self.assertEqual(a.summarize_activity(p)['items'],2)


if __name__=='__main__':unittest.main()
