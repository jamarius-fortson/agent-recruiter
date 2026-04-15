<div align="center">

# agent-recruiter

**Autonomous talent sourcing, powered by multi-agent AI.**

Five agents collaborate to automate the recruiting pipeline:
JD Parser → Candidate Sourcer → Resume Screener → Match Scorer → Outreach Drafter.

One command: `agent-recruiter source "Senior Python Engineer"`

[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-blue?style=flat-square)](https://pypi.org/project/agent-recruiter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

[Quick Start](#-quick-start) · [Agent Pipeline](#-agent-pipeline) · [CLI](#-cli) · [Scoring](#-match-scoring)

</div>

---

## ⚠️ Disclaimer

**This tool is for educational and portfolio demonstration purposes.** Automated recruiting tools carry significant ethical responsibilities including bias mitigation, data privacy compliance (GDPR, CCPA), and fair hiring practices. Always ensure human oversight in hiring decisions. This tool does not access private data — it only processes information you provide (resumes, job descriptions).

---

## 🔥 The Problem

> *"Recruiters spend up to 30 hours a week on sourcing alone."*
> — Phenom AI Recruiting Guide, 2026

> *"One recruiter with AI tooling can manage pipelines 5-10x larger than before."*
> — AI Candidate Sourcing Guide, 2026

Every recruiting AI tool costs $100-$500+/month per seat (hireEZ, Juicebox, Fetcher, SeekOut). They're closed-source SaaS platforms locked behind demos and sales calls.

**agent-recruiter** is the open-source alternative. Five specialized AI agents collaborate to:
1. Parse and structure any job description
2. Analyze candidate resumes against requirements
3. Score candidates on skill match, experience, and culture fit
4. Draft personalized outreach messages
5. Produce a ranked shortlist with reasoning

All local. All transparent. All auditable.

---

## ⚡ Quick Start

```bash
pip install agent-recruiter
```

### From a job description

```bash
agent-recruiter source \
  --jd job_description.txt \
  --resumes candidates/ \
  --output shortlist.json

# ┌────────────────────────────────────────────────────────────┐
# │  agent-recruiter — Senior Python Engineer                  │
# ├────────────────────────────────────────────────────────────┤
# │  Parsed: 8 required skills, 5 preferred, 3-5 yr exp       │
# │  Screened: 25 resumes                                      │
# │  Shortlisted: 7 candidates (score ≥ 75%)                   │
# │                                                            │
# │  #1  Sarah Chen        92%  ████████████████████░░  │
# │  #2  Marcus Rivera     88%  █████████████████░░░░░  │
# │  #3  Aisha Patel       85%  ████████████████░░░░░░  │
# │  #4  James O'Brien     81%  ████████## 🧬 Architecture: The Production-Grade Pipeline

agent-recruiter is built with **FAANG-standard engineering principles** for scalability, observability, and resilience.

### High-Performance Parallelism
Unlike naive implementations that process resumes sequentially, agent-recruiter utilizes **asyncio-driven massive parallelism**. 
- **Phase 1 (Sequential):** JD Parser extracts structured requirements using GPT-4o.
- **Phase 2 (Parallel):** Resume Screeners process dozens of resumes concurrently.
- **Phase 3 (Parallel):** GitHub Analyst performs technical signal audits.
- **Phase 4 (Parallel):** Outreach Drafters generate personalized messages.
- **Phase 5 (Parallel):** Interview Generator crafts candidate-specific technical evaluations.

### 🏛️ Enterprise Hardening
- **Managed Concurrency:** Adaptive semaphore pool prevents LLM rate-limiting (429s) during bulk sourcing.
- **Content-Addressable Cache:** Local file-based caching with SHA-256 ensures zero-cost re-runs.
- **Interactive Console:** Premium glassmorphic HTML reporting with tabbed modals and interview plans.
- **Ethical Audit:** Built-in bias mitigation and opt-in "Blind Recruitment" mode for masked PII.
- **Cloud Persistence:** Optional Supabase integration for team collaboration and sync.

---

## 🖥️ CLI Expert Edition

```bash
# Full expert pipeline with technical signal and dashboard generation
agent-recruiter source \
  --jd job.txt \
  --resumes ./vault \
  --github \
  --report dashboard.html

# Enable Blind Recruitment Mode for de-biased hiring
agent-recruiter source --jd job.txt --resumes ./vault --blind

# Sync local results to your Supabase Cloud instance
agent-recruiter sync --file shortlist.json
```
  --screener-model gpt-4o-mini \
  --verbose

# Live candidate screening
agent-recruiter screen \
  --jd job_description.txt \
  --resume candidate_resume.pdf

# Enable OpenTelemetry tracing
agent-recruiter --telemetry source ...
```

---

## 📊 Match Scoring Rubric

The scoring system evaluates candidates across five critical dimensions:

| Dimension | Weight | Expert Evaluation Logic |
|-----------|:------:|-------------------------|
| **Skill Match** | 40% | Core requirement coverage, preferred skill bonuses, normalization |
| **Experience Fit** | 30% | Targeted seniority range, over/under-qualification penalties |
| **Project Relevance** | 15% | Semantic overlap in key projects and achievements |
| **Education** | 10% | Alignment with target degrees and educational levels |
| **Signals** | 5% | Professional impact: OSS, talks, leadership, and community |
---

## 🖥️ CLI

```bash
# Full pipeline: parse JD → screen resumes → score → outreach
agent-recruiter source \
  --jd job_description.txt \
  --resumes candidates/ \
  --output shortlist.json \
  --top 10 \
  --min-score 70

# Parse a job description only
agent-recruiter parse-jd job_description.txt
# → Outputs structured requirements as JSON

# Screen a single resume against a JD
agent-recruiter screen \
  --jd job_description.txt \
  --resume candidate_resume.pdf

# Score candidates from a CSV
agent-recruiter score \
  --jd job_description.txt \
  --candidates candidates.csv

# Generate outreach for top candidates
agent-recruiter outreach \
  --shortlist shortlist.json \
  --tone professional \
  --sender "Alex from Acme Corp"

# Batch: process multiple JDs
agent-recruiter batch \
  --jd-dir job_descriptions/ \
  --resumes candidates/ \
  --output-dir results/
```

---

## 📊 Match Scoring

The scoring system evaluates candidates across multiple dimensions:

### Score Breakdown

| Dimension | Weight | What's Evaluated |
|-----------|:------:|-----------------|
| **Skill Match** | 40% | Required skills found, proficiency level, tech stack overlap |
| **Experience Fit** | 30% | Years of experience, relevance of past roles, industry match |
| **Project Relevance** | 15% | Specific projects/achievements aligned to the role |
| **Education** | 10% | Degree match, relevant certifications |
| **Signals** | 5% | Open source contributions, speaking, publications |

### Score Interpretation

```
90-100%  ██████████████████████  Exceptional fit — interview immediately
80-89%   ████████████████████    Strong fit — high priority
70-79%   ██████████████████      Good fit — worth considering
60-69%   ████████████████        Partial fit — gaps to discuss
<60%     ██████████████          Weak fit — likely not a match
```

### Anti-Bias Safeguards

The scoring system is designed to minimize bias:
- **Skills-first evaluation** — scores are based on demonstrated skills and experience, not demographics
- **Structured criteria** — every score is backed by specific evidence from the resume
- **Transparent reasoning** — each candidate report explains exactly why the score was given
- **Configurable weights** — adjust the scoring model to your hiring philosophy
- **No name/gender/age analysis** — personal identifiers are not factors in scoring

---

## 📋 Input Formats

### Job Description (plain text or markdown)

```text
Senior Python Engineer — Acme Corp

We're looking for a Senior Python Engineer to join our AI platform team.

Requirements:
- 5+ years Python experience
- Experience with FastAPI or Django
- Strong understanding of distributed systems
- Experience with AWS (EC2, Lambda, S3)
- Familiarity with LLMs and agent frameworks

Nice to have:
- Experience with LangGraph or CrewAI
- Open source contributions
- Experience with Kubernetes
```

### Resumes (folder of PDFs, DOCX, TXT, or MD files)

```
candidates/
├── sarah_chen_resume.pdf
├── marcus_rivera_resume.docx
├── aisha_patel_resume.txt
└── ...
```

### Or a CSV

```csv
name,email,resume_text,linkedin_url
Sarah Chen,sarah@email.com,"5 years Python, FastAPI, AWS...",https://linkedin.com/in/sarah
```

---

## 📐 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     agent-recruiter                        │
│                                                           │
│  ┌────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │ JD Parser  │  │  Resume     │  │  Match Scorer   │    │
│  │ Agent      │  │  Screener   │  │                 │    │
│  │            │  │  Agent      │  │  Skill: 40%     │    │
│  │ Extracts   │  │  (parallel) │  │  Experience: 30%│    │
│  │ structured │  │             │  │  Projects: 15%  │    │
│  │ reqs       │  │  Extracts   │  │  Education: 10% │    │
│  │            │  │  skills &   │  │  Signals: 5%    │    │
│  │            │  │  experience │  │                 │    │
│  └─────┬──────┘  └──────┬──────┘  └───────┬─────────┘    │
│        │                │                  │              │
│  ┌─────▼────────────────▼──────────────────▼───────────┐  │
│  │               Outreach Drafter                       │  │
│  │  • Personalized subject + body per candidate         │  │
│  │  • References specific resume highlights             │  │
│  │  • Configurable tone (professional/casual/startup)   │  │
│  └─────────────────────┬───────────────────────────────┘  │
│                        │                                  │
│  ┌─────────────────────▼───────────────────────────────┐  │
│  │              Report Generator                        │  │
│  │  • Ranked shortlist (JSON)                           │  │
│  │  • Per-candidate score breakdown                     │  │
│  │  • Outreach drafts (Markdown/Email)                  │  │
│  │  • CLI Rich table output                             │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 🔌 Configuration

```python
from agent_recruiter import RecruitingPipeline

pipeline = RecruitingPipeline(
    model="gpt-4o",                    # Primary model
    screener_model="gpt-4o-mini",      # Cheaper for bulk screening
    scorer_model="gpt-4o",             # Accurate for scoring
    outreach_model="gpt-4o",           # Quality for personalization
    
    # Scoring weights
    skill_weight=0.40,
    experience_weight=0.30,
    project_weight=0.15,
    education_weight=0.10,
    signal_weight=0.05,
    
    # Filters
    min_score=70,
    top_k=10,
    
    # Outreach
    outreach_tone="professional",       # professional | casual | startup
    sender_name="Alex Johnson",
    company_name="Acme Corp",
)

shortlist = await pipeline.run(
    jd_path="job_description.txt",
    resume_dir="candidates/",
)
```

---

## 🆚 How This Compares

| Tool | Open Source | Multi-Agent | Self-Hosted | CLI | Cost |
|------|:-:|:-:|:-:|:-:|------|
| **agent-recruiter** | ✅ | ✅ (5 agents) | ✅ | ✅ | Free + LLM cost |
| hireEZ | ❌ | ✅ | ❌ | ❌ | $$$/month |
| Juicebox | ❌ | ✅ | ❌ | ❌ | $$$/month |
| Fetcher | ❌ | Partial | ❌ | ❌ | $$$/month |
| SeekOut | ❌ | Partial | ❌ | ❌ | $$$/month |
| Findem | ❌ | ✅ | ❌ | ❌ | $$$$/month |

**The key differentiator:** Self-hosted, auditable, zero vendor lock-in. You own the pipeline and the data. Scoring logic is transparent and configurable. Perfect for teams that need control over their hiring AI.

---

## 🛡️ Ethical Considerations

Automated recruiting carries real risks. agent-recruiter is built with these principles:

1. **Transparency** — Every score includes reasoning. No black-box decisions.
2. **Auditability** — Full JSON output shows exactly how each candidate was evaluated.
3. **Human-in-the-loop** — The tool produces recommendations, not decisions. A human must review every shortlist.
4. **Bias awareness** — Skills-first scoring, no name/gender/age analysis, configurable weights.
5. **Data privacy** — No data leaves your machine except LLM API calls. No candidate data is stored externally.
6. **Compliance** — Designed with EU AI Act, CCPA, and EEOC guidelines in mind. Document and audit your hiring AI.

---

## 🗺️ Roadmap

- [x] JD parsing agent (structured requirements extraction)
- [x] Resume screening agent (skill/experience extraction)
- [x] Multi-dimensional match scoring
- [x] Outreach draft generation
- [x] CLI with Rich output
- [x] Anti-bias scoring design
- [ ] PDF/DOCX resume parsing (via PyMuPDF)
- [ ] GitHub profile analysis (contributions, languages, stars)
- [ ] LinkedIn profile parsing
- [ ] Candidate comparison table
- [ ] Interview question generation per candidate
- [ ] ATS integration (Greenhouse, Lever API export)
- [ ] Diversity analytics dashboard
- [ ] Configurable scoring rubrics (YAML)
- [ ] Batch processing for multiple roles

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

**High-impact contributions:**
- **PDF/DOCX resume parsing** — extract text from common resume formats
- **GitHub integration** — analyze candidate's open-source contributions
- **Interview question generation** — tailored questions per candidate's gaps
- **ATS export** — format output for Greenhouse, Lever, Ashby
- **Bias testing** — automated bias audits on scoring output
- **Multilingual support** — parse resumes in non-English languages

---

## License

[MIT](LICENSE) — Recruit responsibly.

<div align="center">

**[agent-recruiter](https://github.com/daniellopez882/agent-recruiter)** by [Daniel López Orta](https://github.com/daniellopez882)

*Five agents. One shortlist. Zero recruiter fatigue.*

</div>
