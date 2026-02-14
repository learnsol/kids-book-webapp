import sys
import types
import unittest
from unittest.mock import patch


if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")
    openai_stub.OpenAI = object
    openai_stub.AsyncAzureOpenAI = object
    sys.modules["openai"] = openai_stub

if "dotenv" not in sys.modules:
    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv_stub

from agents.editor_agent import EditorAgent
from agents.story_processor import StoryProcessor


class _FakeCompletionClient:
    def __init__(self):
        self.calls = 0
        self.chat = types.SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls += 1
        if self.calls < 2:
            raise RuntimeError("temporary failure")
        message = types.SimpleNamespace(content="Edited story text")
        choice = types.SimpleNamespace(message=message)
        return types.SimpleNamespace(choices=[choice])


class AgentAndProcessorTests(unittest.TestCase):
    def test_editor_filter_content_removes_banned_terms(self):
        agent = EditorAgent.__new__(EditorAgent)
        filtered = agent.filter_content("Happy start. A scary ending.")
        self.assertIn("Happy start.", filtered)
        self.assertNotIn("scary", filtered.lower())

    def test_editor_edit_story_retries_then_succeeds(self):
        agent = EditorAgent.__new__(EditorAgent)
        agent.client = _FakeCompletionClient()
        agent.config = {
            "deployment_name": "model",
            "prompt": {"system": "system prompt"},
            "temperature": 0.7,
            "max_tokens": 256,
            "max_retries": 2,
        }
        with patch("agents.editor_agent.time.sleep", return_value=None):
            result = agent.edit_story("Once upon a time")
        self.assertEqual(result["final_story"], "Edited story text")
        self.assertEqual(agent.client.calls, 2)

    def test_story_processor_generates_html(self):
        processor = StoryProcessor()
        html = processor.process("Line 1\nLine 2", "https://img.example/cover.png", "prompt")
        self.assertIn("<p>Line 1</p>", html)
        self.assertIn("https://img.example/cover.png", html)

    def test_story_processor_text_analytics_client_missing_config_returns_none(self):
        processor = StoryProcessor()
        processor.azure_config = {}
        self.assertIsNone(processor.create_text_analytics_client())


if __name__ == "__main__":
    unittest.main()
