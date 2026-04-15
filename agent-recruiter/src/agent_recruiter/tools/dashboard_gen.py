"""Premium HTML dashboard generator for candidate shortlists — Interactive Edition."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from ..models import Shortlist

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Recruiter │ {job_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0b0f19;
            --surface: #161b2c;
            --surface-hover: #1f2937;
            --primary: #38bdf8;
            --primary-glow: rgba(56, 189, 248, 0.3);
            --accent: #818cf8;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --border: rgba(255, 255, 255, 0.1);
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --glass: rgba(255, 255, 255, 0.03);
        }}

        * {{
            margin: 0; padding: 0; box-sizing: border-box;
            font-family: 'Inter', sans-serif;
        }}

        body {{
            background: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            background-image: radial-gradient(circle at 0% 0%, #1e293b 0%, #0b0f19 50%);
        }}

        /* Sidebar */
        aside {{
            width: 280px;
            border-right: 1px solid var(--border);
            padding: 40px 24px;
            display: flex;
            flex-direction: column;
            gap: 32px;
            height: 100vh;
            position: sticky;
            top: 0;
            background: rgba(11, 15, 25, 0.5);
            backdrop-filter: blur(20px);
        }}

        .logo {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 12px;
            background: linear-gradient(to right, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        nav {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .nav-item {{
            padding: 12px 16px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-dim);
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .nav-item:hover, .nav-item.active {{
            background: var(--glass);
            color: var(--text-main);
        }}

        .nav-item.active {{
            background: var(--primary-glow);
            color: var(--primary);
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}

        /* Main Content */
        main {{
            flex: 1;
            padding: 60px 80px;
            max-width: 1400px;
        }}

        header {{
            margin-bottom: 48px;
        }}

        header h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.5rem;
            margin-bottom: 8px;
        }}

        .stats-row {{
            display: flex;
            gap: 24px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: var(--surface);
            padding: 20px 24px;
            border-radius: 20px;
            border: 1px solid var(--border);
            flex: 1;
        }}

        .stat-val {{
            display: block;
            font-size: 1.8rem;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            color: var(--primary);
        }}

        .stat-label {{
            font-size: 0.8rem;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        /* Candidate List */
        .candidate-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 24px;
        }}

        .candidate-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            transition: all 0.3s;
            cursor: pointer;
            position: relative;
        }}

        .candidate-card:hover {{
            transform: translateY(-4px);
            border-color: var(--primary);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}

        .score-badge {{
            position: absolute;
            top: 24px;
            right: 24px;
            background: var(--primary-glow);
            color: var(--primary);
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 800;
            font-size: 1.1rem;
        }}

        .cand-name {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 4px;
            font-family: 'Outfit', sans-serif;
        }}

        .cand-title {{
            color: var(--text-dim);
            font-size: 0.9rem;
            margin-bottom: 16px;
        }}

        .pill-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }}

        .pill {{
            background: rgba(255,255,255,0.05);
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.75rem;
            color: var(--text-dim);
        }}

        .match-bar-bg {{
            height: 6px;
            background: rgba(255,255,255,0.05);
            border-radius: 3px;
            margin-top: 20px;
        }}

        .match-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            border-radius: 3px;
        }}

        /* Modal */
        #modal-overlay {{
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            display: none;
            justify-content: center;
            align-items: center;
            padding: 40px;
            z-index: 1000;
        }}

        .modal-content {{
            background: var(--surface);
            max-width: 900px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            border-radius: 32px;
            border: 1px solid var(--border);
            padding: 48px;
            position: relative;
        }}

        .close-btn {{
            position: absolute;
            top: 32px; right: 32px;
            cursor: pointer;
            font-size: 1.5rem;
            color: var(--text-dim);
        }}

        /* Tabs inside modal */
        .modal-tabs {{
            display: flex;
            gap: 32px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 32px;
        }}

        .modal-tab-item {{
            padding: 12px 0;
            cursor: pointer;
            color: var(--text-dim);
            font-weight: 600;
            position: relative;
        }}

        .modal-tab-item.active {{
            color: var(--primary);
        }}

        .modal-tab-item.active::after {{
            content: '';
            position: absolute;
            bottom: -1px; left: 0; right: 0;
            height: 2px;
            background: var(--primary);
        }}

        /* Custom scrollbar */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-dim); }}

        h3 {{ margin-bottom: 16px; font-family: 'Outfit', sans-serif; }}
        p {{ line-height: 1.6; color: #d1d5db; margin-bottom: 16px; }}
        
        .q-box {{
            background: rgba(255,255,255,0.03);
            border-left: 4px solid var(--primary);
            padding: 16px;
            margin-bottom: 16px;
            border-radius: 0 12px 12px 0;
        }}

        @media (max-width: 1024px) {{
            aside {{ display: none; }}
            main {{ padding: 40px 24px; }}
        }}
    </style>
</head>
<body>
    <aside>
        <div class="logo">
            <span>✧</span> Agent Recruiter
        </div>
        <nav>
            <div class="nav-item active">Candidates</div>
            <div class="nav-item">Analytics</div>
            <div class="nav-item">Outreach Logs</div>
            <div class="nav-item">Settings</div>
        </nav>
        <div style="margin-top: auto; color: var(--text-dim); font-size: 0.8rem;">
            FAANG Edition v0.3.0
        </div>
    </aside>

    <main>
        <header>
            <h1>{job_title}</h1>
            <p style="color: var(--text-dim);">Expert analysis complete. {count} elite candidates identified at {job_company}.</p>
        </header>

        <div class="stats-row">
            <div class="stat-card">
                <span class="stat-val">{total_screened}</span>
                <span class="stat-label">Processed</span>
            </div>
            <div class="stat-card">
                <span class="stat-val">{count}</span>
                <span class="stat-label">Shortlisted</span>
            </div>
            <div class="stat-card">
                <span class="stat-val">${cost}</span>
                <span class="stat-label">Total Cost</span>
            </div>
            <div class="stat-card">
                <span class="stat-val">{latency}s</span>
                <span class="stat-label">Pipeline Time</span>
            </div>
        </div>

        <div class="candidate-grid" id="candidate-grid">
            <!-- Rendered by JS -->
        </div>
    </main>

    <div id="modal-overlay">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">×</span>
            <div id="modal-body">
                <!-- Loaded on click -->
            </div>
        </div>
    </div>

    <script>
        const data = {data_json};

        function renderCandidates() {{
            const grid = document.getElementById('candidate-grid');
            grid.innerHTML = data.candidates.map((cand, idx) => `
                <div class="candidate-card" onclick="openModal(${{idx}})">
                    <div class="score-badge">${{cand.overall_score.toFixed(0)}}%</div>
                    <div class="cand-name">${{cand.candidate.name}}</div>
                    <div class="cand-title">${{cand.candidate.current_role}} @ ${{cand.candidate.current_company || 'Stealth'}}</div>
                    
                    <div class="pill-group">
                        ${{cand.matched_skills.slice(0, 5).map(s => `<span class="pill">${{s}}</span>`).join('')}}
                    </div>

                    <div style="font-size: 0.85rem; color: #d1d5db; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-top: 12px;">
                        ${{cand.strengths[0] || 'Top matching profile.'}}
                    </div>

                    <div class="match-bar-bg">
                        <div class="match-bar-fill" style="width: ${{cand.overall_score}}%"></div>
                    </div>
                </div>
            `).join('');
        }}

        function openModal(idx) {{
            const cand = data.candidates[idx];
            const draft = data.outreach_drafts[idx] || {{ subject: 'N/A', body: 'No draft available.' }};
            const overlay = document.getElementById('modal-overlay');
            const body = document.getElementById('modal-body');

            const interviewHtml = cand.interview_plan ? `
                <h3>Personalized Interview Plan</h3>
                <p>${{cand.interview_plan.reasoning}}</p>
                ${{cand.interview_plan.questions.map(q => `
                    <div class="q-box">
                        <div style="font-weight: 700; margin-bottom: 4px;">${{q.question}}</div>
                        <div style="font-size: 0.8rem; color: var(--primary);">Target: ${{q.target_skill}} | Intensity: ${{q.difficulty}}</div>
                        <div style="font-size: 0.85rem; margin-top: 8px; color: var(--text-dim); font-style: italic;">Expected: ${{q.expected_answer_signal}}</div>
                    </div>
                `).join('')}}
            ` : '<h3>Interview Plan</h3><p>Not generated for this candidate.</p>';

            body.innerHTML = `
                <div style="margin-bottom: 40px;">
                    <div style="font-size: 0.9rem; color: var(--primary); font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Detailed Assessment</div>
                    <h2 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; margin-bottom: 8px;">${{cand.candidate.name}}</h2>
                    <p style="font-size: 1.1rem; color: var(--text-dim);">${{cand.candidate.summary}}</p>
                </div>

                <div class="modal-tabs">
                    <div class="modal-tab-item active" onclick="switchTab(this, 'score')">Expert Scoring</div>
                    <div class="modal-tab-item" onclick="switchTab(this, 'interview')">Interview Prep</div>
                    <div class="modal-tab-item" onclick="switchTab(this, 'outreach')">Outreach Draft</div>
                </div>

                <div id="tab-score" class="tab-pane">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px;">
                        <div>
                            <h3>Evaluation Reasoning</h3>
                            <p>${{cand.reasoning}}</p>
                            
                            <h3 style="margin-top: 24px;">Growth Opportunities (Gaps)</h3>
                            <ul style="color: #d1d5db; padding-left: 16px;">
                                ${{cand.gaps.map(g => `<li style="margin-bottom: 8px;">${{g}}</li>`).join('')}}
                            </ul>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); padding: 32px; border-radius: 24px;">
                            <h3>Score Breakdown</h3>
                            <div style="display: flex; flex-direction: column; gap: 16px;">
                                ${{[
                                    ['Skills', cand.skill_score],
                                    ['Experience', cand.experience_score],
                                    ['Project depth', cand.project_score],
                                    ['Signals', cand.signal_score]
                                ].map(([label, score]) => `
                                    <div>
                                        <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-bottom: 4px;">
                                            <span>${{label}}</span>
                                            <span>${{score.toFixed(0)}}%</span>
                                        </div>
                                        <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px;">
                                            <div style="height: 100%; width: ${{score}}%; background: var(--primary); border-radius: 2px;"></div>
                                        </div>
                                    </div>
                                `).join('')}}
                            </div>
                        </div>
                    </div>
                </div>

                <div id="tab-interview" class="tab-pane" style="display: none;">
                    ${{interviewHtml}}
                </div>

                <div id="tab-outreach" class="tab-pane" style="display: none;">
                    <h3>Draft Outreach</h3>
                    <div style="background: #000; padding: 24px; border-radius: 16px; border: 1px solid var(--border); font-family: 'Courier New', monospace; font-size: 0.95rem;">
                        <div style="color: var(--primary); margin-bottom: 16px;">Subject: ${{draft.subject}}</div>
                        <div style="white-space: pre-wrap;">${{draft.body}}</div>
                    </div>
                </div>
            `;
            
            overlay.style.display = 'flex';
        }}

        function closeModal() {{
            document.getElementById('modal-overlay').style.display = 'none';
        }}

        function switchTab(el, tabName) {{
            // Active state for tabs
            document.querySelectorAll('.modal-tab-item').forEach(t => t.classList.remove('active'));
            el.classList.add('active');

            // Toggle panes
            document.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');
            document.getElementById('tab-' + tabName).style.display = 'block';
        }}

        // Close on background click
        document.getElementById('modal-overlay').addEventListener('click', (e) => {{
            if (e.target.id === 'modal-overlay') closeModal();
        }});

        renderCandidates();
    </script>
</body>
</html>
"""

def generate_dashboard(shortlist: Shortlist, output_path: str = "shortlist_report.html"):
    """Render a premium, interactive HTML dashboard from the shortlist results."""
    data_json = json.dumps(shortlist.to_dict())
    
    html = DASHBOARD_TEMPLATE.format(
        job_title=shortlist.job_title,
        job_company=shortlist.job_company,
        date=datetime.now().strftime("%B %d, %Y"),
        count=shortlist.shortlisted_count,
        total_screened=shortlist.total_screened,
        data_json=data_json,
        latency=f"{shortlist.total_latency_seconds:.1f}",
        cost=f"{shortlist.total_cost_usd:.3f}"
    )

    Path(output_path).write_text(html, encoding="utf-8")
    return output_path
