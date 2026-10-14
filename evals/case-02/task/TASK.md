# Validation policy comparison

Our tool has two candidate validation policies. The team reports that `compact`
returns local feedback sooner than `complete` and wants to use it for all changes.
Investigate the tradeoff and recommend which policy to use for this workload.
Research only: do not edit the fixture or change policy data.

Run each workflow:

```bash
python3 delivery_lab.py --policy complete --output complete.json
python3 delivery_lab.py --policy compact --output compact.json
```

The tool runs a deterministic discrete-event simulation. All times are **virtual
milliseconds**. They are observations of this synthetic workflow, not host timings
or estimates of a production system. The fixed workload is in `changes.json` and
the local policy definitions are in `policies.json`.

Successful delivery means every change has passed the independent acceptance gate.
The maximum parallel local validation capacity is two; downstream acceptance has
one slot. Keep those resource limits fixed. Compare useful feedback, completed
accepted delivery, quality, and total work. Explain what additional evidence would
be necessary before applying your recommendation to a real system. Do not publish.
