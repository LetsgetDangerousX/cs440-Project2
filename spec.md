# Specification: Agent Skills Component

Status: As implemented in PR #3, with partial Lab 4 evidence from PR #4.
Updated 2026-11-22. Original requirements were written 2026-11-18 in PR #2.
This revision distinguishes delivered behavior from unmet original commitments;
it does not declare all original acceptance criteria satisfied.

## Requirements And Delivered Behavior

| ID | Requirement And Current Implementation |
| --- | --- |
| REQ-001 | Discover immediate folders under workspace-root `skills/` and `skill/`. Accept a single file whose name lowercases to `skill.md`; extract name, description, relative path, and body. Missing roots yield an empty registry. Invalid metadata, empty bodies, oversized/unreadable files, ambiguous filenames, and resolved paths outside the workspace are skipped with registry diagnostics. Duplicate names retain the first valid entry and diagnose later entries. Directory-enumeration failures are not handled as recoverable diagnostics. |
| REQ-002 | Compare each normal user prompt against skill names/descriptions with deterministic lexical cosine similarity. Log all candidate scores, threshold, selected name or no-match, and decision reason. Automatically activate at most one skill per request. The default threshold is `0.2`; ties use the skill name. There is no explicit user `skill:<name>` directive or named-request precedence. |
| REQ-003 | Provide `use_skill(name, query)` when skills are available. Validate a known exact name, a nonempty need description, and that the skill is not already active. Log query similarity for valid calls, but activate the requested name regardless of its score or the scored winner. The call consumes an ordinary tool step; multiple different skills may be active. |
| REQ-004 | Add full cached skill bodies to a dedicated active-instructions section outside transcript clipping, retaining them for the request. Instructions guide the model through ordinary tools, with existing path, approval, read-only, depth, and step checks unchanged. Loading is not workflow completion; unsupported prerequisites are not automatically detected or separately validated. |
| REQ-005 | Append timestamped `prompt`, `similarity`, `skill_activated`, and `skill_executed` events to `.mini-coding-agent/skills.log`, correlated by request and session IDs. Record full initiating prompts and valid execution-time queries, scores, algorithm, threshold, activation name/path/trigger, abbreviated tool activity, and abbreviated final text. This is activity logging, not the originally planned full provenance and verified lifecycle audit. See the audit contract and gaps below. |
| REQ-006 | Preserve the existing loop, tools, and JSON session format when no skills exist or match. Active instruction sections clear before and after requests, on reset, and are empty on construction/resume. Skills are not embedded in session JSON or restored as active on resume. Default delegated children are bounded/read-only and receive no skills or skill log. Ordinary historical tool results may still appear in the transcript. |
| REQ-007 | Reuse the unchanged Lab 5 `delegate` and `hook-check` skills where applicable to the supplied Lab 4 assignment. The reference handout and a real Ollama attempt are now recorded, but only partial configuration work was attempted. The run demonstrated no-match and automatic `delegate` activation, not `hook-check` execution or a complete Lab 4 solution. Full rubric acceptance remains open. |
| REQ-008 | Maintain intent, specification, plan, task/requirement traceability, and execution evidence as SDLC project files. PR #4 added skill documentation and reproduction steps to `README.md` and evidence to `LAB4_RUN.md`. `EXAMPLE.md` remains the original generic agent walkthrough, not a skills example. This revision updates the SDLC status without treating traceability coverage as implementation or lab sign-off. |

## Discovery And Skill Format

`SkillRegistry` reads metadata and bodies at agent construction, not on every
request or activation. It scans `skills/` before `skill/`, sorting immediate
folders by name within each root. Folder names need not equal metadata names;
metadata names are exact, case-sensitive registry keys. Diagnostics are stored
in `SkillRegistry.diagnostics`, not automatically displayed by the CLI or written
to the skills log.

The standard-library parser supports a limited YAML-style frontmatter subset:
scalar `name` and `description` values, optional surrounding quotes, and folded
or literal description blocks (`>`, `|`, `>-`, `|-`). This is not general YAML.
Files must have `---` delimiters, both metadata fields, and a nonempty body.
The limit is **20,000 characters for the entire decoded file**, not just the
body. Bodies are stripped of leading/trailing whitespace, cached, and injected
without transcript clipping.

Activation does not reread the file, revalidate its path, or compute a hash.
There is no separate active-skill count or aggregate instruction-size limit.

## Selection Contract

1. Lowercase the query and each skill's `name + description`; count tokens
   matching `[a-z0-9]+` after removing the fixed `STOPWORDS` set in
   [mini_coding_agent.py](mini_coding_agent.py).
2. Compute cosine similarity of the token-count vectors; empty vectors score
   zero. Round each score to four decimal places before sorting and threshold
   comparison.
3. Sort by descending rounded score and then case-sensitive skill name. Select
   the first strictly positive score at or above `0.2`. Empty/stopword-only
   queries produce `empty query` when candidates exist; an empty registry
   produces `no match`.
4. Log `above threshold`, `tie broken by name`, `empty query`, or `no match`.
   Automatic activation uses trigger `auto`; its similarity event uses `prompt`.
5. For a valid `use_skill` call, log the same scoring result with trigger
   `use_skill` and the `requested` name, then activate that exact name. The
   similarity event's `selected` name is the scoring result and may differ from
   the activation.

The threshold is fixed by the shipped default and exercised by
[tests/test_skill_scoring.py](tests/test_skill_scoring.py); no standalone
calibration report was supplied. Matching is lexical, not semantic: synonyms and
incidental name mentions have no special treatment.

## Audit Contract And Unmet Original Commitments

The append-only JSON-lines skills log is separate from session JSON and
transcript rendering. Each event contains `ts`, `event`, `request_id`, and
`session_id`. A no-match request records `prompt` and `similarity` only.
Each activated skill records its name, path, and trigger, then receives a
`skill_executed` event when request finalization runs, even if no tools ran or
the request failed.

Activity collected while a skill is active is associated with every active skill,
not proven to be caused by any particular instruction. Per-tool argument JSON
and result text are each clipped to 300 characters; final text is clipped to
500. The session transcript stores ordinary tool arguments and returned output
separately; returned tool output is already subject to the existing 4,000-character
limit. Individual activity entries have no timestamp or activation ID.

Unlike the original REQ-005 acceptance target, the implementation does **not**
record skill content/hashes, activation IDs, structured loaded/started/completed/
failed/incomplete states, or verified completion conditions. Validation failures
occur before `tool_use_skill` logs query similarity; they are visible in ordinary
tool history, and in active-skill activity only if a skill was already active.
An exception during model execution finalizes active-skill logs with generic
failure text rather than a structured exception outcome.

`skill_executed` means the request ended while those instructions were active;
it is not evidence that the workflow or Lab 4 succeeded. Reset clears session
history/memory and active instructions but does not erase the separate skills log.
Default child sessions are saved without skills, and the parent delegate result
does not include a child session ID for audit correlation.

Other unmet original commitments include explicit user-name precedence,
per-activation file revalidation, aggregate activation bounds, fully recoverable
discovery failures, and comprehensive skill-specific resume/delegation evidence.
These remain limitations, not silently satisfied acceptance criteria.

## Scenarios And Evidence

1. A matching prompt injects a skill body before the first model call and retains
   it across turns; the next unrelated request omits the active body.
2. An unrelated prompt logs no-match and runs the existing agent loop.
3. A valid `use_skill` call makes a named skill available in subsequent prompts;
   unknown names, empty queries, and repeated activations are rejected.
4. Approval-denied actions remain denied and are logged as activity when a skill
   is active. A skill referencing unavailable tools or incompatible shell
   commands can still fail; the model is responsible for attempting its steps.
5. The Lab 4 attempt wrote an incorrect grid description, exhausted six steps
   while following incompatible shell instructions, and later wrote three
   specialist files missing Claude frontmatter.

Model-independent evidence is in
[tests/test_skills.py](tests/test_skills.py) and
[tests/test_skill_scoring.py](tests/test_skill_scoring.py), alongside existing
session/delegation tests in
[tests/test_mini_coding_agent.py](tests/test_mini_coding_agent.py).
These tests do not establish real-model correctness.

## Lab 4 Inputs And Release Gate

[docs/lab4-instructions.md](docs/lab4-instructions.md) now supplies the reference
assignment: configure context engineering strategies 1 and 4 for the 4x4 vacuum
robot problem, with appropriate files and a project-structure README. Environment
implementation and Q-learning are outside this lab's scope.

[LAB4_RUN.md](LAB4_RUN.md) records three requests on 2026-11-19 using Ollama
`qwen3.5:4b` in a separate Git workspace, with `--approval auto` and a
900-second timeout. Requests 1 and 2a used six steps; request 2b used fifteen.
This differs from the plan's proposed `--approval ask` demonstration; the CLI
default remains `ask`, and `auto` permits arbitrary model shell commands/writes.

Recorded outcomes include `delegate` scores of `0.4518` and `0.3525`, a
no-match request, Windows Command Prompt incompatibilities, incorrect grid
content, and missing specialist frontmatter. Full external logs/artifacts and
the team's answer-key repositories are not committed here; excerpts and reported
comparisons cannot substitute for independently checking those resources.

REQ-007 remains partial until the grid and specialist configuration are corrected,
strategy 1 hook/context configuration and applicable `hook-check` execution are
demonstrated, the required README is verified, and the complete submission is
checked against the handout. No skill rewrite or new lab run is part of this
documentation reconciliation.
