"""JD Parser Agent — extracts structured requirements from job descriptions."""

from __future__ import annotations

import logging

from ..models import JobRequirements
from .base import BaseAgent

logger = logging.getLogger("agent-recruiter")

JD_PARSER_SYSTEM_PROMPT = """You are a senior recruiting specialist at a top-tier tech firm. Your task is to parse unstructured job descriptions into structured requirements for automated candidate matching.

Extract the following:
- Title and Company
- Mandatory (Required) Skills vs. Nice-to-have (Preferred) Skills
- Minimum years of experience (be precise, extract the number)
- Educational requirements
- Key responsibilities

Respond ONLY with a JSON object. Ensure numerical values for years_experience. If a range is given, extract the minimum for `min_years_experience`."""

class JDParserAgent(BaseAgent):
    """Agent that handles job description parsing."""

    async def parse(self, jd_text: str) -> tuple[JobRequirements, float]:
        """Parse job description text into structured requirements."""
        
        # LLM parsing with JSON mode and Pydantic model validation
        requirements, cost = await self._call_llm(
            system_prompt=JD_PARSER_SYSTEM_PROMPT,
            user_prompt=f"Parse this job description:\n\n{jd_text[:8000]}", # LLM window protection
            response_model=JobRequirements
        )
        
        # Attach raw text for record keeping
        requirements.raw_text = jd_text
        
        return requirements, cost
