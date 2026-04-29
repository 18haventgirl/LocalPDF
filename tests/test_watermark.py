"""加水印功能测试"""

import os
from pathlib import Path

import pytest


class TestWatermarkLogic:
    """测试加水印核心逻辑"""

    def test_text_watermark_center(self, sample_pdf, tmp_path):
        from src.ui.pages.watermark_page import WatermarkPage

        output = str(tmp_path / "watermarked.pdf")
        result = WatermarkPage._do_text_watermark(
            sample_pdf, output,
            text="CONFIDENTIAL", font_size=50,
            color=(0.8, 0.8, 0.8), opacity=0.3,
            angle=45, mode="center",
        )

        assert result is True
        assert os.path.exists(output)
        assert os.path.getsize(output) > 0

    def test_text_watermark_tile(self, sample_pdf, tmp_path):
        from src.ui.pages.watermark_page import WatermarkPage

        output = str(tmp_path / "watermarked.pdf")
        result = WatermarkPage._do_text_watermark(
            sample_pdf, output,
            text="DRAFT", font_size=30,
            color=(0.9, 0.9, 0.9), opacity=0.2,
            angle=30, mode="tile",
        )

        assert result is True
        assert os.path.exists(output)

    def test_text_watermark_corner(self, sample_pdf, tmp_path):
        from src.ui.pages.watermark_page import WatermarkPage

        output = str(tmp_path / "watermarked.pdf")
        result = WatermarkPage._do_text_watermark(
            sample_pdf, output,
            text="SAMPLE", font_size=40,
            color=(0.7, 0.7, 0.7), opacity=0.5,
            angle=0, mode="corner",
        )

        assert result is True

    def test_text_watermark_progress(self, sample_pdf, tmp_path):
        from src.ui.pages.watermark_page import WatermarkPage

        calls = []
        output = str(tmp_path / "watermarked.pdf")
        WatermarkPage._do_text_watermark(
            sample_pdf, output,
            text="TEST", font_size=50,
            color=(0.8, 0.8, 0.8), opacity=0.3,
            angle=45, mode="center",
            progress_callback=lambda c, t: calls.append((c, t)),
        )

        assert len(calls) == 3

    def test_image_watermark_center(self, sample_pdf, sample_image, tmp_path):
        from src.ui.pages.watermark_page import WatermarkPage

        output = str(tmp_path / "watermarked.pdf")
        result = WatermarkPage._do_image_watermark(
            sample_pdf, output,
            wm_image_path=sample_image,
            scale=0.5, opacity=0.3, angle=0, mode="center",
        )

        assert result is True
        assert os.path.exists(output)

    def test_image_watermark_tile(self, sample_pdf, sample_image, tmp_path):
        from src.ui.pages.watermark_page import WatermarkPage

        output = str(tmp_path / "watermarked.pdf")
        result = WatermarkPage._do_image_watermark(
            sample_pdf, output,
            wm_image_path=sample_image,
            scale=0.3, opacity=0.2, angle=45, mode="tile",
        )

        assert result is True
