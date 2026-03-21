"""
🤖 مساعد المسترال (Mistral Helper)
الذكاء الاصطناعي المنطقي للمشروع، ويتولى الألغاز النصية والمتقاطعة والأمثال.
"""

import os
import json
import time
import streamlit as st

try:
    from mistralai import Mistral
    _HAS_MISTRAL = True
    _MISTRAL_STYLE = "new"
except ImportError:
    try:
        from mistralai.client import MistralClient as Mistral
        _HAS_MISTRAL = True
        _MISTRAL_STYLE = "legacy"
    except ImportError:
        _HAS_MISTRAL = False
        _MISTRAL_STYLE = None

def get_api_key() -> str:
    """استرجاع مفتاح Mistral من الإعدادات"""
    if not _HAS_MISTRAL:
        return ""
    try:
        if "MISTRAL_API_KEY" in st.secrets:
            return st.secrets["MISTRAL_API_KEY"]
    except Exception:
        pass
    return os.environ.get("MISTRAL_API_KEY", "")

def is_ai_available() -> bool:
    """التحقق من توفر مكتبة Mistral ووجود مفتاح API صحيح"""
    if not _HAS_MISTRAL:
        return False
    return bool(get_api_key())

def get_client() -> Mistral:
    """إعداد وإرجاع عميل Mistral"""
    if not is_ai_available():
        raise RuntimeError("مفتاح Mistral غير متوفر أو المكتبة غير منصبة.")
    
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        import config
        model_name = getattr(config, 'MISTRAL_MODEL', 'mistral-large-latest')
    except Exception:
        model_name = 'mistral-large-latest'
    
    # تصحيح الموديلات القديمة إذا كان العميل قديم
    if _MISTRAL_STYLE == "legacy" and "latest" in model_name:
        if "large" in model_name: model_name = "mistral-medium"
        elif "small" in model_name: model_name = "mistral-small"
        
    api_key = get_api_key()
    if _MISTRAL_STYLE == "new":
        return Mistral(api_key=api_key), model_name
    else:
        # MistralClient constructor in legacy version
        from mistralai.client import MistralClient
        return MistralClient(api_key=api_key), model_name

def _clean_json_response(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def mistral_solve_proverb(emojis: str, letters: str = "", hint: str = "", word_count: int = 0) -> dict:
    """
    استنتاج المثل العربي من مجموعة إيموجي باستخدام براعة Mistral اللغوية.
    """
    if not is_ai_available():
        return {"error": "مفتاح Mistral API غير متوفر."}
    
    try:
        client, model = get_client()
        prompt = f"""
أنت خبير في الأمثال والحكم العربية التراثية والشعبية. 
مهمتك هي ترجمة الإيموجي التالية إلى مثل أو حكمة عربية شهيرة بصيغتها الأصلية المستخدمة في الألغاز.

الإيموجي: {emojis}

تلميحات مساعدة:
- الحروف المتاحة في اللوحة (إن توفرت تساعدك في استنتاج كلمات المثل): {letters}
- تلميح إضافي للموضوع (إن وجد): {hint}
- عدد كلمات المثل (إن كان أكبر من 0 يجب أن تطابق): {word_count if word_count > 0 else 'غير محدد'}

أرجع النتيجة بتنسيق JSON حصراً بهذا الهيكل بدون إضافات نصية:
{{
  "proverb": "المثل الأكثر دقة ومطابقة",
  "confidence": 95,
  "meaning": "شرح لمعنى المثل",
  "emoji_analysis": "تفسير سريع لكيف يرمز كل إيموجي لكلمات المثل",
  "alternatives": [
    {{"proverb": "مثل بديل1", "confidence": 80}},
    {{"proverb": "مثل بديل2", "confidence": 60}}
  ]
}}
        """
        if _MISTRAL_STYLE == "new":
            response = client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
        else:
            # Legacy style
            from mistralai.models.chat_completion import ChatMessage
            response = client.chat(
                model=model,
                messages=[ChatMessage(role="user", content=prompt)]
            )
        
        json_str = _clean_json_response(response.choices[0].message.content)
        return json.loads(json_str)
        
    except Exception as e:
        return {"error": f"خطأ في الاتصال بمسترال: {str(e)}"}

def mistral_solve_logic(arabic_letters: str, topic: str = "", image_description: str = "", trie_results=None, word_lengths=None, partial_words=None) -> dict:
    """
    منطق Mistral لدمج الحروف واستخراج الكلمات بالطول أو استنتاج الكلمات الناقصة في المتقاطعة.
    """
    if not is_ai_available():
         return {"error": "مفتاح Mistral API غير متوفر."}
         
    if trie_results is None:
        trie_results = []
        
    try:
        client, model = get_client()
        prompt = f"""
أنت خبير في لعبة الكلمات العربية (مثل كلمات كراش) وتعرف كيف تحل مراحل "الكلمات المبعثرة" و "الكلمات المتقاطعة". 
لديك الحروف المعطاة في اللوحة (لوحة المفاتيح أدناه): "{arabic_letters}"
وبناءً على الموضوع (إن وجد): "{topic}"
ووصف الصورة المعطى للحالة: "{image_description}"
أطوال الكلمات المطلوبة (إن توفرت): {word_lengths}
الكلمات المتقاطعة الناقصة في الشبكة (تحتوي على فراغ `_`): {partial_words}

مهمتك:
1. في الكلمات المتقاطعة: إذا توفرت "كلمات متقاطعة ناقصة" مثل (`م _ س و م`)، استنتج الكلمة الكاملة المرتبطة بقوة بتفاصيل الصورة (مثلاً: ساحر يقطع امرأة -> مقسوم). وتأكد أن الحرف الناقص لتكملة الكلمة موجود ضمن الحروف المعطاة "{arabic_letters}".
2. في الكلمات المبعثرة: استخرج الكلمات المتوافقة مع أطوال المربعات المطلوبة "{word_lengths}".
3. استخرج الكلمات ذات المعنى المرتبطة بشدة بوصف المشهد، ولا تتجاوز تكرارات الحروف المتاحة.
4. القاموس العادي استخرج هذه الكلمات مبدئياً: {trie_results[:20]}...

أرجع النتيجة بتنسيق JSON حصراً بهذا الهيكل:
{{
  "ai_topic": "لخص الفكرة العامة للمشهد واللغز بكلمتين",
  "words": ["الكلمة_المكتملة_الأولى", "الكلمة_الثانية"],
  "explanation": "شرح منطقي قصير جداً لسبب اختيارك الكلمات بناءً على تقاطعها مع المشهد والمربعات/الفراغات"
}}
        """
        if _MISTRAL_STYLE == "new":
            response = client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
        else:
            # Legacy style
            from mistralai.models.chat_completion import ChatMessage
            response = client.chat(
                model=model,
                messages=[ChatMessage(role="user", content=prompt)]
            )
        
        json_str = _clean_json_response(response.choices[0].message.content)
        ai_data = json.loads(json_str)
        
        ai_words = ai_data.get("words", [])
        
        # تصفية الكلمات المستخرجة للتأكد من أنها تصاغ فعلاً من الحروف المتاحة
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
        return {"error": f"خطأ في الاتصال بمسترال: {str(e)}"}
