"""MarkItDown-based extractor for all document formats."""

import re
from pathlib import Path
from typing import Optional

from markitdown import MarkItDown

from llm_context_processor.extractors.base import BaseExtractor, ExtractionResult


class MarkItDownExtractor(BaseExtractor):
    """Unified extractor using Microsoft's MarkItDown for all document types."""

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".doc",
        ".pptx",
        ".ppt",
        ".xlsx",
        ".xls",
        ".xlsb",
        ".txt",
        ".html",
        ".htm",
        ".xml",
        ".csv",
        ".tsv",
        ".md",
        ".rtf",
        ".odt",
        ".epub",
        ".zip",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".mp3",
        ".wav",
        ".m4a",
    }

    def __init__(self) -> None:
        """Initialize MarkItDown converter without LLM features."""
        self.converter = MarkItDown(enable_plugins=False)

    def can_extract(self, file_path: str) -> bool:
        """Check if file extension is supported."""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: str) -> ExtractionResult:
        """Extract text using MarkItDown library."""
        try:
            result = self.converter.convert(file_path)

            if not result or not result.text_content:
                return ExtractionResult(
                    text="",
                    success=False,
                    error_message="No content extracted by MarkItDown",
                    extraction_method="markitdown",
                )

            text = result.text_content.strip()

            quality_issues = self._detect_quality_issues(text, file_path)

            if quality_issues:
                return ExtractionResult(
                    text=text,
                    success=False,
                    error_message=f"Quality issues detected: {quality_issues}",
                    extraction_method="markitdown",
                )

            return ExtractionResult(
                text=text,
                success=True,
                extraction_method="markitdown",
            )

        except Exception as e:
            return ExtractionResult(
                text="",
                success=False,
                error_message=f"Extraction failed: {str(e)}",
                extraction_method="markitdown",
            )

    def _detect_quality_issues(self, text: str, file_path: str) -> Optional[str]:
        """Detect quality issues in extracted text."""
        if not text or len(text.strip()) == 0:
            return "empty_text"

        if len(text) < 50:
            return "very_short_text"

        garbled_ratio = self._calculate_garbled_ratio(text)
        if garbled_ratio > 0.3:
            return f"high_garbled_ratio_{garbled_ratio:.2f}"

        words = text.split()
        if len(words) < 10:
            return "very_few_words"

        try:
            file_size_kb = Path(file_path).stat().st_size / 1024
            if file_size_kb > 100 and len(text) < 200:
                return f"size_mismatch_file={file_size_kb:.0f}kb_text={len(text)}chars"
        except (FileNotFoundError, OSError):
            pass

        return None

    def _calculate_garbled_ratio(self, text: str) -> float:
        """Calculate ratio of garbled/problematic characters."""
        if not text:
            return 0.0

        garbled_patterns = [
            r'[\x00-\x08\x0B\x0C\x0E-\x1F]',
            r'�',
            r'\ufffd',
            r'[^\x00-\x7F\u0080-\uFFFF]',
        ]

        garbled_count = 0
        for pattern in garbled_patterns:
            garbled_count += len(re.findall(pattern, text))

        return garbled_count / max(len(text), 1)

    def is_extraction_quality_sufficient(self, result: ExtractionResult) -> bool:
        """Check if extraction quality is sufficient."""
        if not result.success:
            return False

        if result.char_count < 50:
            return False

        if result.error_message:
            return False

        return True
