"""拆分 PDF 页面"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QTabWidget, QRadioButton, QButtonGroup, QFileDialog,
)
from PySide6.QtCore import Qt
from pathlib import Path

from src.ui.pages.base_page import BasePage
from src.workers.pdf_worker import PDFWorker
from src.utils.validators import validate_page_range


class SplitPage(BasePage):
    """拆分 PDF 功能页面"""

    def __init__(self, parent=None):
        self._mode_tabs: QTabWidget | None = None
        self._range_edit: QLineEdit | None = None
        self._pages_spin: QSpinBox | None = None
        super().__init__(accept_types=[".pdf"], title="拆分 PDF", parent=parent)

    def create_settings_widget(self) -> QWidget | None:
        self._mode_tabs = QTabWidget()

        # 模式1: 按页码范围
        range_widget = QWidget()
        range_layout = QHBoxLayout(range_widget)
        range_layout.setContentsMargins(12, 12, 12, 12)
        range_layout.addWidget(QLabel("页码范围:"))
        self._range_edit = QLineEdit()
        self._range_edit.setPlaceholderText("例如: 1-3, 5, 8-10")
        range_layout.addWidget(self._range_edit)
        self._mode_tabs.addTab(range_widget, "按页码范围")

        # 模式2: 每N页拆分
        n_widget = QWidget()
        n_layout = QHBoxLayout(n_widget)
        n_layout.setContentsMargins(12, 12, 12, 12)
        n_layout.addWidget(QLabel("每"))
        self._pages_spin = QSpinBox()
        self._pages_spin.setRange(1, 9999)
        self._pages_spin.setValue(10)
        n_layout.addWidget(self._pages_spin)
        n_layout.addWidget(QLabel("页拆分为一个文件"))
        n_layout.addStretch()
        self._mode_tabs.addTab(n_widget, "每N页拆分")

        # 模式3: 拆成单页
        single_widget = QWidget()
        single_layout = QHBoxLayout(single_widget)
        single_layout.setContentsMargins(12, 12, 12, 12)
        single_layout.addWidget(QLabel("每页生成一个独立 PDF 文件"))
        single_layout.addStretch()
        self._mode_tabs.addTab(single_widget, "拆成单页")

        return self._mode_tabs

    def on_start(self):
        files = self.get_files()
        if not files:
            self.show_toast("请先选择文件", "warning")
            return

        input_path = files[0]
        mode_index = self._mode_tabs.currentIndex()

        if mode_index == 0:  # 按页码范围
            mode = "range"
            range_str = self._range_edit.text().strip()
            ok, msg = validate_page_range(range_str, 9999)
            if not ok:
                self.show_toast(msg, "warning")
                return
        elif mode_index == 1:  # 每N页
            mode = "every_n"
        else:  # 单页
            mode = "single"

        self._progress.set_status("正在拆分...")
        self._start_btn.setEnabled(False)

        self._worker = PDFWorker(
            self._do_split,
            input_path,
            mode,
            self._range_edit.text().strip() if mode_index == 0 else None,
            self._pages_spin.value() if mode_index == 1 else 1,
            str(Path(input_path).parent / f"{Path(input_path).stem}_split"),
        )
        self._worker.progress.connect(lambda c, t: self._progress.set_progress(c, t))
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @staticmethod
    def _do_split(input_path, mode, range_str, pages_per_split, output_dir, progress_callback=None):
        import pypdf
        from src.utils.file_utils import safe_output_path

        reader = pypdf.PdfReader(input_path)
        total = len(reader.pages)
        stem = Path(input_path).stem

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_files = []

        if mode == "range":
            from src.ui.pages.split_page import SplitPage
            groups = SplitPage._parse_page_ranges(range_str, total)
        elif mode == "every_n":
            groups = [
                list(range(i + 1, min(i + pages_per_split, total) + 1))
                for i in range(0, total, pages_per_split)
            ]
        else:
            groups = [[i] for i in range(1, total + 1)]

        for idx, pages in enumerate(groups):
            writer = pypdf.PdfWriter()
            for p in pages:
                writer.add_page(reader.pages[p - 1])

            # 按页码范围命名
            if len(pages) == 1:
                out_name = f"{stem}_p{pages[0]:04d}.pdf"
            else:
                out_name = f"{stem}_p{pages[0]:04d}-{pages[-1]:04d}.pdf"

            out_path = safe_output_path(str(Path(output_dir) / out_name))
            writer.write(out_path)
            writer.close()
            output_files.append(out_path)

            if progress_callback:
                progress_callback(idx + 1, len(groups))

        return output_files

    @staticmethod
    def _parse_page_ranges(range_str, max_page):
        groups = []
        for part in range_str.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-")
                start, end = int(start), int(end)
                groups.append(list(range(start, end + 1)))
            else:
                groups.append([int(part)])
        return groups

    def _on_finished(self, result):
        self._start_btn.setEnabled(True)
        self._output_dir = str(Path(result[0]).parent) if result else ""
        self._progress.set_status(f"✅ 拆分完成! 共生成 {len(result)} 个文件")
        self._open_dir_btn.setVisible(True)

    def _on_error(self, msg):
        self._start_btn.setEnabled(True)
        self._progress.set_status(f"❌ 拆分失败: {msg}")
