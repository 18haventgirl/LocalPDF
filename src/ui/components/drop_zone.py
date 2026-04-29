"""通用拖拽上传区域组件"""

import os
from pathlib import Path

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent, QMouseEvent


class DropZone(QFrame):
    """通用拖拽上传区域"""

    files_dropped = Signal(list)   # 发射文件路径列表
    clicked = Signal()             # 点击打开文件选择器

    def __init__(
        self,
        accept_types: list[str] | None = None,
        multi: bool = True,
        parent=None,
    ):
        """
        Args:
            accept_types: 允许的文件后缀, 如 [".pdf"] 或 [".png", ".jpg"]
            multi: 是否允许多文件
        """
        super().__init__(parent)
        self.setObjectName("dropzone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(200)

        self.accept_types = [t.lower() for t in accept_types] if accept_types else None
        self.multi = multi

        # 布局：图标 + 提示文字
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addStretch()

        self._icon_label = QLabel("📄")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet("font-size: 48px; border: none;")
        layout.addWidget(self._icon_label)

        self._text_label = QLabel("拖拽文件到这里\n或点击选择文件")
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text_label.setStyleSheet(
            "color: #64748B; font-size: 15px; border: none;"
        )
        layout.addWidget(self._text_label)

        if self.accept_types:
            ext_text = "、".join(self.accept_types)
            self._hint_label = QLabel(f"支持格式: {ext_text}")
            self._hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._hint_label.setStyleSheet(
                "color: #94A3B8; font-size: 12px; border: none;"
            )
            layout.addWidget(self._hint_label)

        layout.addStretch()

    # ---- 拖拽事件 ----

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # 检查是否有至少一个匹配类型的文件
            for url in event.mimeData().urls():
                if self._validate_file(url.toLocalFile()):
                    event.acceptProposedAction()
                    self.setProperty("dragActive", True)
                    self.style().polish(self)
                    return

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.setProperty("dragActive", False)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragActive", False)
        self.style().polish(self)

        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if self._validate_file(path):
                files.append(path)

        if not self.multi and len(files) > 1:
            files = files[:1]

        if files:
            self.files_dropped.emit(files)

    # ---- 点击事件 ----

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    # ---- 内部方法 ----

    def _validate_file(self, path: str) -> bool:
        """验证文件类型"""
        if not os.path.isfile(path):
            return False
        if self.accept_types:
            return Path(path).suffix.lower() in self.accept_types
        return True
