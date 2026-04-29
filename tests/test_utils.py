"""工具函数和校验器测试"""

import os
from pathlib import Path

import pytest

from src.utils.file_utils import safe_output_path, get_file_size_str, ensure_dir
from src.utils.validators import validate_pdf_file, validate_image_file, validate_page_range


class TestFileUtils:

    def test_safe_output_path_no_conflict(self, tmp_path):
        path = str(tmp_path / "new_file.pdf")
        result = safe_output_path(path)
        assert result == path

    def test_safe_output_path_conflict(self, tmp_path):
        path = str(tmp_path / "existing.pdf")
        Path(path).touch()
        result = safe_output_path(path)
        assert result != path
        assert "_1" in result

    def test_safe_output_path_multiple_conflicts(self, tmp_path):
        base = tmp_path / "file.pdf"
        base.touch()
        (tmp_path / "file_1.pdf").touch()
        (tmp_path / "file_2.pdf").touch()
        result = safe_output_path(str(base))
        assert "_3" in result

    def test_get_file_size_bytes(self):
        assert get_file_size_str(500) == "500 B"

    def test_get_file_size_kb(self):
        result = get_file_size_str(1024 * 5)
        assert "KB" in result

    def test_get_file_size_mb(self):
        result = get_file_size_str(1024 * 1024 * 2)
        assert "MB" in result

    def test_get_file_size_gb(self):
        result = get_file_size_str(1024 * 1024 * 1024 * 1.5)
        assert "GB" in result

    def test_ensure_dir_creates(self, tmp_path):
        new_dir = str(tmp_path / "a" / "b" / "c")
        result = ensure_dir(new_dir)
        assert result.exists()


class TestValidators:

    def test_validate_pdf_valid(self, sample_pdf):
        ok, msg = validate_pdf_file(sample_pdf)
        assert ok is True

    def test_validate_pdf_nonexistent(self):
        ok, msg = validate_pdf_file("/nonexistent/file.pdf")
        assert ok is False
        assert "不存在" in msg

    def test_validate_pdf_wrong_ext(self, tmp_path):
        path = tmp_path / "file.txt"
        path.write_text("hello")
        ok, msg = validate_pdf_file(str(path))
        assert ok is False
        assert "PDF" in msg

    def test_validate_pdf_empty(self, tmp_path):
        path = tmp_path / "empty.pdf"
        path.touch()
        ok, msg = validate_pdf_file(str(path))
        assert ok is False
        assert "空" in msg

    def test_validate_image_valid(self, sample_image):
        ok, msg = validate_image_file(sample_image)
        assert ok is True

    def test_validate_image_nonexistent(self):
        ok, msg = validate_image_file("/nonexistent/img.png")
        assert ok is False

    def test_validate_page_range_valid(self):
        ok, msg = validate_page_range("1-3, 5, 8-10", 20)
        assert ok is True

    def test_validate_page_range_empty(self):
        ok, msg = validate_page_range("", 10)
        assert ok is False

    def test_validate_page_range_invalid_format(self):
        ok, msg = validate_page_range("abc", 10)
        assert ok is False

    def test_validate_page_range_out_of_bounds(self):
        ok, msg = validate_page_range("1-100", 10)
        assert ok is False
        assert "超出范围" in msg

    def test_validate_page_range_reversed(self):
        ok, msg = validate_page_range("10-5", 20)
        assert ok is False
        assert "起始页" in msg
