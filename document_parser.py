"""
DocumentParser: Extracts raw text from different file types.
  - PDF  → PyMuPDF (fitz); falls back to PaddleOCR for scanned pages
  - Images (PNG/JPG) → PaddleOCR
  - Excel (.xlsx/.xls) → Pandas
"""

import os
from pathlib import Path


class DocumentParser:
    def __init__(self):
        # Lazy-load heavy libraries only when needed
        self._ocr_engine = None

    # ------------------------------------------------------------------
    # OCR engine (shared between image and scanned-PDF paths)
    # ------------------------------------------------------------------
    def _get_ocr(self):
        if self._ocr_engine is None:
            print("  [Parser] Initialising PaddleOCR (first run may download model weights)...")
            import os, inspect
            # Suppress C++ / Paddle verbose logs
            os.environ.setdefault("GLOG_minloglevel", "3")
            os.environ.setdefault("GLOG_logtostderr", "0")
            os.environ.setdefault("FLAGS_call_stack_level", "0")

            os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

            from paddleocr import PaddleOCR

            # PaddleOCR v3+ removed use_angle_cls, show_log and lang from __init__.
            # Detect version and build kwargs accordingly.
            init_params = inspect.signature(PaddleOCR.__init__).parameters
            ocr_kwargs = {}
            if "use_angle_cls" in init_params:
                ocr_kwargs["use_angle_cls"] = True   # v2 only
            if "lang" in init_params:
                ocr_kwargs["lang"] = "en"            # v2 only
            if "show_log" in init_params:
                ocr_kwargs["show_log"] = False        # v2 only

            self._ocr_engine = PaddleOCR(**ocr_kwargs)
            self._ocr_version = 3 if "use_angle_cls" not in init_params else 2
        return self._ocr_engine

    def _run_ocr(self, img_np):
        """
        Run OCR on a numpy image array.
        Handles the API differences between PaddleOCR v2 and v3:
          v2: ocr(img, cls=True)  → list of [[box, (text, score)], ...]
          v3: predict(img)        → list of result dicts with rec_texts / rec_scores
        Returns a flat list of extracted text strings.
        """
        ocr = self._get_ocr()

        if self._ocr_version == 2:
            # v2 API
            result = ocr.ocr(img_np, cls=True)
            lines = []
            if result and result[0]:
                for line in result[0]:
                    lines.append(line[1][0])   # (text, confidence)[0]
            return lines
        else:
            # v3 API — predict() returns a list of OCRResult objects (one per image)
            results = ocr.predict(img_np)
            lines = []
            for res in results:
                # Each res is a dict-like OCRResult; rec_texts is the list of strings
                texts = res.get("rec_texts", []) if hasattr(res, "get") else []
                lines.extend(texts)
            return lines

    # ------------------------------------------------------------------
    # PDF extraction (text-layer first, OCR fallback for scanned pages)
    # ------------------------------------------------------------------
    def _extract_pdf(self, file_path: str) -> str:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        full_text_parts = []

        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text").strip()

            if page_text:
                # Normal text-layer page
                full_text_parts.append(f"--- Page {page_num} ---\n{page_text}")
            else:
                # Scanned page: render to image and run OCR
                print(f"  [Parser] Page {page_num} has no text layer → running OCR…")
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")

                # PaddleOCR accepts file paths OR raw numpy arrays
                import numpy as np
                import cv2

                nparr = np.frombuffer(img_bytes, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                ocr_lines = self._run_ocr(img_np)
                ocr_text = "\n".join(ocr_lines)
                full_text_parts.append(f"--- Page {page_num} (OCR) ---\n{ocr_text}")

        doc.close()
        return "\n\n".join(full_text_parts)

    # ------------------------------------------------------------------
    # Image extraction
    # ------------------------------------------------------------------
    def _extract_image(self, file_path: str) -> str:
        import numpy as np
        import cv2

        img_np = cv2.imread(file_path)
        if img_np is None:
            raise ValueError(f"Could not read image file: {file_path}")

        lines = self._run_ocr(img_np)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Excel extraction
    # ------------------------------------------------------------------
    def _extract_excel(self, file_path: str) -> str:
        import pandas as pd

        xls = pd.ExcelFile(file_path)
        text_parts = []

        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name)
            # Fill NaN with empty string so they don't show as "nan"
            df = df.fillna("")
            text_parts.append(f"=== Sheet: {sheet_name} ===")

            # Column headers
            text_parts.append("Columns: " + " | ".join(str(c) for c in df.columns))

            # Each row as a readable sentence
            for _, row in df.iterrows():

                row_parts = []

                for col, val in row.items():
                    if str(val).strip():
                        row_parts.append(f"{col}: {val}")

                # Combine Reading + Unit into a natural engineering value
                if "Reading" in row and "Unit" in row:
                    reading = str(row["Reading"]).strip()
                    unit = str(row["Unit"]).strip()

                    if reading and unit:
                        row_parts.append(f"Measured Value: {reading} {unit}")

                text_parts.append(", ".join(row_parts))

        return "\n".join(text_parts)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def parse(self, file_path: str) -> str:
        """
        Auto-detect file type and extract text.
        Returns the full extracted text as a single string.
        """
        ext = Path(file_path).suffix.lower()

        print(f"\n  [Parser] Extracting text from {Path(file_path).name} …")

        if ext == ".pdf":
            text = self._extract_pdf(file_path)
        elif ext in {".png", ".jpg", ".jpeg"}:
            text = self._extract_image(file_path)
        elif ext in {".xlsx", ".xls"}:
            text = self._extract_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        char_count = len(text)
        print(f"\n{'='*50}")
        print(f"TEXT EXTRACTION COMPLETE")
        print(f"  Characters extracted: {char_count:,}")
        print(f"{'='*50}")

        return text
