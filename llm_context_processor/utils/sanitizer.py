"""Text sanitization utilities for cleaning extracted content."""

import re
import unicodedata

# Pre-compiled regex patterns for performance
_WHITESPACE_PATTERNS = [
    (re.compile(r" {10,}"), " "),
    (re.compile(r" {2,}"), " "),
    (re.compile(r"\n{3,}"), "\n\n"),
    (re.compile(r" +\n"), "\n"),
    (re.compile(r"\n +"), "\n"),
]

_EXCEL_PATTERNS = [
    (re.compile(r"\\\\+n"), "\n"),
    (re.compile(r"\\n"), "\n"),
    (re.compile(r"Unnamed: \d+"), "Col"),
    (re.compile(r"\bNaN\b"), "-"),
    (re.compile(r"(\w+)\.\d+"), r"\1"),
]

_EXCEL_DATETIME_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

_REDUNDANT_PATTERNS = [
    (re.compile(r"[-=_]{10,}"), "---"),
    (re.compile(r"[.]{3,}"), "..."),
    (re.compile(r"[-]{3,}"), "---"),
    (re.compile(r"[=]{3,}"), "==="),
    (re.compile(r"[,;]{2,}"), ","),
]

_NUMBER_DATE_PATTERNS = [
    (re.compile(r"(\d+)\.0+\b"), r"\1"),
    (re.compile(r"(\d+)\.0+%"), r"\1%"),
    (re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})"), r"\1/\2/\3"),
]

_CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_TABLE_SPACES_PATTERN = re.compile(r" {2,}")
_ALPHANUMERIC_PATTERN = re.compile(r"[a-zA-Z0-9]")

_UNICODE_ESCAPE_PATTERN = re.compile(r"/uni[0-9A-Fa-f]{4,5}")
_MULTILINE_DIGIT_PATTERN = re.compile(r"^\s*\d+\s*\(\d+\)\s*$", re.MULTILINE)
_FINAL_NEWLINE_PATTERN = re.compile(r"\n{3,}")

_WATERMARK_PATTERNS = [
    re.compile(r"Tämä julkaisu on ladattu SFS Online-palvelusta.*?(?=\n|$)"),
    re.compile(r"Tämä julkaisu on ostettu SFS Kaupasta.*?(?=\n|$)"),
    re.compile(r"Lataaja: IP-käyttäjä\..*?(?=\n|$)"),
    re.compile(r"Julkaisua saa tulostaa 1 kpl ja asentaa 1 työasemalle\..*?(?=\n|$)"),
    re.compile(r"Suomen Standardisoimisliitto SFS SFS-EN.*?(?=\n|$)"),
    re.compile(r"Finnish Standards Association SFS \d+.*?(?=\n|$)"),
    re.compile(r"Monta tapaa tilata.*?(?=\n|$)"),
    re.compile(r"Pysy ajan tasalla.*?(?=\n|$)"),
    re.compile(r"SFS-kauppa.*?(?=\n|$)"),
    re.compile(r"SFS Online.*?(?=\n|$)"),
    re.compile(r"Asiakaspalvelu auttaa.*?(?=\n|$)"),
    re.compile(r"facebook\.com/Standardeista.*?(?=\n|$)"),
    re.compile(r"@standardeista.*?(?=\n|$)"),
    re.compile(r"Haluatko tietää.*?(?=\n|$)"),
    re.compile(r"Tilaa sähköinen.*?(?=\n|$)"),
    re.compile(r"Verkkokaupassa.*?(?=\n|$)"),
    re.compile(r"Kiinnostuitko.*?(?=\n|$)"),
    re.compile(r"Ota yh.*?(?=\n|$)"),
    re.compile(r"Tätä julkaisua myy.*?(?=\n|$)"),
    re.compile(r"Julkaistu: SFS.*?(?=\n|$)"),
    re.compile(r"Copyright \(C\) SFS\..*?(?=\n|$)"),
    re.compile(r"\(C\) ISO \d+ - All rights reserved.*?(?=\n|$)"),
    re.compile(r"\(C\) SFS \d+ for the translation.*?(?=\n|$)"),
    re.compile(r"\(C\) \d+ CEN/CLC.*?(?=\n|$)"),
    re.compile(r"CEN-CENELEC Management Centre:.*?(?=\n|$)"),
    re.compile(r"Tietopalvelumme tarjoaa.*?(?=\n|$)"),
    re.compile(r"Lue lisää www.*?(?=\n|$)"),
    re.compile(r"Kysy lisää SFS:n asiakaspalve.*?(?=\n|$)"),
]

_WHITESPACE_LINE_PATTERNS = [
    (re.compile(r" {50,}([^\s\n]+.*?[^\s\n]+) {10,}\\\\n"), r"\1\n"),
    (re.compile(r" {20,}\\\\n"), "\n"),
    (re.compile(r"^ {20,}(.{1,50}) {10,}$", re.MULTILINE), r"\1"),
]


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace to reduce token count."""
    for pattern, replacement in _WHITESPACE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def clean_excel_artifacts(text: str) -> str:
    """Clean Excel/spreadsheet-specific artifacts."""
    for pattern, replacement in _EXCEL_PATTERNS:
        text = pattern.sub(replacement, text)

    # Special handling for datetime pattern
    text = _EXCEL_DATETIME_PATTERN.sub(
        lambda m: m.group(0).split()[0] if ' ' in m.group(0) else m.group(0),
        text
    )
    return text


def remove_redundant_patterns(text: str) -> str:
    """Remove patterns that repeat excessively."""
    for pattern, replacement in _REDUNDANT_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def optimize_numbers_and_dates(text: str) -> str:
    """Optimize number and date formatting."""
    for pattern, replacement in _NUMBER_DATE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def clean_special_characters(text: str) -> str:
    """Clean special characters and normalize unicode."""
    text = unicodedata.normalize("NFKC", text)

    replacements = {
        '"': '"',
        '"': '"',
        "'": "'",
        "'": "'",
        "—": "-",
        "–": "-",
        "…": "...",
        "€": "EUR",
        "§": "section",
        "®": "(R)",
        "©": "(C)",
        "™": "(TM)",
        "°": "deg",
        "±": "+/-",
        "×": "x",
        "÷": "/",
        "≤": "<=",
        "≥": ">=",
        "≠": "!=",
        "≈": "~=",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = _CONTROL_CHARS_PATTERN.sub("", text)
    return text


def compress_table_formatting(text: str) -> str:
    """Compress table-like structures."""
    lines = text.split("\n")
    compressed_lines = []

    for line in lines:
        if line.count(" ") > 10 or line.count("\t") > 3:
            compressed_line = _TABLE_SPACES_PATTERN.sub(" | ", line.strip())
            compressed_lines.append(compressed_line)
        else:
            compressed_lines.append(line)

    return "\n".join(compressed_lines)


def remove_excessive_whitespace_patterns(text: str) -> str:
    """Remove specific patterns of excessive whitespace."""
    for pattern, replacement in _WHITESPACE_LINE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def remove_empty_sections(text: str) -> str:
    """Remove sections that are essentially empty."""
    lines = text.split("\n")
    meaningful_lines = []

    for line in lines:
        stripped = line.strip()
        if _ALPHANUMERIC_PATTERN.search(stripped):
            meaningful_lines.append(line)
        elif stripped and len(stripped) <= 3:
            meaningful_lines.append(line)

    return "\n".join(meaningful_lines)


def remove_pdf_watermarks_and_unicode_escapes(text: str) -> str:
    """Remove PDF watermarks and unicode escape sequences."""
    text = _UNICODE_ESCAPE_PATTERN.sub("", text)

    for pattern in _WATERMARK_PATTERNS:
        text = pattern.sub("", text)

    text = _MULTILINE_DIGIT_PATTERN.sub("", text)

    return text


def sanitize_text(text: str) -> str:
    """Apply all sanitization steps to reduce token count while preserving meaning."""
    if not text or not text.strip():
        return text

    text = remove_pdf_watermarks_and_unicode_escapes(text)
    text = clean_special_characters(text)
    text = clean_excel_artifacts(text)
    text = remove_excessive_whitespace_patterns(text)
    text = normalize_whitespace(text)
    text = remove_redundant_patterns(text)
    text = optimize_numbers_and_dates(text)
    text = compress_table_formatting(text)
    text = remove_empty_sections(text)

    text = text.strip()
    text = _FINAL_NEWLINE_PATTERN.sub("\n\n", text)

    return text
