"""Fixed synthetic service contract used by the candidate evaluation tool."""

import hashlib
import json
import time
from pathlib import Path


def evaluate(request_file: Path) -> dict:
    # Simulate waiting for the fixed backend to finish before it consumes a request.
    time.sleep(0.06)
    candidate = json.loads(request_file.read_text(encoding="utf-8"))
    score = sum((index + 1) * value for index, value in enumerate(candidate["values"]))
    encoded = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
    return {
        "candidate_id": candidate["id"],
        "score": score,
        "request_sha256": hashlib.sha256(encoded).hexdigest(),
    }
