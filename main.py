"""LocalPDF — 纯本地 PDF 工具箱"""

import sys
from pathlib import Path

# 将项目根目录加入 sys.path，确保 src 包可导入
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.app import create_application
from src.ui.main_window import MainWindow


def main():
    app = create_application()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
