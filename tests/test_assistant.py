import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistant import asr, chat, config, server  # noqa: E402


class TestServerHealth(unittest.TestCase):
    @patch("assistant.server.server_up", return_value=False)
    def test_start_server_requires_flm(self, _mock_up):
        with patch("shutil.which", return_value=None):
            with self.assertRaises(SystemExit):
                server.ensure_flm()

    def test_server_up_detects_down(self):
        # no server should be running in a fresh test env
        self.assertFalse(server.server_up())


class TestASRRequest(unittest.TestCase):
    def test_transcribe_requires_running_server(self):
        with patch("assistant.server.server_up", return_value=False):
            with self.assertRaises(RuntimeError):
                asr.transcribe_text("/does/not/matter.wav")


class TestChatRequest(unittest.TestCase):
    def test_chat_requires_running_server(self):
        with patch("assistant.server.server_up", return_value=False):
            with self.assertRaises(RuntimeError):
                chat.chat_reply("hi")


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        self.assertTrue(config.FLM_BASE.startswith("http://"))
        self.assertEqual(config.LLM_MODEL, "gemma3:1b")
        self.assertEqual(config.ASR_MODEL, "whisper-v3")


if __name__ == "__main__":
    unittest.main(verbosity=2)