"""PDF ↔ 图片 转换页面"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QTabWidget, QFileDialog,
)
from PySide6.QtCore import Qt

from src.ui.pages.base_page import BasePage
from src.ui.components.drop_zone import DropZone
from src.workers.pdf_worker import PDFWorker
from src.utils.file_utils import safe_output_path, get_file_size_str


class ConvertPage(BasePage):
    """PDF ↔ 图片 互转功能页面"""

    # PDF → 图片模式的接受类型
    PDF_ACCEPT = [".pdf"]
    # 图片 → PDF 模式的接受类型
    IMG_ACCEPT = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"]

    def __init__(self, parent=None):
        self._mode_tabs: QTabWidget | None = None
        # PDF → 图片 控件
        self._format_combo: QComboBox | None = None
        self._dpi_combo: QComboBox | None = None
        self._quality_spin: QSpinBox | None = None
        self._quality_label: QLabel | None = None
        # 图片 → PDF 控件
        self._page_size_combo: QComboBox | None = None
        super().__init__(accept_types=self.PDF_ACCEPT, title="转换", parent=parent)

    def create_settings_widget(self) -> QWidget | None:
        self._mode_tabs = QTabWidget()
        self._mode_tabs.currentChanged.connect(self._on_mode_changed)

        # ---- PDF → 图片 ----
        pdf2img_widget = QWidget()
        pdf2img_layout = QHBoxLayout(pdf2img_widget)
        pdf2img_layout.setContentsMargins(12, 12, 12, 12)
        pdf2img_layout.setSpacing(16)

        pdf2img_layout.addWidget(QLabel("输出格式:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["PNG", "JPG", "TIFF"])
        self._format_combo.currentTextChanged.connect(self._on_format_changed)
        pdf2img_layout.addWidget(self._format_combo)

        pdf2img_layout.addWidget(QLabel("DPI:"))
        self._dpi_combo = QComboBox()
        self._dpi_combo.addItems(["72", "150", "200", "300"])
        self._dpi_combo.setCurrentText("200")
        pdf2img_layout.addWidget(self._dpi_combo)

        self._quality_label = QLabel("JPG 质量:")
        pdf2img_layout.addWidget(self._quality_label)
        self._quality_spin = QSpinBox()
        self._quality_spin.setRange(1, 100)
        self._quality_spin.setValue(90)
        pdf2img_layout.addWidget(self._quality_spin)
        self._quality_label.setVisible(True)
        self._quality_spin.setVisible(True)

        pdf2img_layout.addStretch()
        self._mode_tabs.addTab(pdf2img_widget, "PDF → 图片")

        # ---- 图片 → PDF ----
        img2pdf_widget = QWidget()
        img2pdf_layout = QHBoxLayout(img2pdf_widget)
        img2pdf_layout.setContentsMargins(12, 12, 12, 12)
        img2pdf_layout.setSpacing(16)

        img2pdf_layout.addWidget(QLabel("页面大小:"))
        self._page_size_combo = QComboBox()
        self._page_size_combo.addItems(["自适应", "A4", "Letter"])
        img2pdf_layout.addWidget(self._page_size_combo)

        img2pdf_layout.addStretch()
        self._mode_tabs.addTab(img2pdf_widget, "图片 → PDF")

        return self._mode_tabs

    def _on_mode_changed(self, index: int):
        """切换模式时更新 DropZone 接受的文件类型"""
        if index == 0:
            self._drop_zone.accept_types = [t.lower() for t in self.PDF_ACCEPT]
            self._drop_zone._text_label.setText("拖拽 PDF 文件到这里\n或点击选择文件")
        else:
            self._drop_zone.accept_types = [t.lower() for t in self.IMG_ACCEPT]
            self._drop_zone._text_label.setText("拖拽图片文件到这里\n或点击选择文件")
        # 更新格式提示
        if hasattr(self._drop_zone, '_hint_label'):
            ext_text = "、".join(self._drop_zone.accept_types)
            self._drop_zone._hint_label.setText(f"支持格式: {ext_text}")

    def _on_format_changed(self, text: str):
        """切换输出格式时显示/隐藏 JPG 质量选项"""
        is_jpg = text == "JPG"
        self._quality_label.setVisible(is_jpg)
        self._quality_spin.setVisible(is_jpg)

    def get_file_dialog_filter(self) -> str:
        if self._mode_tabs and self._mode_tabs.currentIndex() == 1:
            return "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp)"
        return "PDF 文件 (*.pdf)"

    def on_start(self):
        files = self.get_files()
        if not files:
            self.show_toast("请先选择文件", "warning")
            return

        mode = self._mode_tabs.currentIndex()

        if mode == 0:
            self._start_pdf_to_images(files)
        else:
            self._start_images_to_pdf(files)

    def _start_pdf_to_images(self, files: list[str]):
        input_path = files[0]
        p = Path(input_path)
        output_dir = str(p.parent / f"{p.stem}_images")
        self._output_dir = output_dir

        fmt = self._format_combo.currentText().lower()
        dpi = int(self._dpi_combo.currentText())
        quality = self._quality_spin.value()

        self._start_btn.setEnabled(False)
        self._progress.set_status("正在转换...")

        self._worker = PDFWorker(
            self._do_pdf_to_images,
            input_path, output_dir, fmt, dpi, quality,
        )
        self._worker.progress.connect(lambda c, t: self._progress.set_progress(c, t))
        self._worker.finished.connect(self._on_finished_images)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _start_images_to_pdf(self, files: list[str]):
        p = Path(files[0])
        output_path = safe_output_path(str(p.parent / "merged_images.pdf"))
        self._output_dir = str(p.parent)

        size_map = {"自适应": "auto", "A4": "A4", "Letter": "Letter"}
        page_size = size_map[self._page_size_combo.currentText()]

        self._start_btn.setEnabled(False)
        self._progress.set_status("正在转换...")

        self._worker = PDFWorker(
            self._do_images_to_pdf,
            files, output_path, page_size,
        )
        self._worker.progress.connect(lambda c, t: self._progress.set_progress(c, t))
        self._worker.finished.connect(self._on_finished_pdf)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @staticmethod
    def _do_pdf_to_images(input_path, output_dir, fmt, dpi, quality, progress_callback=None):
        import fitz

        doc = fitz.open(input_path)
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        stem = Path(input_path).stem
        output_files = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=matrix)

            out_name = f"{stem}_page_{page_num + 1:04d}.{fmt}"
            out_path = str(Path(output_dir) / out_name)

            if fmt == "jpg":
                pix.save(out_path, jpg_quality=quality)
            else:
                pix.save(out_path)

            output_files.append(out_path)
            if progress_callback:
                progress_callback(page_num + 1, len(doc))

        doc.close()
        return output_files

    @staticmethod
    def _do_images_to_pdf(image_paths, output_path, page_size, progress_callback=None):
        import fitz

        doc = fitz.open()

        for idx, img_path in enumerate(image_paths):
            img_doc = fitz.open(img_path)
            pdfbytes = img_doc.convert_to_pdf()
            img_doc.close()

            img_pdf = fitz.open("pdf", pdfbytes)

            if page_size == "A4":
                a4 = fitz.paper_rect("a4")
                page = doc.new_page(width=a4.width, height=a4.height)
            elif page_size == "Letter":
                letter = fitz.paper_rect("letter")
                page = doc.new_page(width=letter.width, height=letter.height)
            else:
                src = img_pdf[0].rect
                page = doc.new_page(width=src.width, height=src.height)

            page.show_pdf_page(page.rect, img_pdf, 0)
            img_pdf.close()

            if progress_callback:
                progress_callback(idx + 1, len(image_paths))

        doc.save(output_path)
        doc.close()
        return output_path

    def _on_finished_images(self, result):
        self._start_btn.setEnabled(True)
        self._progress.set_status(f"✅ 转换完成! 共生成 {len(result)} 张图片")
        self._open_dir_btn.setVisible(True)

    def _on_finished_pdf(self, result):
        self._start_btn.setEnabled(True)
        self._progress.set_status("✅ 图片转 PDF 完成!")
        self._open_dir_btn.setVisible(True)

    def _on_error(self, msg):
        self._start_btn.setEnabled(True)
        self._progress.set_status(f"❌ 转换失败: {msg}")
