"""测试公共 fixtures"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir(tmp_path):
    """提供临时目录"""
    return str(tmp_path)


@pytest.fixture
def sample_pdf(tmp_path):
    """创建一个简单的测试 PDF 文件（3 页）"""
    import fitz

    pdf_path = str(tmp_path / "test_sample.pdf")
    doc = fitz.open()

    for i in range(3):
        page = doc.new_page(width=595, height=842)  # A4
        text = f"Test Page {i + 1}"
        shape = page.new_shape()
        shape.insert_text(
            fitz.Point(100, 100), text,
            fontsize=20, color=(0, 0, 0),
        )
        shape.commit()

    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def sample_pdf_small(tmp_path):
    """创建一个单页测试 PDF"""
    import fitz

    pdf_path = str(tmp_path / "test_single.pdf")
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    shape = page.new_shape()
    shape.insert_text(fitz.Point(100, 100), "Single Page", fontsize=20)
    shape.commit()
    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def sample_image(tmp_path):
    """创建一个测试 PNG 图片"""
    from PIL import Image

    img_path = str(tmp_path / "test_image.png")
    img = Image.new("RGB", (200, 300), color=(255, 0, 0))
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_pdfs(tmp_path):
    """创建多个测试 PDF 文件"""
    import fitz

    paths = []
    for idx in range(3):
        pdf_path = str(tmp_path / f"file_{idx + 1}.pdf")
        doc = fitz.open()
        for p in range(2):
            page = doc.new_page(width=595, height=842)
            shape = page.new_shape()
            shape.insert_text(
                fitz.Point(100, 100),
                f"File {idx + 1} - Page {p + 1}",
                fontsize=20,
            )
            shape.commit()
        doc.save(pdf_path)
        doc.close()
        paths.append(pdf_path)

    return paths
