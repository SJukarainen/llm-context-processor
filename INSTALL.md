# Quick Installation Guide

This guide is for basic Python users who want to get started quickly.

## Prerequisites

- Python 3.10 or higher installed on your system
- pip (Python package installer) - usually comes with Python

To check if you have Python installed:
```bash
python --version
# or
python3 --version
```

## Installation

Install directly from GitHub with a single command:

```bash
pip install git+https://github.com/SJukarainen/llm-context-processor.git
```

That's it! The tool is now installed and ready to use.

## Basic Usage

After installation, use the `llm-context-processor` command from your terminal:

### Process a Single File

```bash
llm-context-processor document.pdf
```

This creates `document.md` in the same directory as your PDF.

### Process a Folder

```bash
llm-context-processor /path/to/documents
```

This creates a `processed-documents` folder containing:
- Individual markdown files for each document
- A combined markdown file with all documents merged
- A JSON file with metadata and statistics

### Specify Output Location

```bash
llm-context-processor document.pdf --output-dir /path/to/output
```

## What You Get

When you process documents, the tool creates:

1. **Individual Markdown Files**: One `.md` file for each processed document
2. **Combined Markdown File**: All documents merged into a single file (when processing folders)
3. **JSON Metadata**: Statistics about processing (tokens, word count, etc.)

## Supported File Types

The tool handles 25+ file formats including:
- PDF documents
- Microsoft Office files (Word, Excel, PowerPoint)
- Images (JPG, PNG, etc.)
- Audio files (MP3, WAV)
- HTML and text files

See the full [README](README.md) for the complete list and advanced options.

## Common Options

```bash
# Don't create the combined markdown file
llm-context-processor /path/to/docs --no-combined-file

# Don't create JSON metadata
llm-context-processor /path/to/docs --no-json

# Limit maximum file size to 50MB
llm-context-processor /path/to/docs --max-file-size 50
```

## Updating the Tool

To update to the latest version:

```bash
pip install --upgrade git+https://github.com/SJukarainen/llm-context-processor.git
```

## Troubleshooting

### Command not found

If you get a "command not found" error, try:
```bash
python -m llm_context_processor document.pdf
```

### Permission errors

On Mac/Linux, you might need to use `pip3` instead of `pip`:
```bash
pip3 install git+https://github.com/SJukarainen/llm-context-processor.git
```

## Need More Help?

- See the full [README](README.md) for advanced usage and configuration options
- Check the [GitHub repository](https://github.com/SJukarainen/llm-context-processor) for issues and updates
