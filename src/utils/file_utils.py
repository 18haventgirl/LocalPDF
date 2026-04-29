"""文件路径处理、命名冲突处理等工具函数"""

import os
from pathlib import Path


def safe_output_path(path: str) -> str:
    """如果文件已存在，自动添加 _1, _2 后缀避免覆盖"""
    p = Path(path)
    if not p.exists():
        return path
    counter = 1
    while True:
        new_path = p.parent / f"{p.stem}_{counter}{p.suffix}"
        if not new_path.exists():
            return str(new_path)
        counter += 1


def get_file_size_str(size_bytes: int) -> str:
    """将字节数转换为人类可读的文件大小字符串"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def ensure_dir(path: str) -> Path:
    """确保目录存在，不存在则创建"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
