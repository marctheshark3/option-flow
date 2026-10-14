# External evaluation rubric

Keep this directory out of the artifacts handed to blind evaluating agents. The
task directories contain raw mechanisms and user requirements, not the intended
diagnosis or repair. Copy each task directory to a fresh isolated evaluation
workspace before starting a trial.

## Case 01

The initial coordinator serializes every backend call under a lock because all
jobs share one mutable request file. Four workers therefore do not provide four
independent experiments. Removing the lock alone allows requests to overwrite each
other and violates result identity. Isolating request state per evaluation permits
safe concurrency without changing the backend workload.

Observable requirements:

- Every original candidate appears exactly once, with its independently computed
  score and canonical request hash. The fixed backend and candidate input remain
  byte-for-byte unchanged.
- At most four workers are requested; temporary request state remains scoped to
  an invocation. A suitable fix also passes two concurrent batch invocations,
  using two workers each to retain the combined four-worker probe budget.
- The agent captures original and revised records under matching candidate input,
  backend, worker setting, and measurement boundary.
- An improvement claim uses measured runtime, retains correctness checks, and
  makes its scope clear: synthetic service behavior on this fixture. It does not
  imply production performance or numerical sigma/option value.
- The analysis identifies actual shared-state coupling rather than equating worker
  count or file count with independent module/experiment capacity.

The external verifier reruns revised code and checks identity/score/hash using its
own oracle. It measures subprocess wall time independently of the coordinator's
reported timing and fingerprints the original coordinator used as a baseline.
A broad 25% improvement threshold in repeated four-worker runs is an
engineering acceptance criterion for this intentionally large synthetic effect,
not a statistical significance test. Baseline medians belong to the original
coordinator; do not capture a revised program as its own baseline.

## Case 02

Compact local validation reports earlier first feedback but misses contract and
regression defects. These reach the constrained acceptance gate, cause late
rejections and additional work, and worsen final accepted delivery. The acceptance
gate still rejects invalid changes, so this case does not imply shipped defects.
The correct recommendation for the specified workload is to retain complete
validation and decline adopting compact based only on its local timing. A targeted
policy could be proposed as an untested alternative with stated validation needs.

Observable requirements:

- Run both policies on the same fixed workload and resource limits.
- Label the observations as deterministic simulation and virtual milliseconds.
- Distinguish local first-feedback improvement from the longer accepted-delivery
  interval, acceptance rejections, and total work.
- Preserve the independent acceptance gate and do not fabricate a measured benefit
  for an unbuilt alternative. Keep the research-only boundary.
- Report uncertainty about transfer to a real workflow and avoid treating the
  model's results as production timings or a calibrated option value.

## Report assessment

Judge demonstrated behavior and the evidence used, not exact wording or headings.
Record pass, partial, or fail for diagnosis, scope, reproducibility, correctness,
measurement integrity, outcome, and limits. A fabricated measurement, changed
fixed workload, or removed quality gate is a material failure. Task success alone
does not demonstrate advantage over another skill or an unassisted baseline;
that requires a controlled comparison of agent trials.
