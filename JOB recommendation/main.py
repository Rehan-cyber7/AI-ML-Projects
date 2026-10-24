"""
Interactive CLI Application for AI-Based Job Recommendation System.
"""

import sys
from tabulate import tabulate
from database import DatabaseHandler, DEFAULT_DB_PATH
from recommender import HybridRecommenderEngine
from generate_data import populate_synthetic_data

def display_menu():
    print("\n" + "="*60)
    print("      AI-BASED JOB RECOMMENDATION SYSTEM - CLI STUDIO")
    print("="*60)
    print("1. Find Top Job Recommendations for a Candidate (Job Seeker Portal)")
    print("2. Find Top Candidate Matches for a Job Posting (Recruiter Portal)")
    print("3. List All Job Postings")
    print("4. List All Candidate Profiles")
    print("5. Add New Job Requirement")
    print("6. Add New Candidate Profile")
    print("7. Run System Analytics & Benchmark")
    print("8. Exit CLI")
    print("="*60)

def main():
    db = DatabaseHandler(DEFAULT_DB_PATH)
    engine = HybridRecommenderEngine()

    if not db.get_all_jobs():
        populate_synthetic_data(DEFAULT_DB_PATH)

    while True:
        display_menu()
        choice = input("Enter option (1-8): ").strip()

        if choice == "1":
            candidates = db.get_all_candidates()
            table_data = [[c["id"], c["name"], c["current_title"], f"${c['expected_salary']:,}"] for c in candidates]
            print("\nAvailable Candidates:")
            print(tabulate(table_data, headers=["ID", "Name", "Title", "Salary Expectation"], tablefmt="grid"))
            
            cand_id_str = input("\nEnter Candidate ID: ").strip()
            if not cand_id_str.isdigit():
                continue
            
            cand = db.get_candidate_by_id(int(cand_id_str))
            if not cand:
                continue

            jobs = db.get_all_jobs()
            recs = engine.recommend_jobs_for_candidate(cand, jobs, top_k=5)

            print(f"\nTop 5 Job Recommendations for {cand['name']} ({cand['current_title']}):")
            rec_table = []
            for r in recs:
                matched_s = ", ".join(r["skill_analysis"]["matched_skills"]) or "None"
                missing_s = ", ".join(r["skill_analysis"]["missing_required_skills"]) or "None"
                rec_table.append([
                    r["job_id"], r["job_title"], r["job_company"],
                    f"{r['match_percentage']}%", matched_s, missing_s
                ])
            print(tabulate(rec_table, headers=["Job ID", "Title", "Company", "Match Score", "Matched Skills", "Missing Required Skills"], tablefmt="grid"))

        elif choice == "2":
            jobs = db.get_all_jobs()
            table_data = [[j["id"], j["title"], j["company"], j["location"], f"${j['min_salary']:,} - ${j['max_salary']:,}"] for j in jobs]
            print("\nAvailable Job Postings:")
            print(tabulate(table_data, headers=["ID", "Title", "Company", "Location", "Salary Range"], tablefmt="grid"))

            job_id_str = input("\nEnter Job ID: ").strip()
            if not job_id_str.isdigit():
                continue

            job = db.get_job_by_id(int(job_id_str))
            if not job:
                continue

            candidates = db.get_all_candidates()
            recs = engine.recommend_candidates_for_job(job, candidates, top_k=5)

            print(f"\nTop 5 Candidate Matches for {job['title']} at {job['company']}:")
            rec_table = []
            for r in recs:
                drivers = " | ".join(r["key_match_drivers"][:2])
                rec_table.append([
                    r["candidate_id"], r["candidate_name"], r["candidate_title"],
                    f"{r['match_percentage']}%", drivers
                ])
            print(tabulate(rec_table, headers=["Candidate ID", "Name", "Title", "Match Score", "Key Drivers"], tablefmt="grid"))

        elif choice == "3":
            jobs = db.get_all_jobs()
            table_data = [[j["id"], j["title"], j["company"], j["category"], j["location"], j["work_type"]] for j in jobs]
            print(tabulate(table_data, headers=["ID", "Title", "Company", "Category", "Location", "Work Type"], tablefmt="grid"))

        elif choice == "4":
            candidates = db.get_all_candidates()
            table_data = [[c["id"], c["name"], c["current_title"], f"{c['years_experience']} Yrs", c["location"]] for c in candidates]
            print(tabulate(table_data, headers=["ID", "Name", "Title", "Experience", "Location"], tablefmt="grid"))

        elif choice == "7":
            stats = db.get_stats()
            print(f"Total Jobs: {stats['total_jobs']} | Total Candidates: {stats['total_candidates']} | Avg Match: {stats['average_match_score']}%")

        elif choice == "8":
            sys.exit(0)

if __name__ == "__main__":
    main()