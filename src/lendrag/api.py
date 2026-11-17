"""REST API + a small web UI.  Run:  uv run uvicorn lendrag.api:app --reload"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import Settings
from .llm import LLMError
from .rag import answer_question
from .retrieval import Retriever

STATIC = Path(__file__).parent / "static"
state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    state["settings"] = settings
    state["retriever"] = Retriever(settings)
    yield
    state["retriever"].close()


app = FastAPI(title="Lending Policy Assistant", version="0.1.0", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class Source(BaseModel):
    number: int
    document: str
    section: str
    text: str
    cited: bool


class AskResponse(BaseModel):
    answer: str
    answered: bool
    sources: list[Source]
    latency_ms: int


@app.get("/health")
def health() -> dict:
    s: Settings = state["settings"]
    return {"status": "ok", "chunks": len(state["retriever"].chunks), "chat_model": s.chat_model}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        result = answer_question(req.question, state["retriever"], state["settings"])
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return AskResponse(
        answer=result.text,
        answered=result.answered,
        latency_ms=result.latency_ms,
        sources=[
            Source(number=i, document=c.title, section=c.section, text=c.text, cited=i in result.cited)
            for i, c in enumerate(result.sources, start=1)
        ],
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")
