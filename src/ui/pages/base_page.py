"""功能页面基类 — 所有功能页面复用的布局模式"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QScrollArea, QFrame,
)
from PySide6.QtCore import Qt, Signal

from src.ui.components.drop_zone import DropZone
from src.ui.components.file_list import FileListWidget
from src.ui.components.progress_bar import ProgressBarWidget
from src.ui.components.toast import Toast


class BasePage(QWidget):
    """
    功能页面基类

    布局结构：
    ┌─────────────────────────┐
    │  可滚动内容区             │
    │  ├ 拖拽上传区 DropZone   │
    │  ├ 文件列表              │
    │  └ 参数设置面板          │
    ├─────────────────────────┤
    │  进度条 (固定)           │
    │  操作按钮 (固定)         │
    └─────────────────────────┘
    """

    def __init__(
        self,
        accept_types: list[str] | None = None,
        title: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self._accept_types = accept_types or [".pdf"]

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- 可滚动内容区 ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(24, 24, 24, 16)
        content_layout.setSpacing(16)

        # 1. 拖拽上传区
        self._drop_zone = DropZone(accept_types=self._accept_types)
        self._drop_zone.files_dropped.connect(self._on_files_dropped)
        self._drop_zone.clicked.connect(self._on_drop_zone_clicked)
        content_layout.addWidget(self._drop_zone)

        # 2. 文件列表
        self._file_list = FileListWidget()
        self._file_list.files_changed.connect(self._on_files_changed)
        content_layout.addWidget(self._file_list)

        # 3. 参数设置面板（子类提供）
        settings_widget = self.create_settings_widget()
        if settings_widget:
            content_layout.addWidget(settings_widget)

        content_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        # ---- 固定底部栏 ----
        bottom_bar = QFrame()
        bottom_bar.setObjectName("bottomBar")
        bottom_layout = QVBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(24, 12, 24, 16)
        bottom_layout.setSpacing(10)

        # 进度条
        self._progress = ProgressBarWidget()
        bottom_layout.addWidget(self._progress)

        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self._start_btn = QPushButton("▶  开始处理")
        self._start_btn.setEnabled(False)
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.setFixedHeight(42)
        self._start_btn.setMinimumWidth(160)
        self._start_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #2563EB; color: white;"
            "  border: none; border-radius: 8px;"
            "  padding: 0 28px; font-size: 14px; font-weight: 600;"
            "  letter-spacing: 1px;"
            "}"
            "QPushButton:hover { background-color: #1D4ED8; }"
            "QPushButton:pressed { background-color: #1E40AF; }"
            "QPushButton:disabled { background-color: #CBD5E1; color: #94A3B8; }"
        )
        self._start_btn.clicked.connect(self._on_start)
        btn_layout.addWidget(self._start_btn)

        self._open_dir_btn = QPushButton("📂  打开输出目录")
        self._open_dir_btn.setVisible(False)
        self._open_dir_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_dir_btn.setFixedHeight(42)
        self._open_dir_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: white; color: #2563EB;"
            "  border: 1.5px solid #CBD5E1; border-radius: 8px;"
            "  padding: 0 20px; font-size: 13px; font-weight: 500;"
            "}"
            "QPushButton:hover { border-color: #2563EB; background-color: #EFF6FF; }"
        )
        self._open_dir_btn.clicked.connect(self._on_open_output_dir)
        btn_layout.addWidget(self._open_dir_btn)

        btn_layout.addStretch()
        bottom_layout.addLayout(btn_layout)

        main_layout.addWidget(bottom_bar)

        self._output_dir: str = ""

    # ---- 子类可重写的方法 ----

    def create_settings_widget(self) -> QWidget | None:
        """创建参数设置面板，子类重写此方法"""
        return None

    def get_file_dialog_filter(self) -> str:
        """文件选择对话框的过滤器"""
        return "PDF 文件 (*.pdf)"

    def on_files_added(self, paths: list[str]):
        """文件添加后的回调，子类可重写"""
        pass

    def on_start(self):
        """开始处理，子类必须重写"""
        raise NotImplementedError

    def validate_before_start(self) -> tuple[bool, str]:
        """开始前校验，子类可重写返回 (ok, error_msg)"""
        if self._file_list.file_count() == 0:
            return False, "请先选择文件"
        return True, ""

    # ---- 公开接口 ----

    def get_files(self) -> list[str]:
        return self._file_list.get_files()

    def get_output_dir(self) -> str:
        return self._output_dir

    def show_toast(self, message: str, toast_type: str = "info"):
        toast = Toast(message, toast_type=toast_type, parent=self.window())
        toast.show_at(self.window())

    # ---- 内部方法 ----

    def _on_files_dropped(self, paths: list[str]):
        self._file_list.add_files(paths)
        self.on_files_added(paths)

    def _on_drop_zone_clicked(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择文件", "", self.get_file_dialog_filter()
        )
        if files:
            self._file_list.add_files(files)
            self.on_files_added(files)

    def _on_files_changed(self, files: list[str]):
        self._start_btn.setEnabled(len(files) > 0)

    def _on_start(self):
        ok, msg = self.validate_before_start()
        if not ok:
            self.show_toast(msg, "warning")
            return
        self.on_start()

    def _on_open_output_dir(self):
        if self._output_dir:
            import subprocess
            subprocess.Popen(["explorer", self._output_dir])
