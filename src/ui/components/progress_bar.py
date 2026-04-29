"""通用进度条组件"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt


class ProgressBarWidget(QWidget):
    """带文字说明的进度条组件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)

        # 状态文字行
        info_layout = QHBoxLayout()
        self._status_label = QLabel("就绪")
        self._status_label.setStyleSheet("color: #64748B; font-size: 12px;")
        info_layout.addWidget(self._status_label)

        info_layout.addStretch()

        self._percent_label = QLabel("")
        self._percent_label.setStyleSheet("color: #64748B; font-size: 12px;")
        info_layout.addWidget(self._percent_label)

        layout.addLayout(info_layout)

        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)

    def set_status(self, text: str):
        """设置状态文字"""
        self._status_label.setText(text)

    def set_progress(self, current: int, total: int):
        """设置进度 (current / total)"""
        if total > 0:
            percent = int(current / total * 100)
            self._progress_bar.setValue(percent)
            self._percent_label.setText(f"{current}/{total} ({percent}%)")
        else:
            self._progress_bar.setValue(0)
            self._percent_label.setText("")

    def reset(self):
        """重置进度条"""
        self._progress_bar.setValue(0)
        self._status_label.setText("就绪")
        self._percent_label.setText("")

    def set_indeterminate(self, text: str = "处理中..."):
        """设置为不确定进度模式"""
        self._progress_bar.setRange(0, 0)
        self._status_label.setText(text)
        self._percent_label.setText("")

    def set_determinate(self):
        """恢复为确定进度模式"""
        self._progress_bar.setRange(0, 100)
