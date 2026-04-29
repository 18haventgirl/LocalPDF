"""PDF ↔ 图片转换功能测试"""

import os
from pathlib import Path

import pytest


class TestPdfToImages:
    """测试 PDF → 图片 转换"""

    def test_pdf_to_png(self, sample_pdf, tmp_path):
        from src.ui.pages.convert_page import ConvertPage

        output_dir = str(tmp_path / "images")
        result = ConvertPage._do_pdf_to_images(
            sample_pdf, output_dir, "png", 200, 90
        )

        assert len(result) == 3
        for f in result:
            assert os.path.exists(f)
            assert f.endswith(".png")

    def test_pdf_to_jpg(self, sample_pdf, tmp_path):
        from src.ui.pages.convert_page import ConvertPage

        output_dir = str(tmp_path / "images")
        result = ConvertPage._do_pdf_to_images(
            sample_pdf, output_dir, "jpg", 150, 85
        )

        assert len(result) == 3
        for f in result:
            assert f.endswith(".jpg")
            assert os.path.getsize(f) > 0

    def test_pdf_to_images_progress(self, sample_pdf, tmp_path):
        from src.ui.pages.convert_page import ConvertPage

        calls = []
        output_dir = str(tmp_path / "images")
        ConvertPage._do_pdf_to_images(
            sample_pdf, output_dir, "png", 72, 90,
            progress_callback=lambda c, t: calls.append((c, t)),
        )

        assert len(calls) == 3
        assert calls[-1] == (3, 3)

    def test_pdf_to_images_naming(self, sample_pdf, tmp_path):
        from src.ui.pages.convert_page import ConvertPage

        output_dir = str(tmp_path / "images")
        result = ConvertPage._do_pdf_to_images(
            sample_pdf, output_dir, "png", 72, 90
        )

        for i, f in enumerate(result):
            assert f"page_{i + 1:04d}" in Path(f).name


class TestImagesToPdf:
    """测试 图片 → PDF 转换"""

    def test_single_image_to_pdf(self, sample_image, tmp_path):
        from src.ui.pages.convert_page import ConvertPage

        output = str(tmp_path / "output.pdf")
        result = ConvertPage._do_images_to_pdf([sample_image], output, "auto")

        assert result == output
        assert os.path.exists(output)

    def test_multiple_images_to_pdf(self, tmp_path):
        from src.ui.pages.convert_page import ConvertPage
        from PIL import Image

        paths = []
        for i in range(3):
            img_path = str(tmp_path / f"img_{i}.png")
            img = Image.new("RGB", (200, 300), color=(i * 50, 100, 200))
            img.save(img_path)
            paths.append(img_path)

        output = str(tmp_path / "output.pdf")
        result = ConvertPage._do_images_to_pdf(paths, output, "auto")

        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_images_to_pdf_a4(self, sample_image, tmp_path):
        from src.ui.pages.convert_page import ConvertPage

        output = str(tmp_path / "output.pdf")
        result = ConvertPage._do_images_to_pdf([sample_image], output, "A4")

        assert os.path.exists(output)

    def test_images_to_pdf_progress(self, tmp_path):
        from src.ui.pages.convert_page import ConvertPage
        from PIL import Image

        paths = []
        for i in range(2):
            img_path = str(tmp_path / f"img_{i}.png")
            Image.new("RGB", (100, 100)).save(img_path)
            paths.append(img_path)

        calls = []
        output = str(tmp_path / "output.pdf")
        ConvertPage._do_images_to_pdf(
            paths, output, "auto",
            progress_callback=lambda c, t: calls.append((c, t)),
        )

        assert len(calls) == 2
