"""从 PDF 中提取图片页面"""

import os
from pathlib import Path

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt

from src.ui.pages.base_page import BasePage
from src.workers.pdf_worker import PDFWorker
from src.utils.file_utils import get_file_size_str


class ExtractPage(BasePage):
    """从 PDF 中提取嵌入图片"""

    def __init__(self, parent=None):
        self._format_combo: QComboBox | None = None
        super().__init__(accept_types=[".pdf"], title="提取图片", parent=parent)

    def create_settings_widget(self) -> QWidget | None:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("输出格式:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["保持原格式", "全部转为 PNG", "全部转为 JPG"])
        layout.addWidget(self._format_combo)
        layout.addStretch()

        return widget

    def on_start(self):
        files = self.get_files()
        if not files:
            self.show_toast("请先选择文件", "warning")
            return

        input_path = files[0]
        p = Path(input_path)
        output_dir = str(p.parent / f"{p.stem}_images")
        self._output_dir = output_dir

        fmt_map = {0: "original", 1: "png", 2: "jpg"}
        output_fmt = fmt_map[self._format_combo.currentIndex()]

        self._start_btn.setEnabled(False)
        self._progress.set_status("正在提取图片...")

        self._worker = PDFWorker(
            self._do_extract, input_path, output_dir, output_fmt,
        )
        self._worker.progress.connect(lambda c, t: self._progress.set_progress(c, t))
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @staticmethod
    def _do_extract(input_path, output_dir, output_fmt, progress_callback=None):
        import fitz

        doc = fitz.open(input_path)
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        extracted = []
        seen_xrefs = set()
        img_counter = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            images = page.get_images(full=True)

            for img_info in images:
                xref = img_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]

                    img_counter += 1

                    if output_fmt == "png":
                        out_ext = "png"
                    elif output_fmt == "jpg":
                        out_ext = "jpg"
                    else:
                        out_ext = ext

                    img_name = f"image_{img_counter:03d}.{out_ext}"
                    out_path = str(Path(output_dir) / img_name)

                    if output_fmt != "original" and output_fmt != ext:
                        from PIL import Image
                        import io
                        pil_img = Image.open(io.BytesIO(image_bytes))
                        if output_fmt == "jpg":
                            pil_img = pil_img.convert("RGB")
                            pil_img.save(out_path, format="JPEG", quality=95)
                        else:
                            pil_img.save(out_path, format="PNG")
                    else:
                        with open(out_path, "wb") as f:
                            f.write(image_bytes)

                    extracted.append({
                        "path": out_path,
                        "page": page_num + 1,
                        "size": os.path.getsize(out_path),
                    })
                except Exception:
                    continue

            if progress_callback:
                progress_callback(page_num + 1, len(doc))

        doc.close()
        return extracted

    def _on_finished(self, result):
        self._start_btn.setEnabled(True)
        self._open_dir_btn.setVisible(True)
        count = len(result)
        total_size = sum(item["size"] for item in result)
        self._progress.set_status(
            f"✅ 提取完成! 共 {count} 张图片, 总大小 {get_file_size_str(total_size)}"
        )

    def _on_error(self, msg):
        self._start_btn.setEnabled(True)
        self._progress.set_status(f"❌ 提取失败: {msg}")
