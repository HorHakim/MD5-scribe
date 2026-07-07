# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

MD5-scribe turns a voice recording into a structured JSON report (title, summary, key points, decisions, actions). It has two layers:

- `src/` — the multi-agent pipeline (business logic). Pure Python, no web framework. Usable standalone from the CLI.
- `app/` — a FastAPI + HTMX web UI wrapping the pipeline. Records audio via the browser's MediaRecorder API (no file upload), posts it to the server, and renders the report as an HTML fragment.

## Commands

```bash
# Setup (venv already exists at env/)
./env/bin/pip install -r requirements.txt

# Run the web app (from repo root — required for absolute path resolution to work correctly, see below)
./env/bin/uvicorn app.main:app --reload --port 8000
# then open http://localhost:8000/

# Run a single pipeline agent directly (CLI usage, also from repo root)
./env/bin/python src/manager_agent.py         # full pipeline on data/AUDIO.mp3
./env/bin/python src/speech_to_text_agent.py  # STT only
./env/bin/python src/moderator_agent.py       # moderation only, tests both a benign and an injection sample
./env/bin/python src/summary_agent.py         # summarization only
```

There is no test suite, linter, or build step configured in this repo.

`GROQ_API_KEY` must be set (via `.env` at the repo root, or injected as an env var in production) — `src/config.py` raises at import time if it's missing.

## Architecture

### Pipeline (`src/`)

Flat imports throughout (`from config import ...`, not package-relative) — this is intentional so each agent file keeps working as a standalone CLI script (`python src/xxx.py`) run from the repo root. Do not turn `src/` into a proper package (no `src/__init__.py`, no relative imports) without also reconsidering how `app/main.py` bootstraps `sys.path`.

- `agent.py` — base class `Agent`: holds a shared `Groq` client (`self.client`) and a static `read_file` helper for loading system prompts. Every other agent subclasses this.
- `config.py` — model names (`STT_MODEL`, `LLM_MODEL`, both served through the Groq API — `LLM_MODEL` is `openai/gpt-oss-120b` hosted on Groq, not the OpenAI API), `GROQ_API_KEY`, and `BASE_DIR`/`PROMPTS_DIR` (absolute paths, `Path(__file__).resolve().parent.parent`-based) used by the other agents to load prompt files regardless of the process's current working directory.
- `speech_to_text_agent.py` — `SpeechToTextAgent.get_text_from_audio(audio_file_path: str) -> str`. Opens the file by disk path (not bytes/stream) and calls Groq's Whisper (`whisper-large-v3-turbo`).
- `moderator_agent.py` — `ModeratorAgent.moderate_transcript(text: str) -> dict` with shape `{"prompt_injection": bool, "raison": str}`. Prompt is `prompts/moderator_prompt_system.txt`. Detects attempts to redirect/reconfigure the downstream summarizer (not just any imperative language in the transcript — reported speech like "dis à Marc de rappeler le client" is legitimate content, not injection).
- `summary_agent.py` — `SummaryAgent.summarise_text(text: str) -> dict` with shape `{"titre", "resume", "points_cles", "decisions", "actions"}`. Prompt is `prompts/summary_prompt_system.txt`. **Quirk**: per the prompt's own spec, `decisions`/`actions` are either a list of strings or the literal string `"null"` (not JSON `null`, not an empty list) when there's nothing to report — anything consuming this dict must normalize that marker (see `app/schemas.py`).
- `manager_agent.py` — orchestrator, the pipeline's single entry point: `ManagerAgent.summaries_audio(audio_file_path: str) -> dict`. Calls STT → moderation → summary in sequence. Raises `PromptInjectionDetected(reason)` if moderation flags the transcript, instead of returning a summary. No retry/timeout handling around the Groq calls — SDK exceptions propagate as-is.

### Web app (`app/`)

A thin HTTP adapter over `src/`, kept as a separate top-level package specifically so `src/` never has to depend on FastAPI/Jinja2/pydantic. `app/main.py` bootstraps this by inserting `src/` into `sys.path` before importing from it:

```python
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))
from manager_agent import ManagerAgent, PromptInjectionDetected
```

- `main.py` — `ManagerAgent()` is instantiated once at module load (Groq clients are reusable). `GET /` renders the recorder page. `POST /report` accepts `audio: UploadFile` (multipart, whatever blob MediaRecorder produced — webm/ogg/mp4), writes it to a named temp file (extension inferred from `content_type`, since `get_text_from_audio` needs a disk path), runs the pipeline, and always deletes the temp file in a `finally`. The route is a plain `def` (not `async def`) so FastAPI runs it in a threadpool — the Groq SDK calls inside are blocking.
- Error mapping: `PromptInjectionDetected` → HTTP 422 + `partials/error_moderation.html` (shows the reason). Any other exception → HTTP 500 + `partials/error_generic.html` (generic message to the client; full traceback goes to the server log via `logger.exception`, never to the client).
- `schemas.py` — `SummaryReport` Pydantic model; a `field_validator` on `decisions`/`actions` collapses the `"null"` string marker (and `None`) to `[]`. This is the one place that quirk is handled.
- Templates use Jinja2's default autoescaping — the LLM-generated report text is rendered as-is, escaping is what makes that safe.
- `static/js/recorder.js` — vanilla JS using `MediaRecorder`. On stop, it builds a `File` from the recorded `Blob` and injects it into a hidden `<input type="file">` via the `DataTransfer` trick, then calls `form.requestSubmit()`. This lets htmx's own `hx-encoding="multipart/form-data"` handle the actual submission — there's no manual `fetch`/swap code.
- htmx is vendored at `static/js/vendor/htmx.min.js` (no CDN dependency at runtime).
- **htmx + non-2xx responses**: htmx does not swap content on error status codes by default. `templates/base.html` registers an `htmx:beforeSwap` listener that forces the swap for 422/500 so the error partials actually render, while still preserving the real HTTP status code.

### Deployment

`Procfile` runs `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, intended for Railway (ephemeral filesystem, no persistence — every request is processed and forgotten, nothing is written to disk beyond the request-scoped temp audio file). Because `PROMPTS_DIR` in `config.py` is resolved from `__file__`, the app works regardless of the process's working directory — this matters since Railway's start command doesn't guarantee `cwd` is the repo root the way local CLI usage does.
