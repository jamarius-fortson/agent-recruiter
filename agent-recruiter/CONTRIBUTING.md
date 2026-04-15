# Contributing to agent-recruiter

## Setup
```bash
git clone https://github.com/daniellopez882/agent-recruiter.git
cd agent-recruiter
pip install -e ".[dev,all]"
pytest tests/ -v
```

## Ethical Guidelines
- Never add features that discriminate based on protected characteristics
- All scoring must be transparent and auditable
- Ensure human-in-the-loop for all hiring decisions
- Follow EEOC, GDPR, CCPA, and EU AI Act guidelines

## High-Impact Contributions
- **PDF/DOCX parsing** — robust resume text extraction
- **GitHub profile analysis** — score open-source contributions
- **Interview question generation** — tailored per candidate's gaps
- **ATS export** — Greenhouse, Lever, Ashby integration
- **Bias audit tool** — detect scoring bias across demographics
- **Multilingual resumes** — parse non-English resumes
