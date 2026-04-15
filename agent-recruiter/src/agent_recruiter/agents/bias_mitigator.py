"""Agent for ensuring fairness and reducing bias in the recruitment pipeline."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field
from .base import BaseAgent
from ..models import CandidateProfile, MatchScore

class BiasAuditResult(BaseModel):
    is_biased: bool = False
    flagged_signal: List[str] = Field(default_factory=list)
    reasoning: str = ""
    mitigation_suggestion: str = ""

class BiasMitigatorAgent(BaseAgent):
    """Audits matches for potential bias and suggests DEI-compliant improvements."""

    async def audit_match(self, candidate: CandidateProfile, score: MatchScore) -> tuple[BiasAuditResult, float]:
        """Audit the match reasoning for gendered, age-based, or institutional bias."""
        system_prompt = (
            "You are an expert DEI (Diversity, Equity, and Inclusion) auditor for a major tech company. "
            "Your role is to analyze a candidate evaluation for hidden or explicit bias. "
            "Flag any reliance on prestige-based hiring (e.g., 'exclusive school'), "
            "age-related proxies (e.g., 'recent graduate' as an experience cap), "
            "or gendered phrasing."
        )
        
        user_prompt = (
            f"Analyze this evaluation for candidate: {candidate.name}\n"
            f"Match Reasoning: {score.reasoning}\n"
            "Identify if any biased signals were used to compute the score."
        )
        
        return await self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=BiasAuditResult
        )

    def mask_pii(self, profile: CandidateProfile) -> CandidateProfile:
        """Create a 'Blinded' version of the profile to reduce unconscious bias."""
        blinded = profile.model_copy(deep=True)
        # Masking PII
        blinded.name = "Candidate [Masked]"
        # Optionally mask location or years (though usually years are relevant for seniority)
        return blinded
