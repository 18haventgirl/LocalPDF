"""QApplication 初始化 + 主题加载"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


def get_assets_dir() -> Path:
    """获取 assets 目录路径，兼容 PyInstaller 打包后的路径"""
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "assets"


def load_stylesheet() -> str:
    """加载全局 QSS 样式表"""
    qss_path = get_assets_dir() / "styles" / "main.qss"
    if qss_path.exists():
        return qss_path.read_text(encoding="utf-8")
    return ""


def create_application() -> QApplication:
    """创建并配置 QApplication"""
    # Windows 高 DPI 适配
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("LocalPDF")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("LocalPDF")

    # 设置应用图标
    icon_path = get_assets_dir() / "logo.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 加载样式表
    app.setStyleSheet(load_stylesheet())

    return app
