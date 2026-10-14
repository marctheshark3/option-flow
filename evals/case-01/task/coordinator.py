"""Coordinate a batch of candidate evaluations and preserve their results."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import tempfile
import threading
import time

import backend


def _expected(candidate: dict) -> tuple[int, str]:
    score = sum((i + 1) * value for i, value in enumerate(candidate["values"]))
    encoded = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
    return score, hashlib.sha256(encoded).hexdigest()


def run_batch(candidates: list[dict], workers: int) -> dict:
    started = time.perf_counter()
    results = []
    input_lock = threading.Lock()
    with tempfile.TemporaryDirectory(prefix="candidate-evaluation-") as temporary:
        spool = Path(temporary)

        def run_one(candidate: dict) -> dict:
            dispatched = time.perf_counter()
            with input_lock:
                acquired = time.perf_counter()
                request_file = spool / "request.json"
                request_file.write_text(json.dumps(candidate), encoding="utf-8")
                result = backend.evaluate(request_file)
            completed = time.perf_counter()
            expected_score, expected_sha256 = _expected(candidate)
            correct = (
                result["candidate_id"] == candidate["id"]
                and result["score"] == expected_score
                and result["request_sha256"] == expected_sha256
            )
            return {
                "requested_id": candidate["id"],
                "result": result,
                "correct": correct,
                "dispatched_ms": (dispatched - started) * 1000,
                "queue_wait_ms": (acquired - dispatched) * 1000,
                "feedback_ms": (completed - dispatched) * 1000,
                "completed_ms": (completed - started) * 1000,
            }

        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(run_one, candidates))
    completed = time.perf_counter()
    return {
        "schema_version": 1,
        "kind": "synthetic-runtime-observation",
        "workers": workers,
        "candidate_count": len(candidates),
        "runtime": platform.python_version(),
        "workload_sha256": hashlib.sha256(
            json.dumps(candidates, sort_keys=True).encode()
        ).hexdigest(),
        "elapsed_ms": (completed - started) * 1000,
        "accepted_result_count": sum(item["correct"] for item in results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, choices=(1, 2, 3, 4), default=1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    candidates = json.loads(Path(__file__).with_name("candidates.json").read_text())
    record = run_batch(candidates, args.workers)
    encoded = json.dumps(record, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if record["accepted_result_count"] == len(candidates) else 1


if __name__ == "__main__":
    raise SystemExit(main())
