"""加水印页面"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QTabWidget, QPushButton,
    QFileDialog, QColorDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from src.ui.pages.base_page import BasePage
from src.workers.pdf_worker import PDFWorker
from src.utils.file_utils import safe_output_path


class WatermarkPage(BasePage):
    """加水印功能页面"""

    def __init__(self, parent=None):
        self._color: tuple[float, float, float] = (0.8, 0.8, 0.8)
        self._wm_type_tabs: QTabWidget | None = None
        # 文字水印控件
        self._text_edit: QLineEdit | None = None
        self._font_size_spin: QSpinBox | None = None
        self._opacity_spin: QDoubleSpinBox | None = None
        self._angle_spin: QSpinBox | None = None
        self._mode_combo: QComboBox | None = None
        self._color_btn: QPushButton | None = None
        # 图片水印控件
        self._wm_image_path: str = ""
        self._wm_image_label: QLabel | None = None
        self._img_opacity_spin: QDoubleSpinBox | None = None
        self._img_scale_spin: QSpinBox | None = None
        self._img_angle_spin: QSpinBox | None = None
        self._img_mode_combo: QComboBox | None = None

        super().__init__(accept_types=[".pdf"], title="加水印", parent=parent)

    def create_settings_widget(self) -> QWidget | None:
        self._wm_type_tabs = QTabWidget()

        # ========== 文字水印 ==========
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(12, 12, 12, 12)
        text_layout.setSpacing(10)

        # 水印文字
        row = QHBoxLayout()
        row.addWidget(QLabel("水印文字:"))
        self._text_edit = QLineEdit("机密文件")
        self._text_edit.setPlaceholderText("输入水印文字（支持中文）")
        row.addWidget(self._text_edit)
        text_layout.addLayout(row)

        # 字体大小 + 颜色
        row = QHBoxLayout()
        row.addWidget(QLabel("字号:"))
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(6, 200)
        self._font_size_spin.setValue(40)
        self._font_size_spin.setSuffix(" pt")
        row.addWidget(self._font_size_spin)

        row.addWidget(QLabel("颜色:"))
        self._color_btn = QPushButton("  ")
        self._color_btn.setFixedSize(32, 32)
        self._update_color_btn()
        self._color_btn.clicked.connect(self._pick_color)
        row.addWidget(self._color_btn)
        row.addStretch()
        text_layout.addLayout(row)

        # 透明度 + 角度
        row = QHBoxLayout()
        row.addWidget(QLabel("透明度:"))
        self._opacity_spin = QDoubleSpinBox()
        self._opacity_spin.setRange(0.05, 1.0)
        self._opacity_spin.setValue(0.30)
        self._opacity_spin.setSingleStep(0.05)
        self._opacity_spin.setDecimals(2)
        row.addWidget(self._opacity_spin)

        row.addWidget(QLabel("角度:"))
        self._angle_spin = QSpinBox()
        self._angle_spin.setRange(-180, 180)
        self._angle_spin.setValue(45)
        self._angle_spin.setSuffix("°")
        row.addWidget(self._angle_spin)
        row.addStretch()
        text_layout.addLayout(row)

        # 位置模式
        row = QHBoxLayout()
        row.addWidget(QLabel("位置:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["平铺", "居中", "角落"])
        row.addWidget(self._mode_combo)
        row.addStretch()
        text_layout.addLayout(row)

        self._wm_type_tabs.addTab(text_widget, "文字水印")

        # ========== 图片水印 ==========
        img_widget = QWidget()
        img_layout = QVBoxLayout(img_widget)
        img_layout.setContentsMargins(12, 12, 12, 12)
        img_layout.setSpacing(10)

        # 选择图片
        row = QHBoxLayout()
        self._wm_image_label = QLabel("未选择水印图片")
        self._wm_image_label.setStyleSheet("color: #64748B;")
        row.addWidget(self._wm_image_label)
        btn = QPushButton("选择图片")
        btn.clicked.connect(self._pick_wm_image)
        row.addWidget(btn)
        img_layout.addLayout(row)

        # 缩放 + 透明度
        row = QHBoxLayout()
        row.addWidget(QLabel("缩放:"))
        self._img_scale_spin = QSpinBox()
        self._img_scale_spin.setRange(10, 500)
        self._img_scale_spin.setValue(100)
        self._img_scale_spin.setSuffix("%")
        row.addWidget(self._img_scale_spin)

        row.addWidget(QLabel("透明度:"))
        self._img_opacity_spin = QDoubleSpinBox()
        self._img_opacity_spin.setRange(0.05, 1.0)
        self._img_opacity_spin.setValue(0.30)
        self._img_opacity_spin.setSingleStep(0.05)
        self._img_opacity_spin.setDecimals(2)
        row.addWidget(self._img_opacity_spin)
        row.addStretch()
        img_layout.addLayout(row)

        # 角度 + 位置
        row = QHBoxLayout()
        row.addWidget(QLabel("角度:"))
        self._img_angle_spin = QSpinBox()
        self._img_angle_spin.setRange(-180, 180)
        self._img_angle_spin.setValue(0)
        self._img_angle_spin.setSuffix("°")
        row.addWidget(self._img_angle_spin)

        row.addWidget(QLabel("位置:"))
        self._img_mode_combo = QComboBox()
        self._img_mode_combo.addItems(["平铺", "居中", "角落"])
        row.addWidget(self._img_mode_combo)
        row.addStretch()
        img_layout.addLayout(row)

        self._wm_type_tabs.addTab(img_widget, "图片水印")

        return self._wm_type_tabs

    def _update_color_btn(self):
        r, g, b = self._color
        self._color_btn.setStyleSheet(
            f"background-color: rgb({int(r*255)},{int(g*255)},{int(b*255)}); "
            f"border: 1px solid #CBD5E1; border-radius: 4px;"
        )

    def _pick_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self._color = (color.redF(), color.greenF(), color.blueF())
            self._update_color_btn()

    def _pick_wm_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择水印图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if path:
            self._wm_image_path = path
            self._wm_image_label.setText(Path(path).name)

    def on_start(self):
        files = self.get_files()
        if not files:
            self.show_toast("请先选择文件", "warning")
            return

        input_path = files[0]
        p = Path(input_path)
        output_path = safe_output_path(str(p.parent / f"{p.stem}_watermarked{p.suffix}"))
        self._output_dir = str(p.parent)

        wm_type = self._wm_type_tabs.currentIndex()
        self._start_btn.setEnabled(False)
        self._progress.set_status("正在添加水印...")

        if wm_type == 0:
            mode_map = {"平铺": "tile", "居中": "center", "角落": "corner"}
            self._worker = PDFWorker(
                self._do_text_watermark,
                input_path, output_path,
                self._text_edit.text(),
                self._font_size_spin.value(),
                self._color,
                self._opacity_spin.value(),
                self._angle_spin.value(),
                mode_map[self._mode_combo.currentText()],
            )
        else:
            mode_map = {"平铺": "tile", "居中": "center", "角落": "corner"}
            self._worker = PDFWorker(
                self._do_image_watermark,
                input_path, output_path,
                self._wm_image_path,
                self._img_scale_spin.value() / 100.0,
                self._img_opacity_spin.value(),
                self._img_angle_spin.value(),
                mode_map[self._img_mode_combo.currentText()],
            )

        self._worker.progress.connect(lambda c, t: self._progress.set_progress(c, t))
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @staticmethod
    def _do_text_watermark(
        input_path, output_path, text, font_size, color, opacity, angle, mode,
        progress_callback=None,
    ):
        import fitz
        import math

        has_cjk = any(
            '\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4dbf'
            for ch in text
        )
        fontname = "china-s" if has_cjk else "helv"

        doc = fitz.open(input_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect
            use_morph = angle not in (0, 90, 180, 270)

            if mode == "tile":
                x_step = font_size * 6
                y_step = font_size * 3
                for x in range(0, int(rect.width) + int(x_step), int(x_step)):
                    for y in range(0, int(rect.height) + int(y_step), int(y_step)):
                        shape = page.new_shape()
                        pt = fitz.Point(x, y)
                        if use_morph:
                            shape.insert_text(
                                pt, text, fontsize=font_size, color=color,
                                fontname=fontname, fill_opacity=opacity,
                                morph=(pt, fitz.Matrix(angle)),
                            )
                        else:
                            shape.insert_text(
                                pt, text, fontsize=font_size, color=color,
                                fontname=fontname, fill_opacity=opacity,
                                rotate=angle,
                            )
                        shape.commit(overlay=True)

            elif mode == "center":
                center = fitz.Point(rect.width / 2, rect.height / 2)
                shape = page.new_shape()
                if use_morph:
                    shape.insert_text(
                        center, text, fontsize=font_size, color=color,
                        fontname=fontname, fill_opacity=opacity,
                        morph=(center, fitz.Matrix(angle)),
                    )
                else:
                    shape.insert_text(
                        center, text, fontsize=font_size, color=color,
                        fontname=fontname, fill_opacity=opacity,
                        rotate=angle,
                    )
                shape.commit(overlay=True)

            elif mode == "corner":
                margin = max(font_size, 30)
                corner_pt = fitz.Point(margin, rect.height - margin)
                shape = page.new_shape()
                if use_morph:
                    shape.insert_text(
                        corner_pt, text, fontsize=font_size, color=color,
                        fontname=fontname, fill_opacity=opacity,
                        morph=(corner_pt, fitz.Matrix(angle)),
                    )
                else:
                    shape.insert_text(
                        corner_pt, text, fontsize=font_size, color=color,
                        fontname=fontname, fill_opacity=opacity,
                        rotate=angle,
                    )
                shape.commit(overlay=True)

            if progress_callback:
                progress_callback(page_num + 1, len(doc))

        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        return True

    @staticmethod
    def _do_image_watermark(
        input_path, output_path, wm_image_path, scale, opacity, angle, mode,
        progress_callback=None,
    ):
        import fitz
        import math

        doc = fitz.open(input_path)

        img_doc = fitz.open(wm_image_path)
        pdf_bytes = img_doc.convert_to_pdf()
        img_doc.close()
        wm_pdf = fitz.open("pdf", pdf_bytes)
        wm_page_src = wm_pdf[0]

        wm_w = wm_page_src.rect.width * scale
        wm_h = wm_page_src.rect.height * scale

        use_morph = angle not in (0, 90, 180, 270)

        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect

            if mode == "tile":
                x_step = wm_w * 1.5
                y_step = wm_h * 1.5
                for x in range(0, int(rect.width) + int(x_step), int(x_step)):
                    for y in range(0, int(rect.height) + int(y_step), int(y_step)):
                        target = fitz.Rect(x, y, x + wm_w, y + wm_h)
                        if use_morph:
                            # 先创建旋转后的水印页再叠加
                            rot_doc = _rotate_pdf_page(wm_pdf, angle)
                            page.show_pdf_page(target, rot_doc, 0, overlay=True)
                            rot_doc.close()
                        else:
                            page.show_pdf_page(
                                target, wm_pdf, 0, overlay=True,
                                rotate=angle,
                            )

            elif mode == "center":
                cx = (rect.width - wm_w) / 2
                cy = (rect.height - wm_h) / 2
                target = fitz.Rect(cx, cy, cx + wm_w, cy + wm_h)
                if use_morph:
                    rot_doc = _rotate_pdf_page(wm_pdf, angle)
                    page.show_pdf_page(target, rot_doc, 0, overlay=True)
                    rot_doc.close()
                else:
                    page.show_pdf_page(
                        target, wm_pdf, 0, overlay=True, rotate=angle,
                    )

            elif mode == "corner":
                margin = 20
                target = fitz.Rect(
                    rect.width - wm_w - margin,
                    rect.height - wm_h - margin,
                    rect.width - margin,
                    rect.height - margin,
                )
                if use_morph:
                    rot_doc = _rotate_pdf_page(wm_pdf, angle)
                    page.show_pdf_page(target, rot_doc, 0, overlay=True)
                    rot_doc.close()
                else:
                    page.show_pdf_page(
                        target, wm_pdf, 0, overlay=True, rotate=angle,
                    )

            if progress_callback:
                progress_callback(page_num + 1, len(doc))

        wm_pdf.close()
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        return True

    def _on_finished(self, result):
        self._start_btn.setEnabled(True)
        self._progress.set_status("✅ 水印添加完成!")
        self._open_dir_btn.setVisible(True)

    def _on_error(self, msg):
        self._start_btn.setEnabled(True)
        self._progress.set_status(f"❌ 添加水印失败: {msg}")


def _rotate_pdf_page(src_pdf, angle):
    """创建一个旋转后的单页 PDF 副本"""
    import fitz
    out = fitz.open()
    src_page = src_pdf[0]
    w, h = src_page.rect.width, src_page.rect.height
    new_page = out.new_page(width=w, height=h)
    new_page.show_pdf_page(src_page.rect, src_pdf, 0, rotate=angle)
    return out
