"""Define the configurable parameters for the team."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, asdict
from typing import Annotated, Optional

from langchain_core.runnables import RunnableConfig, ensure_config

import prompts


@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent."""

    system_prompt: str = field(
        default=prompts.SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
            "This prompt sets the context and behavior for the agent."
        },
    )

    model: str = field(
        default="gpt-4o-mini", # "claude-3-5-sonnet-20240620"
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: model-name."
        },
    )
    temperature: float = field(default=0.9)

    max_tokens: int = field(default=1000)

    timeout: int = field(default=60)

    max_retries: int = field(default=3)

    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})

@dataclass(kw_only=True)
class Sales_Agent_Configuration(Configuration):
    system_prompt: str = field(
        default=prompts.SALES_AGENT_PROMPT,
        metadata={
            "description": "Sales Agent system prompt."
        },
    )

@dataclass(kw_only=True)
class Understanding_Agent_Configuration(Configuration):
    system_prompt: str = field(
        default=prompts.UNDERSTANDING_AGENT_PROMPT,
        metadata={
            "description": "Understanding Agent system prompt."
        },
    )


@dataclass(kw_only=True)
class Product_Agent_Configuration(Configuration):
    system_prompt: str = field(
        default=prompts.PRODUCT_AGENT_PROMPT,
        metadata={
            "description": "Product Agent system prompt."
        },
    )

@dataclass(kw_only=True)
class Intent_Router_Configuration(Configuration):
    system_prompt: str = field(
        default=prompts.INTENT_ROUTER_PROMPT,
        metadata={
            "description": "Intent Agent Router system prompt."
        },
    )