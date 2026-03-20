"""
======================================
 👁 استخراج الحروف من الصور (OCR)
======================================
استخدام Tesseract OCR لقراءة الحروف
العربية من صور لعبة كلمات كراش
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def check_dependencies() -> dict:
    """التحقق من وجود المكتبات المطلوبة"""
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


def extract_letters_from_image(
    image_path: str,
    lang: str = "ara",
    preprocess: str = "thresh"
) -> str:
    """
    استخراج الحروف العربية من صورة

    Args:
        image_path: مسار الصورة
        lang: اللغة (ara للعربية)
        preprocess: نوع المعالجة المسبقة (thresh, blur, adaptive)

    Returns:
        الحروف المستخرجة
    """
    deps = check_dependencies()

    if not deps["cv2"]:
        print("❌ مكتبة OpenCV غير مثبتة: pip install opencv-python")
        return ""
    if not deps["pytesseract"]:
        print("❌ مكتبة pytesseract غير مثبتة: pip install pytesseract")
        return ""

    import cv2
    import pytesseract

    # إعداد مسار Tesseract
    if os.path.exists(config.TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

    # التحقق من وجود الصورة
    if not os.path.exists(image_path):
        print(f"❌ الصورة غير موجودة: {image_path}")
        return ""

    try:
        # قراءة الصورة
        image = cv2.imread(image_path)
        if image is None:
            print("❌ فشل في قراءة الصورة")
            return ""

        # تحويل إلى درجات الرمادي
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # المعالجة المسبقة
        if preprocess == "thresh":
            # عتبة بسيطة
            _, processed = cv2.threshold(gray, 0, 255,
                                        cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif preprocess == "blur":
            # تنعيم ثم عتبة
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, processed = cv2.threshold(blurred, 0, 255,
                                        cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif preprocess == "adaptive":
            # عتبة تكيفية
            processed = cv2.adaptiveThreshold(gray, 255,
                                             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 11, 2)
        else:
            processed = gray

        # استخراج النص
        custom_config = f'--oem 3 --psm 6 -l {lang}'
        text = pytesseract.image_to_string(processed, config=custom_config)

        # استخراج الحروف العربية فقط
        arabic_letters = re.findall(r'[\u0600-\u06FF]', text)
        result = ''.join(arabic_letters)

        if result:
            print(f"✅ تم استخراج {len(result)} حرف: {result}")
        else:
            print("⚠️ لم يتم استخراج أي حروف عربية")

        return result

    except Exception as e:
        print(f"❌ خطأ في OCR: {e}")
        return ""


def extract_from_game_screenshot(
    image_path: str,
    region: tuple = None
) -> str:
    """
    استخراج الحروف من لقطة شاشة اللعبة مع قص منطقة الحروف

    Args:
        image_path: مسار الصورة
        region: منطقة القص (x, y, w, h) أو None للصورة كاملة

    Returns:
        الحروف المستخرجة
    """
    deps = check_dependencies()
    if not deps["cv2"]:
        return extract_letters_from_image(image_path)

    import cv2

    image = cv2.imread(image_path)
    if image is None:
        return ""

    # قص المنطقة إذا تم تحديدها
    if region:
        x, y, w, h = region
        image = image[y:y+h, x:x+w]
        # حفظ الصورة المقصوصة مؤقتاً
        temp_path = image_path + "_cropped.png"
        cv2.imwrite(temp_path, image)
        result = extract_letters_from_image(temp_path)
        # حذف الصورة المؤقتة
        try:
            os.remove(temp_path)
        except Exception:
            pass
        return result

    return extract_letters_from_image(image_path)


def manual_input_fallback() -> str:
    """إدخال يدوي كبديل في حال فشل OCR"""
    print("\n📝 أدخل الحروف يدوياً (بدون مسافات):")
    letters = input("   ← ").strip()
    # تصفية الحروف العربية فقط
    arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')
    return arabic


# === اختبار ===
if __name__ == "__main__":
    print("=" * 50)
    print("   اختبار وحدة OCR")
    print("=" * 50)

    deps = check_dependencies()
    print(f"\n  OpenCV: {'✅' if deps['cv2'] else '❌'}")
    print(f"  Pytesseract: {'✅' if deps['pytesseract'] else '❌'}")
    print(f"  Pillow: {'✅' if deps['PIL'] else '❌'}")

    # اختبار يدوي
    letters = manual_input_fallback()
    print(f"\n  الحروف المدخلة: {letters}")