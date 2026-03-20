"""
📜 صفحة الأمثال العربية
"""

import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.proverbs import solve_proverb, get_all_proverbs, complete_proverb, PROVERBS_DB


st.set_page_config(page_title="أمثال عربية", page_icon="📜", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif !important; }
.proverb-card {
    background: linear-gradient(135deg, #1e2130, #2a2d3e);
    border: 1px solid #3a3d4e;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0.8rem 0;
    border-right: 4px solid #667eea;
}
.proverb-text {
    font-size: 1.3rem;
    font-weight: 700;
    color: #fafafa;
}
.proverb-tags {
    color: #888;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📜 الأمثال والحكم العربية")
st.markdown("ابحث في قاعدة بيانات الأمثال الشعبية العربية")
st.markdown("---")

# طريقة البحث
search_method = st.radio(
    "طريقة البحث",
    ["🔍 بحث بكلمة مفتاحية", "✏️ إكمال مثل", "📚 عرض الكل"],
    horizontal=True
)

if search_method == "🔍 بحث بكلمة مفتاحية":
    keyword = st.text_input("أدخل كلمة مفتاحية", placeholder="مثال: صبر، علم، عمل")
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

elif search_method == "✏️ إكمال مثل":
    start = st.text_input("أدخل بداية المثل", placeholder="مثال: الصبر")
    if start:
        results = complete_proverb(start)
        if results:
            for p in results:
                st.markdown(f"""
                <div class="proverb-card">
                    <div class="proverb-text">📜 {p}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لم يتم العثور على أمثال تبدأ بهذا النص")

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