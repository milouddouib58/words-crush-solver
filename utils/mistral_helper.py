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
except ImportError:
    _HAS_MISTRAL = False

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
        
    return Mistral(api_key=get_api_key()), model_name

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
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        json_str = _clean_json_response(response.choices[0].message.content)
        return json.loads(json_str)
        
    except Exception as e:
        return {"error": f"خطأ في الاتصال بمسترال: {str(e)}"}

def mistral_solve_logic(arabic_letters: str, topic: str = "", image_description: str = "", trie_results=None) -> dict:
    """
    منطق Mistral لدمج الحروف مع وصف الصورة (القادم من Gemini) واستخراج الكلمات.
    """
    if not is_ai_available():
         return {"error": "مفتاح Mistral API غير متوفر."}
         
    if trie_results is None:
        trie_results = []
        
    try:
        client, model = get_client()
        prompt = f"""
أنت خبير في لعبة الكلمات العربية (مثل كلمات كراش). 
لديك الحروف المبعثرة التالية: "{arabic_letters}"
وبناءً على الموضوع (إن وجد): "{topic}"
ووصف الصورة المعطى للحالة (إن وجد): "{image_description}"

استخرج الكلمات العربية المنطقية ذات المعنى والتي يمكن تشكيلها حصرياً من الحروف المتاحة (يمكنك تكرار الحرف بقدر عدد مرات ظهوره في سلسلة الحروف المعطاة وليس أكثر).
ركز خصوصاً على إيجاد الكلمات المرتبطة بالصورة، واستخدم معرفتك اللغوية لإنتاج كلمات إضافية دقيقة قد يغفل عنها القاموس العادي المعطى لك كالتالي: {trie_results[:20]}...

أرجع النتيجة بتنسيق JSON حصراً بهذا الهيكل:
{{
  "ai_topic": "لخص الموضوع أو الفكرة العامة للحل ومحتوى الصورة بلونين",
  "words": ["كلمة1", "كلمة2", "كلمة3"],
  "explanation": "لماذا اقترحت هذه الكلمات بناءً على وصف المشهد"
}}
        """
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
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
