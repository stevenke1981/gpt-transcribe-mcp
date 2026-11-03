import asyncio
import os
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import server


class ServerTests(unittest.TestCase):
    def test_tool_discovery(self):
        tools = asyncio.run(server.server.list_tools())
        self.assertIn('transcribe_audio', [tool.name for tool in tools])

    def test_invalid_path(self):
        with self.assertRaises(ValueError):
            server.transcribe_audio('relative.wav')

    def test_missing_key_and_mock_response(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.wav'
            with wave.open(str(path), 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(8000)
                wav.writeframes(b'\0\0' * 8000)
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(ValueError, 'OPENAI_API_KEY'):
                    server.transcribe_audio(str(path))
            response = MagicMock()
            response.json.return_value = {'text': '測試'}
            response.headers = {'x-request-id': 'mock-request'}
            client = MagicMock()
            client.__enter__.return_value.post.return_value = response
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}), patch.object(server.httpx, 'Client', return_value=client):
                result = server.transcribe_audio(str(path))
            self.assertEqual(result['text'], '測試')
            self.assertEqual(result['audio_seconds'], 1)
            self.assertEqual(result['request_id'], 'mock-request')
            response.raise_for_status.assert_called_once()


if __name__ == '__main__':
    unittest.main()
