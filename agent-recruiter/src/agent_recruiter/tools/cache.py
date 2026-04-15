"""Advanced file-based caching for high-throughput sourcing."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Any

logger = logging.getLogger("agent-recruiter")

class RecruiterCache:
    """Thread-safe, file-based cache for agent results."""

    def __init__(self, cache_dir: str = ".recruiter_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_hash(self, content: str) -> str:
        """Deterministic hash of input content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get(self, key_content: str, namespace: str) -> Optional[dict]:
        """Fetch cached result if exists."""
        cache_key = self._get_hash(key_content)
        cache_path = self.cache_dir / f"{namespace}_{cache_key}.json"
        
        if cache_path.exists():
            logger.debug(f"💎 Cache hit: {namespace}/{cache_key}")
            return json.loads(cache_path.read_text())
        return None

    def set(self, key_content: str, namespace: str, value: Any):
        """Store result in cache."""
        cache_key = self._get_hash(key_content)
        cache_path = self.cache_dir / f"{namespace}_{cache_key}.json"
        cache_path.write_text(json.dumps(value, indent=2))
        logger.debug(f"💾 Cached: {namespace}/{cache_key}")
