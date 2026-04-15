# Agent Recruiter - Expert Developer Dashboard (Makefile)

PROJECT_NAME = agent-recruiter
PYTHON = python
PIP = pip
PYTEST = pytest
RUFF = ruff
MYPY = mypy

.PHONY: help install dev test lint clean release

help:
	@echo "Available commands:"
	@echo "  install   Install production dependencies"
	@echo "  dev       Install development dependencies"
	@echo "  test      Run all tests (pytest)"
	@echo "  lint      Verify code style (ruff, mypy)"
	@echo "  clean     Remove temporary files and caches"
	@echo "  source    Run the pipeline (example usage)"

install:
	$(PIP) install .

dev:
	$(PIP) install -e .[dev]

test:
	$(PYTEST) tests/ -v

lint:
	$(RUFF) check src/
	$(MYPY) src/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

source:
	agent-recruiter --verbose source --jd sample_jd.txt --resumes sample_resumes/
