import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assistant import asr, chat, config, server, history, tts  # noqa: E402


class TestServerHealth(unittest.TestCase):
    @patch("assistant.server.server_up", return_value=False)
    def test_start_server_requires_flm(self, _mock_up):
        with patch("shutil.which", return_value=None):
            with self.assertRaises(SystemExit):
                server.ensure_flm()

    def test_server_up_false_when_endpoint_unreachable(self):
        with patch("assistant.server.urllib.request.urlopen",
                   side_effect=OSError("refused")):
            self.assertFalse(server.server_up())


class TestASRRequest(unittest.TestCase):
    def test_transcribe_requires_running_server(self):
        # asr.py binds `server_up` by name at import, so patch it there.
        with patch("assistant.asr.server_up", return_value=False):
            with self.assertRaises(RuntimeError):
                asr.transcribe_text("/does/not/matter.wav")


class TestChatRequest(unittest.TestCase):
    def test_chat_requires_running_server(self):
        with patch("assistant.chat.server_up", return_value=False):
            with self.assertRaises(RuntimeError):
                chat.chat_reply("hi")


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        self.assertTrue(config.FLM_BASE.startswith("http://"))
        self.assertEqual(config.LLM_MODEL, "gemma3:1b")
        self.assertEqual(config.ASR_MODEL, "whisper-v3")


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()) / "chat-history.json"

    def tearDown(self):
        self.tmp.unlink(missing_ok=True)

    def test_load_missing_returns_fresh(self):
        h = history.load_history(self.tmp)
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["role"], "system")

    def test_round_trip(self):
        msgs = [
            dict(history.SYSTEM_PROMPT),
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]
        history.save_history(msgs, self.tmp)
        self.assertEqual(history.load_history(self.tmp), msgs)

    def test_corrupt_file_returns_fresh(self):
        self.tmp.write_text("{not json")
        h = history.load_history(self.tmp)
        self.assertEqual(h[0]["role"], "system")

    def test_clear_removes_file(self):
        history.save_history([dict(history.SYSTEM_PROMPT)], self.tmp)
        history.clear_history(self.tmp)
        self.assertFalse(self.tmp.exists())


class TestTTS(unittest.TestCase):
    def test_speak_does_not_use_output_raw(self):
        with patch("assistant.tts.ensure_voice"), \
             patch("assistant.tts.shutil.which", return_value="/usr/bin/pw-play"), \
             patch("assistant.tts.subprocess.run") as m_run, \
             patch("assistant.tts.subprocess.Popen") as m_popen:
            m_popen.return_value.wait.return_value = 0
            tts.speak("hello there")
        argv = m_run.call_args[0][0]
        self.assertIn("piper-tts", argv)
        self.assertIn("-f", argv)
        self.assertNotIn("--output-raw", argv)

    def test_speak_skips_empty_text(self):
        with patch("assistant.tts.ensure_voice") as m_ensure, \
             patch("assistant.tts.subprocess.run") as m_run:
            tts.speak("   ")
        m_ensure.assert_not_called()
        m_run.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)