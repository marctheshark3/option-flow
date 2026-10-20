# Log interpretation

Tool calls, shell events and scientific maps are different units. A code execution
call can compose several commands or MCP calls, then yield. A later wait can own
the remainder. A child session has its own calls. Report the observed scope and
cutoff and never add overlapping intervals as project elapsed time.

Codex JSONL uses response_item function_call/custom_tool_call and corresponding
outputs keyed by call_id. Claude JSONL uses message.content tool_use/tool_result
blocks. The helper uses explicit session_meta ids when present; otherwise each
input file is a distinct scope. Split Claude logs need normalization to a single
file if their pairing spans files. Missing timestamps or results stay unpaired.
Duplicate calls/results, malformed lines, incomplete tails and negative clocks
are reported separately. Invalid JSON lines can hide events; disclose incomplete
coverage rather than treating the summary as exhaustive.

The output's nearest-rank median and p95 measure harness round trips. Deliberate
waits/sleeps can dominate summed latency without being waste. Their duration says
nothing about whether the concurrent work was useful. The union of observed
intervals is covered tool time, not total engineering time or attention.

T3 activity is summarized context: status=failed can mean diff found changes or
rg found no matches. Truncated text can hide diagnostics. Inspect the consequential
result before classifying it. Do not turn text matches into a calibrated failure
rate. The analyzer emits neither tool arguments nor outputs; still review tool
names, source identities and any extra manual evidence before external sharing.

Use timestamps to define the two feedback clocks. Count review rework and source
versions when available, but do not estimate inference billing from context size.
Before/after comparisons require the same workload and acceptance checks. Warm
cache, changed inputs, concurrency and a different result criterion are confounders.
A synthetic fixture proves a bounded behavior, not an end-to-end speedup.
