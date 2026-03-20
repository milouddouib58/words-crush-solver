"""
🧠 مساعد الذكاء الاصطناعي (Gemini Helper)
يتعامل مع واجهة برمجة تطبيقات Google Gemini لحل مراحل اللعبة ذكياً.
"""

import os
import json
import streamlit as st

try:
    import google.generativeai as genai
    _HAS_GEMINI = True
except ImportError:
    _HAS_GEMINI = False

def get_api_key() -> str:
    """استرجاع مفتاح API من إعدادات Streamlit أو متغيرات البيئة"""
    if not _HAS_GEMINI:
        return ""
    
    # Check Streamlit secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    
    # Check OS environment
    return os.environ.get("GEMINI_API_KEY", "")

def is_ai_available() -> bool:
    """التحقق من توفر مكتبة Gemini ووجود مفتاح API صحيح"""
    if not _HAS_GEMINI:
        return False
    return bool(get_api_key())

def get_model(model_name=None):
    """إعداد وإرجاع نموذج Gemini"""
    if not is_ai_available():
        raise RuntimeError("الذكاء الاصطناعي غير متوفر أو المفتاح مفقود.")
    
    if model_name is None:
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            import config
            model_name = getattr(config, 'GEMINI_MODEL', 'gemini-2.0-flash')
        except Exception:
            model_name = 'gemini-2.0-flash'

    api_key = get_api_key()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def _clean_json_response(text: str) -> str:
    """تنظيف النص الراجع من Gemini لاستخراج JSON فقط"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def ai_solve_from_image(image, extra_info="") -> dict:
    """
    محلل الصور لحل المرحلة الكاملة ذكياً.
    يأخذ كائن PIL Image ونص إضافي.
    """
    if not is_ai_available():
        return {"error": "مفتاح API غير متوفر. الرجاء إعداده أولاً."}
    
    try:
        model = get_model()
        prompt = f"""
أنت مساعد خبير في حل لعبة "كلمات كراش" العربية. سأعطيك صورة شاشة لمرحلة من اللعبة.
مهمتك هي اكتشاف نوع المرحلة (كلمات مبعثرة، مقاطع، أمثال، إلخ) وموضوعها، ثم استخراج الكلمات الممكنة والحلول المنطقية.
استخرج الحروف الموجودة، وإذا كان هناك صورة دلالية فصفها باختصار.
وإذا كان هناك إيموجي يدل على مثل عربي، استنتجه.

معلومات إضافية عن المرحلة: {extra_info}

من فضلك أرجع النتيجة بتنسيق JSON حصراً بدون أي نص خارجي، وفق الهيكل التالي:
{{
  "confidence": 85,
  "stage_type": "نوع المرحلة مثل 'كلمات مبعثرة' أو 'أمثال'",
  "topic": "موضوع المرحلة إن وجد",
  "image_description": "وصف الصورة إن وجدت",
  "available_letters": "الحروف المتوفرة للحل",
  "proverb": "المثل المكتشف إن كانت مرحلة أمثال",
  "solution": {{
    "main_words": ["كلمة1", "كلمة2"],
    "by_length": {{"3": ["كلم", "لكم"], "4": ["كلام"]}},
    "bonus_words": ["كلمةإضافية"]
  }},
  "explanation": "شرح ملخص لكيفية الاستنتاج",
  "tips": ["نصيحة1", "نصيحة2"]
}}
        """
        response = model.generate_content([prompt, image])
        json_str = _clean_json_response(response.text)
        
        result = json.loads(json_str)
        result["raw_response"] = response.text
        return result
        
    except Exception as e:
         return {"error": str(e)}

def ai_solve_proverb(emojis: str, letters: str = "", hint: str = "", word_count: int = 0) -> dict:
    """
    استنتاج المثل العربي من مجموعة إيموجي.
    """
    if not is_ai_available():
        return {"error": "مفتاح API غير متوفر. الرجاء إعداده أولاً."}
    
    try:
        model = get_model()
        prompt = f"""
أنت خبير في الأمثال والحكم العربية التراثية والشعبية. 
مهمتك هي ترجمة الإيموجي التالية إلى مثل أو حكمة عربية شهيرة جداً تستخدم في ألعاب العقل والألغاز كالعبة كلمات كراش.

الإيموجي: {emojis}

تلميحات مساعدة:
- الحروف المتاحة في اللوحة (إذا توفرت تساعدك): {letters}
- تلميح إضافي (إن وجد): {hint}
- عددلمات المثل (إن كان أكبر من 0 يجب أن تطابق): {word_count if word_count > 0 else 'غير محدد'}

أرجع النتيجة بتنسيق JSON حصراً بهذا الهيكل:
{{
  "proverb": "المثل الأكثر دقة ومطابقة",
  "confidence": 95,
  "meaning": "شرح لمعنى المثل",
  "emoji_analysis": "تفسير سريع لكيف يرمز الإيموجي للمثل",
  "alternatives": [
    {{"proverb": "مثل بديل1", "confidence": 80}},
    {{"proverb": "مثل بديل2", "confidence": 60}}
  ]
}}
        """
        response = model.generate_content(prompt)
        json_str = _clean_json_response(response.text)
        return json.loads(json_str)
        
    except Exception as e:
        return {"error": str(e)}

def hybrid_solve(trie, arabic_letters: str, topic: str = "", image_description: str = "") -> dict:
    """
    دمج قدرات القاموس المحلي مع الذكاء الاصطناعي لاستخراج أصح الكلمات.
    """
    from core.scrambler import solve_scrambled
    
    # 1. استخراج من القاموس المحلي
    trie_results = solve_scrambled(trie, arabic_letters, min_len=2)
    
    if not is_ai_available():
        return {
            "trie_results": trie_results,
            "ai_extra": [],
            "combined": trie_results,
            "ai_topic": "",
            "explanation": "الذكاء الاصطناعي معطل. هذه النتائج من القاموس فقط."
        }
    
    # 2. استخراج ذكي بواسطة AI
    try:
        model = get_model()
        prompt = f"""
بناءً على الحروف المبعثرة المتاحة التالية: "{arabic_letters}"
وبناءً على الموضوع (إن وجد): "{topic}"
ووصف الصورة (إن وجد): "{image_description}"

استخرج الكلمات العربية ذات المعنى والتي يمكن تشكيلها فقط وحصرياً من الحروف المتاحة (يمكنك التكرار بقدر عدد مرات ظهور الحرف ولكن ليس أكثر).
ركز خصوصاً على الكلمات المرتبطة بالموضوع أو وصف الصورة.

أرجع النتيجة בתنسيق JSON فقط:
{{
  "ai_topic": "لخص الموضوع أو الفكرة العامة للحل",
  "words": ["كلمة1", "كلمة2"],
  "explanation": "لماذا اقترحت هذه الكلمات بناءً على الموضوع المرجح"
}}
        """
        response = model.generate_content(prompt)
        json_str = _clean_json_response(response.text)
        ai_data = json.loads(json_str)
        
        ai_words = ai_data.get("words", [])
        
        # الجمع وتصفية المكررات
        # نتأكد أن كلمات الـ AI مصنوعة فعلا من حروف اللوحة إذا أمكن
        valid_ai_words = []
        for w in ai_words:
            # check validity against letters
            w_chars = list(w)
            avail_chars = list(arabic_letters)
            valid = True
            for ch in w_chars:
                if ch in avail_chars:
                    avail_chars.remove(ch)
                else:
                    valid = False
                    break
            if valid and w not in trie_results:
                valid_ai_words.append(w)
                
        combined = list(trie_results) + valid_ai_words
        
        return {
            "trie_results": trie_results,
            "ai_extra": valid_ai_words,
            "combined": combined,
            "ai_topic": ai_data.get("ai_topic", ""),
            "explanation": ai_data.get("explanation", "")
        }
    except Exception as e:
        return {
            "trie_results": trie_results,
            "ai_extra": [],
            "combined": trie_results,
            "ai_topic": "Error",
            "explanation": "حدث خطأ في الاتصال بالذكاء الاصطناعي: " + str(e)
        }

def ai_solve_scrambled(letters: str) -> list:
    """احتياطي في حال تم طلبه بشكل مباشر"""
    res = hybrid_solve(None, letters)
    return res.get("ai_extra", [])

