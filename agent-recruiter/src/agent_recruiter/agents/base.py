"""Base agent class with LLM orchestration and resilience."""

from __future__ import annotations

import logging
from typing import Any, Type, TypeVar, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("agent-recruiter")

T = TypeVar("T", bound=BaseModel)

class BaseAgent:
    """Foundational agent with retry logic and structured extraction."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        self.model = model
        self.temperature = temperature
        self.client = AsyncOpenAI()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def _call_llm(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Optional[Type[T]] = None
    ) -> tuple[Any, float]:
        """Call LLM and optionally parse into a Pydantic model."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Use JSON mode if response_model is provided
        kwargs = {}
        if response_model:
            kwargs["response_format"] = {"type": "json_object"}

        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            **kwargs
        )

        content = resp.choices[0].message.content or ""
        
        # Calculate cost (rough estimate for gpt-4o family)
        prompt_tokens = resp.usage.prompt_tokens
        completion_tokens = resp.usage.completion_tokens
        
        # Pricing per 1M tokens
        pricing = {
            "gpt-4o": (2.50, 10.00),
            "gpt-4o-mini": (0.15, 0.60),
        }
        input_price, output_price = pricing.get(self.model, (2.50, 10.00))
        cost = (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000

        if response_model:
            try:
                # Clean potential markdown fences if JSON mode failed/wasn't used correctly
                clean_content = content.strip()
                if clean_content.startswith("```json"):
                    clean_content = clean_content.removeprefix("```json").removesuffix("```").strip()
                
                return response_model.model_validate_json(clean_content), cost
            except Exception as e:
                logger.error(f"Failed to parse LLM response into {response_model.__name__}: {e}")
                logger.debug(f"Raw content: {content}")
                raise
        
        return content, cost
