"""
👁 استخراج الحروف من الصور (OCR)
- جميع المكتبات اختيارية
- يعمل بدونها مع إدخال يدوي
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_ocr_deps() -> dict:
    """التحقق من وجود المكتبات المطلوبة"""
    status = {"cv2": False, "pytesseract": False, "PIL": False}

    try:
        import cv2
        status["cv2"] = True
    except (ImportError, Exception):
        pass

    try:
        import pytesseract
        status["pytesseract"] = True
    except (ImportError, Exception):
        pass

    try:
        from PIL import Image
        status["PIL"] = True
    except (ImportError, Exception):
        pass

    return status


def extract_letters_from_image(image_path_or_bytes, lang="ara"):
    """استخراج الحروف العربية من صورة"""
    try:
        import cv2
        import numpy as np
        import pytesseract
    except ImportError:
        return ""

    try:
        if isinstance(image_path_or_bytes, bytes):
            nparr = np.frombuffer(image_path_or_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_path_or_bytes, str):
            image = cv2.imread(image_path_or_bytes)
        else:
            return ""

        if image is None:
            return ""

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, processed = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        text = pytesseract.image_to_string(
            processed, config=f'--oem 3 --psm 6 -l {lang}'
        )

        arabic_letters = re.findall(r'[\u0600-\u06FF]', text)
        return ''.join(arabic_letters)

    except Exception:
        return ""


def extract_from_pil_image(pil_image, lang="ara"):
    """استخراج من صورة PIL مباشرة"""
    try:
        import pytesseract
        text = pytesseract.image_to_string(pil_image, lang=lang)
        arabic_letters = re.findall(r'[\u0600-\u06FF]', text)
        return ''.join(arabic_letters)
    except (ImportError, Exception):
        return ""
