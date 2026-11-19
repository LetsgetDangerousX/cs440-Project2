# Implementation Plan: Agent Skills Component

Date: 2026-11-18. Status: Proposed, not implemented.
Inputs: [intend.md](intend.md), [spec.md](spec.md), the existing agent and skills.

## Summary

Add a seventh component in the existing Python module: a `SkillRegistry` that
discovers skill metadata, ranks candidates, and loads instructions. Integrate
automatic selection into `MiniAgent.ask`, explicit execution-time selection into
the tool registry, active instructions into `prompt`, and structured audit events
into `SessionStore` persistence. Do not introduce a second agent loop.

## Technical Context

- Python 3.10+, Ollama, existing pytest/FakeModelClient helpers; no new runtime
  service. Keep metadata parsing within the specified subset unless a maintained
  YAML parser is deliberately selected and declared as a dependency.
- `MiniAgent.ask` controls model/tool turns; `run_tool` and `validate_tool`
  enforce permissions. These are the integration points, not shell execution of
  Markdown files.
- `build_prefix` is stable. Put changing active instructions in `prompt`, outside
  history clipping, and clear them between requests. Do not inject all skill bodies.
- `SessionStore` already saves JSON under `.mini-coding-agent/sessions/`.
  Add an optional `skill_events` collection with legacy-session defaults rather
  than new transcript roles that `history_text` cannot currently render.
- The Lab 5 skills already exist: `skills/delegate/SKILL.md` provides the bounded
  delegation workflow, and `skills/hook-check/SKILL.md` checks context-switcher
  hook routing. Reuse both as the component's initial skill catalog; do not
  create replacements. Check their referenced Claude/AIMA resources in the
  Lab 4 workspace before attempting the applicable workflow.

## Constraints And Guidelines

No project constitution, upstream architecture artifacts, or applicable migration
guidelines were supplied. This is a local component addition, not a rewrite.
Use the assignment specification and existing agent conventions as constraints:
retain one module, existing tool protocol, local storage, bounded execution, and
all permission checks. Do not add a framework, vector database, or custom
specialist runtime. The lab demonstration remains gated on actual lab inputs.

## Proposed Selection And Execution Contract

1. Discover immediate skill folders beneath both workspace-root `skills/` and
   `skill/`. Resolve and validate paths, including symlinks, with workspace
   containment rules. Sort results; reject duplicate names or ambiguous files.
2. Snapshot validated metadata per request. Tokenize names/descriptions and query
   with one documented lowercase word-token rule. Compute cosine similarity of
   token-count vectors using the standard library; empty vectors score zero.
   This is lexical similarity, not semantic understanding.
3. Start with a provisional threshold of `0.25`; calibrate using relevant,
   unrelated, and overlapping prompts before freezing it. Log the actual value.
   Select the highest eligible score; break ties by normalized skill name and
   path. A narrow, documented `skill:<name>` directive requests an exact name
   without guessing from incidental mentions. Unknown names produce diagnostics.
4. Add `use_skill(name, query)` for needs discovered after the initial prompt.
   Validate the name against the registry, score/log the query, and mark this as
   model-requested activation rather than threshold-based automatic selection.
   Load through one shared activation path; suppress repeated activation within
   the request and bound the active-skill count/content size.
5. Revalidate and read the complete body at activation, recording its content hash.
   Reject empty/oversized bodies or changed/unsafe paths. Keep loaded instructions
   in a dedicated request-scoped section with their identity and provenance.
   Instructions remain subordinate to system rules, user scope, and permissions.
6. Tool calls still pass through `run_tool`. Associate subsequent actions with
   active activation IDs without claiming a particular instruction caused them.
   Mark started only when workflow actions occur. Finalize as incomplete unless
   the skill's completion conditions have recorded supporting outcomes; verify
   Lab 4 correctness independently against its rubric. No silent auto-execution
   of shell snippets, unsupported specialists, or recursive activation loops.

The first falsifiable implementation hypothesis is that instructions retained in
`prompt` can guide the existing loop without changing tool execution. Check it
with `FakeModelClient`: a matching request must put the body in the first and
subsequent prompts, produce linked ordinary tool events, and omit it on the next
unrelated request. Failure means repairing context lifetime before adding more
routing behavior.

## Implementation Steps And Tasks

### Phase 1: Inputs And SDLC Baseline

Plan item **1.1**. Requirements: REQ-007, REQ-008.

- [ ] T001 [Plan:1.1] Review `intend.md` and `spec.md`; supply the Lab 4 assignment/rubric and project path. The Lab 5 skills are already `delegate` and `hook-check`; only missing Lab 4 inputs block the lab phase. Record permission in `spec.md` if skill adaptation is needed.
- [ ] T002 [Plan:1.1] Approve the proposed contracts in `plan.md` and capture the existing `python -m pytest -q` result before implementation. Keep the two checkpoint files aligned with approved changes.

### Phase 2: Discovery And Selection

Plan item **2.1**. Requirements: REQ-001, REQ-002.

- [ ] T003 [Plan:2.1] Add `SkillRegistry` metadata discovery/loading in `mini_coding_agent.py`, including supported frontmatter, both folder/file spellings, deterministic ordering, containment, limits, and recoverable diagnostics.
- [ ] T004 [Plan:2.1] Implement exact-name requests and deterministic scoring in `mini_coding_agent.py`; calibrate the threshold with recorded matching/nonmatching/ambiguous examples from the existing `delegate` and `hook-check` descriptions, verifying that both are discoverable and individually selectable.

### Phase 3: Runtime Integration And Audit

Plan item **3.1**. Requirements: REQ-003, REQ-004, REQ-005, REQ-006.

- [ ] T005 [Plan:3.1] Integrate selection and active-skill context with `MiniAgent.ask` and `prompt` in `mini_coding_agent.py`; run the focused FakeModelClient context-lifetime check immediately before extending integration.
- [ ] T006 [Plan:3.1] Register and validate `use_skill` in `mini_coding_agent.py`, including its prompt/example contract, shared activation path, duplicate guard, step accounting, and unchanged action permissions.
- [ ] T007 [Plan:3.1] Add durable `skill_events` in `mini_coding_agent.py` with request/activation IDs, full query, scored candidates, threshold/algorithm, trigger source, path/hash, lifecycle, tool results, and errors; default missing fields on legacy sessions.
- [ ] T008 [Plan:3.1] Check reset/resume and delegation handling in `mini_coding_agent.py`: no stale request context, no implicit rerun on resume, read-only children keep their restrictions, and child audit events remain discoverable through linked session IDs.

### Phase 4: Existing Lab 5 Skills Applied To Lab 4

Plan item **4.1**. Requirements: REQ-004, REQ-005, REQ-007.

- [ ] T009 [Plan:4.1] After T001 supplies the Lab 4 inputs, check prerequisites for the existing `skills/delegate/SKILL.md` and `skills/hook-check/SKILL.md` workflows. Reuse them without rewriting by default; adapt only with permission, preserving their substantive procedures and documenting portability changes.
- [ ] T010 [Plan:4.1] Run the mini agent against the supplied Lab 4 workspace with the real assignment prompt and Ollama; make both existing skills available inside that target workspace and activate the applicable workflow when needed. Capture selection, instructions, tool actions, and final artifacts. Use `--approval ask` for the demonstration.
- [ ] T011 [Plan:4.1] Create `LAB4_RUN.md` with the exact command, prompt, model/configuration, skill identity/hash, scores, session/evidence paths, rubric results, and limitations. Report an unsuccessful attempt honestly; do not mark Lab 4 solved without independent checks.

### Phase 5: Verification And Handoff

Plan item **5.1**. Requirements: REQ-001 through REQ-008.

- [ ] T012 [Plan:5.1] Run the verification cases below using existing helpers in `tests/test_mini_coding_agent.py` or a temporary harness; run the existing suite and record actual results in `LAB4_RUN.md`. Add permanent regression cases only if test changes are authorized.
- [ ] T013 [Plan:5.1] Update `README.md` and `EXAMPLE.md` with the seventh component, supported skill format, selection rules, execution-time tool, audit interpretation, and reproducible example. Update SDLC/checkpoint status from real evidence, keeping unresolved requirements open.

Dependencies: T001 gates T009-T011. T002 precedes implementation. T003 precedes
T004-T005; T005 precedes T006-T008. Runtime integration must pass verification
before T010. T012-T013 complete the handoff, not an automatic success declaration.

## Verification Criteria

- Discovery: both root and filename spellings, multiline description, missing
  roots, malformed/duplicate files, unreadable/oversized content, path/symlink escape.
- Routing: relevant and unrelated queries, explicit request, unknown skill,
  empty query, ties, stable scores, execution-time request, duplicate suppression.
- Execution: instructions persist through multiple turns but not the next request;
  expected normal tool actions occur; denied writes/shell actions stay denied;
  missing prerequisites and exhausted step budgets are visible failures/incomplete.
- Persistence: full prompt and candidate scores survive save/load; activation and
  tool events correlate; legacy sessions load; reset/resume/delegation do not leak
  active instructions or silently erase required demonstration evidence.
- Regression: `python -m pytest -q`, or `uv run python -m pytest -q` in the project
  environment. Model-independent checks use `FakeModelClient`; they do not prove
  real Ollama instruction-following or Lab 4 correctness.
- Demonstration: real Ollama run plus Lab 4's supplied verification procedure.
  Missing lab resources or unavailable Ollama are reported as blocked, not passed.
- Audit files contain full prompts and tool output; inspect/redact secrets before
  sharing evidence, while retaining the original local record. Record redactions.

## Project Files

Keep implementation in `mini_coding_agent.py` and reuse the existing test helpers.
SDLC files: `intend.md`, `spec.md`, `plan.md`, and the two traceability checkpoints.
Reuse `skills/delegate/SKILL.md` and `skills/hook-check/SKILL.md`; update either
only as authorized. Create `LAB4_RUN.md` during
execution, linking actual lab artifacts and saved sessions rather than fabricating
sample output. No separate task directory or new framework is needed.

## Requirement Mapping

| Requirement | Plan Items | Tasks | Expected Evidence |
| --- | --- | --- | --- |
| REQ-001 | 2.1, 5.1 | T003, T012 | Registry discovery and boundary checks |
| REQ-002 | 2.1, 5.1 | T004, T012 | Reproducible scores and routing decisions |
| REQ-003 | 3.1, 5.1 | T006, T012 | Validated execution-time skill tool |
| REQ-004 | 3.1, 4.1, 5.1 | T005, T006, T009, T012 | Persistent instructions and permission outcomes |
| REQ-005 | 3.1, 4.1, 5.1 | T007, T010, T011, T012 | Correlated session audit and lab evidence |
| REQ-006 | 3.1, 5.1 | T008, T012 | Legacy/resume/reset/delegation checks |
| REQ-007 | 1.1, 4.1, 5.1 | T001, T009, T010, T011, T012 | Actual Lab 4 rubric and verified artifacts |
| REQ-008 | 1.1, 5.1 | T001, T002, T013 | Reviewed SDLC files and usage documentation |

All eight requirements have planned coverage; none is claimed implemented.