"""The Claude-backed path, exercised against a stub SDK.

There is no API key in CI, so the model itself is not called here. What is
tested is the part that can be wrong without anyone noticing: that a tool_use
response is dispatched to the real tools, that the result is fed back in the
shape the Messages API expects, that the loop terminates, and that the history
is left in a state a follow-up question can continue from.
"""
from __future__ import annotations

import sys
import types
import unittest
from dataclasses import dataclass, field
from typing import Any

from deal_agent import tools
from deal_agent.agent import ClaudeAnswerer


@dataclass
class _TextBlock:
    text: str
    type: str = "text"


@dataclass
class _ToolUseBlock:
    name: str
    input: dict[str, Any]
    id: str = "toolu_1"
    type: str = "tool_use"


@dataclass
class _Response:
    content: list[Any]
    stop_reason: str


@dataclass
class _StubMessages:
    scripted: list[_Response]
    calls: list[dict[str, Any]] = field(default_factory=list)

    def create(self, **kwargs: Any) -> _Response:
        # The agent passes its live history list, which keeps growing - snapshot
        # it so each recorded call shows what was actually sent at the time.
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.scripted[min(len(self.calls) - 1, len(self.scripted) - 1)]


class _StubClient:
    def __init__(self, scripted: list[_Response]) -> None:
        self.messages = _StubMessages(scripted)


class _StubAnthropic:
    """Stands in for the `anthropic` module."""

    def __init__(self, scripted: list[_Response]) -> None:
        self.scripted = scripted
        self.client: _StubClient | None = None

    def Anthropic(self, api_key: str | None = None) -> _StubClient:  # noqa: N802
        self.client = _StubClient(self.scripted)
        return self.client


class ClaudeLoopTest(unittest.TestCase):
    def _install(self, scripted: list[_Response]) -> _StubAnthropic:
        stub = _StubAnthropic(scripted)
        module = types.ModuleType("anthropic")
        module.Anthropic = stub.Anthropic  # type: ignore[attr-defined]
        self.addCleanup(sys.modules.pop, "anthropic", None)
        sys.modules["anthropic"] = module
        return stub

    def test_tool_call_is_dispatched_and_answer_returned(self):
        stub = self._install(
            [
                _Response([_ToolUseBlock("model_exits", {})], "tool_use"),
                _Response([_TextBlock("The pref is short by $4.41M. [S9]")], "end_turn"),
            ]
        )
        agent = ClaudeAnswerer(api_key="stub")
        answer = agent.ask("Is the liqpref satisfied?")

        self.assertEqual(answer, "The pref is short by $4.41M. [S9]")
        assert stub.client is not None
        self.assertEqual(len(stub.client.messages.calls), 2)

        # The tool result must go back as a user turn carrying real tool output.
        second_call = stub.client.messages.calls[1]
        tool_turn = second_call["messages"][-1]
        self.assertEqual(tool_turn["role"], "user")
        block = tool_turn["content"][0]
        self.assertEqual(block["type"], "tool_result")
        self.assertEqual(block["tool_use_id"], "toolu_1")
        self.assertIn("NLPF liqpref", block["content"])

    def test_every_advertised_tool_round_trips(self):
        for schema in tools.TOOL_SCHEMAS:
            arguments = (
                {"total_future_proceeds": 200}
                if schema["name"] == "outcome_analysis"
                else {}
            )
            stub = self._install(
                [
                    _Response([_ToolUseBlock(schema["name"], arguments)], "tool_use"),
                    _Response([_TextBlock("ok")], "end_turn"),
                ]
            )
            agent = ClaudeAnswerer(api_key="stub")
            self.assertEqual(agent.ask("q"), "ok", schema["name"])
            assert stub.client is not None
            result = stub.client.messages.calls[1]["messages"][-1]["content"][0]["content"]
            self.assertNotIn("failed on", result, schema["name"])
            self.assertGreater(len(result), 40, schema["name"])

    def test_loop_gives_up_instead_of_spinning(self):
        self._install([_Response([_ToolUseBlock("deal_terms", {})], "tool_use")])
        agent = ClaudeAnswerer(api_key="stub", max_turns=3)
        self.assertIn("Gave up", agent.ask("loop forever"))

    def test_history_supports_follow_ups(self):
        self._install([_Response([_TextBlock("first")], "end_turn")])
        agent = ClaudeAnswerer(api_key="stub")
        agent.ask("one")
        agent.ask("two")
        roles = [turn["role"] for turn in agent.history]
        self.assertEqual(roles, ["user", "assistant", "user", "assistant"])

    def test_tools_and_system_prompt_are_actually_sent(self):
        stub = self._install([_Response([_TextBlock("hi")], "end_turn")])
        ClaudeAnswerer(api_key="stub").ask("q")
        assert stub.client is not None
        call = stub.client.messages.calls[0]
        self.assertEqual(
            [t["name"] for t in call["tools"]], [t["name"] for t in tools.TOOL_SCHEMAS]
        )
        self.assertIn("cite section ids", call["system"])


if __name__ == "__main__":
    unittest.main()
