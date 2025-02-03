"""Utility & helper functions."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from dataclasses import asdict
from configuration import Configuration


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(config: Configuration) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        config (Configuration): Configuration object.
    """
    return init_chat_model(**{k: v for k, v in asdict(config).items() if k != "system_prompt"})
