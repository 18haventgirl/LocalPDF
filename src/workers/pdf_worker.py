"""通用 PDF 操作后台线程"""

from PySide6.QtCore import QThread, Signal


class PDFWorker(QThread):
    """通用 PDF 操作后台线程"""

    progress = Signal(int, int)      # (current, total)
    finished = Signal(object)        # 操作结果（dict 或 list 或 bool）
    error = Signal(str)              # 错误信息

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._cancelled = False

    def run(self):
        try:
            # 注入进度回调
            self.kwargs["progress_callback"] = self._on_progress
            result = self.func(*self.args, **self.kwargs)
            if not self._cancelled:
                self.finished.emit(result)
        except Exception as e:
            if not self._cancelled:
                self.error.emit(str(e))

    def cancel(self):
        """请求取消操作（注意：实际取消需要 core 函数配合检查）"""
        self._cancelled = True

    def _on_progress(self, current: int, total: int):
        if not self._cancelled:
            self.progress.emit(current, total)
