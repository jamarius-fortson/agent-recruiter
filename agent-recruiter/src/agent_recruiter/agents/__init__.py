"""Agent pipeline — orchestrates JD parsing, screening, scoring, and outreach."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional, List

from ..models import (
    CandidateProfile, OutreachDraft, Shortlist,
)
from ..scoring import compute_match_score
from ..tools import read_jd, read_resumes_from_dir

from .jd_parser import JDParserAgent
from .resume_screener import ResumeScreenerAgent
from .outreach_drafter import OutreachDrafterAgent
from .github_analyst import GitHubAnalystAgent
from .bias_mitigator import BiasMitigatorAgent
from .interview_gen import InterviewGeneratorAgent
from ..tools.cache import RecruiterCache

logger = logging.getLogger("agent-recruiter")


class RecruitingPipeline:
    """Production-grade multi-agent recruiting pipeline with parallel processing."""

    def __init__(
        self,
        model: str = "gpt-4o",
        screener_model: str = "gpt-4o-mini",
        outreach_model: Optional[str] = None,
        min_score: float = 70,
        top_k: int = 10,
        outreach_tone: str = "professional",
        sender_name: str = "",
        company_name: str = "",
        skill_weight: float = 0.40,
        experience_weight: float = 0.30,
        project_weight: float = 0.15,
        education_weight: float = 0.10,
        signal_weight: float = 0.05,
        analyze_github: bool = True,
        blind_mode: bool = False,
        max_concurrency: int = 20,
        use_cache: bool = True,
    ):
        self.min_score = min_score
        self.top_k = top_k
        self.outreach_tone = outreach_tone
        self.sender_name = sender_name
        self.company_name = company_name
        self.analyze_github = analyze_github
        self.blind_mode = blind_mode
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.cache = RecruiterCache() if use_cache else None
        self.weights = {
            "skill": skill_weight,
            "experience": experience_weight,
            "project": project_weight,
            "education": education_weight,
            "signal": signal_weight,
        }

        # Initialize Agents
        self.jd_parser = JDParserAgent(model=model)
        self.screener = ResumeScreenerAgent(model=screener_model)
        self.drafter = OutreachDrafterAgent(model=outreach_model or model)
        self.github_analyst = GitHubAnalystAgent(model=screener_model)
        self.bias_mitigator = BiasMitigatorAgent(model=screener_model)
        self.interview_gen = InterviewGeneratorAgent(model=model)

    async def run(
        self,
        jd_path: str,
        resume_dir: Optional[str] = None,
        resume_texts: Optional[list[tuple[str, str]]] = None,
    ) -> Shortlist:
        """Run the full pipeline with maximum concurrency."""
        start = time.monotonic()
        total_cost = 0.0

        # Phase 1: Parse JD (Sequential dependency)
        logger.info(f"🚀 Processing job description: {jd_path}")
        jd_text = read_jd(jd_path)
        
        from ..models import JobRequirements
        cached_jd = self.cache.get(jd_text, "jd") if self.cache else None
        if cached_jd:
            requirements = JobRequirements.model_validate(cached_jd)
            cost = 0.0
        else:
            requirements, cost = await self.jd_parser.parse(jd_text)
            if self.cache:
                self.cache.set(jd_text, "jd", requirements.model_dump())
        
        total_cost += cost
        logger.info(f"✅ JD Parsed: {requirements.title} at {requirements.company}")

        # Phase 2: Load Resumes
        if resume_dir:
            raw_resumes = read_resumes_from_dir(resume_dir)
        elif resume_texts:
            raw_resumes = resume_texts
        else:
            raw_resumes = []

        if not raw_resumes:
            logger.warning("⚠️ No resumes found to process.")
            return Shortlist(job_title=requirements.title, job_company=requirements.company)

        # Phase 3: Parallel Screening with Concurrency & Cache
        logger.info(f"🔍 Screening {len(raw_resumes)} resumes in parallel (Concurrency={self.semaphore._value})...")
        async def _screen_with_semaphore(text, filename):
            if self.cache:
                cached = self.cache.get(text, "resume")
                if cached:
                    return CandidateProfile.model_validate(cached), 0.0

            async with self.semaphore:
                profile, cost = await self.screener.screen(text, filename)
                if self.cache:
                    self.cache.set(text, "resume", profile.model_dump())
                return profile, cost

        screen_tasks = [
            _screen_with_semaphore(text, filename) 
            for filename, text in raw_resumes
        ]
        screen_results = await asyncio.gather(*screen_tasks, return_exceptions=True)
        
        profiles: List[CandidateProfile] = []
        for res in screen_results:
            if isinstance(res, Exception):
                logger.error(f"❌ Screening task failed: {res}")
                continue
            profile, cost = res
            profiles.append(profile)
            total_cost += cost

        # Phase 4: Scoring (Deterministic)
        logger.info(f"⚖️ Scoring {len(profiles)} candidates...")
        scores = []
        for profile in profiles:
            score = compute_match_score(
                profile, requirements,
                **self.weights
            )
            scores.append(score)

        # Preliminary filter
        qualified = [s for s in scores if s.overall_score >= self.min_score]
        qualified.sort(key=lambda s: s.overall_score, reverse=True)
        shortlisted = qualified[:self.top_k]

        # Phase 5: Deep Technical Signal (GitHub)
        if self.analyze_github and shortlisted:
            logger.info("📡 Analyzing GitHub profiles for top candidates...")
            async def _analyze_with_semaphore(url):
                if self.cache:
                    cached = self.cache.get(url, "github")
                    if cached:
                        from .github_analyst import GitHubAnalysisResult
                        return GitHubAnalysisResult.model_validate(cached), 0.0

                async with self.semaphore:
                    res, cost = await self.github_analyst.analyze(url)
                    if self.cache:
                        self.cache.set(url, "github", res.model_dump())
                    return res, cost

            github_tasks = []
            for s in shortlisted:
                github_tasks.append(_analyze_with_semaphore(f"github.com/{s.candidate.name.replace(' ', '')}"))
            
            github_results = await asyncio.gather(*github_tasks, return_exceptions=True)
            for i, res in enumerate(github_results):
                if isinstance(res, Exception):
                    continue
                gh_result, cost = res
                total_cost += cost
                new_score = self.github_analyst.integrate_github_score(shortlisted[i].overall_score, gh_result)
                shortlisted[i].overall_score = new_score
                if gh_result.expert_signals:
                    shortlisted[i].strengths.insert(0, f"GitHub Signal: {gh_result.expert_signals[0]}")
            
            shortlisted.sort(key=lambda s: s.overall_score, reverse=True)

        # Phase 6: Ethical Audit (De-biasing)
        logger.info("⚖️ Performing ethical bias audit on top candidates...")
        async def _audit_with_semaphore(cand, score):
            async with self.semaphore:
                return await self.bias_mitigator.audit_match(cand, score)

        audit_tasks = [
            _audit_with_semaphore(s.candidate, s)
            for s in shortlisted
        ]
        audit_results = await asyncio.gather(*audit_tasks, return_exceptions=True)
        for i, res in enumerate(audit_results):
            if isinstance(res, Exception):
                continue
            audit, cost = res
            total_cost += cost
            if audit.is_biased:
                logger.warning(f"⚠️ Bias warning for {shortlisted[i].candidate.name}: {audit.reasoning}")
                shortlisted[i].gaps.append(f"Fairness Audit: {audit.mitigation_suggestion}")

        # Phase 7: Parallel Outreach Drafting
        logger.info(f"✍️ Drafting outreach for {len(shortlisted)} candidates...")
        async def _draft_with_semaphore(score):
            async with self.semaphore:
                return await self.drafter.draft(
                    score, requirements, 
                    tone=self.outreach_tone,
                    sender_name=self.sender_name,
                    company_name=self.company_name
                )

        draft_tasks = [
            _draft_with_semaphore(score)
            for score in shortlisted
        ]
        draft_results = await asyncio.gather(*draft_tasks, return_exceptions=True)
        
        outreach: List[OutreachDraft] = []
        for res in draft_results:
            if isinstance(res, Exception):
                logger.error(f"❌ Outreach task failed: {res}")
                continue
            draft, cost = res
            outreach.append(draft)
            total_cost += cost

        # Phase 8: Technical Interview Planning
        logger.info("🎤 Designing technical interview plans for top candidates...")
        async def _plan_with_semaphore(cand, reqs, score):
            async with self.semaphore:
                return await self.interview_gen.generate_plan(cand, reqs, score)

        interview_tasks = [
            _plan_with_semaphore(s.candidate, requirements, s)
            for s in shortlisted
        ]
        interview_results = await asyncio.gather(*interview_tasks, return_exceptions=True)
        for i, res in enumerate(interview_results):
            if isinstance(res, Exception):
                continue
            plan, cost = res
            total_cost += cost
            shortlisted[i].interview_plan = plan.model_dump()

        # Final Opt-in blinding (PII masking)
        if self.blind_mode:
            logger.info("🛡️ Blinding mode active: Masking candidate identities.")
            for s in shortlisted:
                s.candidate = self.bias_mitigator.mask_pii(s.candidate)
        
        latency = time.monotonic() - start
        logger.info(f"✨ Pipeline complete in {latency:.1f}s. Total cost: ${total_cost:.4f}")

        return Shortlist(
            job_title=requirements.title,
            job_company=requirements.company,
            total_screened=len(raw_resumes),
            candidates=shortlisted,
            outreach_drafts=outreach,
            total_latency_seconds=latency,
            total_cost_usd=total_cost,
        )
