"""Setup script for llm-context-processor."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="llm-context-processor",
    version="1.0.0",
    description="Convert documents to markdown using MarkItDown for LLM context",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/llm-context-processor",
    packages=find_packages(),
    install_requires=[
        "markitdown[all]>=0.1.0",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "llm-context-processor=llm_context_processor.cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
