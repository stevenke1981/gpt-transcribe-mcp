"""Narrow OpenAI transcription MCP for the authorized zodiac audio review."""
import hashlib
import os
import wave
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

server = FastMCP('openai-audio-transcription')


@server.tool()
def transcribe_audio(audio_path: str) -> dict:
    """Transcribe one mono PCM WAV using OpenAI gpt-transcribe; billable."""
    path = Path(audio_path)
    if not path.is_absolute() or not path.is_file() or path.suffix.lower() != '.wav':
        raise ValueError('Expected an absolute path to an existing WAV file')
    with wave.open(str(path), 'rb') as wav:
        seconds = wav.getnframes() / wav.getframerate()
    if seconds <= 0 or seconds > 240 or path.stat().st_size > 25_000_000:
        raise ValueError('This task permits at most 240 seconds and 25 MB per request')
    if not os.environ.get('OPENAI_API_KEY'):
        raise ValueError('OPENAI_API_KEY is not configured')
    with path.open('rb') as audio, httpx.Client(timeout=180) as client:
        response = client.post('https://api.openai.com/v1/audio/transcriptions',
            headers={'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY']},
            data={'model': 'gpt-transcribe', 'language': 'zh', 'response_format': 'json'},
            files={'file': (path.name, audio, 'audio/wav')})
    response.raise_for_status()
    result = response.json()
    return {'model': 'gpt-transcribe', 'audio_seconds': seconds,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'text': result['text'], 'usage': result.get('usage'),
            'request_id': response.headers.get('x-request-id')}


if __name__ == '__main__':
    server.run(transport='stdio')
