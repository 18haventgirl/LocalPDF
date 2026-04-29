"""合并 PDF 功能测试"""

import os
from pathlib import Path

import pypdf
import pytest


class TestMergeLogic:
    """测试合并 PDF 核心逻辑（直接调用 MergePage._do_merge）"""

    def test_merge_two_files(self, sample_pdfs, tmp_path):
        from src.ui.pages.merge_page import MergePage

        output = str(tmp_path / "merged.pdf")
        result = MergePage._do_merge(sample_pdfs[:2], output)

        assert result is True
        assert os.path.exists(output)

        reader = pypdf.PdfReader(output)
        assert len(reader.pages) == 4  # 每个文件 2 页

    def test_merge_three_files(self, sample_pdfs, tmp_path):
        from src.ui.pages.merge_page import MergePage

        output = str(tmp_path / "merged.pdf")
        result = MergePage._do_merge(sample_pdfs, output)

        assert result is True
        reader = pypdf.PdfReader(output)
        assert len(reader.pages) == 6

    def test_merge_progress_callback(self, sample_pdfs, tmp_path):
        from src.ui.pages.merge_page import MergePage

        progress_calls = []

        def on_progress(current, total):
            progress_calls.append((current, total))

        output = str(tmp_path / "merged.pdf")
        MergePage._do_merge(sample_pdfs[:2], output, progress_callback=on_progress)

        assert len(progress_calls) == 4
        assert progress_calls[-1] == (4, 4)

    def test_merge_single_file_raises(self, sample_pdf, tmp_path):
        """单个文件合并时仍应成功（验证逻辑层面）"""
        from src.ui.pages.merge_page import MergePage

        output = str(tmp_path / "merged.pdf")
        result = MergePage._do_merge([sample_pdf], output)
        assert result is True

    def test_merge_nonexistent_file_raises(self, tmp_path):
        from src.ui.pages.merge_page import MergePage

        output = str(tmp_path / "merged.pdf")
        with pytest.raises(Exception):
            MergePage._do_merge(["/nonexistent/file.pdf"], output)
