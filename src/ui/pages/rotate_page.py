"""旋转 PDF 页面"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QGroupBox, QRadioButton, QButtonGroup,
)
from PySide6.QtCore import Qt

from src.ui.pages.base_page import BasePage
from src.workers.pdf_worker import PDFWorker
from src.utils.file_utils import safe_output_path
from src.utils.validators import validate_page_range


class RotatePage(BasePage):
    """旋转 PDF 功能页面"""

    def __init__(self, parent=None):
        self._angle_combo: QComboBox | None = None
        self._all_pages_radio: QRadioButton | None = None
        self._range_radio: QRadioButton | None = None
        self._range_edit: QLineEdit | None = None
        self._page_group: QButtonGroup | None = None
        super().__init__(accept_types=[".pdf"], title="旋转 PDF", parent=parent)

    def create_settings_widget(self) -> QWidget | None:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 旋转角度
        angle_row = QHBoxLayout()
        angle_row.addWidget(QLabel("旋转角度:"))
        self._angle_combo = QComboBox()
        self._angle_combo.addItems(["90° 顺时针", "180°", "270° 顺时针 (90° 逆时针)"])
        self._angle_combo.setCurrentIndex(0)
        angle_row.addWidget(self._angle_combo)
        angle_row.addStretch()
        layout.addLayout(angle_row)

        # 应用范围
        scope_group = QGroupBox("应用范围")
        scope_layout = QVBoxLayout(scope_group)

        self._all_pages_radio = QRadioButton("全部页面")
        self._all_pages_radio.setChecked(True)
        scope_layout.addWidget(self._all_pages_radio)

        range_row = QHBoxLayout()
        self._range_radio = QRadioButton("指定页码:")
        self._range_edit = QLineEdit()
        self._range_edit.setPlaceholderText("例如: 1-3, 5, 8-10")
        self._range_edit.setEnabled(False)
        range_row.addWidget(self._range_radio)
        range_row.addWidget(self._range_edit)
        scope_layout.addLayout(range_row)

        self._page_group = QButtonGroup()
        self._page_group.addButton(self._all_pages_radio, 0)
        self._page_group.addButton(self._range_radio, 1)
        self._page_group.idToggled.connect(self._on_scope_changed)

        layout.addWidget(scope_group)
        return widget

    def _on_scope_changed(self, _id: int, checked: bool):
        if checked:
            is_range = self._range_radio.isChecked()
            self._range_edit.setEnabled(is_range)

    def on_start(self):
        files = self.get_files()
        if not files:
            self.show_toast("请先选择文件", "warning")
            return

        input_path = files[0]

        # 确定角度
        angle_map = {0: 90, 1: 180, 2: 270}
        angle = angle_map[self._angle_combo.currentIndex()]

        # 确定页码范围
        if self._all_pages_radio.isChecked():
            pages = "all"
        else:
            pages = self._range_edit.text().strip()
            if not pages:
                self.show_toast("请输入页码范围", "warning")
                return
            # 校验格式
            try:
                import pypdf
                reader = pypdf.PdfReader(input_path)
                ok, msg = validate_page_range(pages, len(reader.pages))
                if not ok:
                    self.show_toast(msg, "warning")
                    return
            except Exception as e:
                self.show_toast(f"无法读取 PDF: {e}", "error")
                return

        p = Path(input_path)
        output_path = safe_output_path(
            str(p.parent / f"{p.stem}_rotated{p.suffix}")
        )
        self._output_dir = str(p.parent)

        self._start_btn.setEnabled(False)
        self._progress.set_status("正在旋转...")
        self._progress.set_indeterminate("正在旋转...")

        self._worker = PDFWorker(
            self._do_rotate, input_path, output_path, angle, pages,
        )
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @staticmethod
    def _do_rotate(input_path, output_path, angle, pages, progress_callback=None):
        import pypdf
        from src.utils.validators import validate_page_range

        reader = pypdf.PdfReader(input_path)
        writer = pypdf.PdfWriter()
        total = len(reader.pages)

        target_pages = set()
        if pages == "all":
            target_pages = set(range(total))
        else:
            for part in pages.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = part.split("-")
                    for i in range(int(start), int(end) + 1):
                        target_pages.add(i - 1)
                else:
                    target_pages.add(int(part) - 1)

        for i in range(total):
            page = reader.pages[i]
            if i in target_pages:
                page.rotate(angle)
            writer.add_page(page)

        writer.write(output_path)
        writer.close()
        return True

    def _on_finished(self, result):
        self._start_btn.setEnabled(True)
        self._progress.set_determinate()
        self._progress.set_status("✅ 旋转完成!")
        self._open_dir_btn.setVisible(True)

    def _on_error(self, msg):
        self._start_btn.setEnabled(True)
        self._progress.set_determinate()
        self._progress.set_status(f"❌ 旋转失败: {msg}")
