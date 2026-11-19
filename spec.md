# Specification: Agent Skills Component

Status: Draft requirements derived from the assignment, 2026-11-18.
Technical choices in the plan are proposals pending review.

## Requirements

| ID | Requirement And Acceptance Criterion |
| --- | --- |
| REQ-001 | Discover workspace-local folder skills in `skills/<name>/SKILL.md` and `skill/<name>/skill.md`, accepting either filename casing on case-sensitive systems too. Extract a unique name, description, relative path, and body. Missing roots mean an empty registry; invalid, duplicate, or unreadable entries produce diagnostics without crashing the agent. |
| REQ-002 | Compare each normal user prompt with skill names/descriptions using a documented, deterministic similarity algorithm. Record every candidate score, threshold, selected skill or no-match decision, and tie-break reason. Choose at most one automatic skill per request. A named skill request takes precedence and is identified as explicit rather than a similarity success. |
| REQ-003 | Allow the model to request a skill during execution using a validated tool with a skill name and a description of its current need. Apply the same selection, logging, and safety rules; do not activate the same skill repeatedly within one request. |
| REQ-004 | Load the selected instructions into a dedicated active-skill prompt section and keep them available for the remaining request. Let the model follow them through ordinary tools. Enforce existing approval, path, read-only, depth, and step limits; reject unsupported prerequisites clearly. Never equate reading a skill file with completing its workflow. |
| REQ-005 | Persist the full initiating prompt, execution-time query if any, candidate scores, algorithm/configuration, decision, skill path/content hash, activation, related tool outcomes, and final status with timestamps and request/activation IDs. Distinguish loaded, started, completed, failed, and incomplete; final prose alone is not proof of completion. Record no-match and denied/failed actions too. |
| REQ-006 | Preserve existing agent behavior when no skills exist or match. Load legacy sessions safely, keep skill audit data separate from transcript rendering, isolate request-scoped active instructions, and maintain bounded delegation and read-only children. |
| REQ-007 | Reuse the existing Lab 5 skills, `delegate` and `hook-check`, as applicable when the mini agent attempts Lab 4. No new skill authoring is required. Supply the actual assignment, required project files, prompt, command/model configuration, session evidence, produced artifacts, and rubric-based verification. Report failures or missing prerequisites honestly; claim success only against the supplied Lab 4 criteria. |
| REQ-008 | Keep intent, specification, implementation plan, requirement/task traceability, and eventual execution evidence as project files representing SDLC stages. Document skill format, scoring, limitations, and a reproducible usage example. |

## Skill Format

The existing files use YAML-style frontmatter with `name` and `description`,
followed by Markdown instructions. Initially support a documented subset:
scalar names and single-line or folded/literal multiline descriptions. Use a
maintained YAML parser if broader YAML compatibility is needed; do not claim
general YAML support from an ad hoc parser. Do not silently truncate instructions:
reject oversized skills with a useful diagnostic and a documented size limit.

## Scenarios

1. A prompt matching a skill description activates its instructions before the
   first model call; subsequent actions follow existing tool permissions.
2. An unrelated prompt records a no-match decision and follows the original loop.
3. During a task, the model identifies a need, requests a named skill through
   `use_skill`, and receives its instructions for subsequent model calls.
4. A skill references unavailable files or unsupported specialist agents; the
   agent records the blocker rather than claiming successful execution.
5. The supplied Lab 4 task is attempted using the applicable existing `delegate`
   and `hook-check` workflows, and its result is checked against the assignment,
   not merely the agent's final answer.

## Open Inputs And Release Gate

The Lab 5 skills are already supplied in `skills/delegate/SKILL.md` and
`skills/hook-check/SKILL.md`; discovering or authoring a replacement is not a
prerequisite. The remaining inputs are the Lab 4 assignment/rubric and project
resources. The skills reference Claude/AIMA resources not present in this
workspace, so check their availability in the Lab 4 project before execution.
Obtain permission only if adapting their instructions becomes necessary.
Component work can proceed after design review; REQ-007 cannot be signed off
until the lab inputs are available and the actual demonstration is verified.