---
name: option-flow
description: Find and resolve bottlenecks in code, tools, and development feedback when slow iteration, coupled changes, overloaded parallel work, or uncertain implementation choices obstruct a defined outcome.
---

# Option Flow

Remove the constraint preventing useful experiments or safe delivery. Improve a
defined outcome with evidence and proportionate effort. Match the work to the
request: research produces findings; implementation produces a verified change.
Routine work with a known direct solution does not need a separate investigation.

## Use optionality to ask better questions

The inspiration is `(N × K / T) × σ`: independently workable modules, parallel
experiments per module, experiment-cycle duration, and uncertainty. Use it as a
directional lens. It is not a calibrated productivity score or financial
valuation. Read [optionality and measurement](references/optionality-and-measurement.md)
when interpreting the model, planning concurrent trials, or comparing timings.

- **N:** Which implementations can change behind stable contracts? Inspect
  coordinated edits, shared state, locks, fixtures, and verification dependencies.
- **K:** Which materially different alternatives can be isolated and evaluated
  within the available resources? Agent, branch, and file counts are not evidence
  of independent experiments. Isolation does not guarantee uncorrelated outcomes.
- **T:** How long until the experiment yields a trustworthy decision? Include
  relevant setup, waiting, execution, retries, validation, and interpretation.
- **σ:** Which unknown could change the decision, and what evidence distinguishes
  the plausible outcomes? Record that uncertainty rather than invent a multiplier.

An experiment needs a hypothesis, a useful readout, and a decision it can affect.
Include the incumbent when comparing replacements; retaining it or rejecting a
candidate can be the right result. Define essential acceptance checks before
selection so faster candidates are not rewarded for weaker behavior.

## Find the limiting mechanism

Establish the user's outcome, what counts as finished, the system boundary, the
representative workload, and relevant quality and resource limits. Use existing
evidence before adding instrumentation. Missing observations remain unknown.

Trace representative work through setup, execution, waiting, handoffs, retries,
and rework. Keep two clocks: **time to useful experimental evidence** and **time
to an accepted or delivered result**. Record explicit start and finish events.
Keep wall time, human attention, and aggregate compute separate; do not sum
overlapping stages into an elapsed total.

Explain the mechanism behind a suspected constraint. A long wait could result
from saturation, batching, dependency, or missing context. Source inspection
supports hypotheses; observations support a bounded diagnosis. When explanations
compete, choose a small probe that could distinguish them. Inspect shared
capacity and coordination before adding parallel work.

For new code or tools, establish a stable seam and an inexpensive evaluator for
the consequential uncertain choice. Explore only the alternatives justified by
that choice, retaining a straightforward path when the answer is already known.

## Intervene and verify

Choose a proportionate, preferably reversible intervention that tests the
suspected mechanism. Examples include isolated fixtures, clearer tool arguments,
smaller reviewable batches, incremental verification, and bounded concurrency.
Consider architecture changes when their benefit justifies migration and upkeep.
Keep changes within the user's authorized scope.

Compare equivalent workloads, acceptance criteria, environments, and resource
budgets. Note material confounders such as warm caches, changed inputs, or tool
versions. Repeat when variation makes one run uninformative. Preserve required
correctness, compatibility, and verification; a failed or unverified candidate
does not establish a successful delivery improvement. When comparing unlike
budgets, report the tradeoff explicitly instead of claiming an equal-cost gain.

Check both clocks and the whole outcome. A shorter feedback loop can move the
queue into review or integration. Include failures, rework, attention, and compute
cost where relevant. Adopt, revise, or reject based on those observations. Treat
a new limiting boundary as a finding only when evidence supports it. Stop when
the requested outcome is handled.

## Make the result reviewable

Return a compact decision record: intended outcome, observed constraint and
evidence, intervention, comparable result, cost, limitations, and adoption
decision. Distinguish observations, estimates, and predictions. If evidence is
insufficient, state the missing observation and a useful next probe. A dashboard,
new service, fixed artifact directory, or scalar score is unnecessary.
