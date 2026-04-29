"""拆分 PDF 功能测试"""

import os
from pathlib import Path

import pypdf
import pytest


class TestSplitLogic:
    """测试拆分 PDF 核心逻辑"""

    def test_split_by_range(self, sample_pdf, tmp_path):
        from src.ui.pages.split_page import SplitPage

        output_dir = str(tmp_path / "split_out")
        result = SplitPage._do_split(
            sample_pdf, "range", "1-2, 3", 1, output_dir
        )

        assert len(result) == 2
        for f in result:
            assert os.path.exists(f)

        reader = pypdf.PdfReader(result[0])
        assert len(reader.pages) == 2

        reader = pypdf.PdfReader(result[1])
        assert len(reader.pages) == 1

    def test_split_every_n(self, sample_pdf, tmp_path):
        from src.ui.pages.split_page import SplitPage

        output_dir = str(tmp_path / "split_out")
        result = SplitPage._do_split(
            sample_pdf, "every_n", None, 1, output_dir
        )

        assert len(result) == 3
        for f in result:
            reader = pypdf.PdfReader(f)
            assert len(reader.pages) == 1

    def test_split_single_pages(self, sample_pdf, tmp_path):
        from src.ui.pages.split_page import SplitPage

        output_dir = str(tmp_path / "split_out")
        result = SplitPage._do_split(
            sample_pdf, "single", None, 1, output_dir
        )

        assert len(result) == 3
        for f in result:
            assert os.path.exists(f)
            reader = pypdf.PdfReader(f)
            assert len(reader.pages) == 1

    def test_split_progress_callback(self, sample_pdf, tmp_path):
        from src.ui.pages.split_page import SplitPage

        calls = []
        output_dir = str(tmp_path / "split_out")
        SplitPage._do_split(
            sample_pdf, "single", None, 1, output_dir,
            progress_callback=lambda c, t: calls.append((c, t)),
        )

        assert len(calls) == 3
        assert calls[-1] == (3, 3)

    def test_parse_page_ranges(self):
        from src.ui.pages.split_page import SplitPage

        result = SplitPage._parse_page_ranges("1-3, 5, 8-10", 10)
        assert result == [[1, 2, 3], [5], [8, 9, 10]]
