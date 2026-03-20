"""
======================================
 📜 حل الأمثال والحكم
======================================
قاعدة بيانات أمثال عربية مع البحث
"""

from typing import List, Optional
import re


# قاعدة بيانات الأمثال الشعبية
PROVERBS_DB = {
    # أمثال عن الصبر
    "الصبر مفتاح الفرج": ["صبر", "مفتاح", "فرج"],
    "اصبر تنل": ["صبر", "نيل"],
    "من صبر ظفر": ["صبر", "ظفر", "نصر"],
    "الصبر جميل": ["صبر", "جمال"],

    # أمثال عن العلم
    "العلم نور": ["علم", "نور", "معرفة"],
    "اطلب العلم من المهد إلى اللحد": ["علم", "طلب", "تعلم"],
    "العلم في الصغر كالنقش في الحجر": ["علم", "صغر", "نقش", "حجر"],
    "من جد وجد": ["جد", "اجتهاد", "عمل"],

    # أمثال عن الحكمة
    "رأس الحكمة مخافة الله": ["حكمة", "خوف", "الله"],
    "الحكمة ضالة المؤمن": ["حكمة", "إيمان"],
    "خير الكلام ما قل ودل": ["كلام", "قليل", "دلالة"],

    # أمثال عن الصداقة
    "الصديق وقت الضيق": ["صديق", "ضيق", "صداقة"],
    "قل لي من تصاحب أقل لك من أنت": ["صاحب", "صداقة"],
    "الجار قبل الدار": ["جار", "دار", "بيت"],

    # أمثال عن العمل
    "يد واحدة لا تصفق": ["يد", "تعاون"],
    "العمل عبادة": ["عمل", "عبادة"],
    "إن لم تكن ذئبا أكلتك الذئاب": ["ذئب", "قوة"],
    "الوقت كالسيف إن لم تقطعه قطعك": ["وقت", "سيف"],

    # أمثال عن المال
    "القرش الأبيض ينفع في اليوم الأسود": ["مال", "ادخار", "قرش"],
    "المال يجيب المال": ["مال", "ثروة"],
    "من اقتصد لا يفتقر": ["اقتصاد", "فقر"],

    # أمثال عن الأخلاق
    "من زرع حصد": ["زرع", "حصاد"],
    "الحسود لا يسود": ["حسد", "سيادة"],
    "الكلمة الطيبة صدقة": ["كلمة", "طيب", "صدقة"],
    "لا تؤجل عمل اليوم إلى الغد": ["تأجيل", "عمل", "غد"],

    # أمثال عن الأكل
    "المعدة بيت الداء": ["معدة", "داء", "مرض", "أكل"],
    "العقل السليم في الجسم السليم": ["عقل", "جسم", "صحة"],
    "الأكل في وقته صحة": ["أكل", "وقت", "صحة"],

    # أمثال متنوعة
    "درهم وقاية خير من قنطار علاج": ["وقاية", "علاج"],
    "الحاجة أم الاختراع": ["حاجة", "اختراع"],
    "كل طريق وله نهاية": ["طريق", "نهاية"],
    "أعطِ الخبز لخبازه": ["خبز", "خباز", "متخصص"],
    "عصفور في اليد خير من عشرة على الشجرة": ["عصفور", "يد", "شجرة"],
    "لا تبصق في البئر فقد تشرب منه": ["بئر", "ماء"],
    "من حفر حفرة لأخيه وقع فيها": ["حفرة", "أخ"],
    "التكرار يعلم الشطار": ["تكرار", "تعلم"],
    "اتق شر من أحسنت إليه": ["شر", "إحسان"],
    "الجنة تحت أقدام الأمهات": ["جنة", "أم"],
}


def solve_proverb(
    hint: str = None,
    keywords: List[str] = None,
    partial: str = None,
    word_count: int = None
) -> List[str]:
    """
    البحث عن أمثال عربية

    Args:
        hint: تلميح نصي (وصف أو كلمة مفتاحية)
        keywords: قائمة كلمات مفتاحية
        partial: جزء من المثل
        word_count: عدد كلمات المثل

    Returns:
        قائمة الأمثال المطابقة
    """
    results = []

    for proverb, tags in PROVERBS_DB.items():
        score = 0

        # البحث بالتلميح
        if hint:
            hint_lower = hint.strip()
            if hint_lower in proverb:
                score += 10
            for tag in tags:
                if hint_lower in tag or tag in hint_lower:
                    score += 5

        # البحث بالكلمات المفتاحية
        if keywords:
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword in proverb:
                    score += 8
                for tag in tags:
                    if keyword in tag or tag in keyword:
                        score += 3

        # البحث بجزء من المثل
        if partial:
            if partial.strip() in proverb:
                score += 15

        # فلترة بعدد الكلمات
        if word_count:
            if len(proverb.split()) != word_count:
                continue

        if score > 0 or (not hint and not keywords and not partial):
            results.append((proverb, score))

    # ترتيب حسب النقاط
    results.sort(key=lambda x: -x[1])

    return [proverb for proverb, score in results]


def get_all_proverbs() -> List[str]:
    """الحصول على جميع الأمثال"""
    return list(PROVERBS_DB.keys())


def get_proverb_hint(proverb: str) -> Optional[List[str]]:
    """الحصول على الكلمات المفتاحية لمثل معين"""
    return PROVERBS_DB.get(proverb)


def complete_proverb(start: str) -> List[str]:
    """
    إكمال مثل من بدايته

    Args:
        start: بداية المثل

    Returns:
        قائمة الأمثال المطابقة
    """
    return [p for p in PROVERBS_DB.keys() if p.startswith(start.strip())]


def search_proverbs_by_topic(topic: str) -> List[str]:
    """
    البحث عن أمثال حسب الموضوع

    Args:
        topic: الموضوع (مثل: صبر، علم، صداقة)

    Returns:
        قائمة الأمثال المتعلقة بالموضوع
    """
    return solve_proverb(hint=topic)


# === اختبار ===
if __name__ == "__main__":
    print("=" * 50)
    print("   اختبار حل الأمثال")
    print("=" * 50)

    # بحث بتلميح
    print("\n🔍 البحث عن أمثال تتعلق بـ 'العلم':")
    results = solve_proverb(hint="علم")
    for p in results:
        print(f"   📜 {p}")

    # بحث بكلمات مفتاحية
    print("\n🔍 البحث بكلمات: صبر، فرج:")
    results = solve_proverb(keywords=["صبر", "فرج"])
    for p in results:
        print(f"   📜 {p}")

    # إكمال مثل
    print("\n🔍 إكمال 'الصبر':")
    results = complete_proverb("الصبر")
    for p in results:
        print(f"   📜 {p}")