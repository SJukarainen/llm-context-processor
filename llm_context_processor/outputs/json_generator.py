"""JSON metadata output generator for context processor."""

import json
import logging
import os
import threading
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from llm_context_processor.config import JsonOutputConfig

logger = logging.getLogger(__name__)


DOCUMENT_TYPE_MAP = {
    ".pdf": "document",
    ".docx": "document",
    ".doc": "document",
    ".pptx": "presentation",
    ".ppt": "presentation",
    ".xlsx": "spreadsheet",
    ".xls": "spreadsheet",
    ".xlsb": "spreadsheet",
    ".html": "webpage",
    ".htm": "webpage",
    ".xml": "markup",
    ".md": "markdown",
    ".txt": "text",
    ".csv": "data",
    ".tsv": "data",
    ".rtf": "document",
    ".odt": "document",
    ".epub": "document",
}


class JsonOutputGenerator:
    """Generates structured JSON metadata and combined markdown file."""

    def __init__(
        self,
        input_path: str,
        output_path: str,
        config: JsonOutputConfig,
    ):
        self.input_path = input_path
        self.output_path = output_path
        self.config = config
        self.documents: list[dict] = []
        self.extraction_methods: dict[str, int] = defaultdict(int)
        self.total_chars: int = 0
        self.total_words: int = 0
        self.total_tokens: int = 0
        self.documents_lock = threading.Lock()

    def add_document(
        self,
        source_path: str,
        extracted_text: str,
        extraction_method: str,
        word_count: int,
        char_count: int,
    ) -> None:
        """Add a successfully extracted document to the collection."""
        filename = os.path.basename(source_path)
        file_ext = os.path.splitext(filename)[1].lower()

        rel_path = os.path.relpath(source_path, self.input_path)
        folder = os.path.dirname(rel_path)
        if folder == "" or folder == ".":
            folder = "root"

        category = folder.split(os.sep)[0] if folder != "root" else "root"
        category = category.lower().replace(" ", "_")

        document_type = DOCUMENT_TYPE_MAP.get(file_ext, "document")

        doc_id = f"doc_{len(self.documents) + 1:03d}"

        estimated_tokens = char_count // 4

        file_data = {
            "id": doc_id,
            "filename": filename,
            "document_type": document_type,
            "category": category,
            "folder": folder,
            "relative_path": rel_path,
            "content": extracted_text,
            "metadata": {
                "source_path": rel_path,
                "extraction_method": extraction_method,
                "extraction_status": "success",
                "word_count": word_count,
                "char_count": char_count,
                "estimated_tokens": estimated_tokens,
            },
        }

        self.total_chars += char_count
        self.total_words += word_count
        self.total_tokens += estimated_tokens

        with self.documents_lock:
            self.documents.append(file_data)
            self.extraction_methods[extraction_method] += 1

    def write_json_output(self, stats: dict) -> str:
        """Write JSON metadata file and return its path."""
        json_path = self._calculate_json_path()

        documents_for_json = self.documents
        if not self.config.include_content:
            documents_for_json = [
                {k: v for k, v in doc.items() if k != "content"}
                for doc in self.documents
            ]

        json_data = {
            "extraction_info": {
                "total_documents": len(self.documents),
                "successful_extractions": stats.get("processed_files", 0),
                "failed_extractions": stats.get("failed_files", 0),
                "skipped_extractions": stats.get("skipped_files", 0),
                "extraction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_directory": self.input_path,
                "extraction_methods": dict(self.extraction_methods),
                "total_chars": self.total_chars,
                "total_words": self.total_words,
                "estimated_tokens": self.total_tokens,
            },
            "documents": documents_for_json,
        }

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info("Writing JSON metadata: %s", json_path)
            return json_path
        except (IOError, OSError, PermissionError) as e:
            logger.error("Error writing JSON metadata file: %s", e)
            return ""

    def write_combined_file(self) -> str:
        """Write combined markdown file with all documents."""
        if not self.config.create_combined_file:
            return ""

        combined_path = self._calculate_combined_path()

        try:
            with open(combined_path, "w", encoding="utf-8") as f:
                for idx, doc in enumerate(self.documents):
                    if idx > 0:
                        f.write("\n---\n\n")

                    rel_path = doc.get("relative_path", doc.get("filename", "Unknown"))
                    f.write(f"# {rel_path}\n\n")

                    content = doc.get("content", "No content available")
                    f.write(content)
                    f.write("\n")

            logger.info("Writing combined file: %s", combined_path)
            return combined_path

        except (IOError, OSError, PermissionError) as e:
            logger.error("Error writing combined file: %s", e)
            return ""

    def _calculate_json_path(self) -> str:
        """Calculate the path for the JSON metadata file."""
        output_dir = Path(self.output_path)
        output_base = output_dir.name
        json_filename = output_base + self.config.json_filename_suffix
        return str(output_dir / json_filename)

    def _calculate_combined_path(self) -> str:
        """Calculate the path for the combined markdown file."""
        if os.path.isfile(self.input_path):
            input_base = Path(self.input_path).stem
        else:
            input_base = Path(self.input_path).name

        output_dir = Path(self.output_path)
        combined_filename = self.config.combined_filename_prefix + input_base + ".md"
        return str(output_dir / combined_filename)
