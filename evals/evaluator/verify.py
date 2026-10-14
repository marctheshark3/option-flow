"""Independent output oracle and bounded runtime checks for the two fixtures."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_json(folder: Path, script: str, *args: str) -> dict:
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, str(folder / script), *args],
        cwd=folder,
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    if completed.returncode != 0:
        raise AssertionError(f"Program failed ({completed.returncode}): {completed.stderr}")
    record = json.loads(completed.stdout)
    # This measurement is owned by the evaluator, not the program under test.
    record["_verifier_elapsed_ms"] = elapsed_ms
    return record


def check_candidate_record(record: dict, candidates: list[dict]) -> None:
    expected = {}
    for candidate in candidates:
        canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
        expected[candidate["id"]] = {
            "candidate_id": candidate["id"],
            "score": sum((i + 1) * value for i, value in enumerate(candidate["values"])),
            "request_sha256": hashlib.sha256(canonical).hexdigest(),
        }
    results = record["results"]
    assert len(results) == len(expected), "Missing or duplicate results"
    assert {item["requested_id"] for item in results} == set(expected), "Wrong candidate identities"
    assert record["accepted_result_count"] == len(expected), "Not every result accepted"
    assert 1 <= record["workers"] <= 4, "Worker limit changed"
    for result in results:
        assert result["result"] == expected[result["requested_id"]], "Identity, score, or request hash mismatch"
        assert result["correct"] is True, "Correctness check failed"


def verify_shared(folder: Path, manifest: dict, require_improvement: bool,
                  baseline_folder: Path | None = None) -> dict:
    for name in ("backend.py", "candidates.json"):
        assert fingerprint(folder / name) == manifest["case-01"][name], f"Fixed workload changed: {name}"
    candidates = json.loads((folder / "candidates.json").read_text())
    runs = [run_json(folder, "coordinator.py", "--workers", "4") for _ in range(3)]
    for record in runs:
        check_candidate_record(record, candidates)
    with ThreadPoolExecutor(max_workers=2) as pool:
        concurrent = list(pool.map(lambda _: run_json(folder, "coordinator.py", "--workers", "2"), range(2)))
    for record in concurrent:
        check_candidate_record(record, candidates)
    measured = statistics.median(record["_verifier_elapsed_ms"] for record in runs)
    baseline = None
    if baseline_folder:
        for name in ("backend.py", "candidates.json", "coordinator.py"):
            assert fingerprint(baseline_folder / name) == manifest["case-01"][name], "Baseline workload differs"
        baseline_runs = [run_json(baseline_folder, "coordinator.py", "--workers", "4") for _ in range(3)]
        for record in baseline_runs:
            check_candidate_record(record, candidates)
        baseline = statistics.median(record["_verifier_elapsed_ms"] for record in baseline_runs)
    if require_improvement:
        assert baseline is not None, "Provide an unchanged baseline directory for a measured comparison"
        assert measured < baseline * 0.75, "Did not achieve the fixture's broad improvement threshold"
    return {"correct": True, "concurrent_invocations": 2,
            "measurement_boundary": "external subprocess start-to-exit wall time",
            "median_ms": measured,
            "reported_internal_median_ms": statistics.median(record["elapsed_ms"] for record in runs),
            "baseline_median_ms": baseline,
            "ratio": measured / baseline if baseline is not None else None}


def verify_delivery(folder: Path, manifest: dict) -> dict:
    for name in ("delivery_lab.py", "changes.json", "policies.json"):
        assert fingerprint(folder / name) == manifest["case-02"][name], f"Research-only fixture changed: {name}"
    complete = run_json(folder, "delivery_lab.py", "--policy", "complete")
    compact = run_json(folder, "delivery_lab.py", "--policy", "compact")
    for record in (complete, compact):
        assert record["kind"] == "deterministic-discrete-event-simulation"
        assert record["unit"] == "virtual ms"
        assert record["resources"] == {"local_slots": 2, "acceptance_slots": 1}
        assert record["accepted_change_count"] == record["change_count"] == 8
        assert len({item["change"] for item in record["accepted"]}) == 8
        assert all(item["gate_passed"] for item in record["accepted"])
    assert complete["workload_sha256"] == compact["workload_sha256"]
    assert compact["mean_first_feedback_ms"] < complete["mean_first_feedback_ms"]
    assert compact["accepted_delivery_ms"] > complete["accepted_delivery_ms"]
    assert compact["acceptance_rejections"] == 4
    assert complete["acceptance_rejections"] == 0
    return {"correct": True, "complete": {key: complete[key] for key in (
        "mean_first_feedback_ms", "accepted_delivery_ms", "acceptance_rejections", "work_ms")},
        "compact": {key: compact[key] for key in (
        "mean_first_feedback_ms", "accepted_delivery_ms", "acceptance_rejections", "work_ms")}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=("shared", "delivery"), required=True)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--require-improvement", action="store_true")
    parser.add_argument("--baseline-dir", type=Path)
    args = parser.parse_args()
    manifest = json.loads(Path(__file__).with_name("manifest.json").read_text())
    if args.case == "shared":
        result = verify_shared(args.task_dir.resolve(), manifest, args.require_improvement,
                               args.baseline_dir.resolve() if args.baseline_dir else None)
    else:
        result = verify_delivery(args.task_dir.resolve(), manifest)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
