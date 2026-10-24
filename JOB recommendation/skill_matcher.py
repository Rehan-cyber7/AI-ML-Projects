"""
Skill Extraction, Taxonomy Alignment & Skill Match Evaluator Module.
Handles skill normalization, required vs preferred skill weights, and skill gap identification.
"""

from typing import List, Dict, Any, Tuple, Set

SKILL_ALIASES = {
    "py": "Python", "python3": "Python", "cpython": "Python",
    "js": "JavaScript", "node": "JavaScript", "react.js": "React", "reactjs": "React",
    "cpp": "C++", "c plus plus": "C++",
    "ml": "Machine Learning", "dl": "Deep Learning", "neural networks": "Deep Learning",
    "nlp": "NLP", "natural language processing": "NLP", "llm": "NLP", "transformers": "NLP",
    "cv": "Computer Vision", "opencv": "Computer Vision",
    "k8s": "Kubernetes", "containerization": "Docker", "containers": "Docker",
    "aws": "AWS", "amazon web services": "AWS",
    "sql": "SQL", "postgresql": "SQL", "mysql": "SQL", "sqlite": "SQL",
    "pyspark": "Apache Spark", "spark": "Apache Spark",
    "snowflake": "Snowflake", "ga4": "Google Analytics"
}

def normalize_skill(skill: str) -> str:
    cleaned = skill.strip().lower()
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    return skill.strip().title()

def evaluate_skills(candidate_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> Tuple[float, Dict[str, Any]]:
    cand_set: Set[str] = {normalize_skill(s).lower() for s in candidate_skills}
    req_set: Set[str] = {normalize_skill(s).lower() for s in required_skills}
    pref_set: Set[str] = {normalize_skill(s).lower() for s in preferred_skills}

    req_matched = cand_set.intersection(req_set)
    pref_matched = cand_set.intersection(pref_set)

    req_ratio = len(req_matched) / len(req_set) if req_set else 1.0
    pref_ratio = len(pref_matched) / len(pref_set) if pref_set else 1.0

    if pref_set:
        final_score = 0.75 * req_ratio + 0.25 * pref_ratio
    else:
        final_score = req_ratio

    missing_req = [s for s in required_skills if normalize_skill(s).lower() not in cand_set]
    missing_pref = [s for s in preferred_skills if normalize_skill(s).lower() not in cand_set]
    matched_all = [s for s in candidate_skills if normalize_skill(s).lower() in req_set or normalize_skill(s).lower() in pref_set]

    details = {
        "matched_skills": list(set(matched_all)),
        "missing_required_skills": missing_req,
        "missing_preferred_skills": missing_pref,
        "required_match_ratio": round(req_ratio, 2),
        "preferred_match_ratio": round(pref_ratio, 2)
    }

    return round(final_score, 4), details