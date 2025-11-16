"""
NVIDIA NIM LLM integration for browser-use.

This module provides a ChatNvidiaNIM class that wraps the NVIDIA NIM API
using the OpenAI-compatible interface.
"""

from dataclasses import dataclass
from typing import Any

from browser_use.llm.openai.chat import ChatOpenAI


@dataclass
class ChatNvidiaNIM(ChatOpenAI):
    """
    NVIDIA NIM LLM wrapper using OpenAI-compatible API.
    
    NVIDIA NIM provides OpenAI-compatible endpoints, so we can inherit
    from ChatOpenAI and just override the base_url and default model.
    
    Example:
        llm = ChatNvidiaNIM(
            model="qwen/qwen3-next-80b-a3b-instruct",
            api_key="nvapi-xxx",
            temperature=0.6,
            top_p=0.7,
        )
    """
    
    # Override defaults for NVIDIA NIM
    model: str = "qwen/qwen3-next-80b-a3b-instruct"
    base_url: str = "https://integrate.api.nvidia.com/v1"
    temperature: float = 0.6
    top_p: float = 0.7
    max_completion_tokens: int = 4096
    
    @property
    def provider(self) -> str:
        return "nvidia-nim"
    
    @property
    def name(self) -> str:
        return f"nvidia-nim/{self.model}"
