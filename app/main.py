import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from manager_agent import ManagerAgent, PromptInjectionDetected  # noqa: E402

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas import SummaryReport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("md5scribe")

app = FastAPI()
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")

manager_agent = ManagerAgent()

_EXTENSION_BY_MIME = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/mp4": ".mp4",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
}


def _suffix_for(upload: UploadFile) -> str:
    content_type = (upload.content_type or "").split(";")[0].strip().lower()
    if content_type in _EXTENSION_BY_MIME:
        return _EXTENSION_BY_MIME[content_type]
    return Path(upload.filename or "").suffix or ".webm"


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.post("/report", response_class=HTMLResponse)
def create_report(request: Request, audio: UploadFile = File(...)):
    tmp_path = None
    try:
        suffix = _suffix_for(audio)
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            shutil.copyfileobj(audio.file, tmp)
            tmp_path = tmp.name

        raw_report = manager_agent.summaries_audio(tmp_path)
        report = SummaryReport.model_validate(raw_report)
        return templates.TemplateResponse(
            request=request, name="partials/report.html", context={"report": report}
        )

    except PromptInjectionDetected as exc:
        logger.warning("Contenu rejeté par la modération: %s", exc.reason)
        return templates.TemplateResponse(
            request=request,
            name="partials/error_moderation.html",
            context={"reason": exc.reason},
            status_code=422,
        )

    except Exception:
        logger.exception("Erreur inattendue pendant la génération du rapport")
        return templates.TemplateResponse(
            request=request,
            name="partials/error_generic.html",
            context={},
            status_code=500,
        )

    finally:
        audio.file.close()
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
