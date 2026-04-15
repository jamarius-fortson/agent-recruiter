"""Shared test fixtures."""

import pytest

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory with some test data (JD and resumes)."""
    d = tmp_path / "data"
    d.mkdir()
    
    # Sample JD
    jd_file = d / "jd.txt"
    jd_file.write_text("Looking for a Senior Python Backend Engineer with Expertise in Kubernetes, Terraform, and Pydantic. Must have 5+ years experience.")
    
    # Sample Resumes
    resumes_dir = d / "resumes"
    resumes_dir.mkdir()
    
    (resumes_dir / "alice.txt").write_text("Alice Smith - Senior Backend Engineer. 6 years Python experience. Expert in Kubernetes and Pydantic. Works at Tech Co.")
    (resumes_dir / "bob.txt").write_text("Bob Jones - Junior Developer. 1 year Python. Learned Kubernetes last week. No Pydantic.")
    (resumes_dir / "claire.docx").write_text("[DOCX content placeholder: Claire - Lead Kubernetes Engineer, 8 years Python/Golang. Expert in Terraform.]")
    
    return d
