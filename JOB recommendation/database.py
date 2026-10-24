"""
Database Management Layer for AI-Based Job Recommendation System.
Uses SQLite with structured JSON fields for skills and preferences.
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = "job_recommendation.db"

def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS skills_taxonomy (
        skill_name TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        alias_keywords TEXT NOT NULL,
        weight REAL NOT NULL DEFAULT 1.0
    );

    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT NOT NULL,
        work_type TEXT NOT NULL CHECK(work_type IN ('Remote', 'Onsite', 'Hybrid')),
        required_skills TEXT NOT NULL,
        preferred_skills TEXT,
        min_experience INTEGER NOT NULL DEFAULT 0,
        max_experience INTEGER NOT NULL,
        min_salary REAL,
        max_salary REAL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open', 'Closed', 'Paused')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        current_title TEXT NOT NULL,
        skills TEXT NOT NULL,
        years_experience REAL NOT NULL DEFAULT 0.0,
        location TEXT NOT NULL,
        preferred_location TEXT NOT NULL,
        expected_salary REAL,
        education TEXT NOT NULL,
        resume_text TEXT NOT NULL,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS applications_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL,
        match_score REAL CHECK(match_score >= 0.0 AND match_score <= 1.0),
        feedback_status TEXT NOT NULL DEFAULT 'Pending' CHECK(feedback_status IN ('Pending', 'Recommended', 'Applied', 'Shortlisted', 'Rejected', 'Hired')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
        FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
        UNIQUE(job_id, candidate_id)
    );

    CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
    CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
    CREATE INDEX IF NOT EXISTS idx_candidates_location ON candidates(location);
    """)
    conn.commit()
    conn.close()

class DatabaseHandler:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)

    def get_all_jobs(self, status_filter: Optional[str] = "Open") -> List[Dict[str, Any]]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        if status_filter:
            cursor.execute("SELECT * FROM jobs WHERE status = ?", (status_filter,))
        else:
            cursor.execute("SELECT * FROM jobs")
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for r in rows:
            j = dict(r)
            j["required_skills"] = json.loads(j["required_skills"])
            j["preferred_skills"] = json.loads(j["preferred_skills"]) if j["preferred_skills"] else []
            jobs.append(j)
        return jobs

    def get_job_by_id(self, job_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        j = dict(row)
        j["required_skills"] = json.loads(j["required_skills"])
        j["preferred_skills"] = json.loads(j["preferred_skills"]) if j["preferred_skills"] else []
        return j

    def get_all_candidates(self) -> List[Dict[str, Any]]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates")
        rows = cursor.fetchall()
        conn.close()
        
        candidates = []
        for r in rows:
            c = dict(r)
            c["skills"] = json.loads(c["skills"])
            candidates.append(c)
        return candidates

    def get_candidate_by_id(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        c = dict(row)
        c["skills"] = json.loads(c["skills"])
        return c

    def add_job(self, job_data: Dict[str, Any]) -> int:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jobs (title, company, category, location, work_type, required_skills, preferred_skills, min_experience, max_experience, min_salary, max_salary, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_data["title"],
            job_data["company"],
            job_data.get("category", "General"),
            job_data["location"],
            job_data.get("work_type", "Remote"),
            json.dumps(job_data.get("required_skills", [])),
            json.dumps(job_data.get("preferred_skills", [])),
            job_data.get("min_experience", 0),
            job_data.get("max_experience", 5),
            job_data.get("min_salary", 0.0),
            job_data.get("max_salary", 100000.0),
            job_data.get("description", ""),
            job_data.get("status", "Open")
        ))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    def add_candidate(self, cand_data: Dict[str, Any]) -> int:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO candidates (name, email, phone, current_title, skills, years_experience, location, preferred_location, expected_salary, education, resume_text, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cand_data["name"],
            cand_data["email"],
            cand_data.get("phone", ""),
            cand_data.get("current_title", "Job Seeker"),
            json.dumps(cand_data.get("skills", [])),
            cand_data.get("years_experience", 0.0),
            cand_data.get("location", "Remote"),
            cand_data.get("preferred_location", "Remote"),
            cand_data.get("expected_salary", 80000.0),
            cand_data.get("education", "Bachelor"),
            cand_data.get("resume_text", ""),
            cand_data.get("summary", "")
        ))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    def save_feedback(self, job_id: int, candidate_id: int, match_score: float, status: str = "Recommended") -> None:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications_feedback (job_id, candidate_id, match_score, feedback_status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(job_id, candidate_id) DO UPDATE SET
                match_score = excluded.match_score,
                feedback_status = excluded.feedback_status
        """, (job_id, candidate_id, match_score, status))
        conn.commit()
        conn.close()

    def get_stats(self) -> Dict[str, Any]:
        conn = get_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'Open'")
        total_jobs = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM candidates")
        total_candidates = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(match_score) FROM applications_feedback")
        avg_score_row = cursor.fetchone()[0]
        avg_score = round(avg_score_row * 100, 1) if avg_score_row is not None else 0.0
        conn.close()
        return {
            "total_jobs": total_jobs,
            "total_candidates": total_candidates,
            "average_match_score": avg_score
        }