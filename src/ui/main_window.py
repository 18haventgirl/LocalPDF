"""主窗口：左侧导航栏 + 右侧工作区 + 底部状态栏"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QStackedWidget, QPushButton, QStatusBar,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """LocalPDF 主窗口"""

    # 导航项定义：(key, 图标emoji, 显示文字)
    NAV_ITEMS = [
        ("merge",     "📎", "合并"),
        ("split",     "✂️", "拆分"),
        ("rotate",    "🔘", "旋转"),
        ("watermark", "💧", "水印"),
        ("convert",   "🔄", "转换"),
        ("extract",   "🖼️", "提取图片"),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LocalPDF")
        self.setMinimumSize(960, 640)
        self.resize(1080, 720)

        self._nav_buttons: dict[str, QPushButton] = {}
        self._pages: dict[str, QWidget] = {}

        self._init_ui()
        self._load_pages()

        # 默认选中第一个导航项
        first_key = self.NAV_ITEMS[0][0]
        self._nav_buttons[first_key].setChecked(True)
        self._stack.setCurrentWidget(self._pages[first_key])

    def _init_ui(self):
        """初始化界面布局"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- 左侧导航栏 ----
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 应用标题
        title = QLabel("  🔷 LocalPDF")
        title.setObjectName("sidebarTitle")
        sidebar_layout.addWidget(title)

        sidebar_layout.addSpacing(10)

        # 导航按钮
        for key, icon, text in self.NAV_ITEMS:
            btn = QPushButton(f"  {icon}  {text}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._on_nav_clicked(k))
            sidebar_layout.addWidget(btn)
            self._nav_buttons[key] = btn

        sidebar_layout.addStretch()

        # 底部版本信息
        version_label = QLabel("  v1.0.0")
        version_label.setStyleSheet(
            "color: #475569; font-size: 11px; padding: 12px 20px;"
        )
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(sidebar)

        # ---- 右侧工作区 ----
        workspace = QWidget()
        workspace.setStyleSheet("background-color: #F8FAFC;")
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        workspace_layout.addWidget(self._stack)
        main_layout.addWidget(workspace)

        # ---- 底部状态栏 ----
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_label = QLabel("就绪")
        self._status_bar.addWidget(self._status_label)

    def _load_pages(self):
        """加载所有功能页面到 stacked widget"""
        from src.ui.pages.merge_page import MergePage
        from src.ui.pages.split_page import SplitPage
        from src.ui.pages.rotate_page import RotatePage
        from src.ui.pages.watermark_page import WatermarkPage
        from src.ui.pages.convert_page import ConvertPage
        from src.ui.pages.extract_page import ExtractPage

        page_classes = {
            "merge": MergePage,
            "split": SplitPage,
            "rotate": RotatePage,
            "watermark": WatermarkPage,
            "convert": ConvertPage,
            "extract": ExtractPage,
        }

        for key, _, _ in self.NAV_ITEMS:
            page = page_classes[key]()
            self._pages[key] = page
            self._stack.addWidget(page)

    def _on_nav_clicked(self, key: str):
        """导航按钮点击事件"""
        # 取消其他按钮的选中状态
        for k, btn in self._nav_buttons.items():
            btn.setChecked(k == key)

        # 切换页面
        if key in self._pages:
            self._stack.setCurrentWidget(self._pages[key])

        # 更新状态栏
        icon, text = "", key
        for k, ic, tx in self.NAV_ITEMS:
            if k == key:
                icon, text = ic, tx
                break
        self._status_label.setText(f"当前功能: {icon} {text}")
