from __future__ import annotations

from typing import List, Tuple, Dict, Any
import math
from collections import Counter, defaultdict

from app.services.dataset import DatasetLoader, Occupation
from app.services.text_utils import extract_words, split_skills


class CareerMatcher:
    def __init__(self, dataset: DatasetLoader) -> None:
        self.dataset = dataset
        self.occupation_docs: List[str] = []
        self.occupations: List[Occupation] = []

        # Simple TF-IDF data structures
        self.vocabulary: List[str] = []
        self.idf: Dict[str, float] = {}
        self.doc_tfidf_list: List[Dict[str, float]] = []
        self.doc_norms: List[float] = []

    def build(self) -> None:
        # Prepare documents
        self.occupations = self.dataset.get_occupations()
        self.occupation_docs = []
        tokenized_docs: List[List[str]] = []

        for occ in self.occupations:
            doc = " ".join(
                [
                    occ.name,
                    occ.description,
                    " ".join(occ.required_skills),
                    " ".join(occ.optional_skills),
                    occ.typical_education,
                    occ.growth_outlook,
                ]
            )
            self.occupation_docs.append(doc)
            tokens = extract_words(doc)
            tokenized_docs.append(tokens)

        # Build vocabulary and IDF
        num_docs = len(tokenized_docs)
        df_counts: Dict[str, int] = defaultdict(int)
        for tokens in tokenized_docs:
            for term in set(tokens):
                df_counts[term] += 1

        self.vocabulary = sorted(df_counts.keys())
        self.idf = {}
        for term, df in df_counts.items():
            # Smooth IDF
            self.idf[term] = math.log((1 + num_docs) / (1 + df)) + 1.0

        # Compute TF-IDF for documents
        self.doc_tfidf_list = []
        self.doc_norms = []
        for tokens in tokenized_docs:
            tf = Counter(tokens)
            doc_len = max(1, len(tokens))
            weights: Dict[str, float] = {}
            norm_sq = 0.0
            for term, count in tf.items():
                idf = self.idf.get(term, 0.0)
                tf_weight = count / doc_len
                w = tf_weight + 0.0
                w *= idf
                if w:
                    weights[term] = w
                    norm_sq += w * w
            self.doc_tfidf_list.append(weights)
            self.doc_norms.append(math.sqrt(norm_sq) if norm_sq > 0 else 1.0)

    def rank_occupations_by_text(self, text: str, top_k: int = 5) -> List[Tuple[int, float]]:
        if not text or not self.doc_tfidf_list:
            return []

        tokens = extract_words(text)
        if not tokens:
            return []

        tf = Counter(tokens)
        q_len = max(1, len(tokens))
        q_weights: Dict[str, float] = {}
        q_norm_sq = 0.0
        for term, count in tf.items():
            idf = self.idf.get(term, 0.0)
            tf_weight = count / q_len
            w = tf_weight * idf
            if w:
                q_weights[term] = w
                q_norm_sq += w * w
        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0 else 1.0

        sims: List[Tuple[int, float]] = []
        for idx, (doc_weights, doc_norm) in enumerate(zip(self.doc_tfidf_list, self.doc_norms)):
            # Dot product only over overlapping terms
            dot = 0.0
            for term, q_w in q_weights.items():
                d_w = doc_weights.get(term)
                if d_w:
                    dot += q_w * d_w
            sim = dot / (q_norm * doc_norm) if q_norm and doc_norm else 0.0
            sims.append((idx, sim))

        ranked_indices = sorted(sims, key=lambda x: x[1], reverse=True)
        return ranked_indices[:top_k]

    def enrich_ranked_results(self, ranked: List[Tuple[int, float]], user_skills_text: str = "") -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        user_skills = set(split_skills(user_skills_text))
        for idx, score in ranked:
            if idx < 0 or idx >= len(self.occupations):
                continue
            occ = self.occupations[idx]
            occ_skills = set([s.lower() for s in (occ.required_skills + occ.optional_skills)])
            matched = sorted(list(occ_skills.intersection(user_skills)))
            gaps = sorted(list(occ_skills.difference(user_skills)))
            results.append(
                {
                    "id": occ.id,
                    "name": occ.name,
                    "score": float(score),
                    "matched_skills": matched,
                    "skill_gaps": gaps,
                    "avg_salary_usd": occ.avg_salary_usd,
                    "growth_outlook": occ.growth_outlook,
                    "typical_education": occ.typical_education,
                    "description": occ.description,
                }
            )
        return results
