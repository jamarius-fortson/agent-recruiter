"""Outreach Drafter Agent — generates personalized candidate outreach."""

from __future__ import annotations

import logging

from ..models import JobRequirements, MatchScore, OutreachDraft
from .base import BaseAgent

logger = logging.getLogger("agent-recruiter")

OUTREACH_DRAFTER_SYSTEM_PROMPT = """You are a top-tier technical recruiter known for highly personalized, candidate-first outreach.

Your task is to write compelling, brief, and authentic outreach emails. 

Guidelines:
- Highly personalized subject line (mention a specific project or achievement)
- Opening that directly references their work (e.g., specific OSS repo, skill, or project)
- Value proposition: Why this role fits THEIR career growth (not why they're good for us)
- Tone must be precise: Casual/Startup vs. Professional/Enterprise
- Call-to-action should be low-pressure
- Length: Keep it under 150 words

Respond ONLY with a JSON object containing `subject` and `body`."""

class OutreachDrafterAgent(BaseAgent):
    """Agent that handles personalized outreach drafting."""

    async def draft(
        self, 
        match: MatchScore, 
        job: JobRequirements,
        tone: str = "professional",
        sender_name: str = "",
        company_name: str = ""
    ) -> tuple[OutreachDraft, float]:
        """Generate a personalized outreach email for a candidate."""
        
        # Contextual prompt engineering
        user_prompt = f"""Draft a {tone} outreach email for:
        
        CANDIDATE: {match.candidate.name}
        ROLE: {job.title} at {company_name or job.company}
        SENDER: {sender_name}
        
        STRENGTHS: {', '.join(match.strengths)}
        TOP PROJECTS: {'; '.join(match.candidate.key_projects[:2])}
        TOP SKILLS: {', '.join(match.candidate.skills[:5])}
        
        MATCH REASONING: {match.reasoning}
        """

        draft_content, cost = await self._call_llm(
            system_prompt=OUTREACH_DRAFTER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=OutreachDraft
        )
        
        # Metadata attachment
        draft_content.candidate_name = match.candidate.name
        draft_content.tone = tone
        
        return draft_content, cost
