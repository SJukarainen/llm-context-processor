"""Configuration management for llm-context-processor."""

from dataclasses import dataclass, field

import yaml


@dataclass
class OutputConfig:
    """Configuration for output generation."""

    format: str = "md"
    include_metadata_header: bool = True


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
        """Load configuration from YAML file with validation."""
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid YAML configuration: expected dict, got {type(data).__name__}")

        # Validate extraction config values
        extraction_data = data.get("extraction", {})
        if "max_file_size_mb" in extraction_data:
            size = extraction_data["max_file_size_mb"]
            if not isinstance(size, (int, float)) or size <= 0:
                raise ValueError(f"max_file_size_mb must be a positive number, got {size}")

        # Construct configs with validation
        try:
            output_config = OutputConfig(**data.get("output", {}))
            extraction_config = ExtractionConfig(**extraction_data)
            json_output_config = JsonOutputConfig(**data.get("json_output", {}))
        except TypeError as e:
            raise ValueError(f"Invalid configuration parameters: {e}") from e

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
