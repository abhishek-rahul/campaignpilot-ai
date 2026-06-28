from pathlib import Path

import pytest

from app.core.exceptions import ValidationError
from app.rag.document_loader import load_document_text, validate_supported_file


def test_load_text_document(tmp_path: Path):
    path = tmp_path / "guidelines.txt"
    path.write_text("Friendly tone. Mention 25% discount clearly.", encoding="utf-8")

    assert "Friendly tone" in load_document_text(str(path))


def test_unsupported_file_type():
    with pytest.raises(ValidationError) as exc:
        validate_supported_file("guidelines.docx")

    assert exc.value.code == "UNSUPPORTED_FILE_TYPE"
