"""
======================================
 🔍 تصفية النتائج حسب الموضوع
======================================
"""

from typing import List, Optional
import re


# قاموس المواضيع والكلمات المرتبطة
TOPIC_WORDS = {
    "حيوانات": [
        "قط", "كلب", "حصان", "جمل", "أسد", "نمر", "فيل", "غزال",
        "ذئب", "ثعلب", "أرنب", "دب", "حمار", "بقرة", "خروف", "ماعز",
        "ديك", "دجاجة", "حمامة", "نسر", "صقر", "بومة", "عصفور",
        "سمكة", "حوت", "قرش", "سلحفاة", "تمساح", "ثعبان", "ضفدع",
        "نحلة", "فراشة", "عنكبوت", "نملة", "عقرب", "زرافة", "قرد",
        "باندا", "كنغر", "بطريق", "حلزون", "وحيد",
    ],
    "فواكه": [
        "تفاح", "موز", "برتقال", "عنب", "تين", "رمان", "مشمش",
        "خوخ", "كرز", "فراولة", "بطيخ", "شمام", "أناناس", "مانجو",
        "كيوي", "توت", "تمر", "جوز", "لوز", "فستق", "بلح", "ليمون",
    ],
    "خضروات": [
        "طماطم", "خيار", "بصل", "ثوم", "جزر", "بطاطا", "فلفل",
        "باذنجان", "كوسا", "ملفوف", "خس", "سبانخ", "بقدونس",
        "نعناع", "فجل", "لفت", "قرع", "بامية", "ذرة",
    ],
    "مهن": [
        "طبيب", "مهندس", "معلم", "محامي", "طيار", "شرطي", "جندي",
        "صيدلي", "ممرض", "خباز", "نجار", "حداد", "رسام", "كاتب",
        "صحفي", "مزارع", "صياد", "طاهي", "سائق", "بائع", "تاجر",
        "حارس", "عامل", "مدير", "وزير", "قاضي", "سفير",
    ],
    "أدوات": [
        "قلم", "كتاب", "دفتر", "مسطرة", "ممحاة", "مقص",
        "سكين", "شوكة", "ملعقة", "صحن", "كوب", "إبريق",
        "مفتاح", "قفل", "مطرقة", "مسمار", "حبل", "سلسلة",
    ],
    "طبيعة": [
        "شمس", "قمر", "نجم", "سماء", "أرض", "بحر", "نهر",
        "جبل", "وادي", "صحراء", "غابة", "شجرة", "زهرة", "ورد",
        "عشب", "مطر", "ثلج", "رياح", "غيوم", "برق", "رعد",
    ],
    "منزل": [
        "باب", "نافذة", "جدار", "سقف", "أرضية", "درج", "مطبخ",
        "حمام", "غرفة", "صالة", "شرفة", "حديقة", "سرير", "كرسي",
        "طاولة", "خزانة", "مرآة", "ستارة", "سجادة", "وسادة",
        "مصباح", "ثلاجة", "فرن", "غسالة", "تلفاز",
    ],
    "ملابس": [
        "قميص", "بنطال", "فستان", "تنورة", "جاكيت", "معطف",
        "حذاء", "جوارب", "قبعة", "وشاح", "قفازات", "حزام",
        "ربطة", "نظارة", "ساعة", "خاتم", "سوار", "قلادة",
    ],
    "رياضة": [
        "كرة", "ملعب", "حكم", "هدف", "فريق", "لاعب",
        "سباق", "سباحة", "ركض", "قفز", "رمي", "تسلق",
    ],
    "طعام": [
        "خبز", "أرز", "لحم", "دجاج", "سمك", "بيض",
        "حليب", "جبن", "زيت", "سكر", "ملح", "شاي", "قهوة",
        "طعام", "وجبة",
    ],
    "ألوان": [
        "أحمر", "أزرق", "أخضر", "أصفر", "أبيض", "أسود",
        "بني", "رمادي", "برتقالي", "وردي", "بنفسجي",
    ],
    "جسم": [
        "رأس", "عين", "أنف", "فم", "أذن", "يد", "قدم",
        "قلب", "رئة", "كبد", "معدة", "دماغ", "عظم", "دم",
        "شعر", "جلد", "إصبع", "ظهر", "صدر", "كتف", "ركبة",
    ],
}


def filter_by_topic(words: List[str], topic: str) -> List[str]:
    """
    تصفية الكلمات حسب الموضوع

    Args:
        words: قائمة الكلمات
        topic: اسم الموضوع

    Returns:
        الكلمات المنتمية للموضوع
    """
    topic = topic.strip()

    # البحث عن الموضوع في القاموس
    topic_list = None
    for key, value in TOPIC_WORDS.items():
        if topic in key or key in topic:
            topic_list = value
            break

    if topic_list is None:
        # بحث في كل المواضيع عن الكلمة المفتاحية
        all_topic_words = []
        for key, value in TOPIC_WORDS.items():
            if any(topic in w or w in topic for w in value):
                all_topic_words.extend(value)

        if all_topic_words:
            topic_list = all_topic_words
        else:
            return words  # إرجاع الكل إذا لم يُعثر على الموضوع

    # تصفية
    filtered = [w for w in words if w in topic_list]

    return filtered if filtered else words


def filter_by_image_description(
    words: List[str],
    description: str
) -> List[str]:
    """
    تصفية النتائج بناءً على وصف الصورة

    Args:
        words: قائمة الكلمات
        description: وصف الصورة من المستخدم

    Returns:
        الكلمات المتعلقة بوصف الصورة
    """
    if not description:
        return words

    description = description.strip()

    # تحديد الموضوع من الوصف
    detected_topics = []
    for topic, topic_words in TOPIC_WORDS.items():
        # التحقق من تطابق اسم الموضوع
        if topic in description:
            detected_topics.append(topic)
            continue

        # التحقق من تطابق كلمات الموضوع
        for word in topic_words:
            if word in description:
                detected_topics.append(topic)
                break

    if not detected_topics:
        return words

    # جمع كلمات المواضيع المكتشفة
    relevant_words = set()
    for topic in detected_topics:
        relevant_words.update(TOPIC_WORDS.get(topic, []))

    # تصفية
    filtered = [w for w in words if w in relevant_words]

    return filtered if filtered else words


def filter_by_length(
    words: List[str],
    min_len: int = None,
    max_len: int = None,
    exact_len: int = None
) -> List[str]:
    """تصفية حسب طول الكلمة"""
    if exact_len:
        return [w for w in words if len(w) == exact_len]

    result = words
    if min_len:
        result = [w for w in result if len(w) >= min_len]
    if max_len:
        result = [w for w in result if len(w) <= max_len]

    return result


def get_available_topics() -> List[str]:
    """الحصول على قائمة المواضيع المتاحة"""
    return list(TOPIC_WORDS.keys())


def get_topic_words(topic: str) -> List[str]:
    """الحصول على كلمات موضوع معين"""
    for key, value in TOPIC_WORDS.items():
        if topic in key or key in topic:
            return value
    return []


# === اختبار ===
if __name__ == "__main__":
    print("=" * 50)
    print("   اختبار تصفية النتائج")
    print("=" * 50)

    test_words = ["قط", "تفاح", "طبيب", "شمس", "كتاب", "أسد", "موز"]

    print(f"\nالكلمات: {test_words}")

    for topic in ["حيوانات", "فواكه", "مهن"]:
        filtered = filter_by_topic(test_words, topic)
        print(f"\n  {topic}: {filtered}")

    # اختبار تصفية بوصف الصورة
    print("\n  وصف 'حديقة حيوانات':",
          filter_by_image_description(test_words, "حديقة حيوانات"))