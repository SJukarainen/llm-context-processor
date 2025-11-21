"""Command-line interface for llm-context-processor."""

import argparse
import sys
from pathlib import Path

from llm_context_processor import ContextProcessor, ProcessorConfig


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="LLM Context Processor - Convert documents to markdown using MarkItDown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file (output in same directory)
  llm-context-processor document.pdf

  # Process a single file with custom output path
  llm-context-processor document.pdf --output-dir /path/to/output

  # Process a folder (creates processed-[foldername] by default)
  llm-context-processor /path/to/docs

  # Process a folder with custom output directory
  llm-context-processor /path/to/docs --output-dir /path/to/output

  # Disable JSON metadata output
  llm-context-processor /path/to/docs --no-json

  # Use custom configuration
  llm-context-processor /path/to/docs --config config.yaml

  # Generate default config file
  llm-context-processor --generate-config config.yaml
        """,
    )

    parser.add_argument(
        "input_path",
        nargs="?",
        help="Input directory or file to process",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        help="Output directory for processed files (default: same location for files, processed-[foldername] for folders)",
    )

    parser.add_argument(
        "--config",
        "-c",
        help="Path to YAML configuration file",
    )

    parser.add_argument(
        "--generate-config",
        metavar="PATH",
        help="Generate a default configuration file and exit",
    )

    parser.add_argument(
        "--no-metadata-header",
        action="store_true",
        help="Don't include metadata header in output files",
    )

    parser.add_argument(
        "--max-file-size",
        type=float,
        help="Maximum file size to process in MB (default: 100)",
    )

    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Disable JSON metadata generation",
    )

    parser.add_argument(
        "--no-combined-file",
        action="store_true",
        help="Don't create combined markdown file",
    )

    parser.add_argument(
        "--include-content-in-json",
        action="store_true",
        help="Include full content in JSON metadata (memory intensive)",
    )

    args = parser.parse_args()

    if args.generate_config:
        config = ProcessorConfig.default()
        config.to_yaml(args.generate_config)
        print(f"Generated default configuration at: {args.generate_config}")
        return 0

    if not args.input_path:
        parser.print_help()
        print("\nError: input_path is required", file=sys.stderr)
        return 1

    input_path = Path(args.input_path).resolve()

    if not args.output_dir:
        if input_path.is_file():
            output_path = str(input_path.parent / f"{input_path.stem}.md")
        else:
            output_path = str(input_path.parent / f"processed-{input_path.name}")
    else:
        output_path = args.output_dir

    if args.config:
        try:
            config = ProcessorConfig.from_yaml(args.config)
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {args.config}", file=sys.stderr)
            return 1
        except Exception:
            print(f"Error: Failed to load configuration file", file=sys.stderr)
            return 1
    else:
        config = ProcessorConfig.default()

    if args.no_metadata_header:
        config.output.include_metadata_header = False

    if args.max_file_size:
        config.extraction.max_file_size_mb = args.max_file_size

    if args.no_json:
        config.json_output.enabled = False

    if args.no_combined_file:
        config.json_output.create_combined_file = False

    if args.include_content_in_json:
        config.json_output.include_content = True

    try:
        processor = ContextProcessor(
            input_path=str(input_path),
            output_path=output_path,
            config=config,
        )

        print(f"Starting processing...")
        print(f"Input:  {processor.input_path}")
        print(f"Output: {processor.output_path}")
        print()

        processor.process()
        return 0

    except Exception as e:
        print(f"Error: Processing failed - {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
