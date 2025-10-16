from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.services.dataset import DatasetLoader
from app.services.matcher import CareerMatcher
from app.services.assessment import AssessmentService
from app.services.resume_feedback import ResumeFeedbackService
from app.services.chat import ChatService


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Career Guidance AI Chatbot")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class AssessmentRequest(BaseModel):
    interests: str = Field("", description="Your interests and passions")
    skills: str = Field("", description="Your current skills, comma or space separated")
    education: str = Field("", description="Education or certifications")
    experience: str = Field("", description="Past roles, projects, industries")


class MatchRequest(BaseModel):
    skills: str = ""
    interests: Optional[str] = ""
    top_k: int = 5


class ResumeRequest(BaseModel):
    resume_text: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


# Global singletons initialized on startup
_dataset_loader: Optional[DatasetLoader] = None
_matcher: Optional[CareerMatcher] = None
_assessment: Optional[AssessmentService] = None
_resume_feedback: Optional[ResumeFeedbackService] = None
_chat: Optional[ChatService] = None


@app.on_event("startup")
async def on_startup() -> None:
    global _dataset_loader, _matcher, _assessment, _resume_feedback, _chat
    _dataset_loader = DatasetLoader(data_dir=str(BASE_DIR / "data"))
    _dataset_loader.load()

    _matcher = CareerMatcher(_dataset_loader)
    _matcher.build()

    _assessment = AssessmentService(_matcher, _dataset_loader)
    _resume_feedback = ResumeFeedbackService(_matcher, _dataset_loader)
    _chat = ChatService(_matcher, _dataset_loader)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/occupations")
async def list_occupations() -> JSONResponse:
    assert _dataset_loader is not None
    occupations = _dataset_loader.get_occupations_overview()
    return JSONResponse({"occupations": occupations})


@app.post("/api/assess")
async def assess(request: AssessmentRequest) -> JSONResponse:
    assert _assessment is not None
    result = _assessment.assess(
        interests=request.interests,
        skills_text=request.skills,
        education=request.education,
        experience=request.experience,
    )
    return JSONResponse(result)


@app.post("/api/match")
async def match(request: MatchRequest) -> JSONResponse:
    assert _matcher is not None
    combined_text = (request.skills or "") + "\n" + (request.interests or "")
    ranked = _matcher.rank_occupations_by_text(combined_text, top_k=request.top_k)
    enriched = _matcher.enrich_ranked_results(ranked, user_skills_text=request.skills)
    return JSONResponse({"results": enriched})


@app.post("/api/resume_feedback")
async def resume_feedback(request: ResumeRequest) -> JSONResponse:
    assert _resume_feedback is not None
    feedback = _resume_feedback.review_resume(request.resume_text)
    return JSONResponse(feedback)


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> JSONResponse:
    assert _chat is not None
    reply = _chat.reply(message=request.message, session_id=request.session_id)
    return JSONResponse(reply)
