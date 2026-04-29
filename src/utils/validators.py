"""输入校验工具"""

import re
from pathlib import Path


def validate_pdf_file(path: str) -> tuple[bool, str]:
    """
    校验 PDF 文件是否有效

    Returns:
        (is_valid, error_message)
    """
    p = Path(path)
    if not p.exists():
        return False, f"文件不存在: {path}"
    if not p.is_file():
        return False, f"不是有效文件: {path}"
    if p.suffix.lower() != ".pdf":
        return False, f"不是 PDF 文件: {p.name}"
    if p.stat().st_size == 0:
        return False, f"文件为空: {p.name}"
    return True, ""


def validate_image_file(path: str) -> tuple[bool, str]:
    """校验图片文件是否有效"""
    p = Path(path)
    valid_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}
    if not p.exists():
        return False, f"文件不存在: {path}"
    if p.suffix.lower() not in valid_exts:
        return False, f"不支持的图片格式: {p.suffix}"
    return True, ""


def validate_page_range(range_str: str, max_page: int) -> tuple[bool, str]:
    """
    校验页码范围字符串格式是否合法

    格式示例: "1-3, 5, 8-10"
    """
    if not range_str.strip():
        return False, "页码范围不能为空"

    pattern = r"^(\d+(-\d+)?)(,\s*\d+(-\d+)?)*$"
    if not re.match(pattern, range_str.strip()):
        return False, "页码格式无效，请使用如 1-3, 5, 8-10 的格式"

    # 逐段校验范围
    for part in range_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-")
                start, end = int(start), int(end)
                if start > end:
                    return False, f"页码范围无效: {part} (起始页不能大于结束页)"
                if start < 1 or end > max_page:
                    return False, f"页码超出范围: {part} (有效范围: 1-{max_page})"
            except ValueError:
                return False, f"页码格式错误: {part}"
        else:
            try:
                page = int(part)
                if page < 1 or page > max_page:
                    return False, f"页码超出范围: {page} (有效范围: 1-{max_page})"
            except ValueError:
                return False, f"页码格式错误: {part}"

    return True, ""
