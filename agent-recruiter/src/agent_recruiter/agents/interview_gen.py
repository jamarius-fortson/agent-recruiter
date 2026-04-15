"""Agent for generating high-signal, personalized technical interview questions."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field
from .base import BaseAgent
from ..models import CandidateProfile, JobRequirements, MatchScore

class InterviewQuestion(BaseModel):
    question: str
    target_skill: str
    expected_answer_signal: str
    difficulty: str = "Medium" # Junior, Medium, Senior, Expert

class InterviewPlan(BaseModel):
    candidate_name: str
    job_title: str
    questions: List[InterviewQuestion] = Field(default_factory=list)
    reasoning: str = ""

class InterviewGeneratorAgent(BaseAgent):
    """Generates personalized technical interview plans based on candidate gaps."""

    async def generate_plan(self, candidate: CandidateProfile, requirements: JobRequirements, score: MatchScore) -> tuple[InterviewPlan, float]:
        """Craft a personalized interview plan to verify technical depth and address gaps."""
        system_prompt = (
            "You are a Principal Engineer at a top-tier tech firm. "
            "Your goal is to design a 60-minute technical interview for a specific candidate. "
            "Focus on verifying the 'Matched Skills' while probing the identified 'Gaps'. "
            "Questions should be high-signal, avoiding generic trivia."
        )
        
        user_prompt = (
            f"Candidate: {candidate.name}\n"
            f"Job: {requirements.title}\n"
            f"Match Score: {score.overall_score}%\n"
            f"Gaps identified: {', '.join(score.gaps)}\n"
            "Build a personalized interview plan."
        )
        
        return await self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=InterviewPlan
        )
