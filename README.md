# LLM Context Processor

A standalone Python tool for converting documents to markdown format optimized for LLM context windows. Built on Microsoft's MarkItDown library, this processor handles 19 document formats and generates clean, token-efficient markdown output.

## Features

- **19 Document Formats**: PDFs, Office documents (Word, Excel, PowerPoint), HTML, markdown, and more
- **Quality Text Sanitization**: Removes watermarks, normalizes whitespace, optimizes tables for token efficiency
- **JSON Metadata**: Optional structured metadata output with file statistics
- **Combined Output**: Automatically creates a single markdown file combining all processed documents
- **Standalone**: No LLM dependencies - uses only MarkItDown and standard Python packages
- **Easy Installation**: Simple pip install from GitHub

## Supported File Formats

- **Documents**: PDF, DOCX, DOC, RTF, ODT, EPUB
- **Presentations**: PPTX, PPT
- **Spreadsheets**: XLSX, XLS, XLSB
- **Data**: CSV, TSV
- **Web**: HTML, HTM, XML
- **Text**: MD, TXT
- **Archives**: ZIP

> **Note**: MarkItDown also supports images (JPG, PNG, etc.) and audio files (MP3, WAV, M4A) but these require LLM/vision model configuration for OCR and speech-to-text. The default installation only supports document formats listed above.

## Installation

### Simple Installation (Recommended for Users)

```bash
pip install git+https://github.com/SJukarainen/llm-context-processor.git
```

See [INSTALL.md](INSTALL.md) for a beginner-friendly installation guide.

### Developer Installation

```bash
# Clone the repository
git clone https://github.com/SJukarainen/llm-context-processor.git
cd llm-context-processor

# Install in editable mode
pip install -e .
```

## Quick Start

### Process a Single File

```bash
# Output to same directory (document.md)
llm-context-processor document.pdf

# Specify custom output directory
llm-context-processor document.pdf --output-dir /path/to/output
```

### Process a Folder

```bash
# Creates processed-docs/ folder by default
llm-context-processor /path/to/docs

# Custom output directory
llm-context-processor /path/to/docs --output-dir /path/to/output
```

### Combined Markdown Output

When processing a folder, the tool automatically creates a combined markdown file (combined-[foldername].md) containing all processed documents separated by `---` with relative paths as headers:

```markdown
# folder/document1.md

[content]

---

# folder/subfolder/document2.md

[content]
```

## Command-Line Options

```bash
llm-context-processor [INPUT] [OPTIONS]

Arguments:
  INPUT                     Input file or directory to process

Options:
  --output-dir, -o DIR      Output directory (default: same location for files,
                           processed-[name] for folders)
  --config, -c FILE        Load configuration from YAML file
  --no-json                Disable JSON metadata output
  --no-combined-file       Don't create combined markdown file
  --include-content-in-json Include full content in JSON (memory intensive)
  --max-file-size SIZE     Maximum file size in MB (default: 100)
  --no-metadata-header     Don't include metadata header in output files
  --generate-config FILE   Generate default config file and exit
```

## Configuration

### Generate Default Configuration

```bash
llm-context-processor --generate-config config.yaml
```

### Configuration Options

```yaml
output:
  format: md
  include_metadata_header: true
  parallel_structure: true

extraction:
  skip_hidden_files: true
  skip_temp_files: true
  max_file_size_mb: 100.0
  supported_extensions:
    - .pdf
    - .docx
    # ... etc

json_output:
  enabled: true
  create_combined_file: true
  include_content: false
  json_filename_suffix: .json
  combined_filename_prefix: combined-
```

## Programmatic Usage

```python
from llm_context_processor import ContextProcessor, ProcessorConfig

# Use default configuration
processor = ContextProcessor(
    input_path="/path/to/docs",
    output_path="/path/to/output"
)
stats = processor.process()

# Use custom configuration
config = ProcessorConfig.from_yaml("config.yaml")
processor = ContextProcessor(
    input_path="/path/to/docs",
    output_path="/path/to/output",
    config=config
)
stats = processor.process()

# Access processing statistics
print(f"Processed {stats['processed_files']} files")
print(f"Total tokens: {stats['total_tokens']:,}")
```

## Output Structure

### Single File Mode

```
document.pdf  →  document.md
```

### Folder Mode

```
docs/
├── file1.pdf
├── file2.docx
└── subfolder/
    └── file3.xlsx

→ processed-docs/
  ├── file1.md
  ├── file2.md
  ├── subfolder/
  │   └── file3.md
  ├── processed-docs.json          # Optional metadata
  └── combined-docs.md              # Optional combined file
```

## JSON Metadata Format

```json
{
  "extraction_info": {
    "total_documents": 3,
    "successful_extractions": 3,
    "failed_extractions": 0,
    "skipped_extractions": 0,
    "extraction_date": "2025-01-19 10:30:00",
    "total_chars": 50000,
    "total_words": 10000,
    "estimated_tokens": 12500
  },
  "documents": [
    {
      "id": "doc_001",
      "filename": "file1.pdf",
      "document_type": "document",
      "category": "root",
      "folder": "root",
      "relative_path": "file1.pdf",
      "metadata": {
        "extraction_method": "markitdown",
        "word_count": 3500,
        "char_count": 17500,
        "estimated_tokens": 4375
      }
    }
  ]
}
```

## Text Sanitization

The processor applies aggressive text cleaning to reduce token count while preserving meaning:

- Removes PDF watermarks and unicode escapes
- Normalizes special characters
- Cleans Excel artifacts
- Compresses excessive whitespace
- Optimizes table formatting
- Removes empty sections
- Normalizes numbers and dates

## Module Execution

```bash
# Can also be run as a Python module
python -m llm_context_processor /path/to/docs
```

## Requirements

- Python 3.10+
- markitdown[all]
- pyyaml

## License

MIT License

## Credits

Built on Microsoft's [MarkItDown](https://github.com/microsoft/markitdown) library.
