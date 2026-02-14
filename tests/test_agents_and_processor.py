import sys
import types
import unittest
import asyncio
from unittest.mock import AsyncMock, patch


if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")
    openai_stub.OpenAI = object
    openai_stub.AsyncAzureOpenAI = object
    sys.modules["openai"] = openai_stub

if "dotenv" not in sys.modules:
    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv_stub

if "httpx" not in sys.modules:
    httpx_stub = types.ModuleType("httpx")
    httpx_stub.AsyncClient = object
    httpx_stub.Request = object
    httpx_stub.Response = object
    httpx_stub.AsyncHTTPTransport = object
    sys.modules["httpx"] = httpx_stub

from agents.editor_agent import EditorAgent
from agents.illustrator_agent import IllustratorAgent
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


class _FakeImageClient:
    def __init__(self, fail_with=None, success_call_number=2):
        self.calls = 0
        self.fail_with = fail_with
        self.success_call_number = success_call_number
        self.images = self

    async def generate(self, **kwargs):
        self.calls += 1
        if self.fail_with is not None:
            raise self.fail_with
        if self.calls < self.success_call_number:
            raise TimeoutError("temporary timeout")
        return types.SimpleNamespace(data=[types.SimpleNamespace(url="https://img.example/ok.png")])


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
        with patch.object(StoryProcessor, "load_azure_config", return_value={}):
            processor = StoryProcessor()
        html = processor.process("Line 1\nLine 2", "https://img.example/cover.png", "prompt")
        self.assertIn("<p>Line 1</p>", html)
        self.assertIn("https://img.example/cover.png", html)

    def test_story_processor_text_analytics_client_missing_config_returns_none(self):
        with patch.object(StoryProcessor, "load_azure_config", return_value={}):
            processor = StoryProcessor()
        self.assertIsNone(processor.create_text_analytics_client())

    def test_illustrator_retries_transient_error_then_succeeds(self):
        agent = IllustratorAgent.__new__(IllustratorAgent)
        agent.client = _FakeImageClient()
        agent.config = {
            "deployment_name": "image-model",
            "generation_params": {"n": 1},
            "image_size": "1024x1024",
            "max_retries": 2,
        }
        with patch("agents.illustrator_agent.asyncio.sleep", new_callable=AsyncMock) as sleep_mock:
            result = asyncio.run(agent.generate_cover_image("A story"))
        self.assertEqual(result, "https://img.example/ok.png")
        self.assertEqual(agent.client.calls, 2)
        sleep_mock.assert_awaited_once()

    def test_illustrator_does_not_retry_non_transient_error(self):
        agent = IllustratorAgent.__new__(IllustratorAgent)
        agent.client = _FakeImageClient(fail_with=ValueError("invalid prompt"))
        agent.config = {
            "deployment_name": "image-model",
            "generation_params": {"n": 1},
            "image_size": "1024x1024",
            "max_retries": 2,
        }
        with self.assertRaises(ValueError):
            asyncio.run(agent.generate_cover_image("A story"))
        self.assertEqual(agent.client.calls, 1)


if __name__ == "__main__":
    unittest.main()
