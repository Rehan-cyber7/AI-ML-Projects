# AI-Based Job Recommendation System

A Python application that recommends job opportunities for candidates by comparing their profiles with job requirements. It combines text similarity, skill matching, experience fit, salary/location fit, and education alignment to produce ranked recommendations with explanations.

## Features

- Candidate-to-job recommendations.
- Job-to-candidate matching for recruiters.
- Skill analysis, including matched and missing required skills.
- Explainable match drivers and percentage scores.
- Candidate and job records stored in SQLite.
- Web dashboard with job/candidate analytics.
- Command-line interface (CLI) for managing and exploring records.
- Synthetic sample data generation when the database has no jobs.

## Technology Stack

- Python
- NumPy and SciPy
- SQLite
- TF-IDF/text similarity and cosine similarity
- HTML, CSS, and JavaScript
- Python's built-in WSGI development server
- `tabulate` for CLI tables

> The system uses a hybrid recommendation/scoring approach; it is not a deep-learning model.

## Project Structure

```text
JOB recommendation/
├── app.py                  # Web server and JSON API
├── main.py                 # Interactive CLI
├── database.py             # SQLite database layer
├── generate_data.py        # Sample data generator
├── recommender.py          # Hybrid recommendation/scoring engine
├── skill_matcher.py        # Required/preferred skill comparison
├── tfidf_engine.py         # Text similarity utilities
├── job_recommendation.db   # Existing SQLite database (if included)
└── static/
    ├── index.html
    ├── style.css
    └── app.js
```

## Requirements

- Windows, macOS, or Linux
- Python 3.10+ recommended
- Visual Studio Code (optional but recommended)

## Run in VS Code on Windows

1. Extract the project ZIP.
2. In VS Code, select **File → Open Folder** and open the project folder containing `app.py`.
3. Select **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

   If `python` is not recognized, try `py -3.11 -m venv .venv`.

5. Install the dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install numpy scipy tabulate
   ```

6. Start the web dashboard:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

7. Open **http://localhost:8080** in your browser.

Keep the terminal open while using the dashboard. Press `Ctrl+C` in the terminal to stop the server.

### Run the CLI instead

Stop the web server with `Ctrl+C`, then run:

```powershell
.\.venv\Scripts\python.exe main.py
```

Use the numbered menu to view recommendations, browse jobs and candidates, add records, or view analytics.

## API Endpoints

The web server exposes JSON endpoints including:

- `GET /api/jobs` — list jobs.
- `GET /api/candidates` — list candidates.
- `GET /api/recommendations/candidate/<id>` — recommendations for a candidate.
- `GET /api/analytics` — dashboard statistics.

Example: visit **http://localhost:8080/api/jobs** while the server is running.

## How Matching Works

The recommendation engine combines weighted signals:

- Text similarity between candidate information and the job description.
- Required and preferred skill overlap.
- Experience-range fit.
- Salary and location/work-type fit.
- Education-level alignment.

The dashboard shows a match percentage and explanations for key match drivers. Treat this score as a decision-support signal, not a guarantee that a candidate will succeed in a role.

## Troubleshooting

- **`ModuleNotFoundError`:** Install the packages in the same virtual environment used to run the app.
- **Port 8080 is already in use:** Stop the other process using that port or change the port passed to `run_server` in `app.py`.
- **No jobs/candidates appear:** Check that `job_recommendation.db` is present and valid. The application can populate sample data when the database has no jobs.
- **Dashboard does not load:** Confirm the terminal says the server started and open `http://localhost:8080`, not a file path.

## Data and Privacy

The included database may contain demonstration data. Do not publish real candidate names, contact details, resumes, or other personal information without appropriate permission. Review the database before committing it to a public repository.

## Future Improvements

- Resume upload and parsing.
- User authentication and role-based access.
- Admin interface for job management.
- Evaluation against a labeled recommendation dataset.
- Improved accessibility and automated tests.

## License

Add a license if you intend to distribute this project. Check the licenses of any third-party code and dependencies before redistribution.
