"""
🔍 تصفية النتائج حسب الموضوع
"""

from typing import List

TOPIC_WORDS = {
    "حيوانات 🐾": [
        "قط","كلب","حصان","جمل","أسد","نمر","فيل","غزال",
        "ذئب","ثعلب","أرنب","دب","حمار","بقرة","خروف","ماعز",
        "ديك","دجاجة","حمامة","نسر","صقر","بومة","عصفور",
        "سمكة","حوت","قرش","سلحفاة","تمساح","ثعبان","ضفدع",
        "نحلة","فراشة","عنكبوت","نملة","عقرب","زرافة","قرد",
    ],
    "فواكه 🍎": [
        "تفاح","موز","برتقال","عنب","تين","رمان","مشمش",
        "خوخ","كرز","فراولة","بطيخ","شمام","أناناس","مانجو",
        "كيوي","توت","تمر","جوز","لوز","فستق","بلح","ليمون",
    ],
    "خضروات 🥬": [
        "طماطم","خيا��","بصل","ثوم","جزر","بطاطا","فلفل",
        "باذنجان","كوسا","ملفوف","خس","سبانخ","بقدونس",
        "نعناع","فجل","لفت","قرع","بامية","ذرة",
    ],
    "مهن 👨‍⚕️": [
        "طبيب","مهندس","معلم","محامي","طيار","شرطي","جندي",
        "صيدلي","ممر��","خباز","نجار","حداد","رسام","كاتب",
        "صحفي","مزارع","صياد","طاهي","سائق","بائع","تاجر",
    ],
    "أدوات 🔧": [
        "قلم","كتاب","دفتر","مسطرة","ممحاة","مقص",
        "سكين","شوكة","ملعقة","صحن","كوب","إبريق",
        "مفتاح","قفل","مطرقة","مسمار","حبل","سلسلة",
    ],
    "طبيعة 🌿": [
        "شمس","قمر","نجم","سماء","أرض","بحر","نهر",
        "جبل","وادي","صحراء","غابة","شجرة","زهرة","ورد",
        "عشب","مطر","ثلج","رياح","غيوم","برق","رعد",
    ],
    "منزل 🏠": [
        "باب","نافذة","جدار","سقف","أرضية","درج","مطبخ",
        "حمام","غرفة","صالة","شرفة","حديقة","سرير","كرسي",
        "طاولة","خزانة","مرآة","ستارة","سجادة","وسادة",
    ],
    "ملابس 👔": [
        "قميص","بنطال","فستان","تنورة","جاكيت","معطف",
        "حذاء","جوارب","قبعة","وشاح","قفازات","حزام",
    ],
    "رياضة ⚽": [
        "كرة","ملعب","حكم","هدف","فريق","لاعب",
        "سباق","سباحة","ركض","قفز","رمي","تسلق",
    ],
    "طعام 🍽️": [
        "خبز","أرز","لحم","دجاج","سمك","بيض",
        "حليب","جبن","زيت","سكر","ملح","شاي","قهوة",
    ],
    "ألوان 🎨": [
        "أحمر","أزرق","أخضر","أصفر","أبيض","أسود",
        "بني","رمادي","برتقالي","وردي","بنفسجي",
    ],
    "جسم الإنسان 🫀": [
        "رأس","عين","أنف","فم","أذن","يد","قدم",
        "قلب","رئة","كبد","معدة","دماغ","عظم","دم",
    ],
}


def filter_by_topic(words: List[str], topic: str) -> List[str]:
    topic = topic.strip()
    topic_list = None
    for key, value in TOPIC_WORDS.items():
        if topic in key or key in topic:
            topic_list = value
            break
    if topic_list is None:
        all_tw = []
        for key, value in TOPIC_WORDS.items():
            if any(topic in w or w in topic for w in value):
                all_tw.extend(value)
        if all_tw:
            topic_list = all_tw
        else:
            return words
    filtered = [w for w in words if w in topic_list]
    return filtered if filtered else words


def filter_by_image_description(words: List[str], description: str) -> List[str]:
    if not description:
        return words
    detected = []
    for topic, tw in TOPIC_WORDS.items():
        if any(t in description for t in [topic] + tw):
            detected.append(topic)
    if not detected:
        return words
    relevant = set()
    for t in detected:
        relevant.update(TOPIC_WORDS.get(t, []))
    filtered = [w for w in words if w in relevant]
    return filtered if filtered else words


def filter_by_length(words, min_len=None, max_len=None, exact_len=None):
    if exact_len:
        return [w for w in words if len(w) == exact_len]
    result = words
    if min_len:
        result = [w for w in result if len(w) >= min_len]
    if max_len:
        result = [w for w in result if len(w) <= max_len]
    return result


def get_available_topics() -> List[str]:
    return list(TOPIC_WORDS.keys())


def get_topic_words(topic: str) -> List[str]:
    for key, value in TOPIC_WORDS.items():
        if topic in key or key in topic:
            return value
    return []