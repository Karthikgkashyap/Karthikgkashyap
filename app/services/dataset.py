from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
import json


@dataclass
class Occupation:
    id: str
    name: str
    description: str
    required_skills: List[str]
    optional_skills: List[str]
    typical_education: str
    avg_salary_usd: int
    growth_outlook: str


class DatasetLoader:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = Path(data_dir)
        self._occupations: List[Occupation] = []
        self._courses: Dict[str, List[Dict[str, Any]]] = {}

    def load(self) -> None:
        occupations_fp = self.data_dir / "occupations.json"
        courses_fp = self.data_dir / "courses.json"
        self._occupations = []
        if occupations_fp.exists():
            with open(occupations_fp, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for item in raw:
                self._occupations.append(
                    Occupation(
                        id=item["id"],
                        name=item["name"],
                        description=item["description"],
                        required_skills=item.get("required_skills", []),
                        optional_skills=item.get("optional_skills", []),
                        typical_education=item.get("typical_education", ""),
                        avg_salary_usd=item.get("avg_salary_usd", 0),
                        growth_outlook=item.get("growth_outlook", ""),
                    )
                )
        if courses_fp.exists():
            with open(courses_fp, "r", encoding="utf-8") as f:
                self._courses = json.load(f)

    def get_occupations(self) -> List[Occupation]:
        return list(self._occupations)

    def get_courses_for_skill(self, skill: str) -> List[Dict[str, Any]]:
        key = skill.strip().lower()
        return self._courses.get(key, [])

    def get_occupations_overview(self) -> List[Dict[str, Any]]:
        overview = []
        for occ in self._occupations:
            overview.append(
                {
                    "id": occ.id,
                    "name": occ.name,
                    "description": occ.description,
                    "required_skills": occ.required_skills,
                    "optional_skills": occ.optional_skills,
                    "typical_education": occ.typical_education,
                    "avg_salary_usd": occ.avg_salary_usd,
                    "growth_outlook": occ.growth_outlook,
                }
            )
        return overview
