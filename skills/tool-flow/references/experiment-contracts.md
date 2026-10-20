# Experiment contracts

Keep a stable envelope for progress and failure. Preserve a reference runner and
scientific controls while making candidate parameters replaceable. Avoid copying
a runner, auditor, serializer and metadata writer for every small probe.

A useful receipt separates execution state (not entered, running, returned,
completed), validity (unknown, valid, invalid), outcome (unknown, negative,
positive) and adoption authority. An invalid byte control or resource-integrity
violation remains invalid even if retention later fails. Successful execution and
a passing audit can establish a valid negative result. Neither grants adoption.

For completed Boolean observations, accept true and false as values; require true
only for an actual control predicate. Missing, null, strings and integer 1 are
not Boolean observations. Partial stages can legitimately lack fields, provided
stage entry/progress makes that absence explicit. Do not invent measurements.

Before an expensive run, exercise complete positives and negatives, partial
startup, zero-work unknown, invalid controls, resource aborts, serialization and
retention failures. Compare the producer and auditor on the same literal records.
Preserve an earlier invalid cause. Check serializability before paid work and
retain returned work before subsequent checks can fail.

Bind a review to source, contract and input hashes; a changed dependency or
assumption invalidates that review. Cache review disposition, not a past claim
that today's mutable files are unchanged. Rehash current inputs at execution
boundaries and preserve original runtime/qualification identities. A reusable
orchestrator may invoke an existing audited supervisor, but must not silently
replace its native counters or qualification gates.

A compact current record needs outcome/initialization, incumbent evidence,
current hypothesis, next bounded probe, open objection, owner state and links to
history. Keep immutable receipts and history; compact entry points should reduce
rediscovery, not remove failed experiments. One complete review packet should
include the brief, exact delta, acceptance checks, prior objections and response.
