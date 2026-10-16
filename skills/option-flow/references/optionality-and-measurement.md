# Optionality and measurement

Use the model to decide where a useful experiment is blocked. The desired result is a better decision or delivered change, supported by evidence and proportionate cost. `NKσ/T` is a heuristic lens, not a calibrated productivity or economic-value score.

The project's author credits a Gene Kim presentation at an IT Revolution
conference as the inspiration for applying options thinking to bottlenecks.
The sources below include Kim's published explanation and Baldwin and Clark's
underlying research.

## What the variables mean

In [Gene Kim's explanation](https://itrevolution.com/articles/option-value-in-development-manufacturing-dora-metrics/), **N** counts independently workable modules, **K** counts parallel experiments per module, **T** is experiment-cycle duration, and **σ** describes uncertainty or volatility. Apply these meanings to a stated system boundary and proposed change. More files, branches, services, or agents do not establish more independent modules or experiments.

**N — independence.** Determine which implementations can change while other components continue using stable contracts. Check shared state, global configuration, locks, fixtures, ownership, and coordinated releases. Independent editing alone is insufficient: identify how candidates will be tested and incorporated into the whole system. A shared verification stage may constrain delivery even when implementation work is independent. [DORA's loosely coupled teams research](https://dora.dev/capabilities/loosely-coupled-teams/) focuses on independent change, testing, and deployment rather than a prescribed architecture.

**K — useful alternatives.** Count feasible trials of materially different hypotheses. Isolated workspaces establish operational separation; they do not establish statistical independence of outcomes. Candidates derived from the same assumptions may repeat the same mistake. Before adding trials, define an evaluator, resource budget, and selection rule. Include the incumbent as a candidate. Require essential correctness and compatibility, then compare the improvement relevant to the user. Reject unsuccessful replacements; never adopt every experiment merely because it produced an artifact.

**T — usable feedback.** Start and stop the clock at explicit events. Include setup, waiting, execution, retries, validation, interpretation, and the decision. Record what is estimated and what is observed. For heterogeneous modules, describe each module's feasible trial capacity and cycle duration; multiplying global averages can obscure a slow or coupled boundary.

**σ — a consequential unknown.** Identify an assumption whose resolution could change the decision, plausible outcomes, and evidence that would distinguish them. Do not assign an arbitrary numerical uncertainty multiplier. In the underlying theory, σ describes dispersion of possible design values. [Baldwin's retrospective, section 3.3](https://academic.oup.com/icc/article/32/1/11/6868533), explains why practitioners could not reliably estimate it. A named unknown is usually more defensible than a scalar. Flaky feedback and operational failures require investigation; increasing them is not a way to increase useful optionality.

## Keep two clocks

Measure **time to a useful experimental decision** separately from **time to an accepted or delivered change**. State the start and finish events for both. Fast candidate generation can shorten the first while a growing review or integration queue lengthens the second. Use representative work and record waits, handoffs, and rework, following [DORA's value-stream guidance](https://dora.dev/guides/value-stream-management/).

When stages overlap, calculate elapsed time from timestamps or the critical path. Do not add overlapping durations. Keep human attention and aggregate compute cost separate from wall time: three workers running for one hour consume about three worker-hours while one hour elapses.

## Account for selection, costs, and queues

[Baldwin and Clark's model, pp. 194–200](https://homepages.cwi.nl/~storm/teaching/reader/BaldwinClark06.pdf), values the ability to retain superior outcomes and discard inferior ones. Its gross option-value expression is `Σ σ_j Q(k_j)`, where `Q(k)` is the expected best nonnegative result from independent standard-normal trials. Additional trials have diminishing returns. Account separately for architecture, experiment, integration, and testing costs. The model does not validate linear value growth in K.

Investigate a shared queue before increasing arrivals. Concurrency can consume scarce capacity and make feedback slower. [Little's original paper](https://pubsonline.informs.org/doi/abs/10.1287/opre.9.3.383) relates average work in progress, throughput, and elapsed time under its applicable conditions; reducing work in progress does not guarantee unchanged throughput. For runtime constraints, inspect utilization, saturation, and errors using [Gregg's USE method](https://www.brendangregg.com/usemethod.html), including pools and software limits.

Compare alternatives under equivalent workloads, acceptance criteria, environments, and resource budgets. Note cache state and other material confounders. Choose an intervention that tests a plausible mechanism, then reassess the whole outcome and its cost. More activity alone is not evidence of improvement.

*Source check:* The linked article's generated visualization implements a different function that increases with T. Inspect implemented equations and units before treating a plot as evidence. No copied illustration is needed.
