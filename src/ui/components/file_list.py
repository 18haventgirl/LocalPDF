"""文件列表组件（支持拖拽排序和删除）"""

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from src.utils.file_utils import get_file_size_str


class FileListWidget(QWidget):
    """文件列表组件，支持拖拽排序和删除"""

    files_changed = Signal(list)  # 文件列表变化时发射

    def __init__(self, show_page_count: bool = True, parent=None):
        super().__init__(parent)
        self._files: list[str] = []
        self._show_page_count = show_page_count

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题行
        header_layout = QHBoxLayout()
        self._title_label = QLabel("已选择的文件")
        self._title_label.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #334155;"
        )
        header_layout.addWidget(self._title_label)

        header_layout.addStretch()

        self._count_label = QLabel("0 个文件")
        self._count_label.setStyleSheet("color: #64748B; font-size: 12px;")
        header_layout.addWidget(self._count_label)

        self._clear_btn = QPushButton("清空")
        self._clear_btn.setStyleSheet(
            "color: #EF4444; background: transparent; border: none; "
            "font-size: 12px; padding: 2px 8px;"
        )
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.clicked.connect(self.clear_files)
        header_layout.addWidget(self._clear_btn)

        layout.addLayout(header_layout)

        # 列表
        self._list_widget = QListWidget()
        self._list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._list_widget.model().rowsMoved.connect(self._on_order_changed)
        layout.addWidget(self._list_widget)

        # 底部操作按钮
        btn_layout = QHBoxLayout()

        self._move_up_btn = QPushButton("↑ 上移")
        self._move_up_btn.setStyleSheet(
            "color: #64748B; background: white; border: 1px solid #E2E8F0; "
            "border-radius: 4px; padding: 4px 12px; font-size: 12px;"
        )
        self._move_up_btn.clicked.connect(self._move_up)
        btn_layout.addWidget(self._move_up_btn)

        self._move_down_btn = QPushButton("↓ 下移")
        self._move_down_btn.setStyleSheet(
            "color: #64748B; background: white; border: 1px solid #E2E8F0; "
            "border-radius: 4px; padding: 4px 12px; font-size: 12px;"
        )
        self._move_down_btn.clicked.connect(self._move_down)
        btn_layout.addWidget(self._move_down_btn)

        btn_layout.addStretch()

        self._remove_btn = QPushButton("🗑 移除选中")
        self._remove_btn.setStyleSheet(
            "color: #EF4444; background: white; border: 1px solid #FCA5A5; "
            "border-radius: 4px; padding: 4px 12px; font-size: 12px;"
        )
        self._remove_btn.clicked.connect(self._remove_selected)
        btn_layout.addWidget(self._remove_btn)

        layout.addLayout(btn_layout)

    # ---- 公开接口 ----

    def add_files(self, paths: list[str]):
        """添加文件到列表（自动去重）"""
        for path in paths:
            abs_path = str(Path(path).resolve())
            if abs_path not in self._files:
                self._files.append(abs_path)
                self._add_list_item(abs_path)
        self._update_info()

    def get_files(self) -> list[str]:
        """获取当前文件列表（按显示顺序）"""
        return list(self._files)

    def clear_files(self):
        """清空所有文件"""
        self._files.clear()
        self._list_widget.clear()
        self._update_info()

    def file_count(self) -> int:
        return len(self._files)

    # ---- 内部方法 ----

    def _add_list_item(self, path: str):
        """向列表添加一个条目"""
        p = Path(path)
        size = get_file_size_str(p.stat().st_size) if p.exists() else "未知"

        text = f"📄  {p.name}    ({size})"
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, path)
        self._list_widget.addItem(item)

    def _update_info(self):
        """更新文件计数和总大小"""
        count = len(self._files)
        total_size = 0
        for f in self._files:
            try:
                total_size += os.path.getsize(f)
            except OSError:
                pass

        self._count_label.setText(
            f"{count} 个文件 | 总大小: {get_file_size_str(total_size)}"
        )
        self.files_changed.emit(self._files)

    def _on_order_changed(self):
        """拖拽排序后同步内部数据"""
        new_order = []
        for i in range(self._list_widget.count()):
            item = self._list_widget.item(i)
            new_order.append(item.data(Qt.ItemDataRole.UserRole))
        self._files = new_order
        self._update_info()

    def _move_up(self):
        """上移选中项"""
        row = self._list_widget.currentRow()
        if row > 0:
            item = self._list_widget.takeItem(row)
            self._list_widget.insertItem(row - 1, item)
            self._list_widget.setCurrentRow(row - 1)
            self._files.insert(row - 1, self._files.pop(row))
            self._update_info()

    def _move_down(self):
        """下移选中项"""
        row = self._list_widget.currentRow()
        if row < self._list_widget.count() - 1:
            item = self._list_widget.takeItem(row)
            self._list_widget.insertItem(row + 1, item)
            self._list_widget.setCurrentRow(row + 1)
            self._files.insert(row + 1, self._files.pop(row))
            self._update_info()

    def _remove_selected(self):
        """移除选中项"""
        row = self._list_widget.currentRow()
        if row >= 0:
            self._list_widget.takeItem(row)
            self._files.pop(row)
            self._update_info()
