"""自定义异常类"""

import logging
from pathlib import Path


class PDFError(Exception):
    """PDF 操作基础异常"""
    pass


class EncryptedPDFError(PDFError):
    """加密 PDF 错误"""
    pass


class InvalidPageRangeError(PDFError):
    """无效页码范围"""
    pass


class FileOperationError(PDFError):
    """文件操作错误"""
    pass


# 配置日志
def setup_logger() -> logging.Logger:
    """配置并返回应用日志器"""
    log_dir = Path.home() / ".localpdf" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("localpdf")
    logger.setLevel(logging.DEBUG)

    # 文件处理器
    fh = logging.FileHandler(
        log_dir / "error.log", encoding="utf-8"
    )
    fh.setLevel(logging.WARNING)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))
    logger.addHandler(fh)

    return logger


logger = setup_logger()
