const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', () => {
    fetchAnalytics();
    loadSelectOptions();
});

async function fetchAnalytics() {
    try {
        const res = await fetch(`${API_BASE}/analytics`);
        const data = await res.json();
        document.getElementById('kpiJobs').innerText = data.total_jobs;
        document.getElementById('kpiCandidates').innerText = data.total_candidates;
        document.getElementById('kpiAvgScore').innerText = `${data.average_match_score}%`;
    } catch (err) {
        console.error("Error fetching analytics:", err);
    }
}

async function loadSelectOptions() {
    try {
        const resCand = await fetch(`${API_BASE}/candidates`);
        const candidates = await resCand.json();
        const candSelect = document.getElementById('candidateSelect');
        candSelect.innerHTML = '<option value="">-- Choose Candidate --</option>';
        candidates.forEach(c => {
            candSelect.innerHTML += `<option value="${c.id}">${c.name} (${c.current_title})</option>`;
        });

        const resJobs = await fetch(`${API_BASE}/jobs`);
        const jobs = await resJobs.json();
        const jobSelect = document.getElementById('jobSelect');
        jobSelect.innerHTML = '<option value="">-- Choose Job Posting --</option>';
        jobs.forEach(j => {
            jobSelect.innerHTML += `<option value="${j.id}">${j.title} - ${j.company}</option>`;
        });
    } catch (err) {
        console.error("Error loading options:", err);
    }
}

function switchView(viewId) {
    document.querySelectorAll('.portal-view').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

    document.getElementById(viewId).classList.add('active');
    if (viewId === 'candidateView') {
        document.getElementById('tabCandidateView').classList.add('active');
    } else {
        document.getElementById('tabRecruiterView').classList.add('active');
    }
}

async function loadCandidateRecommendations() {
    const id = document.getElementById('candidateSelect').value;
    if (!id) return;

    try {
        const res = await fetch(`${API_BASE}/recommendations/candidate/${id}`);
        const data = await res.json();
        
        const cand = data.candidate;
        document.getElementById('candidateProfileCard').innerHTML = `
            <p><strong>${cand.name}</strong></p>
            <p>${cand.current_title}</p>
            <p><strong>Exp:</strong> ${cand.years_experience} Yrs • <strong>Location:</strong> ${cand.location}</p>
            <p><strong>Desired Salary:</strong> $${cand.expected_salary.toLocaleString()}</p>
            <div class="tag-set">
                ${cand.skills.map(s => `<span class="tag">${s}</span>`).join('')}
            </div>
        `;

        const list = document.getElementById('candidateRecsList');
        if (!data.recommendations || data.recommendations.length === 0) {
            list.innerHTML = '<p class="text-muted">No matching jobs found.</p>';
            return;
        }

        list.innerHTML = data.recommendations.map(r => `
            <div class="rec-card">
                <div style="flex:1;">
                    <h4>${r.job_title} <span class="subtext">at ${r.job_company}</span></h4>
                    <p><strong>Location:</strong> ${r.job_location}</p>
                    <div class="tag-set">
                        ${r.skill_analysis.matched_skills.map(s => `<span class="tag matched">✓ ${s}</span>`).join('')}
                        ${r.skill_analysis.missing_required_skills.map(s => `<span class="tag missing">Missing Req: ${s}</span>`).join('')}
                        ${r.skill_analysis.missing_preferred_skills.map(s => `<span class="tag missing">Missing Pref: ${s}</span>`).join('')}
                    </div>
                    <div class="xai-box">
                        <strong>AI Drivers:</strong>
                        <ul>
                            ${r.key_match_drivers.map(d => `<li>${d}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="match-gauge">
                    <div class="match-score">${r.match_percentage}%</div>
                    <small>Skill: ${Math.round(r.score_breakdown.skill_match * 100)}%</small><br>
                    <small>Exp: ${Math.round(r.score_breakdown.experience_fit * 100)}%</small>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error("Error loading candidate recommendations:", err);
    }
}

async function loadJobRecommendations() {
    const id = document.getElementById('jobSelect').value;
    if (!id) return;

    try {
        const res = await fetch(`${API_BASE}/recommendations/job/${id}`);
        const data = await res.json();

        const j = data.job;
        document.getElementById('jobProfileCard').innerHTML = `
            <p><strong>${j.title}</strong></p>
            <p>${j.company} • ${j.location} (${j.work_type})</p>
            <p><strong>Exp Required:</strong> ${j.min_experience}-${j.max_experience} Yrs</p>
            <p><strong>Salary Range:</strong> $${j.min_salary.toLocaleString()} - $${j.max_salary.toLocaleString()}</p>
            <div class="tag-set">
                ${j.required_skills.map(s => `<span class="tag matched">Req: ${s}</span>`).join('')}
                ${j.preferred_skills.map(s => `<span class="tag">Pref: ${s}</span>`).join('')}
            </div>
        `;

        const list = document.getElementById('recruiterRecsList');
        if (!data.top_candidates || data.top_candidates.length === 0) {
            list.innerHTML = '<p class="text-muted">No candidate matches found.</p>';
            return;
        }

        list.innerHTML = data.top_candidates.map(c => `
            <div class="rec-card">
                <div style="flex:1;">
                    <h4>${c.candidate_name} <span class="subtext">(${c.candidate_title})</span></h4>
                    <p><strong>Exp:</strong> ${c.score_breakdown.experience_fit * 100}% Fit Score</p>
                    <div class="tag-set">
                        ${c.skill_analysis.matched_skills.map(s => `<span class="tag matched">Match: ${s}</span>`).join('')}
                        ${c.skill_analysis.missing_required_skills.map(s => `<span class="tag missing">Gap: ${s}</span>`).join('')}
                    </div>
                    <div class="xai-box">
                        <strong>AI Fit Rationale:</strong>
                        <ul>
                            ${c.key_match_drivers.map(d => `<li>${d}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="match-gauge">
                    <div class="match-score">${c.match_percentage}%</div>
                    <small>Text: ${Math.round(c.score_breakdown.text_similarity * 100)}%</small>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error("Error loading job recommendations:", err);
    }
}

function openModal(id) { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

async function submitCandidate(e) {
    e.preventDefault();
    const skillsArray = document.getElementById('candSkills').value.split(',').map(s => s.trim()).filter(s => s);
    const payload = {
        name: document.getElementById('candName').value,
        email: document.getElementById('candEmail').value,
        current_title: document.getElementById('candTitle').value,
        skills: skillsArray,
        years_experience: parseFloat(document.getElementById('candExp').value),
        expected_salary: parseFloat(document.getElementById('candSalary').value),
        location: document.getElementById('candLoc').value,
        preferred_location: document.getElementById('candPrefLoc').value,
        resume_text: document.getElementById('candResume').value,
        education: "Bachelor"
    };

    await fetch(`${API_BASE}/candidates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    closeModal('candidateModal');
    fetchAnalytics();
    loadSelectOptions();
}

async function submitJob(e) {
    e.preventDefault();
    const reqSkills = document.getElementById('jobReqSkills').value.split(',').map(s => s.trim()).filter(s => s);
    const prefSkills = document.getElementById('jobPrefSkills').value.split(',').map(s => s.trim()).filter(s => s);

    const payload = {
        title: document.getElementById('jobTitle').value,
        company: document.getElementById('jobCompany').value,
        category: document.getElementById('jobCategory').value,
        work_type: document.getElementById('jobWorkType').value,
        required_skills: reqSkills,
        preferred_skills: prefSkills,
        min_experience: parseInt(document.getElementById('jobMinExp').value),
        max_experience: parseInt(document.getElementById('jobMaxExp').value),
        min_salary: parseFloat(document.getElementById('jobMinSal').value),
        max_salary: parseFloat(document.getElementById('jobMaxSal').value),
        location: document.getElementById('jobLoc').value,
        description: document.getElementById('jobDesc').value
    };

    await fetch(`${API_BASE}/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    closeModal('jobModal');
    fetchAnalytics();
    loadSelectOptions();
}