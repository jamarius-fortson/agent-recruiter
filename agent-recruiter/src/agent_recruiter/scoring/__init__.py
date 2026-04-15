"""Match scoring — multi-dimensional candidate evaluation."""

from __future__ import annotations

import logging
import re

from ..models import CandidateProfile, JobRequirements, MatchScore

logger = logging.getLogger("agent-recruiter")


def _normalize_skill(skill: str) -> str:
    """Normalize skill name for matching (e.g., 'Python3' -> 'python')."""
    s = skill.lower().strip()
    s = re.sub(r"[^a-z0-9]", "", s)
    # Common aliases
    aliases = {
        "nodejs": "node", "javascript": "js", "typescript": "ts",
        "postgressql": "postgres", "mongodb": "mongo", "k8s": "kubernetes",
        "reactjs": "react", "vuejs": "vue", "nextjs": "next",
    }
    return aliases.get(s, s)


def compute_match_score(
    candidate: CandidateProfile,
    requirements: JobRequirements,
    skill_weight: float = 0.40,
    experience_weight: float = 0.30,
    project_weight: float = 0.15,
    education_weight: float = 0.10,
    signal_weight: float = 0.05,
) -> MatchScore:
    """Compute a multi-dimensional match score for a candidate.

    Scoring is deterministic and auditable.
    """
    
    # 1. Skill Match (0-100)
    cand_skills_norm = {_normalize_skill(s) for s in candidate.skills}
    
    req_skills_norm = {_normalize_skill(s) for s in requirements.required_skills}
    pref_skills_norm = {_normalize_skill(s) for s in requirements.preferred_skills}

    matched_req_norm = req_skills_norm & cand_skills_norm
    matched_pref_norm = pref_skills_norm & cand_skills_norm
    missing_req_norm = req_skills_norm - cand_skills_norm

    # Reconstruct original names for display
    matched_skills = []
    for s in candidate.skills:
        if _normalize_skill(s) in (matched_req_norm | matched_pref_norm):
            matched_skills.append(s)
            
    missing_skills = []
    for s in requirements.required_skills:
        if _normalize_skill(s) in missing_req_norm:
            missing_skills.append(s)

    req_score = (len(matched_req_norm) / max(len(req_skills_norm), 1)) * 100
    pref_score = (len(matched_pref_norm) / max(len(pref_skills_norm), 1)) * 100 if pref_skills_norm else 100
    
    skill_score = (req_score * 0.8) + (pref_score * 0.2)

    # 2. Experience Fit (0-100)
    target_min = requirements.min_years_experience
    target_max = requirements.max_years_experience or (target_min + 5)
    actual_exp = candidate.years_experience

    if target_min <= actual_exp <= target_max:
        exp_score = 100.0
    elif actual_exp > target_max:
        # Overqualified penalty (gentle)
        over = actual_exp - target_max
        exp_score = max(70.0, 100.0 - (over * 3))
    else:
        # Underqualified penalty (steeper)
        under = target_min - actual_exp
        exp_score = max(20.0, 100.0 - (under * 15))

    # 3. Project Relevance (0-100)
    # Check if key projects mention required stack
    proj_text = " ".join(candidate.key_projects).lower()
    proj_hits = sum(1 for s in req_skills_norm if s in proj_text)
    proj_score = min(100.0, (proj_hits / max(len(req_skills_norm), 1)) * 200)

    # 4. Education (0-100)
    edu_score = 75.0 # Baseline
    cand_edu = candidate.education.lower()
    req_edu = requirements.education.lower()
    
    if any(d in cand_edu for d in ["phd", "doctorate"]):
        edu_score = 100.0
    elif any(d in cand_edu for d in ["master", "msc", "ms "]):
        edu_score = 95.0
    elif any(d in cand_edu for d in ["bachelor", "bsc", "bs "]):
        edu_score = 85.0
        
    if req_edu and any(d in req_edu for d in ["master", "phd"]) and "bachelor" in cand_edu:
        edu_score -= 10 # High req, lower actual

    # 5. Signals (0-100)
    sig_score = min(100.0, len(candidate.signals) * 33.4)

    # Weighted Sum
    overall = (
        skill_score * skill_weight +
        exp_score * experience_weight +
        proj_score * project_weight +
        edu_score * education_weight +
        sig_score * signal_weight
    )

    # Insights
    strengths = []
    gaps = []

    if req_score >= 90:
        strengths.append("Exceptional technical stack alignment")
    elif req_score >= 60:
        strengths.append(f"Strong match for {len(matched_req_norm)} core requirements")
    else:
        gaps.append(f"Significant skills gap: {', '.join(missing_skills[:3])}")

    if exp_score >= 90:
        strengths.append(f"Ideal seniority level ({actual_exp} years)")
    elif actual_exp < target_min:
        gaps.append(f"Seniority gap (found {actual_exp}y, target {target_min}y+)")

    if sig_score > 50:
        strengths.append("Strong professional signals (OSS/Community)")

    return MatchScore(
        candidate=candidate,
        overall_score=round(overall, 1),
        skill_score=round(skill_score, 1),
        experience_score=round(exp_score, 1),
        project_score=round(proj_score, 1),
        education_score=round(edu_score, 1),
        signal_score=round(sig_score, 1),
        matched_skills=sorted(matched_skills),
        missing_skills=sorted(missing_skills),
        strengths=strengths,
        gaps=gaps,
        reasoning=f"Candidate has {actual_exp} years of experience and matches {len(matched_req_norm)}/{len(req_skills_norm)} core skills."
    )
