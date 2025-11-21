"""Configuration management for llm-context-processor."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class OutputConfig:
    """Configuration for output generation."""

    format: str = "md"
    include_metadata_header: bool = True
    parallel_structure: bool = True


@dataclass
class ExtractionConfig:
    """Configuration for extraction behavior."""

    skip_hidden_files: bool = True
    skip_temp_files: bool = True
    max_file_size_mb: float = 100.0
    supported_extensions: list[str] = field(
        default_factory=lambda: [
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
        ]
    )


@dataclass
class JsonOutputConfig:
    """Configuration for JSON metadata output."""

    enabled: bool = True
    create_combined_file: bool = True
    include_content: bool = False
    json_filename_suffix: str = ".json"
    combined_filename_prefix: str = "combined-"


@dataclass
class ProcessorConfig:
    """Main configuration for llm-context-processor."""

    output: OutputConfig = field(default_factory=OutputConfig)
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    json_output: JsonOutputConfig = field(default_factory=JsonOutputConfig)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ProcessorConfig":
        """Load configuration from YAML file."""
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        output_config = OutputConfig(**data.get("output", {}))
        extraction_config = ExtractionConfig(**data.get("extraction", {}))
        json_output_config = JsonOutputConfig(**data.get("json_output", {}))

        return cls(
            output=output_config,
            extraction=extraction_config,
            json_output=json_output_config,
        )

    @classmethod
    def default(cls) -> "ProcessorConfig":
        """Create default configuration."""
        return cls()

    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to YAML file."""
        data = {
            "output": {
                "format": self.output.format,
                "include_metadata_header": self.output.include_metadata_header,
                "parallel_structure": self.output.parallel_structure,
            },
            "extraction": {
                "skip_hidden_files": self.extraction.skip_hidden_files,
                "skip_temp_files": self.extraction.skip_temp_files,
                "max_file_size_mb": self.extraction.max_file_size_mb,
                "supported_extensions": self.extraction.supported_extensions,
            },
            "json_output": {
                "enabled": self.json_output.enabled,
                "create_combined_file": self.json_output.create_combined_file,
                "include_content": self.json_output.include_content,
                "json_filename_suffix": self.json_output.json_filename_suffix,
                "combined_filename_prefix": self.json_output.combined_filename_prefix,
            },
        }

        with open(yaml_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
