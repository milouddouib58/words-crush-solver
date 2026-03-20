"""
======================================
 🖼 تحليل ووصف الصور
======================================
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def analyze_image_simple(image_path: str) -> str:
    """
    تحليل بسيط للصورة (يعتمد على اسم الملف أو المستخدم)

    Args:
        image_path: مسار الصورة

    Returns:
        وصف الصورة
    """
    # تحليل من اسم الملف
    filename = os.path.basename(image_path).lower()
    keywords = {
        "animal": "حيوانات",
        "fruit": "فواكه",
        "food": "طعام",
        "nature": "طبيعة",
        "sport": "رياضة",
        "city": "مدينة",
        "house": "منزل",
    }

    for key, value in keywords.items():
        if key in filename:
            return value

    return ""


def get_image_description_from_user() -> str:
    """
    طلب وصف الصورة من المستخدم

    Returns:
        وصف الصورة
    """
    print("\n🖼 ما هو موضوع الصورة في المرحلة؟")
    print("   المواضيع المتاحة:")
    topics = [
        "حيوانات", "فواكه", "خضروات", "مهن",
        "أدوات", "طبيعة", "منزل", "ملابس",
        "رياضة", "طعام", "ألوان", "جسم"
    ]

    for i, topic in enumerate(topics, 1):
        print(f"   {i:2d}. {topic}", end="")
        if i % 4 == 0:
            print()

    print("\n\n   أو اكتب وصفاً حراً:")
    description = input("   ← ").strip()

    # التحقق من إدخال رقم
    try:
        idx = int(description) - 1
        if 0 <= idx < len(topics):
            return topics[idx]
    except ValueError:
        pass

    return description


def detect_image_colors(image_path: str) -> list:
    """
    اكتشاف الألوان السائدة في الصورة (اختياري)
    """
    try:
        import cv2
        import numpy as np

        image = cv2.imread(image_path)
        if image is None:
            return []

        # تحويل إلى HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # تحليل بسيط للألوان
        colors = []
        h_mean = np.mean(hsv[:, :, 0])

        if h_mean < 15 or h_mean > 165:
            colors.append("أحمر")
        elif 15 <= h_mean < 35:
            colors.append("برتقالي")
        elif 35 <= h_mean < 75:
            colors.append("أخضر")
        elif 75 <= h_mean < 130:
            colors.append("أزرق")

        return colors

    except ImportError:
        return []
    except Exception:
        return []


# === اختبار ===
if __name__ == "__main__":
    print("=" * 50)
    print("   اختبار تحليل الصور")
    print("=" * 50)

    desc = get_image_description_from_user()
    print(f"\n   الوصف: {desc}")