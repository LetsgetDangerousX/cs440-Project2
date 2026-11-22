&nbsp;
# Mini-Coding-Agent

This folder contains a small standalone coding agent:

- code: `mini_coding_agent.py`
- CLI: `mini-coding-agent`

It is a minimal local agent loop with:

- workspace snapshot collection
- stable prompt plus turn state
- structured tools
- approval handling for risky tools
- transcript and memory persistence
- bounded delegation

The model backend is currently based on Ollama.

<a href="https://magazine.sebastianraschka.com/p/components-of-a-coding-agent">
  <img src="https://substack-post-media.s3.amazonaws.com/public/images/49b97718-57f4-4977-99c8-8ad5c4d32af3_1548x862.png" width="500px">
</a>

<br>

**[The detailed tutorial: Components of a Coding Agent](https://magazine.sebastianraschka.com/p/components-of-a-coding-agent)**


&nbsp;
## Six Core Components

<a href="https://magazine.sebastianraschka.com/p/components-of-a-coding-agent">
  <img alt="Six core components of a coding agent" src="https://sebastianraschka.com/images/github/mini-coding-agent/six-components.webp" width="500px">
</a>

This coding harness is organized around six practical building blocks:

1. **Live repo context**  
   The agent collects stable workspace facts upfront, such as repo layout, instructions, and git state.
2. **Prompt shape and cache reuse**  
   A stable prompt prefix, which is separate from the changing request, transcript, and memory so repeated model calls can reuse the static parts efficiently.
3. **Structured tools, validation, and permissions**  
   The model works through named tools with checked inputs, workspace path validation, and approval gates instead of free-form arbitrary actions.
4. **Context reduction and output management**  
   Long outputs are clipped, repeated reads are deduplicated, and older transcript entries are compressed to keep prompt size under control.
5. **Transcripts, memory, and resumption**  
   The runtime keeps both a full durable transcript and a smaller working memory so sessions can be resumed while preserving important state via working memory.
6. **Delegation and bounded subagents**  
   Scoped subtasks can be delegated to helper agents that inherit enough context to help (but operate within limits).
7. **Agent skills** (added for CS 440 Project 2)  
   The agent finds folder skills, picks the one that fits a request, adds its instructions to the prompt, and logs every decision. See [Agent Skills](#agent-skills) below.

&nbsp;
## Agent Skills

This fork adds a seventh component so the agent can use reusable **skills**: folders of instructions it reads only when a request calls for them.

### Skill format

Each skill is a folder under `skills/` (or `skill/`) at the workspace root, holding one `SKILL.md`:

```markdown
---
name: delegate
description: What the skill does and when to use it. Matching depends on these words.
---

# Instructions
Steps the agent follows once the skill is selected.
```

Only `name` and `description` are read at startup. The body is added to the prompt only when the skill is selected.

### How a skill is selected

1. **Scan.** At startup, `SkillRegistry` reads every `skills/<name>/SKILL.md`. Malformed, duplicate, oversized or out-of-workspace files are skipped with a diagnostic.
2. **Match.** Before the first model call, `score_skills` compares the request with each skill's name and description. It counts the words in each (lowercased, common words like "the" removed) and computes their cosine similarity, a score from 0 to 1. The highest score at or above **0.2** wins; ties go to the alphabetically first name.
3. **Load.** The winning skill's instructions are added to the prompt under "Active skill instructions" for the rest of that request, then cleared.

The model can also load a skill partway through a task by calling the `use_skill` tool with a skill name and the reason it needs it. The available skills are listed in the prompt so the model knows what it can ask for.

Child agents created by `delegate` do not get skills.

### The skills log

Every request is logged to `.mini-coding-agent/skills.log` in the workspace, one JSON object per line:

| Event | Contents |
| --- | --- |
| `prompt` | The request as typed |
| `similarity` | Every skill's score, the threshold, the selected skill (or `null`) and the reason |
| `skill_activated` | The skill's name, its file path, and whether it was picked automatically or by `use_skill` |
| `skill_executed` | Every tool call the agent made while the skill was active, with results, and the final answer |

Each line carries a `request_id` and `session_id`, so all events for one request can be traced together. To view the log:

```bash
cat .mini-coding-agent/skills.log            # macOS / Linux
Get-Content .mini-coding-agent\skills.log    # Windows PowerShell
```

### Running Lab 4 with the skills

The agent writes files at the root of its workspace, so run it in a separate Git repo next to this one:

```powershell
mkdir lab4; cd lab4; git init
mkdir skills
Copy-Item -Recurse ..\mini-coding-agent\skills\* skills\
Copy-Item ..\mini-coding-agent\docs\lab4-instructions.md .
git add .; git commit -m "Lab 4 workspace"
python ..\mini-coding-agent\mini_coding_agent.py --cwd . --approval auto --ollama-timeout 900 --max-steps 15
```

On a CPU-only laptop each model step can take several minutes, so the longer timeout and step limit help. Requests that share words with a skill's description select that skill. For example, "Create .claude/agents files for the rl-researcher, env-builder and code-reviewer specialists for Strategy 4 delegation" selects `delegate` with a score of 0.45. Results are in [LAB4_RUN.md](LAB4_RUN.md).

### Limitations

- Matching compares words, not meaning, so synonyms such as "subagents" and "specialists" don't count toward the score.
- The Lab 5 skills were written for macOS and Linux shells. On Windows their shell commands fail, because the agent's `run_shell` uses Command Prompt.

### Project files added for Project 2

| Path | Purpose |
| --- | --- |
| `skills/delegate/`, `skills/hook-check/` | Our two Lab 5 skills |
| `intend.md`, `spec.md`, `plan.md` | SDLC stages: intent, specification, implementation plan |
| `checkpoints/` | Traceability from spec to plan to tasks |
| `docs/lab4-instructions.md` | The Lab 4 handout the agent works from |
| `tests/test_skills.py`, `tests/test_skill_scoring.py` | Tests for discovery, scoring, activation and logging |
| `LAB4_RUN.md` | Commands, log excerpts and results from running Lab 4 with the agent |

&nbsp;
## Requirements

You need:

- Python 3.10+
- Ollama installed
- an Ollama model pulled locally

Optional:

- `uv` for environment management and the `mini-coding-agent` CLI entry point

This project has no Python runtime dependency beyond the standard library, so you can run it directly with `python mini_coding_agent.py` if you do not want to use `uv`.

&nbsp;
## Install Ollama

Install Ollama on your machine so the `ollama` command is available in your shell.

Official installation link: [ollama.com/download](https://ollama.com/download)

Then verify:

```bash
ollama --help
```

Start the server:

```bash
ollama serve
```

In another terminal, pull a model. Example:

```bash
ollama pull qwen3.5:4b
```

Qwen 3.5 model library:

- [ollama.com/library/qwen3.5](https://ollama.com/library/qwen3.5)

The default in this project is `qwen3.5:4b`. If you have sufficient memory, it is worth trying a larger model such as `qwen3.5:9b` or another larger Qwen 3.5 variant. The agent just sends prompts to Ollama's `/api/generate` endpoint.

&nbsp;
## Project Setup

Clone the repo or your fork and change into it:

```bash
git clone https://github.com/rasbt/mini-coding-agent.git
cd mini-coding-agent
```

If you forked it first, use your fork URL instead:

```bash
git clone https://github.com/<your-github-user>/mini-coding-agent.git
cd mini-coding-agent
```



&nbsp;
## Basic Usage

Start the agent:

```bash
cd mini-coding-agent
uv run mini-coding-agent
```

Without `uv`, run the script directly:

```bash
cd mini-coding-agent
python mini_coding_agent.py
```

By default it uses:

- model: `qwen3.5:4b`
- approval: `ask`

For a concrete usage example, see [EXAMPLE.md](EXAMPLE.md).

&nbsp;
## Approval Modes

Risky tools such as shell commands and file writes are gated by approval.

- `--approval ask`
  prompts before risky actions (default and recommended)
- `--approval auto`
  allows risky actions automatically, including arbitrary command execution and file writes by the model; use only with trusted prompts and trusted repositories
- `--approval never`
  denies risky actions

Example:

```bash
uv run mini-coding-agent --approval auto
```



&nbsp;
## Resume Sessions

The agent saves sessions under the target workspace root in:

```text
.mini-coding-agent/sessions/
```

Resume the latest session:

```bash
uv run mini-coding-agent --resume latest
```


Resume a specific session:

```bash
uv run mini-coding-agent --resume 20260401-144025-2dd0aa
```


&nbsp;
## Interactive Commands

Inside the REPL, slash commands are handled directly by the agent instead of
being sent to the model as a normal task.

- `/help`
  shows the list of available interactive commands
- `/memory`
  prints the distilled session memory, including the current task, tracked files, and notes
- `/session`
  prints the path to the current saved session JSON file
- `/reset`
  clears the current session history and distilled memory but keeps you in the REPL
- `/exit`
  exits the interactive session
- `/quit`
  exits the interactive session; alias for `/exit`

&nbsp;
## Main CLI Flags

```bash
uv run mini-coding-agent --help
```

Without `uv`:

```bash
python mini_coding_agent.py --help
```

CLI flags are passed before the agent starts. Use them to choose the workspace,
model connection, resume behavior, approval mode, and generation limits.

Important flags:

- `--cwd`
  sets the workspace directory the agent should inspect and modify; default: `.`
- `--model`
  selects the Ollama model name, such as `qwen3.5:4b`; default: `qwen3.5:4b`
- `--host`
  points the agent at the Ollama server URL (usually not needed); default: `http://127.0.0.1:11434`
- `--ollama-timeout`
  controls how long the client waits for an Ollama response (usually not needed); default: `300` seconds
- `--resume`
  resumes a saved session by id or uses `latest`; default: start a new session
- `--approval`
  controls how risky tools are handled: `ask`, `auto`, or `never`; default: `ask`
- `--max-steps`
  limits how many model and tool turns are allowed for one user request; default: `6`
- `--max-new-tokens`
  caps the model output length for each step; default: `512`
- `--temperature`
  controls sampling randomness; default: `0.2`
- `--top-p`
  controls nucleus sampling for generation; default: `0.9`

&nbsp;
## Example

See [EXAMPLE.md](EXAMPLE.md)

&nbsp;
## Notes & Tips

- The agent expects the model to emit either `<tool>...</tool>` or `<final>...</final>`.
- Different Ollama models will follow those instructions with different reliability.
- If the model does not follow the format well, use a stronger instruction-following model.
- The agent is intentionally small and optimized for readability, not robustness.
