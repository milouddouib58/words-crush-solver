"""
🧠 محرك الذكاء الاصطناعي المركزي (Gemini AI)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
يوفر كل وظائف AI في مكان واحد:
- حل الكلمات المبعثرة بالذكاء
- حل الأمثال من الإيموجي
- تحليل صور المراحل (Vision AI)
- التدقيق اللغوي والسياقي
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_api_key() -> str:
    """الحصول على مفتاح API من عدة مصادر"""
    # 1. من Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    # 2. من متغيرات البيئة
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key

    # 3. من config.py
    key = getattr(config, 'GEMINI_API_KEY', "")
    if key and key != "ضع_مفتاحك_هنا":
        return key

    return ""


def is_ai_available() -> bool:
    """التحقق من توفر الذكاء الاصطناعي"""
    try:
        import google.generativeai
        key = get_api_key()
        return bool(key)
    except ImportError:
        return False


def get_model(vision: bool = False):
    """الحصول على نموذج Gemini"""
    import google.generativeai as genai

    key = get_api_key()
    if not key:
        raise ValueError("مفتاح API غير متوفر")

    genai.configure(api_key=key)

    model_name = config.GEMINI_VISION_MODEL if vision else config.GEMINI_MODEL

    # إعدادات الأمان المخففة للمحتوى التعليمي
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    generation_config = {
        "temperature": 0.3,       # دقة عالية
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 2048,
    }

    model = genai.GenerativeModel(
        model_name,
        safety_settings=safety_settings,
        generation_config=generation_config,
    )

    return model


# ═══════════════════════════════════════════
#  🔤 حل الكلمات المبعثرة بالذكاء الاصطناعي
# ═══════════════════════════════════════════
def ai_solve_scrambled(
    letters: str,
    topic: str = "",
    image_description: str = "",
    word_lengths: list = None
) -> dict:
    """
    حل كلمات مبعثرة باستخدام AI

    Returns:
        dict: {"words": [...], "explanation": "...", "topic": "..."}
    """
    model = get_model()

    lengths_hint = ""
    if word_lengths:
        lengths_hint = f"\nأطوال الكلمات المطلوبة: {', '.join(str(l) for l in word_lengths)} حروف"

    topic_hint = ""
    if topic:
        topic_hint = f"\nموضوع المرحلة: {topic}"

    image_hint = ""
    if image_description:
        image_hint = f"\nوصف الصورة في المرحلة: {image_description}"

    prompt = f"""أنت خبير في حل لعبة "كلمات كراش" العربية.

الحروف المتاحة: {letters}
{topic_hint}
{image_hint}
{lengths_hint}

المطلوب:
1. كوّن جميع الكلمات العربية الصحيحة والحقيقية من هذه الحروف فقط.
2. لا تستخدم أي حرف أكثر من عدد مرات ظهوره في الحروف المتاحة.
3. رتب الكلمات حسب الطول من الأطول للأقصر.
4. إذا كان هناك موضوع، أعطِ الأولوية للكلمات المتعلقة به.

أجب بهذا التنسيق بالضبط (JSON):
{{
    "topic_detected": "الموضوع المكتشف",
    "words_by_length": {{
        "5": ["كلمة1", "كلمة2"],
        "4": ["كلمة3", "كلمة4"],
        "3": ["كلمة5", "كلمة6"]
    }},
    "best_matches": ["أفضل 5 كلمات مطابقة للموضوع"],
    "explanation": "شرح مختصر"
}}

مهم: أجب بـ JSON فقط بدون أي نص إضافي أو علامات markdown.
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # تنظيف الاستجابة
        text = text.replace("```json", "").replace("```", "").strip()

        import json
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            # استخراج الكلمات من النص العادي
            import re
            arabic_words = re.findall(r'[\u0600-\u06FF]{2,}', text)
            result = {
                "topic_detected": topic or "عام",
                "words_by_length": {},
                "best_matches": arabic_words[:10],
                "explanation": text[:200],
                "raw_words": arabic_words
            }

        return result

    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════
#  📜 حل الأمثال من الإيموجي
# ═══════════════════════════════════════════
def ai_solve_proverb(
    emojis: str = "",
    letters: str = "",
    hint: str = "",
    word_count: int = 0
) -> dict:
    """
    حل أمثال عربية من الإيموجي والتلميحات

    Returns:
        dict: {"proverb": "...", "meaning": "...", "alternatives": [...]}
    """
    model = get_model()

    constraints = ""
    if letters:
        constraints += f"\nالحروف المتاحة: {letters}"
    if word_count > 0:
        constraints += f"\nعدد كلمات المثل: {word_count}"
    if hint:
        constraints += f"\nتلميح إضافي: {hint}"

    prompt = f"""أنت خبير في الأمثال الشعبية العربية ولعبة "كلمات كراش".

الرموز التعبيرية (الإيموجي) الموجودة في المرحلة: {emojis}
{constraints}

المطلوب:
1. حلل الإيموجي واستنتج المثل العربي المقصود.
2. تأكد أن حروف المثل تتوافق مع الحروف المتاحة (إن وُجدت).
3. قدم بدائل محتملة إذا كان هناك أكثر من احتمال.

أجب بهذا التنسيق (JSON):
{{
    "proverb": "المثل الأكثر ترجيحاً",
    "confidence": 95,
    "meaning": "شرح المثل",
    "emoji_analysis": "كيف تم ربط الإيموجي بالمثل",
    "alternatives": [
        {{"proverb": "مثل بديل 1", "confidence": 70}},
        {{"proverb": "مثل بديل 2", "confidence": 50}}
    ]
}}

مهم: أجب بـ JSON فقط بدون أي نص إضافي أو علامات markdown.
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        import json
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "proverb": text.split('\n')[0] if text else "لم يتم التعرف",
                "confidence": 50,
                "meaning": "",
                "alternatives": []
            }

    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════
#  📷 تحليل صورة المرحلة بالكامل (Vision AI)
# ═══════════════════════════════════════════
def ai_solve_from_image(pil_image, additional_info: str = "") -> dict:
    """
    تحليل صورة مرحلة كاملة وحلها

    Args:
        pil_image: صورة PIL
        additional_info: معلومات إضافية من المستخدم

    Returns:
        dict: حل شامل للمرحلة
    """
    model = get_model(vision=True)

    extra = ""
    if additional_info:
        extra = f"\nمعلومات إضافية من اللاعب: {additional_info}"

    prompt = f"""أنت خبير محترف في حل لعبة "كلمات كراش" العربية.
أمامك صورة شاشة (Screenshot) كاملة لمرحلة من اللعبة.
{extra}

حلل الصورة بدقة كما يفعل اللاعب المحترف:

1. **نوع المرحلة**: حدد هل هي (كلمات مبعثرة / كلمات متقاطعة / مقاطع / أمثال وإيموجي / صورة وكلمات).

2. **الصورة الرئيسية**: صف الصورة أو الإيموجي في أعلى الشاشة وما تدل عليه.

3. **الحروف المتاحة**: اقرأ كل الحروف الموجودة في الدوائر أو المربعات في أسفل الشاشة.

4. **الحل الكامل**: اكتب جميع الكلمات التي تحل المرحلة:
   - رتبها حسب طولها.
   - تأكد أن كل كلمة تتكون من الحروف المتاحة فقط.
   - أعطِ الأولوية للكلمات المرتبطة بالصورة/الموضوع.

5. **الفراغات**: إذا كانت هناك فراغات ظاهرة في الصورة، حدد عدد حروف كل فراغ واقترح الكلمة المناسبة.

أجب بهذا التنسيق (JSON):
{{
    "stage_type": "نوع المرحلة",
    "image_description": "وصف الصورة/الإيموجي",
    "available_letters": "الحروف المقروءة",
    "topic": "الموضوع المكتشف",
    "solution": {{
        "main_words": ["الكلمات الرئيسية للحل"],
        "by_length": {{
            "6": ["كلمات من 6 حروف"],
            "5": ["كلمات من 5 حروف"],
            "4": ["كلمات من 4 حروف"],
            "3": ["كلمات من 3 حروف"],
            "2": ["كلمات من حرفين"]
        }},
        "bonus_words": ["كلمات إضافية ممكنة"]
    }},
    "proverb": "المثل إذا كانت مرحلة أمثال (أو فارغ)",
    "confidence": 90,
    "explanation": "شرح طريقة الحل",
    "tips": ["نصيحة 1", "نصيحة 2"]
}}

مهم: أجب بـ JSON فقط بدون أي نص إضافي أو علامات markdown.
"""

    try:
        response = model.generate_content([prompt, pil_image])
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        import json
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "stage_type": "غير محدد",
                "raw_response": text,
                "solution": {"main_words": []},
                "confidence": 50
            }

    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════
#  🔍 التدقيق اللغوي بالذكاء الاصطناعي
# ═══════════════════════════════════════════
def ai_verify_words(words: list, context: str = "") -> dict:
    """
    التحقق من صحة الكلمات لغوياً

    Returns:
        dict: {"valid": [...], "invalid": [...], "suggestions": [...]}
    """
    model = get_model()

    prompt = f"""أنت معجم عربي حي. تحقق من الكلمات التالية:

الكلمات: {', '.join(words)}
السياق: {context}

لكل كلمة، حدد:
1. هل هي كلمة عربية صحيحة ومعروفة؟
2. ما معناها المختصر؟

أجب بـ JSON:
{{
    "valid": [
        {{"word": "كلمة", "meaning": "معناها"}}
    ],
    "invalid": ["كلمة_خاطئة1"],
    "suggestions": ["كلمات مقترحة إضافية"]
}}

أجب بـ JSON فقط.
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        import json
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"valid": [], "invalid": [], "suggestions": []}

    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════
#  🎯 الحل الهجين (Trie + AI)
# ═══════════════════════════════════════════
def hybrid_solve(
    trie,
    letters: str,
    topic: str = "",
    image_description: str = "",
    use_ai_verification: bool = True
) -> dict:
    """
    حل هجين: سرعة Trie + ذكاء AI

    Returns:
        dict: نتائج مدمجة ومرتبة
    """
    from core.scrambler import solve_scrambled
    from core.filter import filter_by_topic

    # 1. حل سريع بالـ Trie
    trie_results = solve_scrambled(trie, letters)

    if topic:
        trie_filtered = filter_by_topic(trie_results, topic)
    else:
        trie_filtered = trie_results

    result = {
        "trie_results": trie_filtered,
        "trie_count": len(trie_filtered),
        "ai_results": [],
        "ai_extra": [],
        "verified": [],
        "combined": trie_filtered,
    }

    # 2. إثراء بالذكاء الاصطناعي
    if is_ai_available():
        try:
            ai_result = ai_solve_scrambled(letters, topic, image_description)

            if "error" not in ai_result:
                # استخراج كلمات AI
                ai_words = []

                if "best_matches" in ai_result:
                    ai_words.extend(ai_result["best_matches"])

                if "words_by_length" in ai_result:
                    for length_words in ai_result["words_by_length"].values():
                        if isinstance(length_words, list):
                            ai_words.extend(length_words)

                if "raw_words" in ai_result:
                    ai_words.extend(ai_result["raw_words"])

                # كلمات جديدة من AI غير موجودة في Trie
                ai_extra = [
                    w for w in ai_words
                    if w not in trie_filtered and len(w) >= 2
                ]

                result["ai_results"] = ai_words
                result["ai_extra"] = list(set(ai_extra))
                result["ai_topic"] = ai_result.get("topic_detected", "")
                result["explanation"] = ai_result.get("explanation", "")

                # دمج النتائج
                combined = list(trie_filtered)
                for w in ai_extra:
                    if w not in combined:
                        combined.append(w)

                result["combined"] = combined

        except Exception:
            pass

    return result


# === اختبار سريع ===
if __name__ == "__main__":
    print("=" * 50)
    print("   اختبار محرك الذكاء الاصطناعي")
    print("=" * 50)

    if is_ai_available():
        print("✅ الذكاء الاصطناعي متاح")

        # اختبار حل كلمات
        result = ai_solve_scrambled("كتابلم", "أدوات")
        print(f"\nنتيجة: {result}")
    else:
        print("❌ مفتاح API غير متوفر")
        print("   أضف GEMINI_API_KEY في:")
        print("   - متغيرات البيئة")
        print("   - .streamlit/secrets.toml")
        print("   - config.py")
