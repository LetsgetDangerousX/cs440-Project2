from pathlib import Path

import pytest

from mini_coding_agent import MAX_SKILL_CHARS, SkillLog, SkillRegistry

REPO_ROOT = Path(__file__).resolve().parents[1]


def write_skill(root, folder, text, root_name="skills", filename="SKILL.md"):
    path = root / root_name / folder / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def skill_text(name, description="Does a thing.", body="# Steps\n1. Do it."):
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n"


def test_discovers_the_repo_lab5_skills():
    registry = SkillRegistry(REPO_ROOT)
    assert registry.diagnostics == []
    assert [skill["name"] for skill in registry.skills] == ["delegate", "hook-check"]
    hook = registry.get("hook-check")
    assert hook["path"] == "skills/hook-check/SKILL.md"
    assert hook["description"].startswith("Test the context-switcher hook")
    assert hook["body"].startswith("# Hook check")


def test_missing_roots_give_an_empty_registry(tmp_path):
    registry = SkillRegistry(tmp_path)
    assert registry.skills == []
    assert registry.diagnostics == []


def test_singular_root_and_lowercase_filename(tmp_path):
    write_skill(tmp_path, "pr-review", skill_text("pr-review"), root_name="skill", filename="skill.md")
    registry = SkillRegistry(tmp_path)
    assert registry.get("pr-review")["path"] == "skill/pr-review/skill.md"


def test_folder_without_skill_file_is_ignored(tmp_path):
    (tmp_path / "skills" / "empty").mkdir(parents=True)
    registry = SkillRegistry(tmp_path)
    assert registry.skills == []
    assert registry.diagnostics == []


def test_folded_multiline_description(tmp_path):
    text = "---\nname: multi\ndescription: >\n  First line\n  second line.\n---\nBody.\n"
    write_skill(tmp_path, "multi", text)
    assert SkillRegistry(tmp_path).get("multi")["description"] == "First line second line."


def test_malformed_skills_become_diagnostics(tmp_path):
    write_skill(tmp_path, "no-frontmatter", "# Just markdown\n")
    write_skill(tmp_path, "no-description", "---\nname: no-description\n---\nBody.\n")
    write_skill(tmp_path, "no-body", skill_text("no-body", body=""))
    write_skill(tmp_path, "too-big", skill_text("too-big", body="x" * MAX_SKILL_CHARS))
    registry = SkillRegistry(tmp_path)
    assert registry.skills == []
    messages = "\n".join(registry.diagnostics)
    assert "skills/no-frontmatter/SKILL.md: missing '---' frontmatter" in messages
    assert "skills/no-description/SKILL.md: frontmatter needs both name and description" in messages
    assert "skills/no-body/SKILL.md: no instructions after the frontmatter" in messages
    assert "skills/too-big/SKILL.md: larger than" in messages


def test_duplicate_names_keep_the_first_and_report_the_second(tmp_path):
    write_skill(tmp_path, "one", skill_text("same", description="First."))
    write_skill(tmp_path, "two", skill_text("same", description="Second."))
    registry = SkillRegistry(tmp_path)
    assert [skill["description"] for skill in registry.skills] == ["First."]
    assert registry.diagnostics == [
        "skills/two/SKILL.md: duplicate skill name 'same' (already defined in skills/one/SKILL.md)"
    ]


def test_symlink_outside_the_workspace_is_rejected(tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text(skill_text("escape"), encoding="utf-8")
    workspace = tmp_path / "ws"
    folder = workspace / "skills" / "escape"
    folder.mkdir(parents=True)
    try:
        (folder / "SKILL.md").symlink_to(outside)
    except OSError:
        pytest.skip("symlinks not permitted on this platform")
    registry = SkillRegistry(workspace)
    assert registry.skills == []
    assert registry.diagnostics == ["skills/escape/SKILL.md: resolves outside the workspace"]


def test_skill_log_appends_json_lines(tmp_path):
    log = SkillLog(tmp_path / ".mini-coding-agent" / "skills.log")
    log.write("prompt", request_id="r1", prompt="check the hook")
    log.write("similarity", request_id="r1", selected="hook-check")
    entries = log.read()
    assert [entry["event"] for entry in entries] == ["prompt", "similarity"]
    assert entries[0]["prompt"] == "check the hook"
    assert all("ts" in entry for entry in entries)
    assert len(log.path.read_text(encoding="utf-8").splitlines()) == 2


def test_skill_log_read_without_file(tmp_path):
    assert SkillLog(tmp_path / "missing.log").read() == []


HOOK_BODY = "# Hook check\nRun the hook with fake prompts."


def build_skill_agent(tmp_path, outputs, **kwargs):
    from mini_coding_agent import FakeModelClient, MiniAgent, SessionStore, WorkspaceContext

    (tmp_path / "README.md").write_text("demo\n", encoding="utf-8")
    write_skill(
        tmp_path,
        "hook-check",
        skill_text("hook-check", "Test the context-switcher hook with fake prompts.", HOOK_BODY),
    )
    write_skill(
        tmp_path,
        "delegate",
        skill_text("delegate", "Pick the specialist and write a delegation brief.", "# Delegate\nWrite the brief."),
    )
    return MiniAgent(
        model_client=FakeModelClient(outputs),
        workspace=WorkspaceContext.build(tmp_path),
        session_store=SessionStore(tmp_path / ".mini-coding-agent" / "sessions"),
        approval_policy="auto",
        **kwargs,
    )


def events(agent):
    return [entry["event"] for entry in agent.skill_log.read()]


def test_matching_prompt_activates_skill_for_the_whole_request_only(tmp_path):
    agent = build_skill_agent(
        tmp_path,
        [
            '<tool>{"name":"list_files","args":{"path":"."}}</tool>',
            "<final>Checked.</final>",
            "<final>Hi.</final>",
        ],
    )
    assert agent.ask("test the context-switcher hook with fake prompts") == "Checked."
    first, second = agent.model_client.prompts
    assert HOOK_BODY in first and HOOK_BODY in second

    agent.ask("hello there")
    assert HOOK_BODY not in agent.model_client.prompts[2]
    assert agent.active_skills == []

    log = agent.skill_log.read()
    assert events(agent) == ["prompt", "similarity", "skill_activated", "skill_executed", "prompt", "similarity"]
    assert log[0]["prompt"] == "test the context-switcher hook with fake prompts"
    assert log[1]["selected"] == "hook-check"
    assert {c["name"] for c in log[1]["candidates"]} == {"hook-check", "delegate"}
    assert log[3]["trigger"] == "auto"
    assert [call["tool"] for call in log[3]["tool_calls"]] == ["list_files"]
    assert log[3]["final"] == "Checked."
    assert log[5]["selected"] is None and log[5]["reason"] == "no match"
    assert log[0]["request_id"] == log[3]["request_id"] != log[4]["request_id"]


def test_prefix_lists_skills_and_use_skill(tmp_path):
    agent = build_skill_agent(tmp_path, [])
    assert "use_skill(name: str, query: str)" in agent.prefix
    assert "- hook-check: Test the context-switcher hook" in agent.prefix
    assert HOOK_BODY not in agent.prefix


def test_use_skill_mid_task(tmp_path):
    agent = build_skill_agent(
        tmp_path,
        [
            '<tool>{"name":"use_skill","args":{"name":"hook-check","query":"verify the hook I wrote"}}</tool>',
            "<final>Done.</final>",
        ],
    )
    agent.ask("describe the vacuum grid cells")
    assert HOOK_BODY not in agent.model_client.prompts[0]
    assert HOOK_BODY in agent.model_client.prompts[1]
    log = agent.skill_log.read()
    use_skill_scores = [e for e in log if e["event"] == "similarity" and e["trigger"] == "use_skill"]
    assert use_skill_scores[0]["requested"] == "hook-check"
    assert use_skill_scores[0]["query"] == "verify the hook I wrote"
    executed = [e for e in log if e["event"] == "skill_executed"]
    assert executed[0]["skill"] == "hook-check" and executed[0]["trigger"] == "use_skill"


def test_use_skill_rejects_unknown_and_repeated(tmp_path):
    agent = build_skill_agent(tmp_path, [])
    unknown = agent.run_tool("use_skill", {"name": "pr-review", "query": "review"})
    assert "unknown skill 'pr-review'; available: delegate, hook-check" in unknown
    assert "query must describe" in agent.run_tool("use_skill", {"name": "delegate", "query": ""})

    agent.begin_skill_request("test the context-switcher hook with fake prompts")
    repeated = agent.run_tool("use_skill", {"name": "hook-check", "query": "again"})
    assert "already active" in repeated


def test_skills_do_not_bypass_approval(tmp_path):
    agent = build_skill_agent(
        tmp_path,
        [
            '<tool>{"name":"run_shell","args":{"command":"echo hi","timeout":5}}</tool>',
            "<final>Blocked.</final>",
        ],
    )
    agent.approval_policy = "never"
    agent.ask("test the context-switcher hook with fake prompts")
    executed = [e for e in agent.skill_log.read() if e["event"] == "skill_executed"][0]
    assert executed["tool_calls"][0]["result"] == "error: approval denied for run_shell"


def test_reset_clears_active_skills(tmp_path):
    agent = build_skill_agent(tmp_path, [])
    agent.begin_skill_request("test the context-switcher hook with fake prompts")
    assert agent.active_skills
    agent.reset()
    assert agent.active_skills == []


def test_no_skills_keeps_original_prompt_and_tools(tmp_path):
    from mini_coding_agent import FakeModelClient, MiniAgent, SessionStore, WorkspaceContext

    (tmp_path / "README.md").write_text("demo\n", encoding="utf-8")
    agent = MiniAgent(
        model_client=FakeModelClient(["<final>ok</final>"]),
        workspace=WorkspaceContext.build(tmp_path),
        session_store=SessionStore(tmp_path / ".mini-coding-agent" / "sessions"),
    )
    assert "use_skill" not in agent.tools
    assert "Skills (" not in agent.prefix
    agent.ask("hello")
    assert "Active skill instructions" not in agent.model_client.prompts[0]


def test_child_agents_get_no_skills(tmp_path):
    agent = build_skill_agent(tmp_path, ["<final>child answer</final>"])
    seen = {}
    original_ask = type(agent).ask

    def spy(self, message):
        seen["skills"] = self.skills
        seen["tools"] = set(self.tools)
        return original_ask(self, message)

    from unittest.mock import patch

    with patch.object(type(agent), "ask", spy):
        agent.tool_delegate({"task": "inspect README.md", "max_steps": 1})
    assert seen["skills"] is None
    assert "use_skill" not in seen["tools"]
