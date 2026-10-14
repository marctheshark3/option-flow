"""Deterministic local-validation and acceptance workflow, in virtual milliseconds."""

import argparse
import hashlib
import heapq
import json
from pathlib import Path


def simulate(changes: list[dict], policy: dict) -> dict:
    events = []
    sequence = 0
    trace = []
    accepted = []
    feedback = []
    local_slots = [0, 0]
    gate_available = 0
    local_work = 0
    gate_work = 0
    repair_work = 0
    gate_rejections = 0

    def schedule(at: int, kind: str, change: dict, repaired: bool = False) -> None:
        nonlocal sequence
        sequence += 1
        heapq.heappush(events, (at, sequence, kind, change, repaired))

    def schedule_recheck(ready: int, change: dict) -> None:
        nonlocal local_work
        slot = min(range(2), key=lambda item: local_slots[item])
        start = max(ready, local_slots[slot])
        finish = start + 30
        local_slots[slot] = finish
        local_work += 30
        trace.append({"at_ms": start, "stage": "recheck-start", "change": change["id"]})
        schedule(finish, "ready-for-gate", change, repaired=True)

    for change in changes:
        slot = min(range(2), key=lambda item: local_slots[item])
        start = local_slots[slot]
        finish = start + policy["local_ms"]
        local_slots[slot] = finish
        local_work += policy["local_ms"]
        trace.append({"at_ms": start, "stage": "local-start", "change": change["id"]})
        schedule(finish, "local-result", change)

    while events:
        now, _, kind, change, repaired = heapq.heappop(events)
        trace.append({"at_ms": now, "stage": kind, "change": change["id"]})
        defect = change["defect"]
        if kind == "local-result":
            feedback.append({"change": change["id"], "at_ms": now})
            detected = defect is not None and defect in policy["checks"]
            if detected:
                # A local diagnosis enables a small repair and the complete recheck.
                repair_work += 10
                schedule_recheck(now + 10, change)
            else:
                schedule(now, "ready-for-gate", change, repaired=False)
        elif kind == "ready-for-gate":
            gate_start = max(now, gate_available)
            duration = 90 if defect is not None and not repaired else 10
            gate_available = gate_start + duration
            gate_work += duration
            trace.append({"at_ms": gate_start, "stage": "gate-start", "change": change["id"]})
            schedule(gate_available, "gate-result", change, repaired=repaired)
        elif kind == "gate-result":
            if defect is not None and not repaired:
                gate_rejections += 1
                # A late rejection requires re-preparing the change and rerunning checks.
                repair_work += 40
                schedule_recheck(now + 40, change)
            else:
                accepted.append({"change": change["id"], "accepted_at_ms": now, "gate_passed": True})

    encoded_workload = json.dumps(changes, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema_version": 1,
        "kind": "deterministic-discrete-event-simulation",
        "unit": "virtual ms",
        "resources": {"local_slots": 2, "acceptance_slots": 1},
        "workload_sha256": hashlib.sha256(encoded_workload).hexdigest(),
        "change_count": len(changes),
        "mean_first_feedback_ms": sum(item["at_ms"] for item in feedback) / len(feedback),
        "accepted_delivery_ms": max(item["accepted_at_ms"] for item in accepted),
        "accepted_change_count": len(accepted),
        "acceptance_rejections": gate_rejections,
        "work_ms": {"local_validation": local_work, "acceptance": gate_work, "repair": repair_work},
        "feedback": feedback,
        "accepted": accepted,
        "trace": sorted(trace, key=lambda item: item["at_ms"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=("complete", "compact"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).parent
    policies = json.loads((root / "policies.json").read_text())
    changes = json.loads((root / "changes.json").read_text())
    record = simulate(changes, policies[args.policy])
    record["policy"] = args.policy
    encoded = json.dumps(record, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if record["accepted_change_count"] == len(changes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
