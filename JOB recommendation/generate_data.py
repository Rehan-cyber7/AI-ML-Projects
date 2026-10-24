"""
Synthetic Data Generator for AI-Based Job Recommendation System.
Self-contained database initialization and population.
"""

import sqlite3
import json
import random
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "job_recommendation.db")

SKILLS_TAXONOMY = [
    {"skill_name": "Python", "category": "Software Engineering", "alias_keywords": ["python3", "py", "cpython"], "weight": 1.2},
    {"skill_name": "Java", "category": "Software Engineering", "alias_keywords": ["java8", "jdk", "spring"], "weight": 1.1},
    {"skill_name": "C++", "category": "Software Engineering", "alias_keywords": ["cpp", "c plus plus"], "weight": 1.0},
    {"skill_name": "JavaScript", "category": "Software Engineering", "alias_keywords": ["js", "es6", "node"], "weight": 1.1},
    {"skill_name": "React", "category": "Software Engineering", "alias_keywords": ["reactjs", "react.js"], "weight": 1.0},
    {"skill_name": "Machine Learning", "category": "Data Science / AI", "alias_keywords": ["ml", "predictive modeling"], "weight": 1.3},
    {"skill_name": "Deep Learning", "category": "Data Science / AI", "alias_keywords": ["dl", "neural networks", "pytorch", "tensorflow"], "weight": 1.3},
    {"skill_name": "NLP", "category": "Data Science / AI", "alias_keywords": ["natural language processing", "llm", "transformers"], "weight": 1.2},
    {"skill_name": "Computer Vision", "category": "Data Science / AI", "alias_keywords": ["cv", "opencv"], "weight": 1.2},
    {"skill_name": "SQL", "category": "Data Engineering", "alias_keywords": ["postgresql", "mysql", "sqlite", "t-sql"], "weight": 1.1},
    {"skill_name": "Apache Spark", "category": "Data Engineering", "alias_keywords": ["pyspark", "spark"], "weight": 1.2},
    {"skill_name": "Airflow", "category": "Data Engineering", "alias_keywords": ["apache airflow", "dag"], "weight": 1.0},
    {"skill_name": "Snowflake", "category": "Data Engineering", "alias_keywords": ["snowflake db", "data warehousing"], "weight": 1.1},
    {"skill_name": "Docker", "category": "DevOps", "alias_keywords": ["containerization", "containers"], "weight": 1.1},
    {"skill_name": "Kubernetes", "category": "DevOps", "alias_keywords": ["k8s"], "weight": 1.3},
    {"skill_name": "Terraform", "category": "DevOps", "alias_keywords": ["iac", "infrastructure as code"], "weight": 1.1},
    {"skill_name": "AWS", "category": "DevOps", "alias_keywords": ["amazon web services", "ec2", "s3"], "weight": 1.2},
    {"skill_name": "Penetration Testing", "category": "Cybersecurity", "alias_keywords": ["pen testing", "ethical hacking"], "weight": 1.2},
    {"skill_name": "Network Security", "category": "Cybersecurity", "alias_keywords": ["firewalls", "vpn", "ids/ips"], "weight": 1.1},
    {"skill_name": "SIEM", "category": "Cybersecurity", "alias_keywords": ["splunk", "elastic security"], "weight": 1.1},
    {"skill_name": "Product Roadmap", "category": "Product Management", "alias_keywords": ["roadmapping", "feature prioritization"], "weight": 1.2},
    {"skill_name": "Agile/Scrum", "category": "Product Management", "alias_keywords": ["scrum", "kanban", "sprint planning"], "weight": 1.0},
    {"skill_name": "User Research", "category": "Product Management", "alias_keywords": ["customer interviews", "usability testing"], "weight": 1.1},
    {"skill_name": "Figma", "category": "UI/UX", "alias_keywords": ["figma design", "prototyping"], "weight": 1.2},
    {"skill_name": "Wireframing", "category": "UI/UX", "alias_keywords": ["mockups", "low-fi designs"], "weight": 1.0},
    {"skill_name": "Design Systems", "category": "UI/UX", "alias_keywords": ["component libraries", "ui guidelines"], "weight": 1.1},
    {"skill_name": "SEO", "category": "Marketing", "alias_keywords": ["search engine optimization", "organic search"], "weight": 1.0},
    {"skill_name": "Content Strategy", "category": "Marketing", "alias_keywords": ["copywriting", "content marketing"], "weight": 1.0},
    {"skill_name": "Google Analytics", "category": "Marketing", "alias_keywords": ["ga4", "web analytics"], "weight": 1.1}
]

JOB_DOMAINS = {
    "Software Engineering": [
        ("Backend Engineer", ["Python", "SQL"], ["Docker", "AWS"], 2, 5, 90000, 130000),
        ("Full Stack Developer", ["JavaScript", "React", "Python"], ["AWS"], 1, 4, 80000, 115000),
        ("Senior C++ Developer", ["C++", "SQL"], ["Docker"], 5, 8, 140000, 180000),
        ("Lead Software Architect", ["Java", "Docker", "AWS"], ["Kubernetes", "Terraform"], 8, 12, 170000, 220000),
    ],
    "Data Science / AI": [
        ("AI Research Scientist", ["Python", "Deep Learning", "NLP"], ["Machine Learning"], 3, 7, 130000, 190000),
        ("Machine Learning Engineer", ["Python", "Machine Learning", "SQL"], ["Docker", "AWS"], 2, 6, 110000, 160000),
        ("NLP Engineer", ["Python", "NLP", "Deep Learning"], ["AWS"], 2, 5, 115000, 155000),
        ("Computer Vision Specialist", ["Python", "Computer Vision", "Deep Learning"], ["C++"], 3, 6, 125000, 175000),
    ],
    "Data Engineering": [
        ("Data Engineer", ["SQL", "Python", "Apache Spark"], ["Airflow", "Snowflake"], 2, 5, 100000, 140000),
        ("Senior Data Warehouse Engineer", ["SQL", "Snowflake"], ["Airflow", "AWS"], 5, 9, 145000, 185000),
        ("ETL Developer", ["SQL", "Python"], ["Airflow"], 1, 3, 75000, 105000),
        ("Lead Data Architect", ["Apache Spark", "Snowflake", "AWS", "SQL"], ["Docker"], 8, 12, 165000, 210000),
    ],
    "DevOps": [
        ("DevOps Engineer", ["Docker", "Kubernetes", "AWS"], ["Terraform"], 2, 5, 105000, 145000),
        ("Site Reliability Engineer (SRE)", ["Python", "Kubernetes", "Docker"], ["AWS"], 3, 7, 120000, 165000),
        ("Cloud Infrastructure Engineer", ["AWS", "Terraform"], ["Docker", "Kubernetes"], 4, 8, 130000, 175000),
        ("Junior Systems Administrator", ["AWS"], ["Docker"], 0, 2, 60000, 85000),
    ],
    "Cybersecurity": [
        ("Cybersecurity Analyst", ["Network Security", "SIEM"], ["Penetration Testing"], 1, 4, 85000, 120000),
        ("Penetration Tester", ["Penetration Testing", "Python"], ["Network Security"], 3, 6, 115000, 150000),
        ("Information Security Officer", ["Network Security", "SIEM"], ["AWS"], 6, 10, 150000, 200000),
        ("Security Operations Center (SOC) Lead", ["SIEM", "Network Security"], ["Python"], 5, 8, 130000, 170000),
    ],
    "Product Management": [
        ("Associate Product Manager", ["Agile/Scrum"], ["User Research"], 0, 2, 70000, 95000),
        ("Product Manager", ["Product Roadmap", "Agile/Scrum"], ["User Research"], 3, 6, 110000, 150000),
        ("Senior Technical Product Manager", ["Product Roadmap", "SQL", "Agile/Scrum"], ["AWS"], 5, 9, 140000, 185000),
        ("Director of Product", ["Product Roadmap", "User Research"], ["Agile/Scrum"], 8, 14, 180000, 240000),
    ],
    "UI/UX": [
        ("UI/UX Designer", ["Figma", "Wireframing"], ["Design Systems"], 1, 4, 75000, 110000),
        ("Product Designer", ["Figma", "Design Systems", "User Research"], ["Wireframing"], 3, 6, 105000, 145000),
        ("UX Researcher", ["User Research", "Wireframing"], ["Figma"], 2, 5, 85000, 125000),
        ("Lead Design Systems Specialist", ["Figma", "Design Systems"], ["Wireframing"], 6, 10, 140000, 180000),
    ],
    "Marketing": [
        ("Digital Marketing Specialist", ["SEO", "Google Analytics"], ["Content Strategy"], 1, 3, 60000, 85000),
        ("Content Marketing Manager", ["Content Strategy", "SEO"], ["Google Analytics"], 3, 6, 85000, 120000),
        ("Growth Marketing Manager", ["Google Analytics", "SEO", "SQL"], ["Content Strategy"], 4, 7, 100000, 140000),
        ("SEO Strategist", ["SEO", "Google Analytics"], ["Content Strategy"], 2, 5, 70000, 100000),
    ]
}

COMPANIES = ["TechCorp", "CloudScale Solutions", "DataVision AI", "SecureNet", "CreativeFlow", "GrowthPulse", "Astra Systems", "InnoTech Labs"]
LOCATIONS = ["San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Remote"]
WORK_TYPES = ["Remote", "Onsite", "Hybrid"]

CANDIDATES_DATA = [
    ("Alex Rivera", "alex.rivera@email.com", "555-0101", "Junior Software Developer", ["Python", "JavaScript", "SQL"], 1.0, "Austin, TX", "Remote", 75000, "Bachelor", "Recent CS graduate with internship experience building web apps in Python and React. Passionate about backend development."),
    ("Meera Patel", "meera.patel@email.com", "555-0102", "Associate Data Analyst", ["SQL", "Python", "Google Analytics"], 1.5, "New York, NY", "New York, NY", 70000, "Bachelor", "Detail-oriented data analyst skilled in SQL querying, Python data analysis, and web analytics dashboards."),
    ("Chris Evans", "chris.evans@email.com", "555-0103", "Junior UI/UX Designer", ["Figma", "Wireframing"], 0.5, "San Francisco, CA", "San Francisco, CA", 68000, "Bachelor", "Creative designer with a strong portfolio of mobile app wireframes and interactive Figma prototypes."),
    ("Sophia Kim", "sophia.kim@email.com", "555-0104", "Associate Product Manager", ["Agile/Scrum", "User Research"], 1.0, "Seattle, WA", "Remote", 80000, "Bachelor", "Entry-level PM with strong communication skills and experience facilitating sprint events and customer interviews."),
    ("Jordan Lee", "jordan.lee@email.com", "555-0105", "Junior DevOps Specialist", ["Docker", "AWS"], 1.0, "Remote", "Remote", 72000, "Bachelor", "Hands-on experience configuring AWS EC2 instances, writing Dockerfiles, and setting up basic CI/CD pipelines."),
    ("Daniel Martinez", "daniel.m@email.com", "555-0201", "Backend Engineer", ["Python", "SQL", "Docker", "AWS"], 4.0, "Austin, TX", "Austin, TX", 115000, "Bachelor", "Backend engineer specializing in scalable REST APIs using Python and PostgreSQL hosted on AWS."),
    ("Priya Sharma", "priya.sharma@email.com", "555-0202", "Data Scientist", ["Python", "Machine Learning", "SQL", "NLP"], 3.5, "San Francisco, CA", "Remote", 135000, "Master", "Data scientist experience building predictive machine learning models and NLP sentiment classifiers in production."),
    ("Ethan Wright", "ethan.wright@email.com", "555-0203", "Data Engineer", ["SQL", "Apache Spark", "Airflow", "Python"], 4.0, "Seattle, WA", "Seattle, WA", 125000, "Bachelor", "Built ETL pipelines handling terabytes of daily data using PySpark and managed DAG workflows with Apache Airflow."),
    ("Rachel Green", "rachel.g@email.com", "555-0204", "Product Designer", ["Figma", "Design Systems", "User Research"], 4.5, "New York, NY", "New York, NY", 120000, "Bachelor", "Product designer experienced in maintaining cross-platform design systems and conducting usability tests."),
    ("Marcus Brody", "marcus.b@email.com", "555-0205", "Cybersecurity Analyst", ["Network Security", "SIEM", "Penetration Testing"], 3.0, "Austin, TX", "Remote", 105000, "Bachelor", "SOC analyst proficient in Splunk SIEM monitoring, threat detection, and vulnerability testing."),
    ("Vikram Singh", "vikram.s@email.com", "555-0301", "Senior DevOps Engineer", ["Docker", "Kubernetes", "AWS", "Terraform", "Python"], 7.0, "Seattle, WA", "Remote", 155000, "Bachelor", "Senior Infrastructure Engineer managing multi-cluster Kubernetes deployments on AWS with Infrastructure as Code via Terraform."),
    ("Elena Rostova", "elena.r@email.com", "555-0302", "Senior AI Research Engineer", ["Python", "Deep Learning", "NLP", "Machine Learning"], 6.0, "San Francisco, CA", "San Francisco, CA", 175000, "PhD", "Published AI research engineer focusing on LLMs, transformer architecture fine-tuning, and PyTorch production deployment."),
    ("David Chen", "david.chen@email.com", "555-0303", "Senior Technical Product Manager", ["Product Roadmap", "SQL", "Agile/Scrum", "User Research"], 7.5, "New York, NY", "New York, NY", 160000, "Master", "Technical PM who scaled SaaS products from 10k to 1M MAU. Strong cross-functional alignment skills."),
    ("Hannah Abbott", "hannah.a@email.com", "555-0304", "Senior Data Warehouse Engineer", ["SQL", "Snowflake", "Airflow", "AWS"], 8.0, "Remote", "Remote", 165000, "Bachelor", "Architected enterprise data warehouses on Snowflake and optimized high-volume SQL analytics pipelines."),
    ("Nathan Drake", "nathan.d@email.com", "555-0305", "Growth Marketing Manager", ["Google Analytics", "SEO", "Content Strategy", "SQL"], 6.0, "Austin, TX", "Austin, TX", 130000, "Bachelor", "Data-driven marketing manager who grew organic customer acquisition by 180% YoY through targeted SEO and funnel optimization."),
    ("Sarah Jenkins", "sarah.j@email.com", "555-0401", "Lead Software Architect", ["Java", "C++", "Docker", "AWS", "Kubernetes", "SQL"], 11.0, "San Francisco, CA", "San Francisco, CA", 200000, "Master", "Lead Architect guiding engineering teams of 20+. Expert in microservices architecture, cloud migration, and distributed systems."),
    ("Tariq Al-Mansoor", "tariq.a@email.com", "555-0402", "Lead Data Architect", ["Apache Spark", "Snowflake", "AWS", "SQL", "Python", "Airflow"], 10.0, "New York, NY", "Remote", 195000, "Master", "Architected cloud analytics platforms across finance and tech sectors. Expert in real-time streaming architectures."),
    ("Laura Croft", "laura.c@email.com", "555-0403", "Director of Product", ["Product Roadmap", "User Research", "Agile/Scrum"], 12.0, "Seattle, WA", "Seattle, WA", 220000, "Master", "Product executive with track record of managing $50M+ ARR product portfolios and leading 15+ product managers."),
    ("James Miller", "james.m@email.com", "555-0404", "Lead Design Systems Specialist", ["Figma", "Design Systems", "Wireframing", "User Research"], 9.0, "San Francisco, CA", "Remote", 170000, "Bachelor", "Design leader who built accessible design systems adopted by 100+ product designers across enterprise suites."),
    ("Robert Taylor", "robert.t@email.com", "555-0405", "Chief Information Security Officer", ["Network Security", "SIEM", "Penetration Testing", "AWS"], 14.0, "New York, NY", "New York, NY", 230000, "Master", "Veteran security executive managing enterprise threat postures, compliance frameworks, and incident response teams.")
]

def populate_synthetic_data(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    PRAGMA foreign_keys = ON;

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
    """)

    cursor.execute("DELETE FROM applications_feedback;")
    cursor.execute("DELETE FROM candidates;")
    cursor.execute("DELETE FROM jobs;")
    cursor.execute("DELETE FROM skills_taxonomy;")
    conn.commit()

    for item in SKILLS_TAXONOMY:
        cursor.execute("""
            INSERT INTO skills_taxonomy (skill_name, category, alias_keywords, weight)
            VALUES (?, ?, ?, ?)
        """, (item["skill_name"], item["category"], json.dumps(item["alias_keywords"]), item["weight"]))

    job_id_counter = 1
    for category, job_list in JOB_DOMAINS.items():
        for title, req_skills, pref_skills, min_exp, max_exp, min_sal, max_sal in job_list:
            company = random.choice(COMPANIES)
            location = random.choice(LOCATIONS)
            work_type = random.choice(WORK_TYPES)
            description = f"Seeking a skilled {title} at {company} in {location}. Responsibilities include technical execution, project collaboration, and leverage of skills in {', '.join(req_skills)}."
            
            cursor.execute("""
                INSERT INTO jobs (id, title, company, category, location, work_type, required_skills, preferred_skills, min_experience, max_experience, min_salary, max_salary, description, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')
            """, (
                job_id_counter, title, company, category, location, work_type,
                json.dumps(req_skills), json.dumps(pref_skills), min_exp, max_exp,
                min_sal, max_sal, description
            ))
            job_id_counter += 1

    cand_id_counter = 1
    for name, email, phone, title, skills, exp, loc, pref_loc, salary, edu, resume in CANDIDATES_DATA:
        summary = f"{title} with {exp} years of experience specializing in {', '.join(skills[:3])}."
        
        cursor.execute("""
            INSERT INTO candidates (id, name, email, phone, current_title, skills, years_experience, location, preferred_location, expected_salary, education, resume_text, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cand_id_counter, name, email, phone, title, json.dumps(skills),
            exp, loc, pref_loc, salary, edu, resume, summary
        ))
        cand_id_counter += 1

    conn.commit()
    conn.close()

if __name__ == "__main__":
    populate_synthetic_data()
    print("Synthetic dataset successfully populated.")