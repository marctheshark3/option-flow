"""Positive and negative controls for fixture behavior, not an agent-skill evaluation."""

import json
from pathlib import Path
import shutil
import tempfile

from verify import run_json, verify_delivery, verify_shared


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    manifest = json.loads(Path(__file__).with_name("manifest.json").read_text())
    original = root / "case-01" / "task"
    report = {"baseline": verify_shared(original, manifest, False)}
    with tempfile.TemporaryDirectory(prefix="option-flow-fixture-controls-") as temporary:
        control_root = Path(temporary)
        broken = control_root / "lock-only-removal"
        shutil.copytree(original, broken)
        text = (broken / "coordinator.py").read_text()
        begin = text.index("            with input_lock:\n")
        end = text.index("            completed = time.perf_counter()", begin)
        old = text[begin:end]
        unprotected = "\n".join(line[4:] for line in old.splitlines()[1:]) + "\n"
        (broken / "coordinator.py").write_text(text[:begin] + unprotected + text[end:])
        try:
            run_json(broken, "coordinator.py", "--workers", "4")
        except AssertionError:
            report["unprotected_shared_state_rejected"] = True
        else:
            raise AssertionError("Negative control unexpectedly preserved every identity")

        independent = control_root / "isolated-requests"
        shutil.copytree(broken, independent)
        text = (independent / "coordinator.py").read_text()
        text = text.replace('request_file = spool / "request.json"',
                            'request_file = spool / (candidate["id"] + ".json")')
        (independent / "coordinator.py").write_text(text)
        report["isolated_request_control"] = verify_shared(
            independent, manifest, True, original)

        false_timing = control_root / "changed-timing-only"
        shutil.copytree(original, false_timing)
        text = (false_timing / "coordinator.py").read_text()
        text = text.replace('"elapsed_ms": (completed - started) * 1000',
                            '"elapsed_ms": 0')
        (false_timing / "coordinator.py").write_text(text)
        try:
            verify_shared(false_timing, manifest, True, original)
        except AssertionError as error:
            assert "improvement threshold" in str(error), str(error)
            report["changed_reported_timing_rejected"] = True
        else:
            raise AssertionError("Changed reported timing falsely established improvement")

        changed_baseline = control_root / "changed-baseline"
        shutil.copytree(original, changed_baseline)
        with (changed_baseline / "coordinator.py").open("a") as file:
            file.write("\n# Different baseline revision\n")
        try:
            verify_shared(independent, manifest, True, changed_baseline)
        except AssertionError as error:
            assert "Baseline workload differs" in str(error), str(error)
            report["changed_baseline_rejected"] = True
        else:
            raise AssertionError("A changed baseline was accepted as original")

    report["delivery"] = verify_delivery(root / "case-02" / "task", manifest)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
