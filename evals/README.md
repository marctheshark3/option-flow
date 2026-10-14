# Evaluation fixtures

These synthetic tasks exercise the decisions the skill should improve. They use
Python 3.10+ and its standard library. The installable skill has no runtime.

Run `python3 dev/check.py` from the repository root. This checks the package's
local references and runs executable positive and negative fixture controls.
It is not an agent evaluation or proof of production benefit.

## Independent forward-testing

Copy only a case's `task/` directory into a fresh isolated workspace. Give the
agent the candidate skill and this prompt, substituting the two paths:

> Use $option-flow at <skill-directory> to complete TASK.md in <task-copy>.
> Keep all work and records there; no publication or unrelated changes.

Keep `evaluator/`, this README, other trial results, and expected diagnoses out of
the agent's context. The [external rubric](evaluator/RUBRIC.md) assesses demonstrated
behavior and evidence, with no requirement for exact wording or a fixed tool path.

The cases cover improving a candidate-evaluation tool and researching a validation
policy. The latter reports deterministic **virtual milliseconds**, never host or
production timings. Its research-only scope is part of the evaluation.

After an agent finishes, verify its artifacts independently:

```bash
python3 evals/evaluator/verify.py --case shared --task-dir <case-01-copy> \
  --baseline-dir evals/case-01/task --require-improvement
python3 evals/evaluator/verify.py --case delivery --task-dir <case-02-copy>
```

The first verifier reruns both the fingerprinted original baseline and revised
program, measures subprocess wall time externally, checks every result using its
own oracle, and exercises concurrent invocations.
Its broad 25% improvement threshold is specific to the deliberately large
synthetic effect. It is not a universal target or statistical significance test.

Also review the agent's report against the rubric: automated fixture verification
alone does not establish supported diagnosis, scope, or honest claims. Preserve
raw trial records outside the public repository; publish only a deliberately
summarized account of the outcome and limitations.

To evaluate whether the skill helps beyond existing agent behavior, run the same
tasks without the skill under equivalent tools and budgets, with blind grading
and repeated runs where variation matters. Successful forward trials alone do
not establish that comparative advantage.
