# Intent: Agent Skills Component

Status: Draft for review, 2026-11-18. Planning only; no implementation or lab run has occurred.

## Problem

The mini coding agent has six components but cannot discover, select, or follow
reusable folder-based skills. Existing skill files are not integrated into its
request loop.

## Goal

Add a seventh component that selects relevant skills from a user prompt or an
execution-time need, follows their instructions through existing tools, and
records the prompt, similarity decision, and execution evidence. Demonstrate
the component by reusing the existing Lab 5 skills, `delegate` and `hook-check`,
as applicable to Lab 4. Their instructions already exist; the missing work is
the component that discovers, selects, executes, and logs them.

## Scope And Boundaries

- Reuse the current Python/Ollama agent, tool permissions, and session storage.
- Support folder skills without adding a hosted service or embedding dependency.
- Preserve existing CLI behavior and sessions that predate skills.
- Do not treat Markdown as executable code or bypass tool approval.
- Do not recreate the full Claude specialist-agent or hook runtime.

## Success

A relevant prompt activates the expected skill, an unrelated prompt does not,
and the agent can request a skill after discovering a need during execution.
A reviewer can connect the original prompt to candidate scores, the selected
instructions, resulting tool actions, and independently checked Lab 4 output.

## Required Inputs

Supply the Lab 4 assignment and rubric, and provide its source files and
dependencies. These are prerequisites for the lab demonstration, not for
identifying or creating skills. Preserve both existing skills unless adaptation
is authorized.

See [spec.md](spec.md) for requirements and [plan.md](plan.md) for execution tasks.