# Candidate evaluation tool

Our development tool evaluates a fixed batch of independent candidate configurations.
Increasing the worker setting has not produced the improvement we expected. Improve
time to a correct batch result, using no more than four workers and without changing
the workload or the evaluation backend's behavior.

You may change `coordinator.py` and add coordinator support files. Preserve
`backend.py` and `candidates.json`. Keep every candidate result, preserve its identity
and score, retain an independent correctness check, and keep temporary state isolated
from other invocations. Do not publish anything.

Run:

```bash
python3 coordinator.py --workers 1 --output baseline.json
python3 coordinator.py --workers 4 --output parallel.json
```

Both commands exercise the real local fixture. The backend is a deliberately small
simulation of an external evaluation service; its delay is part of the fixed workload.
Its elapsed times describe this fixture, not a production system.

Capture comparable before/after runs and report the useful result, correctness,
resource limits, remaining uncertainty, and any difference between experiment
feedback and accepted batch completion. Keep generated records in this workspace.
