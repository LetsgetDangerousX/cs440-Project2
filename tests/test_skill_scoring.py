import pytest

import mini_coding_agent

score_skills = getattr(mini_coding_agent, "score_skills", None)
pytestmark = pytest.mark.skipif(score_skills is None, reason="score_skills not written yet")

HOOK_CHECK = {
    "name": "hook-check",
    "description": (
        "Test the context-switcher hook from the shell by feeding it fake prompts and checking which "
        "topic notes it loads. Use after editing scripts/context-switcher.sh or adding a note to "
        ".claude/context/, or when a note doesn't load (or loads twice) as expected."
    ),
}
DELEGATE = {
    "name": "delegate",
    "description": (
        "Parent-side procedure for one Strategy 4 delegation - pick the specialist, assemble a complete "
        "brief, snapshot the worktree, then check the handoff and confirm no unauthorized files changed. "
        "Use before invoking rl-researcher, env-builder, or code-reviewer, or when running the README's "
        "smoke tests."
    ),
}
SKILLS = [DELEGATE, HOOK_CHECK]
THRESHOLD = 0.2


def scores(result):
    return {candidate["name"]: candidate["score"] for candidate in result["candidates"]}


def test_hook_prompt_selects_hook_check():
    result = score_skills("test the context-switcher hook with fake prompts", SKILLS, THRESHOLD)
    assert result["selected"] == "hook-check"
    assert result["reason"] == "above threshold"
    assert result["threshold"] == THRESHOLD


def test_delegation_prompt_selects_delegate():
    result = score_skills("pick a specialist and write a brief", SKILLS, THRESHOLD)
    assert result["selected"] == "delegate"


def test_unrelated_prompt_selects_nothing():
    result = score_skills("hello", SKILLS, THRESHOLD)
    assert result["selected"] is None
    assert result["reason"] == "no match"
    assert scores(result) == {"delegate": 0.0, "hook-check": 0.0}


def test_every_skill_is_a_candidate_sorted_by_score():
    result = score_skills("test the context-switcher hook with fake prompts", SKILLS, THRESHOLD)
    assert [c["name"] for c in result["candidates"]] == ["hook-check", "delegate"]
    values = [c["score"] for c in result["candidates"]]
    assert values == sorted(values, reverse=True)
    assert all(0.0 <= value <= 1.0 for value in values)


@pytest.mark.parametrize("query", ["", "   ", "the and of a to"])
def test_empty_or_stopword_only_query(query):
    result = score_skills(query, SKILLS, THRESHOLD)
    assert result["selected"] is None
    assert result["reason"] == "empty query"
    assert set(scores(result).values()) == {0.0}


def test_stopwords_do_not_create_a_match():
    skills = [{"name": "x", "description": "the and of a to grid"}]
    result = score_skills("the and of a to robot", skills, 0.01)
    assert scores(result) == {"x": 0.0}
    assert result["selected"] is None


def test_case_and_punctuation_are_ignored():
    upper = score_skills("TEST THE CONTEXT-SWITCHER HOOK!", SKILLS, THRESHOLD)
    lower = score_skills("test the context switcher hook", SKILLS, THRESHOLD)
    assert scores(upper) == scores(lower)


def test_identical_text_scores_one_and_meets_an_equal_threshold():
    skills = [{"name": "grid", "description": "vacuum robot"}]
    result = score_skills("grid vacuum robot", skills, 1.0)
    assert scores(result)["grid"] == pytest.approx(1.0)
    assert result["selected"] == "grid"


def test_tie_goes_to_alphabetical_name():
    skills = [
        {"name": "beta", "description": "vacuum robot grid"},
        {"name": "alpha", "description": "vacuum robot grid"},
    ]
    result = score_skills("vacuum robot", skills, THRESHOLD)
    assert result["selected"] == "alpha"
    assert result["reason"] == "tie broken by name"


def test_no_skills():
    result = score_skills("anything at all", [], THRESHOLD)
    assert result == {"candidates": [], "selected": None, "threshold": THRESHOLD, "reason": "no match"}


def test_deterministic():
    query = "check which topic notes the hook loads"
    assert score_skills(query, SKILLS, THRESHOLD) == score_skills(query, SKILLS, THRESHOLD)
