"""
👁 استخراج الحروف من الصور (OCR)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def check_ocr_deps() -> dict:
    status = {"cv2": False, "pytesseract": False, "PIL": False}
    try:
        import cv2
        status["cv2"] = True
    except ImportError:
        pass
    try:
        import pytesseract
        status["pytesseract"] = True
    except ImportError:
        pass
    try:
        from PIL import Image
        status["PIL"] = True
    except ImportError:
        pass
    return status


def extract_letters_from_image(image_path_or_bytes, lang="ara"):
    """استخراج الحروف العربية من صورة"""
    deps = check_ocr_deps()
    if not deps["cv2"] or not deps["pytesseract"]:
        return ""

    import cv2
    import numpy as np
    import pytesseract

    if os.path.exists(config.TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

    try:
        # قراءة من bytes أو مسار
        if isinstance(image_path_or_bytes, bytes):
            nparr = np.frombuffer(image_path_or_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = cv2.imread(image_path_or_bytes)

        if image is None:
            return ""

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, processed = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        custom_config = f'--oem 3 --psm 6 -l {lang}'
        text = pytesseract.image_to_string(processed, config=custom_config)

        arabic_letters = re.findall(r'[\u0600-\u06FF]', text)
        return ''.join(arabic_letters)

    except Exception as e:
        return ""


def extract_from_pil_image(pil_image, lang="ara"):
    """استخراج من صورة PIL مباشرة"""
    deps = check_ocr_deps()
    if not deps["pytesseract"]:
        return ""

    import pytesseract

    if os.path.exists(config.TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

    try:
        text = pytesseract.image_to_string(pil_image, lang=lang)
        arabic_letters = re.findall(r'[\u0600-\u06FF]', text)
        return ''.join(arabic_letters)
    except Exception:
        return ""