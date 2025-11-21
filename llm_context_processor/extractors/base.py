"""Base extractor interface for document extraction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractionResult:
    """Result of text extraction from a document."""

    text: str
    success: bool
    error_message: Optional[str] = None
    char_count: int = 0
    word_count: int = 0
    extraction_method: str = "direct"

    def __post_init__(self) -> None:
        """Calculate counts after initialization."""
        if self.text:
            self.char_count = len(self.text)
            self.word_count = len(self.text.split())


class BaseExtractor(ABC):
    """Base class for all document extractors."""

    @abstractmethod
    def can_extract(self, file_path: str) -> bool:
        """Check if this extractor can handle the file."""
        pass

    @abstractmethod
    def extract(self, file_path: str) -> ExtractionResult:
        """Extract text from the file."""
        pass

    def is_extraction_quality_sufficient(self, result: ExtractionResult) -> bool:
        """Check if extraction quality is sufficient."""
        if not result.success:
            return False

        if result.char_count < 50:
            return False

        if result.error_message:
            return False

        return True
