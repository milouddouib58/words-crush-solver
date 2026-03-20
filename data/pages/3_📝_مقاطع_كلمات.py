"""
📝 صفحة حل مقاطع الكلمات
"""

import streamlit as st
import time
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.syllables import solve_syllables


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


st.set_page_config(page_title="مقاطع كلمات", page_icon="📝", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif !important; }
.syllable-chip {
    display: inline-block;
    background: #764ba2;
    color: white;
    padding: 8px 18px;
    border-radius: 10px;
    margin: 5px;
    font-size: 1.2rem;
    font-weight: 700;
}
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

st.markdown("# 📝 حل مقاطع الكلمات")
st.markdown("أدخل المقاطع مفصولة بمسافات وسنحاول تركيب كلمات منها")
st.markdown("---")

trie = get_trie()

# الإدخال
syllables_input = st.text_input(
    "✏️ أدخل المقاطع (مفصولة بمسافات)",
    placeholder="مثال: مدر سة",
    help="افصل كل مقطع بمسافة"
)

col1, col2 = st.columns(2)
with col1:
    use_all = st.checkbox("يجب استخدام جميع المقاطع", value=False)
with col2:
    target_len = st.number_input("الطول المطلوب (0 = أي طول)", 0, 15, 0)

# عرض المقاطع
if syllables_input:
    syllables = syllables_input.split()
    chips = ''.join(f'<span class="syllable-chip">{s}</span>' for s in syllables)
    st.markdown(
        f"<div style='text-align:center;margin:1rem 0;'>{chips}</div>",
        unsafe_allow_html=True
    )

# البحث
if st.button("🔍 ركّب الكلمات", type="primary", use_container_width=True):
    if syllables_input:
        syllables = syllables_input.split()
        target = target_len if target_len > 0 else None

        with st.spinner("🔍 جاري التركيب..."):
            start = time.time()
            results = solve_syllables(trie, syllables, target, use_all=use_all)
            elapsed = time.time() - start

        if results:
            st.success(f"✅ تم العثور على **{len(results)}** كلمة ({elapsed:.3f} ث)")
            chips = ''.join(f'<span class="word-result">{w}</span>' for w in results)
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.warning("❌ لم يتم العثور على كلمات")
    else:
        st.warning("⚠️ أدخل المقاطع أولاً")