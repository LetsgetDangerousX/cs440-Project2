# Implementation Plan: Agent Skills Component

Original date: 2026-11-18 (PR #2). Updated: 2026-11-22.
Status: Component shipped in PR #3; documentation and partial Lab 4 run in PR #4.
Inputs: [intend.md](intend.md), [spec.md](spec.md), implementation, tests, and
[LAB4_RUN.md](LAB4_RUN.md). This is a reconciliation of the original plan, not a
claim that every planned deliverable was completed.

## Delivered Architecture

The seventh component lives in the existing
[mini_coding_agent.py](mini_coding_agent.py): `SkillRegistry`, lexical scoring,
`SkillLog`, and request-scoped active instructions. `MiniAgent.ask` selects before
the first model call, `prompt` retains active bodies outside transcript clipping,
and `use_skill` lets the model load another known skill through the ordinary
validated tool loop. No second agent loop or new runtime service was added.

The parser is a standard-library YAML-style subset. Registry construction reads
and caches metadata **and bodies**; activation does not reread or hash files.
Automatic selection uses stopword-filtered `[a-z0-9]+` token counts, cosine
similarity rounded to four decimals, threshold `0.2`, and name-only ties.
There is no `skill:<name>` user directive. Valid model requests activate the exact
requested skill independent of query scores, and duplicate activation is denied.

Logging uses a separate append-only `.mini-coding-agent/skills.log`, not the
proposed `SessionStore.skill_events`. Its four events capture prompts, similarity,
activation, and abbreviated activity/final text with request/session IDs.
`skill_executed` does not encode verified workflow completion. Existing session
JSON remains unchanged; active instructions are not restored on resume. Default
delegated children retain read-only/depth bounds but receive no skills or skill
log, and parent results do not expose child session IDs.

The two original Lab 5 skills were reused unchanged. PR #3 supplied the Lab 4
handout; PR #4 recorded real Ollama configuration attempts and README usage
instructions. Lab 4 is context engineering configuration, not Q-learning code.

## Changes From The Original Proposal

| Original Proposal | Delivered Result / Remaining Gap |
| --- | --- |
| Provisional `0.25` threshold, calibrated before freezing | Default `0.2`; routing tests and real-run scores exist, but no separate calibration report |
| Exact user-name precedence and name/path tie-break | No explicit user directive; rounded-score ties use name; `use_skill` requests an exact name |
| Metadata snapshot per request and revalidated/hash-recorded activation | Files read once at registry construction; cached bodies used without activation-time revalidation/hash |
| Bound active-skill count and total content size | Entire skill file limited to 20,000 characters; no aggregate activation bound beyond registry size/tool steps |
| Session `skill_events`, activation IDs, complete provenance and lifecycle states | Separate JSON-lines log with request/session IDs and abbreviated activity, no hashes or verified lifecycle |
| Linked child skill audit | Default children get no skills/log; no parent-to-child session ID link |
| Demonstrate with `--approval ask` | Recorded run used `auto`; CLI default remains `ask`; this deviation is evidence, not a new safety recommendation |
| Complete Lab 4 validation and skills example in `EXAMPLE.md` | Partial run and README reproduction steps; generic `EXAMPLE.md` unchanged |

See [spec.md](spec.md) for exact contracts and limitations. Original commitments
that were not delivered remain explicit rather than being retroactively passed.

## Implementation Steps And Task Status

Original IDs and plan-item mappings are retained for checkpoint traceability.
Checked tasks have the stated deliverable in the merged PRs. Unchecked tasks
may be partially implemented; their remaining work is described below.
No design approval, pre-implementation test result, or complete lab success is
inferred from the presence of merged code.

### Phase 1: Inputs And SDLC Baseline

Plan item **1.1**. Requirements: REQ-007, REQ-008.

- [x] T001 [Plan:1.1] Supply Lab 4 inputs. PR #3 added [docs/lab4-instructions.md](docs/lab4-instructions.md); PR #4 identifies the separate workspace and answer-key repositories. Skills were reused unchanged, so no adaptation approval was needed. External artifacts remain necessary for reproduction.
- [ ] T002 [Plan:1.1] Capture design approval and the existing suite result before implementation. The original SDLC/checkpoint files exist, but the later PRs do not supply a recorded pre-implementation test result or separate design approval. Do not fabricate retrospective baseline evidence.

### Phase 2: Discovery And Selection

Plan item **2.1**. Requirements: REQ-001, REQ-002.

- [ ] T003 [Plan:2.1] Partial: `SkillRegistry` implements both roots, case-insensitive filename recognition, subset parsing, diagnostics, duplicate handling, file limits, and resolved-file containment. Recoverable directory-enumeration errors and activation-time revalidation from the original contract remain absent.
- [ ] T004 [Plan:2.1] Partial: deterministic scoring with threshold `0.2`, rounded-score/name ordering, and relevant/unrelated/tie regression tests shipped. Exact user directives, original precedence behavior, and a separate calibration record did not.

### Phase 3: Runtime Integration And Audit

Plan item **3.1**. Requirements: REQ-003, REQ-004, REQ-005, REQ-006.

- [x] T005 [Plan:3.1] Integrate automatic activation and dedicated request-scoped instructions. FakeModelClient regression coverage verifies bodies in the first/subsequent prompts and their omission on the next unrelated request.
- [x] T006 [Plan:3.1] Register/validate `use_skill(name, query)` with catalog, example, shared activation path, duplicate guard, and ordinary step/approval handling. Named activation is independent of the logged scoring result.
- [ ] T007 [Plan:3.1] Partial: `SkillLog` persists four event types in a separate log. Activation IDs, hashes/content provenance, full outcomes, structured lifecycle states, and comprehensive failed-call scoring remain unimplemented.
- [ ] T008 [Plan:3.1] Partial: reset clears active instructions, construction/resume starts with none, and default children get no skills. Existing session/delegation tests remain; dedicated skill-resume and exception/step-limit coverage plus linked child-session audit evidence are not supplied.

### Phase 4: Existing Lab 5 Skills Applied To Lab 4

Plan item **4.1**. Requirements: REQ-004, REQ-005, REQ-007.

- [ ] T009 [Plan:4.1] Partial: both existing skills were made available unchanged. The recorded attempt exposed Windows shell incompatibilities; complete Claude/AIMA/hook prerequisite checks and an applicable `hook-check` workflow remain open. Adapt skills only with permission.
- [ ] T010 [Plan:4.1] Partial: three real Ollama requests attempted grid documentation and Strategy 4 specialist files using `auto`, not planned `ask`. No-match and `delegate` activation are documented; complete strategies 1/4 configuration, hook execution, and independently verified artifacts are not.
- [ ] T011 [Plan:4.1] Partial: [LAB4_RUN.md](LAB4_RUN.md) supplies prompts, command/model settings, scores, IDs, excerpts, comparisons, and honest failures. Skill hashes, committed full evidence/artifacts, and complete rubric verification are absent.

### Phase 5: Verification And Handoff

Plan item **5.1**. Requirements: REQ-001 through REQ-008.

- [ ] T012 [Plan:5.1] Partial: PR #3 added permanent discovery, scoring, activation, logging, reset, permission, and child-isolation regression tests. The broader original matrix and an actual suite result recorded in [LAB4_RUN.md](LAB4_RUN.md) are not supplied.
- [ ] T013 [Plan:5.1] Partial: PR #4 updated [README.md](README.md) with skills and reproduction steps. This revision reconciles the three SDLC docs and checkpoint status notes. [EXAMPLE.md](EXAMPLE.md) remains generic, and unresolved acceptance criteria remain open.

Original sequencing: T001 gates T009-T011; T002 was intended to precede
implementation; T003 precedes T004-T005; T005 precedes T006-T008; runtime
verification precedes a complete T010; T012-T013 finish handoff. This ordering is
not proof that every prerequisite was fulfilled in the merged work.

## Verification And Remaining Handoff

Available model-independent evidence:

- [tests/test_skills.py](tests/test_skills.py): repository skills, missing roots,
  singular/lowercase spelling, folded descriptions, invalid/oversized content,
  duplicate handling, file-symlink escape, JSON-lines logging, prompt lifetime,
  mid-task activation, invalid/repeated requests, denied approval, reset,
  empty registries, and child isolation.
- [tests/test_skill_scoring.py](tests/test_skill_scoring.py): relevant/unrelated
  prompts, candidate ordering, empty/stopword queries, case/punctuation,
  equal-threshold selection, ties, empty registries, and deterministic results.
- [tests/test_mini_coding_agent.py](tests/test_mini_coding_agent.py): existing
  agent regression coverage, including session save/resume and delegation.

Reproduction commands are `python -m pytest -q` or
`uv run python -m pytest -q` in the project environment. This documentation-only
update does not claim a new test or Ollama run. Test presence is not proof of a
historical passing run or real-model fidelity.

Remaining verification from the original plan includes unreadable-directory/
ambiguous-file boundaries, activation-time file changes, aggregate limits,
skill-specific resume/error/step-limit behavior, and stronger audit provenance.
Those must be paired with implementation work where the required behavior is
currently absent.

For Lab 4, correct and independently verify the 4x4 grid and specialist
frontmatter/permissions, complete Strategy 1 hook/context configuration and
applicable `hook-check` execution, and verify the required project README.
The documented failed six-step attempt and partial fifteen-step retry are not
lab sign-off. Windows `run_shell` uses the platform shell (`cmd.exe`); starting
Windows Python from Git Bash alone does not change that shell. Portable commands
or an appropriate runtime are prerequisites for the original POSIX snippets.

Full logs contain prompts/tool data: inspect and redact sensitive material before
sharing, retain local originals, and record redactions. Published run excerpts
are abbreviated and external evidence is not bundled in this repository.

## Project Files And Requirement Mapping

Implementation remains in [mini_coding_agent.py](mini_coding_agent.py).
Reuse [skills/delegate/SKILL.md](skills/delegate/SKILL.md) and
[skills/hook-check/SKILL.md](skills/hook-check/SKILL.md) without unauthorized
rewrites. SDLC artifacts are [intend.md](intend.md), [spec.md](spec.md), this
plan, and the two [checkpoints](checkpoints/) files. The checkpoints measure
traceability only, not completion.

| Requirement | Plan Items | Tasks | Available Evidence / Open Status |
| --- | --- | --- | --- |
| REQ-001 | 2.1, 5.1 | T003, T012 | Registry/tests; recovery and boundary gaps remain |
| REQ-002 | 2.1, 5.1 | T004, T012 | Lexical scoring/tests; explicit user routing/calibration absent |
| REQ-003 | 3.1, 5.1 | T006, T012 | Validated named execution-time tool and regression cases |
| REQ-004 | 3.1, 4.1, 5.1 | T005, T006, T009, T012 | Request-scoped instructions/approval tests; stronger activation checks and prerequisites open |
| REQ-005 | 3.1, 4.1, 5.1 | T007, T010, T011, T012 | Separate activity log/run excerpts; provenance and lifecycle incomplete |
| REQ-006 | 3.1, 5.1 | T008, T012 | Existing sessions/reset/child isolation; linked audit and skill-resume evidence incomplete |
| REQ-007 | 1.1, 4.1, 5.1 | T001, T009, T010, T011, T012 | Handout and partial real run; full lab verification open |
| REQ-008 | 1.1, 5.1 | T001, T002, T013 | SDLC/checkpoints/README/run log; baseline approval and skills-specific EXAMPLE handoff incomplete |

All eight requirements retain plan/task coverage. Coverage is not an assertion
that their original acceptance criteria are complete.
