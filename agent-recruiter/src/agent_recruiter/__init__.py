"""agent-recruiter: Autonomous talent sourcing powered by multi-agent AI."""

from .models import (
    CandidateProfile, JobRequirements, MatchScore,
    OutreachDraft, Shortlist,
)
from .agents import RecruitingPipeline
from .scoring import compute_match_score

__version__ = "0.1.0"
__all__ = [
    "CandidateProfile", "JobRequirements", "MatchScore",
    "OutreachDraft", "RecruitingPipeline", "Shortlist",
    "compute_match_score",
]
