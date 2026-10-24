"""
Hybrid AI Recommendation Engine for AI-Based Job Recommendation System.
Combines Content TF-IDF, Skill Taxonomy Matching, Experience Level Fit,
Salary/Location Fit, and Education Alignment with Explainable AI (XAI) output.
"""

import math
from typing import List, Dict, Any, Tuple
import numpy as np
from tfidf_engine import compute_cosine_similarity
from skill_matcher import evaluate_skills

class HybridRecommenderEngine:
    WEIGHTS = {
        'text_similarity': 0.35,
        'skill_match': 0.30,
        'experience_fit': 0.15,
        'salary_location': 0.10,
        'education_domain': 0.10
    }

    DEGREE_HIERARCHY = {
        'none': 0, 'high school': 1, 'associate': 2,
        'bachelor': 3, 'master': 4, 'phd': 5
    }

    def evaluate_experience(self, cand_exp: float, min_exp: float, max_exp: float) -> float:
        if min_exp <= cand_exp <= max_exp:
            return 1.0
        elif cand_exp < min_exp:
            gap = min_exp - cand_exp
            return float(np.exp(-0.4 * gap))
        else:
            gap = cand_exp - max_exp
            return float(np.maximum(0.6, 1.0 - 0.05 * gap))

    def evaluate_salary_location(self, cand_sal: float, job_sal_min: float, job_sal_max: float,
                                 cand_loc: str, cand_pref_loc: str, job_loc: str, work_type: str) -> float:
        if job_sal_max is None or job_sal_max == 0:
            sal_score = 1.0
        elif cand_sal <= job_sal_max:
            sal_score = 1.0
        else:
            overage = (cand_sal - job_sal_max) / job_sal_max
            sal_score = float(np.maximum(0.0, 1.0 - overage))

        c_loc_clean = cand_loc.lower()
        p_loc_clean = cand_pref_loc.lower()
        j_loc_clean = job_loc.lower()

        if work_type == "Remote" or "remote" in p_loc_clean or j_loc_clean in p_loc_clean or j_loc_clean in c_loc_clean:
            loc_score = 1.0
        elif "onsite" in work_type.lower() and c_loc_clean == j_loc_clean:
            loc_score = 1.0
        else:
            loc_score = 0.65

        return round(0.5 * sal_score + 0.5 * loc_score, 4)

    def evaluate_education(self, cand_degree: str, required_degree: str = "Bachelor") -> float:
        cand_level = self.DEGREE_HIERARCHY.get(cand_degree.lower(), 3)
        req_level = self.DEGREE_HIERARCHY.get(required_degree.lower(), 3)
        if cand_level >= req_level:
            return 1.0
        return round(cand_level / req_level, 4)

    def match_pair(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        resume_text = f"{candidate.get('current_title', '')} {candidate.get('resume_text', '')} {candidate.get('summary', '')}"
        job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('category', '')}"

        text_sim = compute_cosine_similarity(resume_text, job_text)
        skill_score, skill_details = evaluate_skills(
            candidate.get("skills", []),
            job.get("required_skills", []),
            job.get("preferred_skills", [])
        )
        exp_score = self.evaluate_experience(
            float(candidate.get("years_experience", 0)),
            float(job.get("min_experience", 0)),
            float(job.get("max_experience", 5))
        )
        sal_loc_score = self.evaluate_salary_location(
            float(candidate.get("expected_salary", 80000)),
            float(job.get("min_salary", 0)),
            float(job.get("max_salary", 120000)),
            candidate.get("location", ""),
            candidate.get("preferred_location", ""),
            job.get("location", ""),
            job.get("work_type", "Remote")
        )
        edu_score = self.evaluate_education(
            candidate.get("education", "Bachelor"),
            "Bachelor"
        )

        composite_score = (
            self.WEIGHTS['text_similarity'] * text_sim +
            self.WEIGHTS['skill_match'] * skill_score +
            self.WEIGHTS['experience_fit'] * exp_score +
            self.WEIGHTS['salary_location'] * sal_loc_score +
            self.WEIGHTS['education_domain'] * edu_score
        )

        match_drivers = []
        if skill_details['required_match_ratio'] == 1.0:
            match_drivers.append("100% match on all mandatory required technical skills.")
        elif skill_details['required_match_ratio'] >= 0.67:
            match_drivers.append(f"Strong technical skill overlap ({int(skill_details['required_match_ratio']*100)}% required skills).")

        if exp_score == 1.0:
            match_drivers.append(f"Years of experience ({candidate.get('years_experience')} yrs) falls within requested range ({job.get('min_experience')}-{job.get('max_experience')} yrs).")

        if sal_loc_score >= 0.85:
            match_drivers.append("High alignment on salary expectations and work location/type.")

        if text_sim >= 0.25:
            match_drivers.append("High semantic content relevance between candidate resume and job description.")

        if not match_drivers:
            match_drivers.append("Partial alignment across skills and job profile.")

        return {
            "candidate_id": candidate["id"],
            "candidate_name": candidate.get("name", "Candidate"),
            "candidate_title": candidate.get("current_title", ""),
            "job_id": job["id"],
            "job_title": job.get("title", ""),
            "job_company": job.get("company", ""),
            "job_location": job.get("location", ""),
            "composite_score": round(composite_score, 4),
            "match_percentage": round(composite_score * 100, 1),
            "score_breakdown": {
                "text_similarity": round(text_sim, 4),
                "skill_match": round(skill_score, 4),
                "experience_fit": round(exp_score, 4),
                "salary_location": round(sal_loc_score, 4),
                "education_fit": round(edu_score, 4)
            },
            "skill_analysis": skill_details,
            "key_match_drivers": match_drivers
        }

    def recommend_jobs_for_candidate(self, candidate: Dict[str, Any], jobs: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        results = [self.match_pair(candidate, job) for job in jobs]
        results.sort(key=lambda x: x["composite_score"], reverse=True)
        return results[:top_k]

    def recommend_candidates_for_job(self, job: Dict[str, Any], candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        results = [self.match_pair(cand, job) for cand in candidates]
        results.sort(key=lambda x: x["composite_score"], reverse=True)
        return results[:top_k]