# Intent: Agent Skills Component

Status: Implementation delivered in PR #3; partial Lab 4 demonstration documented
in PR #4. Updated 2026-11-22 against the implementation and recorded run results.
Original intent written 2026-11-18 in PR #2.

## Problem

The original six-component mini coding agent could not discover, select, or
follow reusable folder-based skills. PR #3 integrated the existing skill files
into the request loop as a seventh component.

## Goal

Select relevant skills from a user prompt or an execution-time need, expose their
instructions to the model through the existing loop, and record the prompt,
similarity decision, and resulting tool activity. The delivered component does
this with lexical scoring and a separate JSON-lines log; instruction loading and
logged activity do not establish successful workflow completion.

Demonstrate the component by reusing the existing Lab 5 skills, `delegate` and
`hook-check`, as applicable to Lab 4. PR #4 records a no-match request and two
requests that activated `delegate`; it does not demonstrate `hook-check` execution
or a complete, correct Lab 4 submission.

## Scope And Boundaries

- Reuse the current Python/Ollama agent, tool permissions, and session storage.
- Support folder skills without adding a hosted service or embedding dependency.
- Preserve existing CLI behavior and sessions that predate skills.
- Do not treat Markdown as executable code or bypass tool approval.
- Do not recreate the full Claude specialist-agent or hook runtime.
- Child agents remain bounded and read-only and receive no skill registry.
- Keep this documentation update separate from code changes or skill adaptation.

## Success

A relevant lexical prompt activates the expected skill, an unrelated prompt does
not, and the model can request a known skill during execution with `use_skill`.
The regression tests cover routing, request-scoped instructions, logging, and
unchanged approval checks.

Full demonstration success still requires independently checked Lab 4 output.
[LAB4_RUN.md](LAB4_RUN.md) reports an incorrect grid, failed Windows shell
commands, and specialist files missing required frontmatter. It records useful
partial evidence, not a solved lab. Stronger provenance and completion tracking
from the original plan also remain unimplemented; see [spec.md](spec.md).

## Required Inputs

The assignment reference is now supplied in
[docs/lab4-instructions.md](docs/lab4-instructions.md). Lab 4 concerns context
engineering configuration for strategies 1 and 4, not environment code or
Q-learning. The run used a separate Git workspace and compared output with the
team's original Lab 4 repositories.

The full external sessions, generated files, and answer-key repositories are not
included here; [LAB4_RUN.md](LAB4_RUN.md) contains commands, excerpts, and reported
comparisons. Completing or reproducing the demonstration requires those resources
and the applicable Claude/AIMA/hook prerequisites. Preserve both existing skills
unless adaptation is authorized.

See [spec.md](spec.md) for requirements and [plan.md](plan.md) for execution tasks.