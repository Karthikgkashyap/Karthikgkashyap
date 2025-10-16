from __future__ import annotations

from typing import Dict, Any

from app.services.matcher import CareerMatcher
from app.services.dataset import DatasetLoader
from app.services.text_utils import split_skills


class AssessmentService:
    def __init__(self, matcher: CareerMatcher, dataset: DatasetLoader) -> None:
        self.matcher = matcher
        self.dataset = dataset

    def assess(self, interests: str, skills_text: str, education: str, experience: str) -> Dict[str, Any]:
        combined_text = "\n".join(filter(None, [interests, skills_text, education, experience]))
        ranked = self.matcher.rank_occupations_by_text(combined_text, top_k=5)
        enriched = self.matcher.enrich_ranked_results(ranked, user_skills_text=skills_text)
        # Suggest top courses for top skill gaps
        course_suggestions = {}
        user_skills = set(split_skills(skills_text))
        gap_counts = {}
        for item in enriched:
            for gap in item.get("skill_gaps", []):
                gap_counts[gap] = gap_counts.get(gap, 0) + 1
        top_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for gap, _ in top_gaps:
            course_suggestions[gap] = self.dataset.get_courses_for_skill(gap)
        return {
            "summary": {
                "skills_provided": list(user_skills),
                "top_skill_gaps": [gap for gap, _ in top_gaps],
            },
            "recommendations": enriched,
            "courses": course_suggestions,
        }
