"""
WSGI / HTTP REST API Server & Static Web Server for AI-Based Job Recommendation System.
Includes resilient fallback static file serving to prevent 404 Not Found errors.
"""

import json
import os
import re
from wsgiref.simple_server import make_server

from database import DatabaseHandler, DEFAULT_DB_PATH
from recommender import HybridRecommenderEngine
from generate_data import populate_synthetic_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

EMBEDDED_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Job Recommendation System Studio</title>
    <style>
        :root { --bg: #0b0f19; --card-bg: #151c2c; --border: #232f48; --text-main: #f3f4f6; --text-muted: #9ca3af; --accent-blue: #3b82f6; --accent-green: #10b981; --accent-red: #ef4444; }
        body { margin: 0; font-family: system-ui, -apple-system, sans-serif; background-color: var(--bg); color: var(--text-main); line-height: 1.5; }
        .app-container { max-width: 1200px; margin: 0 auto; padding: 24px; }
        .app-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; }
        .logo-area h1 { margin: 4px 0 0 0; font-size: 1.5rem; }
        .logo-area span { color: var(--accent-blue); }
        .badge-ai { background: var(--accent-blue); color: #fff; font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; font-weight: bold; text-transform: uppercase; }
        .analytics-bar { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 20px 0; }
        .kpi-card { background: var(--card-bg); border: 1px solid var(--border); padding: 16px; border-radius: 8px; }
        .kpi-label { font-size: 0.85rem; color: var(--text-muted); }
        .kpi-value { font-size: 1.8rem; font-weight: bold; margin-top: 4px; }
        .kpi-value.highlight { color: var(--accent-green); }
        .portal-grid { display: grid; grid-template-columns: 320px 1fr; gap: 20px; }
        .sidebar-card, .main-content-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }
        select { width: 100%; padding: 10px; background: var(--bg); color: var(--text-main); border: 1px solid var(--border); border-radius: 6px; margin-bottom: 16px; }
        .cards-list { display: flex; flex-direction: column; gap: 16px; }
        .rec-card { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; display: flex; justify-content: space-between; gap: 16px; }
        .match-score { font-size: 1.5rem; font-weight: bold; color: var(--accent-green); }
        .tag-set { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
        .tag { font-size: 0.75rem; padding: 3px 8px; border-radius: 4px; background: var(--border); }
        .tag.matched { background: rgba(16, 185, 129, 0.2); color: var(--accent-green); }
        .tag.missing { background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }
        .xai-box { margin-top: 10px; background: rgba(59, 130, 246, 0.08); border-left: 3px solid var(--accent-blue); padding: 8px 12px; font-size: 0.82rem; }
    </style>
</head>
<body>
    <div class="app-container">
        <header class="app-header">
            <div class="logo-area">
                <span class="badge-ai">AI Engine</span>
                <h1>JobMatch <span>AI Dashboard</span></h1>
            </div>
        </header>
        <section class="analytics-bar">
            <div class="kpi-card"><span class="kpi-label">Active Jobs</span><div class="kpi-value" id="kpiJobs">0</div></div>
            <div class="kpi-card"><span class="kpi-label">Candidates</span><div class="kpi-value" id="kpiCandidates">0</div></div>
            <div class="kpi-card"><span class="kpi-label">Avg System Match</span><div class="kpi-value highlight" id="kpiAvgScore">0%</div></div>
        </section>
        <div class="portal-grid">
            <aside class="sidebar-card">
                <h3>Select Candidate</h3>
                <select id="candidateSelect" onchange="loadRecommendations()"><option value="">-- Select Candidate --</option></select>
                <div id="candidateDetails"></div>
            </aside>
            <section class="main-content-card">
                <h3>AI Recommended Job Opportunities</h3>
                <div id="recList" class="cards-list"></div>
            </section>
        </div>
    </div>
    <script>
        const API_BASE = '/api';
        document.addEventListener('DOMContentLoaded', async () => {
            const statsRes = await fetch(`${API_BASE}/analytics`);
            const stats = await statsRes.json();
            document.getElementById('kpiJobs').innerText = stats.total_jobs;
            document.getElementById('kpiCandidates').innerText = stats.total_candidates;
            document.getElementById('kpiAvgScore').innerText = stats.average_match_score + '%';

            const candsRes = await fetch(`${API_BASE}/candidates`);
            const candidates = await candsRes.json();
            const sel = document.getElementById('candidateSelect');
            candidates.forEach(c => sel.innerHTML += `<option value="${c.id}">${c.name} (${c.current_title})</option>`);
        });

        async function loadRecommendations() {
            const id = document.getElementById('candidateSelect').value;
            if(!id) return;
            const res = await fetch(`${API_BASE}/recommendations/candidate/${id}`);
            const data = await res.json();
            const cand = data.candidate;
            document.getElementById('candidateDetails').innerHTML = `
                <p><strong>${cand.name}</strong> (${cand.current_title})</p>
                <p>Exp: ${cand.years_experience} Yrs | Location: ${cand.location}</p>
                <p>Desired Salary: $${cand.expected_salary.toLocaleString()}</p>
            `;
            const list = document.getElementById('recList');
            list.innerHTML = data.recommendations.map(r => `
                <div class="rec-card">
                    <div style="flex:1;">
                        <h4 style="margin:0;">${r.job_title} <span style="color:#9ca3af;font-size:0.85rem;">at ${r.job_company}</span></h4>
                        <p style="margin:4px 0;color:#9ca3af;font-size:0.85rem;">Location: ${r.job_location}</p>
                        <div class="tag-set">
                            ${r.skill_analysis.matched_skills.map(s => `<span class="tag matched">✓ ${s}</span>`).join('')}
                            ${r.skill_analysis.missing_required_skills.map(s => `<span class="tag missing">Missing: ${s}</span>`).join('')}
                        </div>
                        <div class="xai-box">
                            <strong>AI Rationale:</strong>
                            <ul style="margin:4px 0 0 16px;padding:0;">
                                ${r.key_match_drivers.map(d => `<li>${d}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    <div style="text-align:center;">
                        <div class="match-score">${r.match_percentage}%</div>
                        <small style="color:#9ca3af;">Fit Score</small>
                    </div>
                </div>
            `).join('');
        }
    </script>
</body>
</html>
"""

class RecommendationAppServer:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db = DatabaseHandler(db_path)
        self.engine = HybridRecommenderEngine()

        jobs = self.db.get_all_jobs()
        if not jobs:
            populate_synthetic_data(db_path)

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', 'GET')

        if method == 'OPTIONS':
            start_response('200 OK', [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type')
            ])
            return [b'']

        if path.startswith('/api/'):
            return self.handle_api(method, path, environ, start_response)

        return self.serve_static(path, start_response)

    def handle_api(self, method, path, environ, start_response):
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
        ]

        if method == 'GET' and path == '/api/jobs':
            jobs = self.db.get_all_jobs()
            return self.send_json(start_response, 200, jobs, headers)

        if method == 'GET' and path == '/api/candidates':
            candidates = self.db.get_all_candidates()
            return self.send_json(start_response, 200, candidates, headers)

        match = re.match(r'^/api/recommendations/candidate/(\d+)$', path)
        if method == 'GET' and match:
            cand_id = int(match.group(1))
            cand = self.db.get_candidate_by_id(cand_id)
            if not cand:
                return self.send_json(start_response, 404, {"error": "Candidate not found"}, headers)
            
            jobs = self.db.get_all_jobs()
            recommendations = self.engine.recommend_jobs_for_candidate(cand, jobs, top_k=10)
            
            for rec in recommendations[:3]:
                self.db.save_feedback(rec["job_id"], cand_id, rec["composite_score"], "Recommended")

            return self.send_json(start_response, 200, {
                "candidate": cand,
                "recommendations": recommendations
            }, headers)

        match = re.match(r'^/api/recommendations/job/(\d+)$', path)
        if method == 'GET' and match:
            job_id = int(match.group(1))
            job = self.db.get_job_by_id(job_id)
            if not job:
                return self.send_json(start_response, 404, {"error": "Job not found"}, headers)

            candidates = self.db.get_all_candidates()
            top_candidates = self.engine.recommend_candidates_for_job(job, candidates, top_k=10)
            
            return self.send_json(start_response, 200, {
                "job": job,
                "top_candidates": top_candidates
            }, headers)

        if method == 'POST' and path == '/api/jobs':
            body = self.read_json_body(environ)
            new_id = self.db.add_job(body)
            created = self.db.get_job_by_id(new_id)
            return self.send_json(start_response, 201, created, headers)

        if method == 'POST' and path == '/api/candidates':
            body = self.read_json_body(environ)
            new_id = self.db.add_candidate(body)
            created = self.db.get_candidate_by_id(new_id)
            return self.send_json(start_response, 201, created, headers)

        if method == 'GET' and path == '/api/analytics':
            stats = self.db.get_stats()
            return self.send_json(start_response, 200, stats, headers)

        return self.send_json(start_response, 404, {"error": "Endpoint not found"}, headers)

    def read_json_body(self, environ):
        try:
            length = int(environ.get('CONTENT_LENGTH', 0))
            body_bytes = environ['wsgi.input'].read(length)
            return json.loads(body_bytes.decode('utf-8'))
        except Exception:
            return {}

    def send_json(self, start_response, status_code, data, headers):
        status_phrase = f"{status_code} OK" if status_code < 400 else f"{status_code} Error"
        start_response(status_phrase, headers)
        return [json.dumps(data, indent=2).encode('utf-8')]

    def serve_static(self, path, start_response):
        if path == '/' or path == '' or path == '/index.html':
            static_index = os.path.join(STATIC_DIR, "index.html")
            if os.path.exists(static_index):
                with open(static_index, "rb") as f:
                    start_response("200 OK", [('Content-Type', 'text/html')])
                    return [f.read()]
            
            root_index = os.path.join(BASE_DIR, "index.html")
            if os.path.exists(root_index):
                with open(root_index, "rb") as f:
                    start_response("200 OK", [('Content-Type', 'text/html')])
                    return [f.read()]

            # Fallback: Serve embedded HTML directly
            start_response("200 OK", [('Content-Type', 'text/html')])
            return [EMBEDDED_INDEX_HTML.encode('utf-8')]

        target_file = os.path.normpath(os.path.join(STATIC_DIR, path.lstrip('/')))
        if not target_file.startswith(STATIC_DIR):
            target_file = os.path.normpath(os.path.join(BASE_DIR, path.lstrip('/')))

        if os.path.exists(target_file) and os.path.isfile(target_file):
            content_type = "text/html"
            if target_file.endswith(".css"):
                content_type = "text/css"
            elif target_file.endswith(".js"):
                content_type = "application/javascript"

            with open(target_file, "rb") as f:
                content = f.read()
            start_response("200 OK", [('Content-Type', content_type)])
            return [content]

        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        return [b"404 Not Found"]

def run_server(port: int = 8080):
    server = make_server('0.0.0.0', port, RecommendationAppServer())
    print(f"Server started on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server(8080)