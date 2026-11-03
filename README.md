# GPT Transcribe MCP

A small Python MCP server exposing `transcribe_audio`, copied from the original local OpenAI audio MCP used for narration review. The server sends a WAV recording to the OpenAI Audio Transcriptions API using model `gpt-transcribe` and requests Chinese output.

## Requirements

- Python 3.10 or newer, `mcp` and `httpx`.
- `OPENAI_API_KEY` in the server process environment, with access to the configured model.
- An existing WAV file at an absolute path, up to 240 seconds and 25,000,000 bytes. The original workflow expects mono PCM WAV; the server measures the duration with Python's `wave` module.

Each call uploads the recording to OpenAI and may incur API charges. Obtain permission from the recording owner and the person paying for API usage before submitting. Actual availability and pricing depend on your OpenAI account and current API offerings.

## Installation

```sh
git clone https://github.com/stevenke1981/gpt-transcribe-mcp.git
cd gpt-transcribe-mcp
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Configure an MCP client to start the environment's Python interpreter with the absolute path to `server.py` as its argument. Supply `OPENAI_API_KEY` securely through the client's environment; never commit it. For example:

```json
{
  "mcpServers": {
    "openai-audio-transcription": {
      "command": "C:\\path\\to\\gpt-transcribe-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\gpt-transcribe-mcp\\server.py"]
    }
  }
}
```

## Use

Call `transcribe_audio` with `{"audio_path": "C:\\absolute\\path\\narration.wav"}`. The result contains the transcript, duration, SHA-256, model name, request ID, and any usage reported by the API. The response does not contain word timestamps and does not verify pronunciation, completeness, or subtitle synchronization. Review audio manually for those purposes.

The original code is intentionally limited to short Chinese WAV inputs; it does not split long recordings. The included checks do not call the live API. Live model access and transcription are not verified by those checks.
