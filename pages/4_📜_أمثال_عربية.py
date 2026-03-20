"""
📜 صفحة الأمثال العربية - مع دعم AI
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.proverbs import (
    solve_proverb, get_all_proverbs,
    complete_proverb, PROVERBS_DB
)
from utils.gemini_helper import is_ai_available, ai_solve_proverb


st.set_page_config(page_title="أمثال عربية", page_icon="📜", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif !important; }
.proverb-card {
    background: linear-gradient(135deg, #1e2130, #2a2d3e);
    border: 1px solid #3a3d4e; border-radius: 12px;
    padding: 1.5rem; margin: 0.8rem 0;
    border-right: 4px solid #667eea;
}
.proverb-text { font-size: 1.3rem; font-weight: 700; color: #fafafa; }
.proverb-tags { color: #888; font-size: 0.85rem; margin-top: 0.5rem; }
.ai-result {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    color: #1a1a2e; padding: 25px; border-radius: 15px;
    text-align: center; font-size: 1.6rem; font-weight: 700;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(67,233,123,0.3);
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📜 الأمثال والحكم العربية")
st.markdown("---")

# طريقة البحث
ai_available = is_ai_available()

methods = ["🔍 بحث في القاعدة المحلية", "✏️ إكمال مثل", "📚 عرض الكل"]
if ai_available:
    methods.insert(0, "🧠 حل بالذكاء الاصطناعي (إيموجي)")

search_method = st.radio("طريقة البحث", methods, horizontal=True)


# ═══ AI Mode ═══
if search_method == "🧠 حل بالذكاء الاصطناعي (إيموجي)":

    st.markdown("### 🎭 أدخل الإيموجي من المرحلة")

    col1, col2 = st.columns(2)

    with col1:
        emojis = st.text_input(
            "الإيموجي",
            placeholder="🐦✋🌳",
            key="ai_emojis"
        )
    with col2:
        letters = st.text_input(
            "الحروف المتاحة (اختياري)",
            placeholder="للتدقيق",
            key="ai_letters"
        )

    hint = st.text_input("تلميح إضافي (اختياري)", key="ai_hint")

    if st.button("🧠 اكتشف المثل", type="primary", use_container_width=True):
        if emojis:
            with st.spinner("🤖 جاري التحليل..."):
                result = ai_solve_proverb(
                    emojis=emojis,
                    letters=letters,
                    hint=hint
                )

            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                proverb = result.get("proverb", "")
                confidence = result.get("confidence", 0)
                meaning = result.get("meaning", "")
                analysis = result.get("emoji_analysis", "")
                alternatives = result.get("alternatives", [])

                st.markdown(f'<div class="ai-result">📜 {proverb}</div>',
                           unsafe_allow_html=True)

                if confidence:
                    color = '#43e97b' if confidence > 70 else '#f5576c'
                    st.markdown(
                        f"<p style='text-align:center;'>"
                        f"الثقة: <b style='color:{color}'>{confidence}%</b></p>",
                        unsafe_allow_html=True
                    )

                if meaning:
                    st.info(f"📖 {meaning}")
                if analysis:
                    st.info(f"🔍 {analysis}")

                if alternatives:
                    with st.expander("🔄 احتمالات أخرى"):
                        for alt in alternatives:
                            if isinstance(alt, dict):
                                st.write(f"  • {alt.get('proverb', '')} ({alt.get('confidence', '')}%)")
                            else:
                                st.write(f"  • {alt}")
        else:
            st.warning("⚠️ أدخل الإيموجي أولاً")


# ═══ Local Search ═══
elif search_method == "🔍 بحث في القاعدة المحلية":
    keyword = st.text_input(
        "أدخل كلمة مفتاحية",
        placeholder="مثال: صبر، علم، عمل"
    )
    if keyword:
        results = solve_proverb(hint=keyword)
        if results:
            st.success(f"تم العثور على **{len(results)}** مثل")
            for p in results:
                tags = PROVERBS_DB.get(p, [])
                st.markdown(f"""
                <div class="proverb-card">
                    <div class="proverb-text">📜 {p}</div>
                    <div class="proverb-tags">🏷️ {', '.join(tags)}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لم يتم العثور على أمثال")

            # اقتراح AI
            if ai_available:
                if st.button("🧠 جرب الذكاء الاصطناعي"):
                    with st.spinner("🤖 ..."):
                        result = ai_solve_proverb(hint=keyword)
                    proverb = result.get("proverb", "")
                    if proverb:
                        st.markdown(f'<div class="ai-result">📜 {proverb}</div>',
                                   unsafe_allow_html=True)


elif search_method == "✏️ إكمال مثل":
    start_text = st.text_input("أدخل بداية المثل", placeholder="مثال: الصبر")
    if start_text:
        results = complete_proverb(start_text)
        if results:
            for p in results:
                st.markdown(f"""
                <div class="proverb-card">
                    <div class="proverb-text">📜 {p}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لم يتم العثور على أمثال")

else:
    proverbs = get_all_proverbs()
    st.info(f"📚 إجمالي الأمثال: **{len(proverbs)}**")
    for i, p in enumerate(proverbs, 1):
        tags = PROVERBS_DB.get(p, [])
        st.markdown(f"""
        <div class="proverb-card">
            <div class="proverb-text">{i}. {p}</div>
            <div class="proverb-tags">🏷️ {', '.join(tags)}</div>
        </div>
        """, unsafe_allow_html=True)
