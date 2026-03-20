"""
🔤 صفحة حل الكلمات المبعثرة
"""

import streamlit as st
import time
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.trie import load_trie
from core.scrambler import solve_scrambled, find_anagrams
from core.filter import (
    filter_by_topic, filter_by_length,
    get_available_topics, get_topic_words
)


# ===== تحميل القاموس =====
@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


# ===== إعداد الصفحة =====
st.set_page_config(page_title="حل الكلمات المبعثرة", page_icon="🔤", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif !important; }
.word-chip {
    display: inline-block;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    margin: 4px;
    font-size: 1.05rem;
    font-weight: 500;
    cursor: default;
    transition: transform 0.2s;
}
.word-chip:hover { transform: scale(1.1); }
.result-header {
    background: linear-gradient(135deg, #1e2130, #2a2d3e);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #3a3d4e;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ===== العنوان =====
st.markdown("# 🔤 حل الكلمات المبعثرة")
st.markdown("أدخل الحروف المتاحة في المرحلة وسنجد لك جميع الكلمات الممكنة")
st.markdown("---")

trie = get_trie()


# ===== الإدخال =====
col1, col2 = st.columns([2, 1])

with col1:
    letters = st.text_input(
        "✏️ أدخل الحروف",
        placeholder="مثال: كتابلمع",
        help="أدخل جميع الحروف المتاحة في المرحلة"
    )

with col2:
    st.markdown("### ⚙️ الإعدادات")
    min_len = st.slider("أقل طول للكلمة", 2, 8, 2)
    max_len = st.slider("أكثر طول للكلمة", 3, 15, 10)


# ===== خيارات التصفية =====
with st.expander("🔍 خيارات التصفية المتقدمة"):
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        selected_topic = st.selectbox(
            "📂 تصفية حسب الموضوع",
            ["بدون تصفية"] + get_available_topics()
        )

    with filter_col2:
        exact_length = st.number_input(
            "📏 طول محدد (0 = الكل)",
            min_value=0, max_value=15, value=0
        )

    image_desc = st.text_input(
        "🖼️ وصف صورة المرحلة (اختياري)",
        placeholder="مثال: حديقة حيوانات"
    )


# ===== زر البحث =====
search_btn = st.button("🔍 ابحث عن الكلمات", type="primary", use_container_width=True)

if search_btn and letters:
    arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')

    if not arabic:
        st.error("❌ يرجى إدخال حروف عربية")
    else:
        with st.spinner("🔍 جاري البحث في القاموس..."):
            start = time.time()
            results = solve_scrambled(
                trie, arabic,
                min_len=min_len,
                max_len=max_len
            )
            elapsed = time.time() - start

        # تطبيق التصفية
        if selected_topic != "بدون تصفية":
            results = filter_by_topic(results, selected_topic)

        if exact_length > 0:
            results = filter_by_length(results, exact_len=exact_length)

        if image_desc:
            from core.filter import filter_by_image_description
            results = filter_by_image_description(results, image_desc)

        # ===== عرض النتائج =====
        if results:
            st.markdown(f"""
            <div class="result-header">
                <h3 style="color:#667eea; margin:0;">
                    ✅ تم العثور على {len(results)} كلمة
                </h3>
                <p style="color:#aaa; margin:0.5rem 0 0 0;">
                    الحروف: {arabic} | الزمن: {elapsed:.3f} ثانية
                </p>
            </div>
            """, unsafe_allow_html=True)

            # تجميع حسب الطول
            by_length = {}
            for w in results:
                by_length.setdefault(len(w), []).append(w)

            # عرض بتبويبات
            tabs = st.tabs([
                f"📏 {l} حروف ({len(ws)})"
                for l, ws in sorted(by_length.items(), reverse=True)
            ])

            for tab, (length, words) in zip(
                tabs,
                sorted(by_length.items(), reverse=True)
            ):
                with tab:
                    chips = ''.join(
                        f'<span class="word-chip">{w}</span>'
                        for w in words
                    )
                    st.markdown(chips, unsafe_allow_html=True)

            # تصدير
            st.markdown("---")
            col_dl1, col_dl2 = st.columns(2)

            with col_dl1:
                st.download_button(
                    "💾 تحميل كملف نصي",
                    '\n'.join(results),
                    f"words_{arabic}.txt",
                    "text/plain",
                    use_container_width=True
                )

            with col_dl2:
                import json
                export = {
                    "letters": arabic,
                    "count": len(results),
                    "words": results,
                    "by_length": {
                        str(k): v for k, v in by_length.items()
                    }
                }
                st.download_button(
                    "📋 تحميل كـ JSON",
                    json.dumps(export, ensure_ascii=False, indent=2),
                    f"words_{arabic}.json",
                    "application/json",
                    use_container_width=True
                )
        else:
            st.warning("❌ لم يتم العثور على كلمات بهذه المعايير")

elif search_btn:
    st.warning("⚠️ يرجى إدخال الحروف أولاً")


# ===== الجناسات =====
st.markdown("---")
with st.expander("🔄 البحث عن جناسات (Anagrams)"):
    anagram_word = st.text_input("أدخل كلمة للبحث عن جناساتها", key="anagram")
    if anagram_word:
        anagrams = find_anagrams(trie, anagram_word)
        if anagrams:
            st.success(f"تم العثور على {len(anagrams)} جناس:")
            for a in anagrams:
                st.markdown(f"  • **{a}**")
        else:
            st.info("لا توجد جناسات لهذه الكلمة")