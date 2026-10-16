# Option Flow

An agent skill for finding and resolving bottlenecks in code, tools, and
development feedback. It helps an agent identify the limiting mechanism, try a
proportionate intervention, and verify the useful outcome and cost.

An IT Revolution conference presentation by **Gene Kim**, attended by this
project's author, inspired Option Flow's use of options thinking to reduce
bottlenecks. His
[published explanation of option value](https://itrevolution.com/articles/option-value-in-development-manufacturing-dora-metrics/)
provides related background.

The skill uses `(N × K / T) × σ`: independent modules, parallel experiments,
experiment duration, and uncertainty. The formula organizes questions about
optionality. Decisions depend on evidence, acceptance criteria, and costs.

## Use it

After installation, try:

> Use $option-flow to find why changes to this tool take so long to validate.
> Fix the limiting step and compare the result without weakening required checks.

For an investigation:

> Use $option-flow to diagnose this workflow. Return the evidence and a proposed
> experiment; keep this pass read-only.

For a new implementation:

> Use $option-flow to identify the uncertain implementation choice, define a
> stable interface, and compare affordable alternatives before committing to one.

The result explains the outcome, constraint, evidence, intervention, comparison,
cost, limitations, and adoption decision. It keeps time to useful experimental
feedback separate from time to an accepted or delivered change.

## Install

The complete package is [skills/option-flow](skills/option-flow). Install that
directory using your agent's skill installer. In Codex, you can ask:

> Install option-flow from https://github.com/marctheshark3/option-flow,
> using the skills/option-flow directory.

Keep the package's references and license together with `SKILL.md`. Codex UI
metadata is included in `agents/openai.yaml`; the workflow itself does not require
a particular model, connector, external service, or private skill.

See the [official skill documentation](https://learn.chatgpt.com/docs/build-skills)
for discovery and installation in your environment. Existing agent permissions
and the scope of the user's request apply to actions taken with the skill.

## What the model means

The [measurement reference](skills/option-flow/references/optionality-and-measurement.md)
explains independence, useful alternatives, two clocks, uncertainty, selection,
costs, and queues, with primary sources. It treats the formula as a directional
guide rather than a calibrated productivity or economic-value score.

## Development and evaluation

The skill is instructions and a reference, with no runtime dependency. The
synthetic evaluation fixtures use Python 3.10 or newer and its standard library.
They exercise executable behavior; they do not prove effectiveness in production.

Run the repository checks:

```bash
python3 dev/check.py
```

See [evals/README.md](evals/README.md) for independent forward-testing. Keep raw
task artifacts separate from evaluator expectations when testing an agent.

Initial forward tests on October 14, 2026 used independent agents given the skill
and raw task artifacts, without the evaluator's expected outcomes. One agent
isolated shared request state and improved the synthetic batch while preserving
all result identities, scores, and hashes. The other retained complete validation
after finding that earlier local responses delayed final accepted delivery and
increased rework. Both passed independent artifact verification and scope review.
These are bounded synthetic results, not production evidence or a controlled
comparison against agents without the skill.

## License

MIT. The included instructions, reference, and synthetic fixtures are original
work. Linked research remains under its authors' licenses; no source screenshots
or article text are bundled.
