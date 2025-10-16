from __future__ import annotations

from typing import Dict, Any, List
import re

from app.services.matcher import CareerMatcher
from app.services.dataset import DatasetLoader
from app.services.text_utils import extract_words, split_skills


class ResumeFeedbackService:
    def __init__(self, matcher: CareerMatcher, dataset: DatasetLoader) -> None:
        self.matcher = matcher
        self.dataset = dataset

    def review_resume(self, resume_text: str) -> Dict[str, Any]:
        words = extract_words(resume_text)
        length = len(resume_text)
        word_count = len(words)

        issues: List[str] = []
        if word_count < 150:
            issues.append("Resume appears short; consider adding more detail.")
        if re.search(r"\bI\b", resume_text):
            issues.append("Avoid first-person pronouns; prefer concise bullet points.")
        if not re.search(r"\b(achieved|reduced|increased|optimized|designed|built|led)\b", resume_text, re.I):
            issues.append("Add action verbs and quantified impact.")

        # Suggest careers based on resume
        ranked = self.matcher.rank_occupations_by_text(resume_text, top_k=5)
        recommendations = self.matcher.enrich_ranked_results(ranked)

        return {
            "metrics": {"chars": length, "words": word_count},
            "issues": issues,
            "recommendations": recommendations,
        }
