from __future__ import annotations

from typing import Dict, Any, Optional, List
import uuid

from app.services.matcher import CareerMatcher
from app.services.dataset import DatasetLoader
from app.services.text_utils import split_skills


class ChatService:
    def __init__(self, matcher: CareerMatcher, dataset: DatasetLoader) -> None:
        self.matcher = matcher
        self.dataset = dataset
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def _ensure_session(self, session_id: Optional[str]) -> str:
        if session_id and session_id in self.sessions:
            return session_id
        new_id = session_id or str(uuid.uuid4())
        if new_id not in self.sessions:
            self.sessions[new_id] = []
        return new_id

    def reply(self, message: str, session_id: Optional[str]) -> Dict[str, Any]:
        sid = self._ensure_session(session_id)
        history = self.sessions[sid]
        history.append({"role": "user", "content": message})

        response_text = self._generate_response(message)
        history.append({"role": "assistant", "content": response_text})

        return {"session_id": sid, "message": response_text}

    def _generate_response(self, message: str) -> str:
        lower = (message or "").lower()
        if any(k in lower for k in ["hello", "hi", "hey"]):
            return (
                "Hi! I’m your career guide. Share your skills, interests, and goals "
                "and I’ll suggest roles and learning paths."
            )
        if "resume" in lower and "feedback" in lower:
            return (
                "Paste sections of your resume here. I’ll analyze structure, action verbs, "
                "and skill alignment, and suggest improvements."
            )
        if "skills" in lower and "match" in lower:
            return (
                "List your skills separated by commas, and optionally your interests. "
                "I’ll match you to relevant occupations."
            )
        # Fallback: offer guidance to try endpoints
        return (
            "You can: (1) Get an assessment via the form on the home page, "
            "(2) POST /api/match with your skills to see top roles, or (3) "
            "POST /api/resume_feedback for resume suggestions."
        )
