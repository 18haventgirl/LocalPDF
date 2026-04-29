"""合并 PDF 页面"""

from pathlib import Path

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QFileDialog

from src.ui.pages.base_page import BasePage
from src.workers.pdf_worker import PDFWorker
from src.utils.file_utils import safe_output_path


class MergePage(BasePage):
    """合并 PDF 功能页面"""

    def __init__(self, parent=None):
        self._output_path_edit: QLineEdit | None = None
        super().__init__(accept_types=[".pdf"], title="合并 PDF", parent=parent)

    def create_settings_widget(self) -> QWidget | None:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("输出文件名:")
        label.setStyleSheet("font-size: 13px; color: #334155;")
        layout.addWidget(label)

        self._output_path_edit = QLineEdit()
        self._output_path_edit.setPlaceholderText("自动生成或手动输入")
        layout.addWidget(self._output_path_edit)

        return widget

    def on_files_added(self, paths: list[str]):
        # 自动生成输出文件名
        files = self.get_files()
        if len(files) >= 2 and self._output_path_edit.text() == "":
            stems = [Path(f).stem for f in files[:3]]
            name = "_".join(stems) + "_merged.pdf"
            output = safe_output_path(str(Path(files[0]).parent / name))
            self._output_path_edit.setText(output)

    def on_start(self):
        files = self.get_files()
        if len(files) < 2:
            self.show_toast("请至少选择两个 PDF 文件", "warning")
            return

        # 确定输出路径
        output_path = self._output_path_edit.text().strip()
        if not output_path:
            stems = [Path(f).stem for f in files[:3]]
            name = "_".join(stems) + "_merged.pdf"
            output_path = safe_output_path(str(Path(files[0]).parent / name))
            self._output_path_edit.setText(output_path)

        self._output_dir = str(Path(output_path).parent)

        # 启动后台线程
        self._start_btn.setEnabled(False)
        self._progress.set_status("正在合并...")
        self._worker = PDFWorker(self._do_merge, files, output_path)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @staticmethod
    def _do_merge(file_paths, output_path, progress_callback=None):
        import pypdf
        from src.core.errors import EncryptedPDFError

        writer = pypdf.PdfWriter()
        total_pages = 0

        for path in file_paths:
            reader = pypdf.PdfReader(path)
            if reader.is_encrypted:
                raise EncryptedPDFError(f"文件已加密: {path}")
            total_pages += len(reader.pages)

        current = 0
        for path in file_paths:
            reader = pypdf.PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)
                current += 1
                if progress_callback:
                    progress_callback(current, total_pages)

        writer.write(output_path)
        writer.close()
        return True

    def _on_progress(self, current, total):
        self._progress.set_progress(current, total)

    def _on_finished(self, result):
        self._start_btn.setEnabled(True)
        file_count = self._file_list.file_count()
        self._progress.set_status(f"✅ 已将 {file_count} 个 PDF 合并为 1 个文件")
        self._open_dir_btn.setVisible(True)

    def _on_error(self, msg):
        self._start_btn.setEnabled(True)
        self._progress.set_status(f"❌ 合并失败: {msg}")
