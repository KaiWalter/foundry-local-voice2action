# foundry-local-voice2action

Implement Voice 2 Action flow with [Foundry Local](https://www.foundrylocal.ai/) and Microsoft [Agent Framework](https://learn.microsoft.com/en-us/agent-framework/)

## Audio Transcription Dependencies

The Whisper-based transcription sample (`sample-transcribe.py`) relies on the FFmpeg CLI for decoding audio files. Install FFmpeg and ensure it is available on your `PATH` before running:

- **Windows:** `winget install Gyan.FFmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add the `bin` folder to `PATH`.
- **macOS (brew):** `brew install ffmpeg`
- **Linux (apt):** `sudo apt-get install ffmpeg`

After installation, re-run `uv run sample-transcribe.py` to verify that Whisper can find the FFmpeg executable.

## Troubleshooting

On corporate machine Foundry Local service is started but cannot be access by the apps. Issue might be that some of the randomly selected ports are blocked by the firewall. To fix this set a port that is not blocked:

```
foundry service set --port 5000
```

## Development Constitution

Follow .specify/memory/constitution.md for the project’s guiding principles:

- Application logic must always be accompanied by automated tests (refer to the Testable Application Logic principle).
- Any flow that invokes Foundry Local, CLI tooling, or other runtimes is currently treated as manual verification and must describe the observed behavior; mark these steps as non-testable following the Invocation Stewardship principle.
- Run all Python scripts and tests via `uv run …`, and use sample-agent-framework.py plus sample-transcribe.py as reference implementations before writing new tooling.
