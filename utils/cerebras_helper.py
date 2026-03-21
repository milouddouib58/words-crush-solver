"""
🤖 مساعد سيريبراس (Cerebras Helper)
المحرك المنطقي فائق السرعة البديل لـ Mistral.
"""

import os
import json
import time
import streamlit as st

try:
    from cerebras.cloud.sdk import Cerebras
    _HAS_CEREBRAS = True
except ImportError:
    _HAS_CEREBRAS = False

def get_api_key() -> str:
    """استرجاع مفتاح Cerebras من الإعدادات"""
    if not _HAS_CEREBRAS:
        return ""
    try:
        if "CEREBRAS_API_KEY" in st.secrets:
            return st.secrets["CEREBRAS_API_KEY"]
    except Exception:
        pass
    return os.environ.get("CEREBRAS_API_KEY", "")

def is_ai_available() -> bool:
    """التحقق من توفر مكتبة Cerebras ووجود مفتاح API"""
    if not _HAS_CEREBRAS:
        return False
    return bool(get_api_key())

def get_client() -> Cerebras:
    """إعداد وإرجاع عميل Cerebras"""
    if not is_ai_available():
        raise RuntimeError("مفتاح Cerebras غير متوفر.")
    
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        import config
        model_name = getattr(config, 'CEREBRAS_MODEL', 'llama3.1-70b')
    except Exception:
        model_name = 'llama3.1-70b'
        
    return Cerebras(api_key=get_api_key()), model_name

def _clean_json_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def cerebras_solve_proverb(emojis: str, letters: str = "", hint: str = "", word_count: int = 0) -> dict:
    """حل الأمثال عبر Cerebras (Llama 3.1)"""
    if not is_ai_available():
        return {"error": "مفتاح Cerebras API غير متوفر."}
    
    try:
        client, model = get_client()
        prompt = f"""
أنت خبير في الأمثال والحكم العربية التراثية والشعبية. 
مهمتك هي ترجمة الإيموجي التالية إلى مثل أو حكمة عربية شهيرة بصيغتها الأصلية المستخدمة في الألغاز.

الإيموجي: {emojis}

تلميحات مساعدة:
- الحروف المتاحة في اللوحة: {letters}
- موضوع المثل: {hint}
- عدد كلمات المثل: {word_count if word_count > 0 else 'غير محدد'}

أرجع النتيجة بصيغة JSON حصراً بهذا الهيكل:
{{
  "proverb": "المثل الأكثر دقة",
  "confidence": 95,
  "meaning": "شرح المثل",
  "emoji_analysis": "تفسير الرموز",
  "alternatives": []
}}
        """
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            response_format={"type": "json_object"}
        )
        
        json_str = _clean_json_response(response.choices[0].message.content)
        return json.loads(json_str)
    except Exception as e:
        return {"error": f"خطأ في Cerebras Proverb: {str(e)}"}

def cerebras_solve_logic(arabic_letters: str, topic: str = "", image_description: str = "", trie_results: list = None, word_lengths: list = None, partial_words: list = None) -> dict:
    """الاستنتاج المنطقي للكلمات باستخدام Cerebras"""
    if not is_ai_available():
        return {"error": "مفتاح Cerebras API غير متوفر."}
    
    try:
        client, model = get_client()
        
        # تحسين البرومبت للكلمات المتقاطعة والمبعثرة
        context = []
        if topic: context.append(f"الموضوع: {topic}")
        if image_description: context.append(f"وصف الصورة: {image_description}")
        if word_lengths: context.append(f"أطوال الكلمات المطلوبة: {word_lengths}")
        if partial_words: context.append(f"كلمات الشبكة الناقصة (علامة _ هي الفراغ): {partial_words}")
        
        prompt = f"""
أنت خبير في حل لغز "كلمات كراش" (Words Crush). 
لديك الحروف التالية: [{arabic_letters}]

{chr(10).join(context)}

المساعدة من القاموس (كلمات ممكنة من الحروف): {trie_results[:20] if trie_results else "لا يوجد"}

المطلوب:
1. استنتج الكلمات التي تناسب {topic} و{image_description} وتطابق {word_lengths} و{partial_words}.
2. يجب أن تتكون الكلمات حصراً من الحروف المعطاة: {arabic_letters}.

أرجع النتيجة بتنسيق JSON حصراً:
{{
  "words": ["الكلمة1", "الكلمة2"],
  "explanation": "شرح منطقي قصير"
}}
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            response_format={"type": "json_object"}
        )
        
        json_str = _clean_json_response(response.choices[0].message.content)
        ai_data = json.loads(json_str)
        
        ai_words = ai_data.get("words", [])
        
        # تصفية التحقق من الحروف
        valid_ai_words = []
        for w in ai_words:
            w_chars = list(w)
            avail_chars = list(arabic_letters)
            valid = True
            for ch in w_chars:
                if ch in avail_chars:
                    avail_chars.remove(ch)
                else:
                    valid = False
            if valid: valid_ai_words.append(w)
            
        return {"words": valid_ai_words, "explanation": ai_data.get("explanation", ""), "model": model}
        
    except Exception as e:
        return {"error": f"خطأ في Cerebras Logic: {str(e)}"}
