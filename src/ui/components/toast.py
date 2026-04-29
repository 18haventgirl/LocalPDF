"""右下角弹出通知组件"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve
from PySide6.QtGui import QColor


class Toast(QWidget):
    """右下角弹出通知，自动消失"""

    _instances: list["Toast"] = []

    def __init__(
        self,
        message: str,
        duration: int = 3000,
        toast_type: str = "info",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("toast")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # 图标映射
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
        }
        icon_text = icons.get(toast_type, icons["info"])

        # 布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        layout.addWidget(icon_label)

        msg_label = QLabel(message)
        msg_label.setStyleSheet(
            "color: white; font-size: 13px; border: none; background: transparent;"
        )
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # 淡入动画
        self._fade_in = QPropertyAnimation(self, b"windowOpacity")
        self._fade_in.setDuration(250)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 定时关闭
        QTimer.singleShot(duration, self._fade_out)

        # 记录实例防止被 GC
        Toast._instances.append(self)

    def show_at(self, parent_widget: QWidget | None = None):
        """在父窗口右下角显示"""
        self.adjustSize()

        if parent_widget:
            parent_rect = parent_widget.geometry()
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.bottom() - self.height() - 20
        else:
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.right() - self.width() - 20
            y = screen.bottom() - self.height() - 20

        # 避免多个 Toast 重叠
        offset_y = len(Toast._instances) * (self.height() + 8)
        self.move(x, y - offset_y)

        self.show()
        self._fade_in.start()

    def _fade_out(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(250)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self._on_closed)
        anim.start()
        self._fade_anim = anim  # 防止 GC

    def _on_closed(self):
        if self in Toast._instances:
            Toast._instances.remove(self)
        self.close()
