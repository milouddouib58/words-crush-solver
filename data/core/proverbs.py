"""
📜 حل الأمثال والحكم
"""

from typing import List, Optional

PROVERBS_DB = {
    "الصبر مفتاح الفرج": ["صبر", "مفتاح", "فرج"],
    "اصبر تنل": ["صبر", "نيل"],
    "من صبر ظفر": ["صبر", "ظفر"],
    "الصبر جميل": ["صبر", "جمال"],
    "العلم نور": ["علم", "نور"],
    "اطلب العلم من المهد إلى اللحد": ["علم", "طلب"],
    "العلم في الصغر كالنقش في الحجر": ["علم", "صغر", "نقش"],
    "من جد وجد": ["جد", "اجتهاد"],
    "رأس الحكمة مخافة الله": ["حكمة", "خوف"],
    "خير الكلام ما قل ودل": ["كلام", "قليل"],
    "الصديق وقت الضيق": ["صديق", "ضيق"],
    "الجار قبل الدار": ["جار", "دار"],
    "يد واحدة لا تصفق": ["يد", "تعاون"],
    "العمل عبادة": ["عمل", "عبادة"],
    "الوقت كالسيف إن لم تقطعه قطعك": ["وقت", "سيف"],
    "من زرع حصد": ["زرع", "حصاد"],
    "الحسود لا يسود": ["حسد", "سيادة"],
    "الكلمة الطيبة صدقة": ["كلمة", "طيب"],
    "لا تؤجل عمل اليوم إلى الغد": ["تأجيل", "عمل"],
    "المعدة بيت الداء": ["معدة", "داء"],
    "العقل السليم في الجسم السليم": ["عقل", "جسم"],
    "درهم وقاية خير من قنطار علاج": ["وقاية", "علاج"],
    "الحاجة أم الاختراع": ["حاجة", "اختراع"],
    "عصفور في اليد خير من عشرة على الشجرة": ["عصفور", "يد"],
    "من حفر حفرة لأخيه وقع فيها": ["حفرة", "أخ"],
    "التكرار يعلم الشطار": ["تكرار", "تعلم"],
    "الجنة تحت أقدام الأمهات": ["جنة", "أم"],
    "القرش الأبيض ينفع في اليوم الأسود": ["مال", "ادخار"],
    "إن لم تكن ذئبا أكلتك الذئاب": ["ذئب", "قوة"],
    "أعطِ الخبز لخبازه": ["خبز", "خباز"],
}


def solve_proverb(
    hint: str = None,
    keywords: List[str] = None,
    partial: str = None,
    word_count: int = None
) -> List[str]:
    results = []
    for proverb, tags in PROVERBS_DB.items():
        score = 0
        if hint:
            h = hint.strip()
            if h in proverb:
                score += 10
            for tag in tags:
                if h in tag or tag in h:
                    score += 5
        if keywords:
            for kw in keywords:
                kw = kw.strip()
                if kw in proverb:
                    score += 8
                for tag in tags:
                    if kw in tag or tag in kw:
                        score += 3
        if partial and partial.strip() in proverb:
            score += 15
        if word_count and len(proverb.split()) != word_count:
            continue
        if score > 0 or (not hint and not keywords and not partial):
            results.append((proverb, score))
    results.sort(key=lambda x: -x[1])
    return [p for p, s in results]


def get_all_proverbs() -> List[str]:
    return list(PROVERBS_DB.keys())


def complete_proverb(start: str) -> List[str]:
    return [p for p in PROVERBS_DB if p.startswith(start.strip())]