"""
✝️ صفحة حل الكلمات المتقاطعة
"""

import streamlit as st
import time
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.crossword import solve_crossword


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


st.set_page_config(page_title="كلمات متقاطعة", page_icon="✝️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
*:not(.material-symbols-rounded):not(.material-icons):not(.stIcon):not([class*="icon"]) { font-family: 'Tajawal', sans-serif !important; }
.pattern-box {
    display: inline-block;
    width: 50px; height: 50px;
    border: 2px solid #667eea;
    border-radius: 8px;
    text-align: center;
    line-height: 50px;
    font-size: 1.5rem;
    font-weight: 700;
    margin: 3px;
    color: white;
}
.pattern-known { background: #667eea; }
.pattern-unknown { background: #2a2d3e; color: #888; }
.word-result {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    margin: 4px;
    font-size: 1.05rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# ✝️ حل الكلمات المتقاطعة")
st.markdown("أدخل النمط واستخدم **?** للحروف المجهولة")
st.markdown("---")

trie = get_trie()

# الإدخال
col1, col2 = st.columns([3, 1])

with col1:
    pattern = st.text_input(
        "✏️ أدخل النمط",
        placeholder="مثال: ???ب  أو  كت??",
        help="استخدم ? أو _ أو . للحروف المجهولة"
    )

with col2:
    max_results = st.number_input("عدد النتائج", 10, 500, 100)

# عرض النمط بصرياً
if pattern:
    boxes = ""
    for ch in pattern:
        if ch in ('?', '_', '.', '*'):
            boxes += '<span class="pattern-box pattern-unknown">?</span>'
        else:
            boxes += f'<span class="pattern-box pattern-known">{ch}</span>'
    st.markdown(f"<div style='text-align:center;margin:1rem 0;'>{boxes}</div>",
                unsafe_allow_html=True)

# البحث
if st.button("🔍 بحث", type="primary", use_container_width=True) and pattern:
    with st.spinner("🔍 جاري البحث..."):
        start = time.time()
        results = solve_crossword(trie, pattern, max_results)
        elapsed = time.time() - start

    if results:
        st.success(f"✅ تم العثور على **{len(results)}** كلمة ({elapsed:.3f} ث)")

        chips = ''.join(f'<span class="word-result">{w}</span>' for w in results)
        st.markdown(chips, unsafe_allow_html=True)

        st.download_button(
            "💾 تحميل",
            '\n'.join(results),
            f"crossword_{pattern}.txt",
            "text/plain"
        )
    else:
        st.warning("❌ لم يتم العثور على كلمات مطابقة")

# أمثلة
st.markdown("---")
with st.expander("💡 أمثلة"):
    st.markdown("""
    | النمط | الوصف |
    |-------|-------|
    | `???ب` | كلمة من 4 حروف تنتهي بالباء |
    | `كت??` | كلمة تبدأ بـ "كت" |
    | `?ل?` | كلمة من 3 حروف وسطها لام |
    | `م???ة` | كلمة من 5 حروف تبدأ بميم وتنتهي بتاء مربوطة |
    """)