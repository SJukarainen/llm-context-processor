"""LLM Context Processor - Convert documents to markdown using MarkItDown."""

from llm_context_processor.config import ProcessorConfig
from llm_context_processor.core import ContextProcessor

__version__ = "1.0.0"

__all__ = [
    "ContextProcessor",
    "ProcessorConfig",
]
