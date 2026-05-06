"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import os
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self):
        # Default to gpt-4o-mini as specified by user
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.llm = ChatOpenAI(model=self.model_name, temperature=0)

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        
        # Extract token usage if available
        input_tokens = None
        output_tokens = None
        if "token_usage" in response.response_metadata:
            usage = response.response_metadata["token_usage"]
            input_tokens = usage.get("prompt_tokens")
            output_tokens = usage.get("completion_tokens")
        
        return LLMResponse(
            content=str(response.content),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=None
        )
