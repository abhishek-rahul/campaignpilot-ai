from __future__ import annotations

from pathlib import Path

from app.core.exceptions import ValidationError

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def validate_supported_file(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValidationError(
            "Unsupported file type",
            code="UNSUPPORTED_FILE_TYPE",
            details=[{"supported_extensions": sorted(SUPPORTED_EXTENSIONS)}],
        )
    return suffix


def load_document_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = validate_supported_file(path.name)
    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8")
    else:
        text = _load_pdf_text(path)
    text = text.strip()
    if not text:
        raise ValidationError("Document did not contain readable text", code="EMPTY_DOCUMENT")
    return text


def _load_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:  # noqa: BLE001
        raise ValidationError("PDF support is not available", code="PDF_LOADER_UNAVAILABLE") from exc

    reader = PdfReader(str(path))
    parts = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n\n".join(part for part in parts if part)
