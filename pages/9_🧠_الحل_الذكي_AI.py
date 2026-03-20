"""
🧠 الحل الذكي بالذكاء الاصطناعي (Dual-LLM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- الموديل البصري (Gemini): يقوم بقراءة الصور واستخراج المشاهد والحروف.
- الموديل المنطقي (Mistral): يعالج الألغاز وتخمين الكلمات بدقة.
"""

import streamlit as st
import time
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.scrambler import solve_scrambled
from core.filter import get_available_topics
from utils.gemini_helper import is_ai_available as is_gemini_av, ai_extract_from_image
from utils.mistral_helper import is_ai_available as is_mistral_av, mistral_solve_logic, mistral_solve_proverb


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()

st.set_page_config(page_title="الحل الذكي AI (ثنائي التعقيد)", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif !important; }

.ai-header {
    text-align: center; padding: 2rem;
    background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%);
    border-radius: 20px; color: #1a1a2e; margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(31,64,55,0.3);
}
.ai-header h1 { font-size: 2.5rem; margin: 0; color: #111; }
.ai-header p { font-size: 1.1rem; opacity: 0.9; }

.word-chip {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; padding: 8px 18px; border-radius: 25px;
    margin: 4px; font-size: 1.1rem; font-weight: 600;
}
.ai-word-chip {
    display: inline-block;
    background: linear-gradient(135deg, #1f4037, #99f2c8);
    color: #111; padding: 8px 18px; border-radius: 25px;
    margin: 4px; font-size: 1.1rem; font-weight: 700;
}
.proverb-result {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white; padding: 25px; border-radius: 15px;
    text-align: center; font-size: 1.6rem; font-weight: 700;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

trie = get_trie()

st.markdown("""
<div class="ai-header">
    <h1>🧠 الحل المزدوج (Gemini + Mistral)</h1>
    <p>بنية ذكاء اصطناعي قوية: Gemini كعين لقراءة الصور، و Mistral كعقل لحل الألغاز المنطقية والأمثال!</p>
</div>
""", unsafe_allow_html=True)

gemini_ready = is_gemini_av()
mistral_ready = is_mistral_av()

if not (gemini_ready and mistral_ready):
    st.error("""
    ⚠️ **الهيكلة المزدوجة تتطلب تفعيل المفاتيح**
    الرجاء تسجيل المفاتيح التالية في الـ Secrets للعمل بكفاءة:
    - `GEMINI_API_KEY`: لمعالجة الصور
    - `MISTRAL_API_KEY`: للحل المنطقي والأمثال
    """)
    st.stop()


st.markdown("## 🎯 اختر طريقة الحل")
mode = st.radio(
    "وضع الحل",
    [
        "📷 حل من صورة الشاشة (Gemini يقرأ ➔ Mistral يحل)",
        "🔤 حل كلمات مبعثرة (Mistral Logic)",
        "📜 حل أمثال من إيموجي (Mistral NLP)",
    ],
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("---")


# ═══════════════════════════════════════════
#  📷 الوضع 1: حل من صورة (الدمج)
# ═══════════════════════════════════════════
if mode == "📷 حل من صورة الشاشة (Gemini يقرأ ➔ Mistral يحل)":
    uploaded = st.file_uploader(
        "📤 ارفع الصورة (Gemini سيصفها، ثم Mistral سيشتق الكلمات المنطقية)",
        type=["png", "jpg", "jpeg", "webp"]
    )
    extra_info = st.text_input("💡 معلومات مساعدة للمُحرك")

    if uploaded:
        from PIL import Image
        image = Image.open(uploaded)
        col_img, col_sol = st.columns([1, 1.3])
        
        with col_img:
            st.image(image, use_container_width=True)

        with col_sol:
            if st.button("🚀 تحليل وحل المرحلة المزدوج", type="primary", use_container_width=True):
                
                # 1. المرحلة البصرية
                with st.spinner("👁️ Gemini يقرأ الصورة حالياً..."):
                    vision_ext = ai_extract_from_image(image, extra_info)
                
                if "error" in vision_ext:
                    st.error(vision_ext["error"])
                else:
                    st.success("✅ أدرك Gemini محتوى الصورة!")
                    st.write(f"**نوع المرحلة المكتشف:** {vision_ext.get('stage_type')}")
                    st.write(f"**رؤية Gemini:** {vision_ext.get('image_description')}")
                    lengths = vision_ext.get("word_lengths", [])
                    if lengths:
                        st.info(f"📏 **المربعات المطلوبة:** {lengths}")
                    
                    # 2. المرحلة المنطقية
                    emojis = vision_ext.get("emojis", "")
                    letters = vision_ext.get("available_letters", "").replace(" ", "")
                    # تصفية فقط الأحرف العربية من result ["available_letters"]
                    arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')
                    
                    if "أمثال" in str(vision_ext.get("stage_type", "")) or (emojis and len(arabic) < 3):
                        st.info("📜 تُصنف كمرحلة أمثال، إحالة لـ Mistral لحلها...")
                        with st.spinner("🤖 Mistral يعالج الإيموجيات..."):
                            m_result = mistral_solve_proverb(emojis=emojis, letters=arabic, hint=vision_ext.get("topic", ""))
                        
                        if m_result.get("proverb"):
                            st.markdown(f"<div class='proverb-result'>📜 {m_result['proverb']}</div>", unsafe_allow_html=True)
                            st.write(f"**التحليل:** {m_result.get('emoji_analysis', '')}")
                        elif "error" in m_result:
                            st.error(m_result["error"])
                            
                    else:
                        st.info("🔤 مرحلة مبعثرة، إحالة لـ Mistral لاشتقاق الكلمات...")
                        with st.spinner("📊 فحص القاموس المحلي..."):
                            trie_words = solve_scrambled(trie, arabic)
                        
                        with st.spinner("🤖 Mistral يشتق الكلمات الناقصة بناءً على وصف Gemini والمربعات..."):
                            m_result = mistral_solve_logic(
                                arabic_letters=arabic,
                                topic=vision_ext.get("topic", ""),
                                image_description=vision_ext.get("image_description", ""),
                                trie_results=trie_words,
                                word_lengths=lengths
                            )
                        
                        if "error" in m_result:
                            st.error(m_result["error"])
                        else:
                            st.markdown("#### المستخرج النهائي:")
                            combined = m_result.get("combined", [])
                            ai_words = m_result.get("ai_extra", [])
                            
                            html = ""
                            for w in combined:
                                if w in ai_words:
                                    html += f"<span class='ai-word-chip'>🤖 {w}</span>"
                                else:
                                    html += f"<span class='word-chip'>{w}</span>"
                            st.markdown(html, unsafe_allow_html=True)
                            
                            if m_result.get("explanation"):
                                with st.expander("💡 شرح Mistral للاستنتاج"):
                                    st.write(m_result["explanation"])


# ═══════════════════════════════════════════
#  🔤 الوضع 2: حل هجين
# ═══════════════════════════════════════════
elif mode == "🔤 حل كلمات مبعثرة (Mistral Logic)":
    col1, col2 = st.columns([2, 1])
    with col1: letters = st.text_input("✏️ الحروف المتاحة المبعثرة", key="h_l")
    with col2: topic = st.selectbox("🏷️ الموضوع (اختياري)", ["بدون"] + get_available_topics(), key="h_t")
    
    desc = st.text_input("🖼️ هل هناك رسمة؟ صِفها هنا لمساعدة Mistral", key="h_d")
    lengths_str = st.text_input("📏 أطوال الكلمات المطلوبة (اختياري مثل: 4, 5)", key="h_len")
    
    if st.button("🚀 حل باستخدام Mistral", type="primary"):
        arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')
        parsed_lengths = []
        if lengths_str:
            try:
                parsed_lengths = [int(x.strip()) for x in lengths_str.split(",")]
            except: pass
        if not arabic:
            st.error("❌ حروف فارغة")
        else:
            with st.spinner("📊 قراءة القاموس..."):
                trie_words = solve_scrambled(trie, arabic)
            
            with st.spinner("🤖 معالجة المنطق عبر Mistral..."):
                topic_str = "" if topic == "بدون" else topic
                res = mistral_solve_logic(arabic, topic=topic_str, image_description=desc, trie_results=trie_words, word_lengths=parsed_lengths)
            
            if "error" in res:
                st.error(res["error"])
            else:
                st.success(f"تم العثور على {len(res.get('combined', []))} كلمة!")
                html = ""
                for w in res.get("combined", []):
                    if w in res.get("ai_extra", []):
                         html += f"<span class='ai-word-chip'>🤖 {w}</span>"
                    else:
                         html += f"<span class='word-chip'>{w}</span>"
                st.markdown(html, unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  📜 الوضع 3: حل أمثال
# ═══════════════════════════════════════════
elif mode == "📜 حل أمثال من إيموجي (Mistral NLP)":
    emojis = st.text_input("🎭 أدخل الإيموجي", placeholder="مثال: 🐦✋🌳")
    letters = st.text_input("🔤 الحروف المتاحة كدليل", placeholder="للتدقيق")
    
    if st.button("🧠 استنتج المثل عبر Mistral", type="primary"):
        if emojis.strip():
            with st.spinner("🤖 Mistral يحلل التعبيرات العامية..."):
                res = mistral_solve_proverb(emojis, letters)
            
            if "error" in res:
                st.error(res["error"])
            else:
                st.markdown(f"<div class='proverb-result'>📜 {res.get('proverb')}</div>", unsafe_allow_html=True)
                st.write(f"**المعنى الدلالي:** {res.get('meaning', '')}")
                alt = res.get("alternatives", [])
                if alt:
                    st.write("**بدائل أخرى قوية:**")
                    for a in alt:
                        if isinstance(a, dict):
                            st.write(f"- {a.get('proverb')} ({a.get('confidence')}%)")
        else:
            st.error("أدخل إيموجي!")
