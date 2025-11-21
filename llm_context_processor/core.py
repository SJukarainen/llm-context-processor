"""Core document processing engine using MarkItDown."""

import os
import sys
import threading
from pathlib import Path
from typing import Optional

from llm_context_processor.config import ProcessorConfig
from llm_context_processor.extractors import MarkItDownExtractor
from llm_context_processor.outputs.json_generator import JsonOutputGenerator
from llm_context_processor.utils.file_utils import (
    create_parallel_output_path,
    ensure_directory_exists,
    get_file_extension,
    get_file_size_mb,
    should_skip_file,
)
from llm_context_processor.utils.sanitizer import sanitize_text


class ContextProcessor:
    """Main class for recursive document text extraction using MarkItDown."""

    def __init__(
        self,
        input_path: str,
        output_path: str,
        config: Optional[ProcessorConfig] = None,
    ):
        """Initialize context processor."""
        self.input_path = os.path.abspath(input_path)
        self.output_path = os.path.abspath(output_path)
        self.config = config or ProcessorConfig.default()

        if self.input_path == self.output_path:
            raise ValueError("Input and output paths cannot be the same")

        if os.path.exists(self.input_path) and os.path.isdir(self.input_path):
            input_resolved = Path(self.input_path).resolve()
            output_resolved = Path(self.output_path).resolve()
            try:
                output_relative = output_resolved.relative_to(input_resolved)
                raise ValueError(
                    f"Output path cannot be inside input directory: {output_relative}"
                )
            except ValueError as e:
                if "Output path cannot be inside" in str(e):
                    raise
                pass

        self.extractor = MarkItDownExtractor()

        self.stats_lock = threading.Lock()
        self.file_stats_lock = threading.Lock()

        self.json_generator: Optional[JsonOutputGenerator] = None
        if self.config.json_output.enabled:
            self.json_generator = JsonOutputGenerator(
                input_path=self.input_path,
                output_path=self.output_path,
                config=self.config.json_output,
            )

        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0,
            "skipped_files": 0,
            "markitdown_extractions": 0,
            "total_chars": 0,
            "total_words": 0,
            "total_tokens": 0,
        }
        self.file_stats: list[dict] = []

        self.json_path: str = ""
        self.combined_path: str = ""

    def process(self) -> dict:
        """Run the processing workflow."""
        if not os.path.exists(self.input_path):
            raise ValueError(f"Input path does not exist: {self.input_path}")

        is_single_file_mode = os.path.isfile(self.input_path)

        if is_single_file_mode:
            if self.output_path.endswith('.md') and not os.path.isdir(self.output_path):
                output_file = self.output_path
                ensure_directory_exists(output_file)
                self._process_single_file(self.input_path, output_file)
            else:
                if not os.path.exists(self.output_path):
                    output_dir = os.path.dirname(self.input_path)
                    base_name = os.path.splitext(os.path.basename(self.input_path))[0]
                    output_file = os.path.join(output_dir, f"{base_name}.md")
                else:
                    output_file = os.path.join(
                        self.output_path,
                        os.path.splitext(os.path.basename(self.input_path))[0] + ".md"
                    )
                ensure_directory_exists(output_file)
                self._process_single_file(self.input_path, output_file)
        else:
            self._process_directory(self.input_path)

        if self.json_generator and not is_single_file_mode:
            self.json_path = self.json_generator.write_json_output(self.stats)
            self.combined_path = self.json_generator.write_combined_file()

        self._print_summary()
        if not is_single_file_mode:
            self._write_summary_file()
        return self.stats

    def _process_directory(self, dir_path: str) -> None:
        """Process all files in directory recursively."""
        all_files = []
        for root, _, files in os.walk(dir_path, followlinks=False):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                all_files.append(file_path)

        for file_path in all_files:
            self._process_file(file_path)

    def _process_file(self, file_path: str) -> None:
        """Process a single file."""
        with self.stats_lock:
            self.stats["total_files"] += 1

        if should_skip_file(os.path.basename(file_path)):
            with self.stats_lock:
                self.stats["skipped_files"] += 1
            print(f"Skipping: {os.path.relpath(file_path, self.input_path)}")
            return

        file_ext = get_file_extension(file_path)
        if file_ext not in self.config.extraction.supported_extensions:
            with self.stats_lock:
                self.stats["skipped_files"] += 1
            print(f"Skipping unsupported: {os.path.relpath(file_path, self.input_path)}")
            return

        file_size_mb = get_file_size_mb(file_path)
        if file_size_mb > self.config.extraction.max_file_size_mb:
            with self.stats_lock:
                self.stats["skipped_files"] += 1
            print(
                f"Skipping large file ({file_size_mb:.1f}MB): {os.path.relpath(file_path, self.input_path)}"
            )
            return

        print(f"Processing: {os.path.relpath(file_path, self.input_path)}")

        output_file_path = create_parallel_output_path(
            file_path, self.input_path, self.output_path, output_ext=".md"
        )
        ensure_directory_exists(output_file_path)

        if file_ext in [".md", ".txt"]:
            print(f"  -> Copying text file directly")
            if self._copy_text_file(file_path, output_file_path):
                with self.stats_lock:
                    self.stats["processed_files"] += 1
            else:
                with self.stats_lock:
                    self.stats["failed_files"] += 1
            return

        if not self.extractor.can_extract(file_path):
            with self.stats_lock:
                self.stats["failed_files"] += 1
            self._write_error_file(
                output_file_path, file_path, f"Unsupported file type: {file_ext}"
            )
            return

        result = self.extractor.extract(file_path)

        if not result.success:
            print(f"  -> Extraction failed: {result.error_message}")
            with self.stats_lock:
                self.stats["failed_files"] += 1
            self._write_error_file(
                output_file_path,
                file_path,
                result.error_message or "Extraction failed",
            )
            return
        else:
            with self.stats_lock:
                self.stats["markitdown_extractions"] += 1

        sanitized_text = sanitize_text(result.text)
        if self._write_output_file(output_file_path, file_path, sanitized_text, result.extraction_method):
            with self.stats_lock:
                self.stats["processed_files"] += 1
        else:
            with self.stats_lock:
                self.stats["failed_files"] += 1

    def _process_single_file(self, file_path: str, output_file: str) -> None:
        """Process a single file with explicit output path."""
        self.stats["total_files"] += 1

        if should_skip_file(os.path.basename(file_path)):
            self.stats["skipped_files"] += 1
            print(f"Skipping: {os.path.basename(file_path)}")
            return

        file_ext = get_file_extension(file_path)
        if file_ext not in self.config.extraction.supported_extensions:
            self.stats["skipped_files"] += 1
            print(f"Skipping unsupported: {os.path.basename(file_path)}")
            return

        file_size_mb = get_file_size_mb(file_path)
        if file_size_mb > self.config.extraction.max_file_size_mb:
            self.stats["skipped_files"] += 1
            print(f"Skipping large file ({file_size_mb:.1f}MB): {os.path.basename(file_path)}")
            return

        print(f"Processing: {os.path.basename(file_path)}")

        if file_ext in [".md", ".txt"]:
            print(f"  -> Copying text file directly")
            if self._copy_text_file(file_path, output_file):
                self.stats["processed_files"] += 1
            else:
                self.stats["failed_files"] += 1
            return

        if not self.extractor.can_extract(file_path):
            self.stats["failed_files"] += 1
            self._write_error_file(output_file, file_path, f"Unsupported file type: {file_ext}")
            return

        result = self.extractor.extract(file_path)

        if not result.success:
            print(f"  -> Extraction failed: {result.error_message}")
            self.stats["failed_files"] += 1
            self._write_error_file(output_file, file_path, result.error_message or "Extraction failed")
            return
        else:
            self.stats["markitdown_extractions"] += 1

        sanitized_text = sanitize_text(result.text)
        if self._write_output_file(output_file, file_path, sanitized_text, result.extraction_method):
            self.stats["processed_files"] += 1
        else:
            self.stats["failed_files"] += 1

    def _write_output_file(
        self, output_path: str, source_path: str, text: str, method: str
    ) -> bool:
        """Write extracted text to output file."""
        try:
            char_count = len(text)
            word_count = len(text.split())
            token_count = char_count // 4

            with self.stats_lock:
                self.stats["total_chars"] += char_count
                self.stats["total_words"] += word_count
                self.stats["total_tokens"] += token_count

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            if self.json_generator:
                self.json_generator.add_document(
                    source_path=source_path,
                    extracted_text=text,
                    extraction_method=method,
                    word_count=word_count,
                    char_count=char_count,
                )

            with self.file_stats_lock:
                self.file_stats.append({
                    "filename": os.path.basename(source_path),
                    "rel_path": os.path.relpath(source_path, self.input_path),
                    "tokens": token_count,
                    "words": word_count,
                    "chars": char_count,
                })

            return True
        except (IOError, OSError, PermissionError):
            print(f"  -> Failed to write output file", file=sys.stderr)
            return False

    def _write_error_file(self, output_path: str, source_path: str, error_msg: str) -> bool:
        """Write error information to output file."""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"Source: {source_path}\n")
                f.write(f"Status: FAILED\n")
                f.write(f"Error: {error_msg}\n")
            return True
        except (IOError, OSError, PermissionError):
            print(f"  -> Failed to write error file", file=sys.stderr)
            return False

    def _copy_text_file(self, source_path: str, output_path: str) -> bool:
        """Copy text file directly and track statistics."""
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                text = f.read()

            char_count = len(text)
            word_count = len(text.split())
            token_count = char_count // 4

            with self.stats_lock:
                self.stats["total_chars"] += char_count
                self.stats["total_words"] += word_count
                self.stats["total_tokens"] += token_count

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            if self.json_generator:
                self.json_generator.add_document(
                    source_path=source_path,
                    extracted_text=text,
                    extraction_method="direct_copy",
                    word_count=word_count,
                    char_count=char_count,
                )

            with self.file_stats_lock:
                self.file_stats.append({
                    "filename": os.path.basename(source_path),
                    "rel_path": os.path.relpath(source_path, self.input_path),
                    "tokens": token_count,
                    "words": word_count,
                    "chars": char_count,
                })

            return True
        except (IOError, OSError, PermissionError, UnicodeDecodeError):
            print(f"  -> Failed to copy text file", file=sys.stderr)
            return False

    def _print_summary(self) -> None:
        """Print processing summary."""
        print("\n" + "=" * 60)
        print("Processing Summary")
        print("=" * 60)
        print(f"Total files found:      {self.stats['total_files']}")
        print(f"Successfully processed: {self.stats['processed_files']}")
        print(f"Failed to process:      {self.stats['failed_files']}")
        print(f"Skipped files:          {self.stats['skipped_files']}")
        print(f"MarkItDown extractions: {self.stats['markitdown_extractions']}")
        print("=" * 60)
        print(f"Output directory: {self.output_path}")
        if self.json_path:
            print(f"JSON metadata:    {self.json_path}")
        if self.combined_path:
            print(f"Combined file:    {self.combined_path}")
        print("=" * 60)

    def _write_summary_file(self) -> None:
        """Write extraction summary statistics to file."""
        summary_dir = Path(self.output_path).parent
        output_base = Path(self.output_path).name
        summary_filename = output_base + "-summary.txt"

        summary_path = summary_dir / summary_filename

        try:
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write("Extraction Summary\n")
                f.write("=" * 80 + "\n\n")

                f.write("Text Statistics:\n")
                f.write(f"  Total characters: {self.stats['total_chars']:,}\n")
                f.write(f"  Total words: {self.stats['total_words']:,}\n")
                f.write(f"  Estimated LLM tokens: {self.stats['total_tokens']:,} (1 token ≈ 4 characters)\n\n")

                f.write("Files:\n")
                f.write(f"  Total files found: {self.stats['total_files']}\n")
                f.write(f"  Successfully processed: {self.stats['processed_files']}\n")
                f.write(f"  Failed to process: {self.stats['failed_files']}\n")
                f.write(f"  Skipped files: {self.stats['skipped_files']}\n\n")

                f.write("Extraction Methods Used:\n")
                f.write(f"  MarkItDown: {self.stats['markitdown_extractions']}\n")
                f.write("\n")

                f.write("=" * 80 + "\n")
                f.write("Per-File Token Breakdown\n")
                f.write("=" * 80 + "\n\n")

                sorted_files = sorted(self.file_stats, key=lambda x: x["tokens"], reverse=True)

                f.write(f"{'File':<50} {'Tokens':>10} {'Words':>10} {'Chars':>12}\n")
                f.write("-" * 80 + "\n")

                for file_stat in sorted_files:
                    filename = file_stat["rel_path"]
                    if len(filename) > 48:
                        filename = "..." + filename[-45:]

                    f.write(
                        f"{filename:<50} {file_stat['tokens']:>10,} {file_stat['words']:>10,} {file_stat['chars']:>12,}\n"
                    )

                f.write("\n" + "=" * 80 + "\n")
                f.write(f"Output directory: {self.output_path}\n")
                f.write("=" * 80 + "\n")

            print(f"\nSummary written to: {summary_path}")
        except (IOError, OSError, PermissionError):
            print(f"Warning: Failed to write summary file", file=sys.stderr)
