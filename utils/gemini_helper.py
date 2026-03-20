"""
👁️ مساعد جيميناي (Gemini Vision Helper)
تم تخصيص هذا الموديول للمعمارية المزدوجة ليكون "عين" التطبيق لقراءة الصور واستخراج محتواها.
"""

import os
import json
import time
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
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")

def is_ai_available() -> bool:
    """التحقق من التوفر"""
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
            model_name = getattr(config, 'GEMINI_VISION_MODEL', 'gemini-2.5-flash')
        except Exception:
            model_name = 'gemini-2.5-flash'

    api_key = get_api_key()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def _clean_json_response(text: str) -> str:
    """تنظيف النص الراجع من Gemini"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def ai_extract_from_image(image, extra_info="") -> dict:
    """
    مستخرج البيانات من الصور باستخدام قدرات Gemini للرؤية.
    لا يقوم بحل اللغز بل يرسل المعطيات لـ Mistral لاحقاً.
    """
    if not is_ai_available():
        return {"error": "مفتاح API الخاص بـ Gemini غير متوفر."}
    
    try:
        model = get_model()
        prompt = f"""
أنت محلل صور خبير للعبة "كلمات كراش" العربية.
المطلوب منك هو تفكيك لقطة الشاشة المرفقة لمعطيات خام بدون محاولة حل اللغز!

يرجى مراقبة الصورة واستخراج الآتي حصراً:
1. الحروف المعروضة كخيارات متناثرة.
2. وصف معمق ودقيق لمحتوى الصورة الاستدلالية (لأن هذا الوصف سيستخدمه ذكاء اصطناعي آخر لحل اللغز).
3. تحديد نوع المرحلة الظاهرة بوضوح (كلمات مبعثرة، أمثال، مقاطع، كلمات متقاطعة).
4. في حالة توفر إيموجيات فقط (لمرحلة الأمثال)، قم باستخراجها بدقة.

معلومات مساعدة: {extra_info}

أرجع النتيجة بصيغة JSON حصراً بهذا الهيكل بدون إضافات نصية:
{{
  "stage_type": "نوع المرحلة",
  "topic": "الفكرة العامة للوحة",
  "image_description": "وصف غني ودقيق لكل ما يظهر في صورة التلميح من كائنات وأشياء واضحة",
  "available_letters": "أسنان، ب، ج... (اكتب الحروف المتوفرة متلاصقة)",
  "emojis": "إن وجدت استخرجها"
}}
        """
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = model.generate_content([prompt, image])
                break
            except Exception as api_err:
                if "429" in str(api_err) and attempt < max_retries - 1:
                    time.sleep(15)
                    continue
                raise api_err
                
        json_str = _clean_json_response(response.text)
        return json.loads(json_str)
        
    except Exception as e:
         return {"error": f"خطأ في الاتصال بـ Gemini (لربما قيود الطلبات 429 أو خطأ في المفتاح): {str(e)}"}
