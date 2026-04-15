"""Agent for analyzing candidate technical depth via GitHub profiles."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field

from .base import BaseAgent

class GitHubAnalysisResult(BaseModel):
    login: str
    total_stars: int = 0
    top_languages: List[str] = Field(default_factory=list)
    expert_signals: List[str] = Field(default_factory=list)
    major_contributions: List[str] = Field(default_factory=list)
    consistency_score: float = 0.0 # 0-1.0
    technical_depth_score: float = 0.0 # 0-100
    summary: str = ""

class GitHubAnalystAgent(BaseAgent):
    """Analyzes a candidate's GitHub profile for deeper technical signal."""

    async def analyze(self, github_url: str) -> tuple[GitHubAnalysisResult, float]:
        """Deep analysis of a GitHub profile."""
        login = github_url.rstrip("/").split("/")[-1]
        
        system_prompt = (
            "You are a Senior Engineering Manager at a top-tier tech company. "
            "Your goal is to evaluate a candidate's technical signal based on their GitHub metadata. "
            "You match their public work against 'Expert' benchmarks: consistency, complexity, "
            "impact on major projects, and specialization."
        )
        
        # In production, we'd fetch actual metadata here using a tool/API.
        # For now, we simulate the 'signal' extraction from the URL metadata.
        user_prompt = f"Perform deep technical analysis for GitHub user: {login}. URL: {github_url}"
        
        return await self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=GitHubAnalysisResult
        )

    def integrate_github_score(self, base_score: float, gh_result: GitHubAnalysisResult) -> float:
        """Boost base score based on GitHub signal (Expert bonus)."""
        bonus = 0.0
        
        # High impact bonus
        if gh_result.total_stars > 100:
            bonus += 5
        if gh_result.major_contributions:
            bonus += 10
        if gh_result.technical_depth_score > 90:
            bonus += 5
        
        return min(100.0, base_score + bonus)
