"""Resume Screener Agent — extracts candidate data from resumes."""

from __future__ import annotations

import logging

from ..models import CandidateProfile
from .base import BaseAgent

logger = logging.getLogger("agent-recruiter")

RESUME_SCREENER_SYSTEM_PROMPT = """You are a senior recruitment analyst specializing in technical talent at top-tier tech firms.

Your task is to analyze resumes and extract professional profiles into structured data.

Extract the following accurately:
- Candidate Name and Email
- Technical Skills (Languages, Frameworks, Infrastructure, Tools)
- Years of professional experience (numeric, total)
- Latest 2 roles (Current and Previous)
- Educational background
- Key projects or achievements (bulleted, impact-focused)
- High-level executive summary (2-3 sentences)

Identify professional signals:
- Open source contributions (stars, PRs)
- Technical talks or community leadership
- Published research or blog posts

Respond ONLY with a JSON object."""

class ResumeScreenerAgent(BaseAgent):
    """Agent that handles resume screening and extraction."""

    async def screen(self, resume_text: str, source_file: str = "") -> tuple[CandidateProfile, float]:
        """Extract structured profile from resume text."""
        
        # Profile extraction with JSON mode and Pydantic validation
        profile, cost = await self._call_llm(
            system_prompt=RESUME_SCREENER_SYSTEM_PROMPT,
            user_prompt=f"Screen this resume:\n\n{resume_text[:12000]}", # Larger window for resumes
            response_model=CandidateProfile
        )
        
        # Attach source metadata and raw text
        profile.source_file = source_file
        profile.raw_text = resume_text
        
        return profile, cost
