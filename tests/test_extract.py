"""从 PDF 提取图片功能测试"""

import os
from pathlib import Path

import pytest


class TestExtractImages:
    """测试从 PDF 中提取图片"""

    @staticmethod
    def _make_pdf_with_image(tmp_path):
        """创建一个包含嵌入图片的测试 PDF"""
        import fitz
        from PIL import Image
        import io

        # 先生成一张图片
        img_path = str(tmp_path / "embedded.png")
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img.save(img_path)

        # 创建 PDF 并插入图片
        pdf_path = str(tmp_path / "with_image.pdf")
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.insert_image(fitz.Rect(50, 50, 200, 200), filename=img_path)
        doc.save(pdf_path)
        doc.close()
        return pdf_path

    def test_extract_original_format(self, tmp_path):
        from src.ui.pages.extract_page import ExtractPage

        pdf_path = self._make_pdf_with_image(tmp_path)
        output_dir = str(tmp_path / "extracted")
        result = ExtractPage._do_extract(pdf_path, output_dir, "original")

        assert len(result) >= 1
        for item in result:
            assert os.path.exists(item["path"])
            assert item["size"] > 0

    def test_extract_to_png(self, tmp_path):
        from src.ui.pages.extract_page import ExtractPage

        pdf_path = self._make_pdf_with_image(tmp_path)
        output_dir = str(tmp_path / "extracted")
        result = ExtractPage._do_extract(pdf_path, output_dir, "png")

        assert len(result) >= 1
        for item in result:
            assert item["path"].endswith(".png")

    def test_extract_to_jpg(self, tmp_path):
        from src.ui.pages.extract_page import ExtractPage

        pdf_path = self._make_pdf_with_image(tmp_path)
        output_dir = str(tmp_path / "extracted")
        result = ExtractPage._do_extract(pdf_path, output_dir, "jpg")

        assert len(result) >= 1
        for item in result:
            assert item["path"].endswith(".jpg")

    def test_extract_progress_callback(self, tmp_path):
        from src.ui.pages.extract_page import ExtractPage

        pdf_path = self._make_pdf_with_image(tmp_path)
        calls = []
        output_dir = str(tmp_path / "extracted")
        ExtractPage._do_extract(
            pdf_path, output_dir, "original",
            progress_callback=lambda c, t: calls.append((c, t)),
        )

        assert len(calls) >= 1

    def test_extract_naming(self, tmp_path):
        from src.ui.pages.extract_page import ExtractPage

        pdf_path = self._make_pdf_with_image(tmp_path)
        output_dir = str(tmp_path / "extracted")
        result = ExtractPage._do_extract(pdf_path, output_dir, "original")

        for item in result:
            name = Path(item["path"]).name
            assert name.startswith("image_")
            assert name.endswith((".png", ".jpg", ".jpeg", ".bmp"))
