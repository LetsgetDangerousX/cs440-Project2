# Lab 4 Run Log: Mini Coding Agent with Skills

Run with `qwen3.5:4b` through Ollama, on a CPU-only Windows laptop (Intel i5-8250U, 16 GB RAM). The agent works in its own Git repo, `Project2/lab4`, which starts with only `lab4-instructions.md` and the two Lab 5 skills (`skills/delegate`, `skills/hook-check`). Our team's original Lab 4 repos are the answer key.

Start command for every request below:

```powershell
cd "...\Team Folder\Project2\lab4"
python ..\mini-coding-agent\mini_coding_agent.py --cwd . --approval auto --ollama-timeout 900 --max-steps 15
```

Requests 1 and 2a ran with the default `--max-steps 6`. Some log lines below are shortened: long `query`, `args` and `session_id` fields were removed so they fit, and the full lines are in `lab4/.mini-coding-agent/skills.log`.

## Summary

| Request | Lab 4 piece | Skill selected | Score | Outcome |
| --- | --- | --- | --- | --- |
| 1 | Strategy 1: AGENTS.md | none | 0.0 / 0.0 | File written, grid wrong |
| 2a | Strategy 4: agent files | delegate | 0.4518 | Ran out of steps, no files |
| 2b | Strategy 4: agent files | delegate | 0.3525 | All three files written |

---

## Request 1: AGENTS.md (no skill expected)

```
mini-coding-agent> Write AGENTS.md describing the vacuum robot grid, the wall, and the rewards from lab4-instructions.md
Done.
```

### Skills log

```json
{"event": "prompt", "prompt": "Write AGENTS.md describing the vacuum robot grid, the wall, and the rewards from lab4-instructions.md", "request_id": "b1331d37", "session_id": "20261119-022726-3897a6", "ts": "2026-11-19T07:27:31.606223+00:00"}
{"algorithm": "cosine similarity of [a-z0-9]+ word counts, stopwords removed, name + description", "candidates": [{"name": "delegate", "score": 0.0}, {"name": "hook-check", "score": 0.0}], "event": "similarity", "query": "Write AGENTS.md describing the vacuum robot grid, the wall, and the rewards from lab4-instructions.md", "reason": "no match", "request_id": "b1331d37", "selected": null, "session_id": "20261119-022726-3897a6", "threshold": 0.2, "trigger": "prompt", "ts": "2026-11-19T07:27:31.609686+00:00"}
```

The request shares no words with either skill description, so both scored 0.0 and no skill was selected. That is the expected result.

### Comparison with the Lab 4 answer

The agent's `AGENTS.md` described a 3×4 grid:

| Item | Lab 4 answer | Agent's AGENTS.md | Correct? |
| --- | --- | --- | --- |
| Grid size | 4×4 | 3×4 | No, dropped the bottom row |
| Start | (0,0) | (0,0) | Yes |
| Wall | (1,1) | (1,1) | Yes |
| −1 square | (3,1) | Missing | No |
| +10 goal | (3,3) | (2,3) | No, shifted up with the missing row |

The whole instructions file fit in the agent's context, so the error came from the 4B model misreading the table.

---

## Request 2a: Strategy 4 agent files, first attempt

```
mini-coding-agent> Create .claude/agents files for the rl-researcher, env-builder and code-reviewer specialists for Strategy 4 delegation
Stopped after reaching the step limit without a final answer.
```

### Skills log

```json
{"event": "prompt", "prompt": "Create .claude/agents files for the rl-researcher, env-builder and code-reviewer specialists for Strategy 4 delegation", "request_id": "2d1a0922", "session_id": "20261119-022726-3897a6", "ts": "2026-11-19T07:42:07.457872+00:00"}
{"algorithm": "cosine similarity of [a-z0-9]+ word counts, stopwords removed, name + description", "candidates": [{"name": "delegate", "score": 0.4518}, {"name": "hook-check", "score": 0.0398}], "event": "similarity", "reason": "above threshold", "request_id": "2d1a0922", "selected": "delegate", "threshold": 0.2, "trigger": "prompt", "ts": "2026-11-19T07:42:07.462147+00:00"}
{"event": "skill_activated", "path": "skills/delegate/SKILL.md", "request_id": "2d1a0922", "skill": "delegate", "trigger": "auto", "ts": "2026-11-19T07:42:07.465316+00:00"}
```

The `skill_executed` event recorded six tool calls, all failed:

| # | Tool | Call | Result |
| --- | --- | --- | --- |
| 1 | `list_files` | `.claude` | Not a directory yet |
| 2 | `read_file` | no path | Invalid arguments |
| 3 | `run_shell` | `git ls-files ... \| xargs -0 shasum > /tmp/snap_before.txt` | Path not found |
| 4 | `run_shell` | same command again | Path not found |
| 5 | `run_shell` | `mkdir -p .claude/agents && ...` | Syntax error |
| 6 | `use_skill` | delegate | Already active |

The agent was following the delegate skill's step 4, "Snapshot, delegate, compare," which uses macOS/Linux commands. On Windows, `run_shell` runs in Command Prompt, so `xargs`, `shasum`, `/tmp` and `mkdir -p` all fail. Our team wrote the skill on macOS/Linux, so this never came up in Lab 5.

---

## Request 2b: Strategy 4 agent files, with write_file

The request kept the skill's vocabulary and added an instruction to avoid the shell.

```
mini-coding-agent> Create .claude/agents files for the rl-researcher, env-builder and code-reviewer specialists for Strategy 4 delegation. Use write_file for each file and do not run shell commands.
Done.
```

### Skills log

```json
{"algorithm": "cosine similarity of [a-z0-9]+ word counts, stopwords removed, name + description", "candidates": [{"name": "delegate", "score": 0.3525}, {"name": "hook-check", "score": 0.0622}], "event": "similarity", "query": "Create .claude/agents files for the rl-researcher, env-builder and code-reviewer specialists for Strategy 4 delegation. Use write_file for each file and do not run shell commands.", "reason": "above threshold", "request_id": "b5cdabfe", "selected": "delegate", "session_id": "20261119-030041-be627e", "threshold": 0.2, "trigger": "prompt", "ts": "2026-11-19T08:01:02.351731+00:00"}
{"event": "skill_activated", "path": "skills/delegate/SKILL.md", "request_id": "b5cdabfe", "session_id": "20261119-030041-be627e", "skill": "delegate", "trigger": "auto", "ts": "2026-11-19T08:01:02.355926+00:00"}
{"event": "skill_executed", "final": "Done.", "path": "skills/delegate/SKILL.md", "request_id": "b5cdabfe", "session_id": "20261119-030041-be627e", "skill": "delegate", "tool_calls": [{"tool": "write_file", "result": "wrote .claude\\agents\\rl-researcher.md (1034 chars)"}, {"tool": "write_file", "result": "wrote .claude\\agents\\env-builder.md (1371 chars)"}, {"tool": "write_file", "result": "wrote .claude\\agents\\code-reviewer.md (1259 chars)"}], "trigger": "auto", "ts": "2026-11-19T08:10:23.064691+00:00"}
```

The extra words lowered delegate's score from 0.4518 to 0.3525, still well above 0.2. The request took about nine minutes and three `write_file` calls.

### Files created

```
.claude/agents/code-reviewer.md
.claude/agents/env-builder.md
.claude/agents/rl-researcher.md
```

### Comparison with the Lab 4 answer

| Item | Our Lab 4 agent files | Agent's files | Match? |
| --- | --- | --- | --- |
| The three specialists | rl-researcher, env-builder, code-reviewer | Same three | Yes |
| Roles | Researcher answers RL theory questions, builder owns the grid environment, reviewer checks a supplied diff | Same roles | Yes |
| Inputs | AIMA source paths, the diff and its base | AIMA paths (`aima/mdp.py`, `aima/reinforcement_learning.py`), diff, base branch | Yes |
| Frontmatter (`name`, `description`, `tools`, `model`) | Present | Missing; files start with a `#` heading | No |
| Read-only limits on researcher and reviewer | Set through `tools: Read, Grep, Glob` | Described in prose only | Partly |

The roles and inputs match the delegate skill's specialist table, which shows the agent used the skill's instructions. Without frontmatter, though, Claude Code would not recognize these files as subagents.

---

## Corrections needed

1. **AGENTS.md grid.** Re-run Request 1 stating the size ("4 rows and 4 columns, wall at (1,1), −1 at (3,1), +10 at (3,3)"), or correct the file by hand and note it here.
2. **Agent file frontmatter.** Add `name`, `description`, `tools` and `model` frontmatter to each `.claude/agents/*.md`, or re-run Request 2b asking for "YAML frontmatter with name, description, tools and model."
3. **Skill portability.** Rewrite the delegate skill's snapshot step for both shells, or note that it requires Git Bash or WSL on Windows.
4. **Matching by words.** A natural request such as "Set up the vacuum robot repository with context engineering strategies 1 and 4" scores hook-check 0.14 and delegate 0.05, below the 0.2 threshold. Word-count similarity doesn't recognize synonyms. Adding more trigger phrases to each skill's description would help.
