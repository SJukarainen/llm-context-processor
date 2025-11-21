"""Text sanitization utilities for cleaning extracted content."""

import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace to reduce token count."""
    text = re.sub(r" {10,}", " ", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" +\n", "\n", text)
    text = re.sub(r"\n +", "\n", text)
    return text


def clean_excel_artifacts(text: str) -> str:
    """Clean Excel/spreadsheet-specific artifacts."""
    text = re.sub(r"\\\\+n", "\n", text)
    text = re.sub(r"\\n", "\n", text)
    text = re.sub(r"Unnamed: \d+", "Col", text)
    text = re.sub(r"\bNaN\b", "-", text)
    text = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", lambda m: m.group(0).split()[0] if ' ' in m.group(0) else m.group(0), text)
    text = re.sub(r"(\w+)\.\d+", r"\1", text)
    return text


def remove_redundant_patterns(text: str) -> str:
    """Remove patterns that repeat excessively."""
    text = re.sub(r"[-=_]{10,}", "---", text)
    text = re.sub(r"[.]{3,}", "...", text)
    text = re.sub(r"[-]{3,}", "---", text)
    text = re.sub(r"[=]{3,}", "===", text)
    text = re.sub(r"[,;]{2,}", ",", text)
    return text


def optimize_numbers_and_dates(text: str) -> str:
    """Optimize number and date formatting."""
    text = re.sub(r"(\d+)\.0+\b", r"\1", text)
    text = re.sub(r"(\d+)\.0+%", r"\1%", text)
    text = re.sub(r"(\d{1,2})/(\d{1,2})/(\d{4})", r"\1/\2/\3", text)
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

    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    return text


def compress_table_formatting(text: str) -> str:
    """Compress table-like structures."""
    lines = text.split("\n")
    compressed_lines = []

    for line in lines:
        if line.count(" ") > 10 or line.count("\t") > 3:
            compressed_line = re.sub(r" {2,}", " | ", line.strip())
            compressed_lines.append(compressed_line)
        else:
            compressed_lines.append(line)

    return "\n".join(compressed_lines)


def remove_excessive_whitespace_patterns(text: str) -> str:
    """Remove specific patterns of excessive whitespace."""
    text = re.sub(r" {50,}([^\s\n]+.*?[^\s\n]+) {10,}\\\\n", r"\1\n", text)
    text = re.sub(r" {20,}\\\\n", "\n", text)
    text = re.sub(r"^ {20,}(.{1,50}) {10,}$", r"\1", text, flags=re.MULTILINE)
    return text


def remove_empty_sections(text: str) -> str:
    """Remove sections that are essentially empty."""
    lines = text.split("\n")
    meaningful_lines = []

    for line in lines:
        stripped = line.strip()
        if re.search(r"[a-zA-Z0-9]", stripped):
            meaningful_lines.append(line)
        elif stripped and len(stripped) <= 3:
            meaningful_lines.append(line)

    return "\n".join(meaningful_lines)


def remove_pdf_watermarks_and_unicode_escapes(text: str) -> str:
    """Remove PDF watermarks and unicode escape sequences."""
    text = re.sub(r"/uni[0-9A-Fa-f]{4,5}", "", text)

    patterns_to_remove = [
        r"Tämä julkaisu on ladattu SFS Online-palvelusta.*?(?=\n|$)",
        r"Tämä julkaisu on ostettu SFS Kaupasta.*?(?=\n|$)",
        r"Lataaja: IP-käyttäjä\..*?(?=\n|$)",
        r"Julkaisua saa tulostaa 1 kpl ja asentaa 1 työasemalle\..*?(?=\n|$)",
        r"Suomen Standardisoimisliitto SFS SFS-EN.*?(?=\n|$)",
        r"Finnish Standards Association SFS \d+.*?(?=\n|$)",
        r"Monta tapaa tilata.*?(?=\n|$)",
        r"Pysy ajan tasalla.*?(?=\n|$)",
        r"SFS-kauppa.*?(?=\n|$)",
        r"SFS Online.*?(?=\n|$)",
        r"Asiakaspalvelu auttaa.*?(?=\n|$)",
        r"facebook\.com/Standardeista.*?(?=\n|$)",
        r"@standardeista.*?(?=\n|$)",
        r"Haluatko tietää.*?(?=\n|$)",
        r"Tilaa sähköinen.*?(?=\n|$)",
        r"Verkkokaupassa.*?(?=\n|$)",
        r"Kiinnostuitko.*?(?=\n|$)",
        r"Ota yh.*?(?=\n|$)",
        r"Tätä julkaisua myy.*?(?=\n|$)",
        r"Julkaistu: SFS.*?(?=\n|$)",
        r"Copyright \(C\) SFS\..*?(?=\n|$)",
        r"\(C\) ISO \d+ - All rights reserved.*?(?=\n|$)",
        r"\(C\) SFS \d+ for the translation.*?(?=\n|$)",
        r"\(C\) \d+ CEN/CLC.*?(?=\n|$)",
        r"CEN-CENELEC Management Centre:.*?(?=\n|$)",
        r"Tietopalvelumme tarjoaa.*?(?=\n|$)",
        r"Lue lisää www.*?(?=\n|$)",
        r"Kysy lisää SFS:n asiakaspalve.*?(?=\n|$)",
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text)

    text = re.sub(r"^\s*\d+\s*\(\d+\)\s*$", "", text, flags=re.MULTILINE)

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
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text
