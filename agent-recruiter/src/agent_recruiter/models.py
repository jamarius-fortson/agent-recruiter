"""Core data models for agent-recruiter."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class JobRequirements(BaseModel):
    """Structured job description parsed by the JD Parser agent."""

    title: str = Field(default="", description="The formal job title")
    company: str = Field(default="", description="The hiring company name")
    team: str = Field(default="", description="The specific team or department")
    description: str = Field(default="", description="Brief summary of the role")
    required_skills: list[str] = Field(default_factory=list, description="Mandatory technical skills")
    preferred_skills: list[str] = Field(default_factory=list, description="Optional/nice-to-have skills")
    min_years_experience: int = Field(default=0, description="Minimum years of experience required")
    max_years_experience: Optional[int] = Field(default=None, description="Maximum target years of experience")
    education: str = Field(default="", description="Required educational background")
    responsibilities: list[str] = Field(default_factory=list, description="Primary duties")
    raw_text: str = Field(default="", description="Original job description text")

    def summary(self) -> str:
        parts = [f"Title: {self.title}"]
        if self.company:
            parts.append(f"Company: {self.company}")
        parts.append(f"Required: {', '.join(self.required_skills)}")
        if self.preferred_skills:
            parts.append(f"Preferred: {', '.join(self.preferred_skills)}")
        parts.append(f"Experience: {self.min_years_experience}+ years")
        if self.education:
            parts.append(f"Education: {self.education}")
        return "\n".join(parts)


class CandidateProfile(BaseModel):
    """Extracted candidate information from a resume."""

    name: str = Field(default="", description="Full name of the candidate")
    email: str = Field(default="", description="Contact email address")
    source_file: str = Field(default="", description="Filename of the resume")
    skills: list[str] = Field(default_factory=list, description="Technical skills extracted")
    years_experience: int = Field(default=0, description="Total years of professional experience")
    current_role: str = Field(default="", description="Most recent job title")
    current_company: str = Field(default="", description="Most recent employer")
    education: str = Field(default="", description="Highest degree or institution")
    certifications: list[str] = Field(default_factory=list, description="Professional certifications")
    key_projects: list[str] = Field(default_factory=list, description="Notable projects or achievements")
    signals: list[str] = Field(default_factory=list, description="Public signals like OSS or talks")
    summary: str = Field(default="", description="Executive summary of the candidate")
    raw_text: str = Field(default="", description="Original resume text")


class MatchScore(BaseModel):
    """Multi-dimensional match score for a candidate."""

    candidate: CandidateProfile
    overall_score: float = Field(default=0.0, description="Weighted aggregate score (0-100)")
    skill_score: float = Field(default=0.0, description="Score based on skill match")
    experience_score: float = Field(default=0.0, description="Score based on years/seniority fit")
    project_score: float = Field(default=0.0, description="Score based on project relevance")
    education_score: float = Field(default=0.0, description="Score based on educational alignment")
    signal_score: float = Field(default=0.0, description="Score based on professional signals")
    matched_skills: list[str] = Field(default_factory=list, description="Required/preferred skills found")
    missing_skills: list[str] = Field(default_factory=list, description="Required skills not found")
    strengths: list[str] = Field(default_factory=list, description="Top positive match points")
    gaps: list[str] = Field(default_factory=list, description="Potential areas of misalignment")
    reasoning: str = Field(default="", description="Detailed explanation of the score")
    interview_plan: Optional[dict] = Field(default=None, description="Personalized technical interview plan")

    @property
    def score_bar(self) -> str:
        filled = int(self.overall_score / 5)
        empty = 20 - filled
        return "█" * filled + "░" * empty


class OutreachDraft(BaseModel):
    """Personalized outreach message for a candidate."""

    candidate_name: str = Field(default="", description="Full name of target candidate")
    subject: str = Field(default="", description="Compelling email subject line")
    body: str = Field(default="", description="Personalized email body")
    tone: str = Field(default="professional", description="The tone used in the draft")


class Shortlist(BaseModel):
    """Final ranked shortlist output."""

    job_title: str = ""
    job_company: str = ""
    total_screened: int = 0
    candidates: list[MatchScore] = Field(default_factory=list)
    outreach_drafts: list[OutreachDraft] = Field(default_factory=list)
    total_latency_seconds: float = 0.0
    total_cost_usd: float = 0.0

    @property
    def shortlisted_count(self) -> int:
        return len(self.candidates)

    def ranked(self) -> list[MatchScore]:
        return sorted(self.candidates, key=lambda c: c.overall_score, reverse=True)

    def to_dict(self) -> dict:
        """Export to JSON-compatible dictionary."""
        return {
            "job": {"title": self.job_title, "company": self.job_company},
            "total_screened": self.total_screened,
            "shortlisted": self.shortlisted_count,
            "candidates": [c.model_dump() for c in self.ranked()],
            "outreach": [o.model_dump() for o in self.outreach_drafts],
            "meta": {
                "latency_s": round(self.total_latency_seconds, 1),
                "cost_usd": round(self.total_cost_usd, 4),
            },
        }
