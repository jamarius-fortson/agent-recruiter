"""Tools for reading resumes and job descriptions from files."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger("agent-recruiter")

# Supported resume file extensions
_TEXT_EXTENSIONS = {".txt", ".md", ".text"}
_DOC_EXTENSIONS = {".pdf", ".docx"}


def read_jd(path: str) -> str:
    """Read a job description from a text file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JD file not found: {path}")
    
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        logger.error(f"Failed to read JD file {path}: {e}")
        raise


def read_resume(path: str) -> str:
    """Read a resume from a file. Supports txt, md, pdf, docx."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Resume not found: {path}")

    suffix = p.suffix.lower()

    if suffix in _TEXT_EXTENSIONS:
        return p.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        return _read_pdf(p)

    if suffix == ".docx":
        return _read_docx(p)

    # Fallback for unknown extensions: try text
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        logger.warning(f"Unsupported format for {path}, skipping.")
        return ""


def read_resumes_from_dir(directory: str) -> List[Tuple[str, str]]:
    """Read all resumes from a directory. Returns [(filename, text)]."""
    d = Path(directory)
    if not d.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    resumes = []
    # Support subdirectories if needed, but keeping it flat for now as per original
    for f in sorted(d.iterdir()):
        if f.is_file() and f.suffix.lower() in (_TEXT_EXTENSIONS | _DOC_EXTENSIONS):
            try:
                text = read_resume(str(f))
                if text.strip():
                    resumes.append((f.name, text))
                    logger.debug(f"Read resume: {f.name} ({len(text)} chars)")
                else:
                    logger.warning(f"Empty resume: {f.name}")
            except Exception as e:
                logger.error(f"Error reading {f.name}: {e}")

    logger.info(f"Read {len(resumes)} resumes from {directory}")
    return resumes


def _read_pdf(path: Path) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        
        text = ""
        with fitz.open(str(path)) as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()
    except ImportError:
        logger.warning(f"PyMuPDF not installed. Cannot parse PDF: {path}")
        return f"[PDF: {path.name} - install pymupdf]"
    except Exception as e:
        logger.error(f"Failed to parse PDF {path}: {e}")
        return ""


def _read_docx(path: Path) -> str:
    """Extract text from a DOCX file."""
    try:
        import docx
        
        doc = docx.Document(str(path))
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except ImportError:
        logger.warning(f"python-docx not installed. Cannot parse DOCX: {path}")
        return f"[DOCX: {path.name} - install python-docx]"
    except Exception as e:
        logger.error(f"Failed to parse DOCX {path}: {e}")
        return ""
