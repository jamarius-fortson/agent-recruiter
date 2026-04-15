"""Comprehensive tests for agent-recruiter."""

import json
from pathlib import Path

import pytest

from agent_recruiter.models import (
    CandidateProfile, JobRequirements, MatchScore,
    OutreachDraft, Shortlist,
)
from agent_recruiter.scoring import compute_match_score
from agent_recruiter.tools import read_jd, read_resumes_from_dir


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

def _make_requirements(**kwargs) -> JobRequirements:
    defaults = {
        "title": "Senior Python Engineer",
        "company": "Acme Corp",
        "required_skills": ["python", "fastapi", "aws", "postgresql"],
        "preferred_skills": ["kubernetes", "langraph", "crewai"],
        "min_years_experience": 5,
        "max_years_experience": 10,
        "education": "Bachelor's degree",
    }
    defaults.update(kwargs)
    return JobRequirements(**defaults)


def _make_candidate(**kwargs) -> CandidateProfile:
    defaults = {
        "name": "Test Candidate",
        "skills": ["python", "fastapi", "aws", "docker"],
        "years_experience": 6,
        "current_role": "Software Engineer",
        "education": "BS Computer Science",
        "key_projects": ["Built FastAPI microservice handling 1M requests/day"],
        "signals": ["Open source contributor"],
    }
    defaults.update(kwargs)
    return CandidateProfile(**defaults)


# ─────────────────────────────────────────────
# JobRequirements Tests
# ─────────────────────────────────────────────

class TestJobRequirements:
    def test_creation(self):
        reqs = _make_requirements()
        assert reqs.title == "Senior Python Engineer"
        assert len(reqs.required_skills) == 4

    def test_to_dict(self):
        reqs = _make_requirements()
        d = reqs.to_dict()
        assert d["title"] == "Senior Python Engineer"
        assert "python" in d["required_skills"]
        json.dumps(d)  # Serializable

    def test_summary(self):
        reqs = _make_requirements()
        s = reqs.summary()
        assert "Senior Python Engineer" in s
        assert "python" in s
        assert "5-10 years" in s


# ─────────────────────────────────────────────
# CandidateProfile Tests
# ─────────────────────────────────────────────

class TestCandidateProfile:
    def test_creation(self):
        c = _make_candidate()
        assert c.name == "Test Candidate"
        assert "python" in c.skills

    def test_to_dict(self):
        c = _make_candidate()
        d = c.to_dict()
        assert d["years_experience"] == 6
        json.dumps(d)


# ─────────────────────────────────────────────
# Match Scoring Tests
# ─────────────────────────────────────────────

class TestMatchScoring:
    def test_perfect_match(self):
        reqs = _make_requirements()
        candidate = _make_candidate(
            skills=["python", "fastapi", "aws", "postgresql", "kubernetes", "langraph"],
            years_experience=7,
            education="MS Computer Science",
            signals=["PyCon speaker", "500 GitHub stars"],
        )
        score = compute_match_score(candidate, reqs)
        assert score.overall_score >= 85

    def test_partial_match(self):
        reqs = _make_requirements()
        candidate = _make_candidate(
            skills=["python", "django"],  # Missing fastapi, aws, postgresql
            years_experience=3,  # Under minimum
        )
        score = compute_match_score(candidate, reqs)
        assert score.overall_score < 70
        assert len(score.missing_skills) > 0

    def test_overqualified(self):
        reqs = _make_requirements(min_years_experience=3, max_years_experience=5)
        candidate = _make_candidate(years_experience=15)
        score = compute_match_score(candidate, reqs)
        assert score.experience_score < 100  # Slight penalty
        assert score.experience_score >= 60  # Not too harsh

    def test_underqualified(self):
        reqs = _make_requirements(min_years_experience=10)
        candidate = _make_candidate(years_experience=2)
        score = compute_match_score(candidate, reqs)
        assert score.experience_score < 50

    def test_no_skills_match(self):
        reqs = _make_requirements(required_skills=["rust", "go", "c++"])
        candidate = _make_candidate(skills=["python", "javascript"])
        score = compute_match_score(candidate, reqs)
        assert score.skill_score < 30
        assert len(score.missing_skills) == 3

    def test_all_skills_match(self):
        reqs = _make_requirements(required_skills=["python", "fastapi"])
        candidate = _make_candidate(skills=["python", "fastapi", "docker"])
        score = compute_match_score(candidate, reqs)
        assert score.skill_score >= 80

    def test_phd_education(self):
        reqs = _make_requirements(education="Master's degree")
        candidate = _make_candidate(education="PhD Computer Science, Stanford")
        score = compute_match_score(candidate, reqs)
        assert score.education_score == 100

    def test_no_degree_when_required(self):
        reqs = _make_requirements(education="Bachelor's degree required")
        candidate = _make_candidate(education="Coding bootcamp")
        score = compute_match_score(candidate, reqs)
        assert score.education_score < 50

    def test_signals_boost(self):
        reqs = _make_requirements()
        no_signals = _make_candidate(signals=[])
        with_signals = _make_candidate(
            signals=["PyCon speaker", "500+ GitHub stars", "Published paper"]
        )
        s1 = compute_match_score(no_signals, reqs)
        s2 = compute_match_score(with_signals, reqs)
        assert s2.signal_score > s1.signal_score

    def test_custom_weights(self):
        reqs = _make_requirements()
        candidate = _make_candidate()
        # All weight on skills
        s1 = compute_match_score(candidate, reqs, skill_weight=1.0,
                                  experience_weight=0, project_weight=0,
                                  education_weight=0, signal_weight=0)
        # All weight on experience
        s2 = compute_match_score(candidate, reqs, skill_weight=0,
                                  experience_weight=1.0, project_weight=0,
                                  education_weight=0, signal_weight=0)
        # Different scores because weights differ
        assert s1.overall_score != s2.overall_score

    def test_score_bar(self):
        reqs = _make_requirements()
        candidate = _make_candidate()
        score = compute_match_score(candidate, reqs)
        bar = score.score_bar
        assert len(bar) == 20
        assert "█" in bar

    def test_to_dict_serializable(self):
        reqs = _make_requirements()
        candidate = _make_candidate()
        score = compute_match_score(candidate, reqs)
        d = score.to_dict()
        json.dumps(d)
        assert "overall_score" in d
        assert "breakdown" in d
        assert "matched_skills" in d

    def test_strengths_populated(self):
        reqs = _make_requirements(required_skills=["python", "fastapi"])
        candidate = _make_candidate(skills=["python", "fastapi", "aws"])
        score = compute_match_score(candidate, reqs)
        assert len(score.strengths) > 0

    def test_gaps_populated_for_weak_candidate(self):
        reqs = _make_requirements(required_skills=["rust", "go", "haskell"])
        candidate = _make_candidate(skills=["python"], years_experience=1)
        score = compute_match_score(candidate, reqs)
        assert len(score.gaps) > 0

    def test_project_relevance(self):
        reqs = _make_requirements(required_skills=["fastapi", "aws"])
        c1 = _make_candidate(key_projects=["Built FastAPI service on AWS Lambda"])
        c2 = _make_candidate(key_projects=["Built a basic website"])
        s1 = compute_match_score(c1, reqs)
        s2 = compute_match_score(c2, reqs)
        assert s1.project_score > s2.project_score


# ─────────────────────────────────────────────
# Shortlist Tests
# ─────────────────────────────────────────────

class TestShortlist:
    def test_ranked_order(self):
        reqs = _make_requirements()
        scores = [
            compute_match_score(_make_candidate(name="Low", skills=["html"]), reqs),
            compute_match_score(_make_candidate(name="High", skills=["python", "fastapi", "aws", "postgresql"]), reqs),
            compute_match_score(_make_candidate(name="Mid", skills=["python", "aws"]), reqs),
        ]
        shortlist = Shortlist(candidates=scores)
        ranked = shortlist.ranked()
        assert ranked[0].overall_score >= ranked[1].overall_score
        assert ranked[1].overall_score >= ranked[2].overall_score

    def test_to_dict_serializable(self):
        reqs = _make_requirements()
        score = compute_match_score(_make_candidate(), reqs)
        sl = Shortlist(
            job_title="Test", job_company="Acme",
            total_screened=10,
            candidates=[score],
            total_cost_usd=0.05,
        )
        d = sl.to_dict()
        json.dumps(d)
        assert d["total_screened"] == 10
        assert d["shortlisted"] == 1


# ─────────────────────────────────────────────
# Tools Tests
# ─────────────────────────────────────────────

class TestTools:
    def test_read_jd(self, tmp_path):
        jd = tmp_path / "jd.txt"
        jd.write_text("Senior Python Engineer at Acme Corp")
        text = read_jd(str(jd))
        assert "Senior Python" in text

    def test_read_jd_missing(self):
        with pytest.raises(FileNotFoundError):
            read_jd("/nonexistent/jd.txt")

    def test_read_resumes_from_dir(self, tmp_path):
        (tmp_path / "alice.txt").write_text("Alice - 5yr Python, AWS")
        (tmp_path / "bob.txt").write_text("Bob - 3yr Java, Spring")
        (tmp_path / "notes.py").write_text("# Not a resume")  # Wrong extension

        resumes = read_resumes_from_dir(str(tmp_path))
        assert len(resumes) == 2
        names = [r[0] for r in resumes]
        assert "alice.txt" in names
        assert "bob.txt" in names

    def test_read_resumes_empty_dir(self, tmp_path):
        resumes = read_resumes_from_dir(str(tmp_path))
        assert resumes == []


# ─────────────────────────────────────────────
# OutreachDraft Tests
# ─────────────────────────────────────────────

class TestOutreachDraft:
    def test_creation(self):
        draft = OutreachDraft(
            candidate_name="Sarah Chen",
            subject="Impressed by your FastAPI work",
            body="Hi Sarah, I noticed your distributed systems project...",
        )
        assert draft.candidate_name == "Sarah Chen"

    def test_to_dict(self):
        draft = OutreachDraft(candidate_name="Test", subject="Hi", body="Hello")
        d = draft.to_dict()
        json.dumps(d)
        assert d["subject"] == "Hi"
