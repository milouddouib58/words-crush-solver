"""
🛠️ أدوات مساعدة إضافية
"""

import streamlit as st
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.scrambler import solve_scrambled, find_anagrams
from core.crossword import solve_crossword
from core.filter import filter_by_topic, get_available_topics, TOPIC_WORDS


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


st.set_page_config(page_title="أدوات مساعدة", page_icon="🛠️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

.word-chip {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; padding: 6px 16px; border-radius: 20px;
    margin: 4px; font-size: 1rem;
}
.tool-card {
    background: linear-gradient(135deg, #1e2130, #2a2d3e);
    border: 1px solid #3a3d4e; border-radius: 12px;
    padding: 1.5rem; text-align: center;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🛠️ أدوات مساعدة")
st.markdown("---")

trie = get_trie()

# ═══ اختيار الأداة ═══
tool = st.selectbox("اختر الأداة", [
    "🔍 التحقق من كلمة",
    "📝 إكمال كلمة",
    "🔄 جناسات (Anagrams)",
    "📊 تحليل الحروف",
    "🎯 حل مرحلة متعددة الأسئلة",
    "📚 استكشاف القاموس",
    "🏷️ استكشاف الموضوعات",
])

st.markdown("---")

# ═══════════════════════════════════
if tool == "🔍 التحقق من كلمة":
    st.markdown("### 🔍 هل هذه الكلمة موجودة في القاموس؟")

    word = st.text_input("أدخل الكلمة", placeholder="مثال: مدرسة")

    if word:
        if trie.search(word):
            st.success(f"✅ الكلمة **{word}** موجودة في القاموس!")
        else:
            st.error(f"❌ الكلمة **{word}** غير موجودة")

            # اقتراحات
            suggestions = []
            for i in range(len(word)):
                pattern = list(word)
                pattern[i] = '?'
                results = solve_crossword(trie, ''.join(pattern))
                suggestions.extend(results)
            suggestions = list(set(suggestions))[:20]

            if suggestions:
                st.info("💡 هل تقصد:")
                chips = ''.join(
                    f'<span class="word-chip">{w}</span>' for w in suggestions
                )
                st.markdown(chips, unsafe_allow_html=True)


# ═══════════════════════════════════
elif tool == "📝 إكمال كلمة":
    st.markdown("### 📝 إكمال كلمة من بدايتها")

    prefix = st.text_input("أدخل بداية الكلمة", placeholder="مثال: مدر")

    if prefix:
        completions = trie.get_words_with_prefix(prefix)

        if completions:
            st.success(f"✅ {len(completions)} كلمة تبدأ بـ **{prefix}**")

            # تجميع حسب الطول
            by_len = {}
            for w in completions:
                by_len.setdefault(len(w), []).append(w)

            for length in sorted(by_len.keys()):
                with st.expander(f"📏 {length} حروف ({len(by_len[length])})"):
                    chips = ''.join(
                        f'<span class="word-chip">{w}</span>'
                        for w in by_len[length]
                    )
                    st.markdown(chips, unsafe_allow_html=True)
        else:
            st.warning(f"❌ لا توجد كلمات تبدأ بـ **{prefix}**")


# ═══════════════════════════════════
elif tool == "🔄 جناسات (Anagrams)":
    st.markdown("### 🔄 إيجاد جناسات الكلمة")
    st.caption("الجناسات: كلمات تُكوّن من نفس الحروف بترتيب مختلف")

    word = st.text_input("أدخل الكلمة", placeholder="مثال: بحر", key="anagram_word")

    if word:
        with st.spinner("🔍 جاري البحث..."):
            anagrams = find_anagrams(trie, word)

        if anagrams:
            st.success(f"✅ {len(anagrams)} جناس لكلمة **{word}**")
            chips = ''.join(
                f'<span class="word-chip">{w}</span>' for w in anagrams
            )
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.info(f"لا توجد جناسات لكلمة **{word}**")

        # كلمات أقصر من نفس الحروف
        st.markdown("#### كلمات أخرى من نفس الحروف:")
        shorter = solve_scrambled(trie, word)
        shorter = [w for w in shorter if w != word]
        if shorter:
            chips = ''.join(
                f'<span class="word-chip">{w}</span>' for w in shorter[:30]
            )
            st.markdown(chips, unsafe_allow_html=True)


# ═══════════════════════════════════
elif tool == "📊 تحليل الحروف":
    st.markdown("### 📊 تحليل الحروف")
    st.caption("اعرف كم كلمة يمكن تكوينها من حروفك")

    letters = st.text_input("أدخل الحروف", key="analyze_letters")

    if letters:
        arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')
        if arabic:
            with st.spinner("🔍 جاري التحليل..."):
                results = solve_scrambled(trie, arabic)

            # إحصائيات
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("عدد الحروف", len(arabic))
            with c2:
                st.metric("عدد الكلمات", len(results))
            with c3:
                if results:
                    st.metric("أطول كلمة", max(len(w) for w in results))
            with c4:
                if results:
                    st.metric("أقصر كلمة", min(len(w) for w in results))

            # توزيع حسب الطول
            if results:
                by_len = {}
                for w in results:
                    by_len.setdefault(len(w), []).append(w)

                try:
                    import plotly.graph_objects as go
                    lengths = sorted(by_len.keys())
                    counts = [len(by_len[l]) for l in lengths]

                    fig = go.Figure(data=[
                        go.Bar(
                            x=[f"{l} حرف" for l in lengths],
                            y=counts,
                            marker_color='#667eea',
                            text=counts,
                            textposition='auto',
                        )
                    ])
                    fig.update_layout(
                        template="plotly_dark", height=350,
                        xaxis_title="طول الكلمة", yaxis_title="العدد",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except ImportError:
                    for l in sorted(by_len.keys()):
                        st.write(f"  {l} حرف: {len(by_len[l])} كلمة")

                # تصفية حسب الموضوع
                st.markdown("#### 🏷️ توزيع حسب الموضوع:")
                for topic_name in get_available_topics():
                    filtered = filter_by_topic(results, topic_name)
                    if filtered and len(filtered) < len(results):
                        st.write(f"  {topic_name}: {len(filtered)} كلمة")


# ═══════════════════════════════════
elif tool == "🎯 حل مرحلة متعددة الأسئلة":
    st.markdown("### 🎯 حل مرحلة بها عدة أسئلة")
    st.caption("أدخل الحروف وأطوال الكلمات المطلوبة")

    letters = st.text_input("الحروف المتاحة", key="multi_letters")
    lengths_input = st.text_input(
        "أطوال الكلمات المطلوبة (مفصولة بفاصلة)",
        placeholder="مثال: 3, 4, 5",
        key="multi_lengths"
    )
    topic = st.selectbox(
        "الموضوع",
        ["بدون"] + get_available_topics(),
        key="multi_topic"
    )

    if letters and lengths_input:
        if st.button("🚀 حل", type="primary", key="multi_solve"):
            arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')
            try:
                lengths = [int(x.strip()) for x in lengths_input.split(',')]
            except ValueError:
                st.error("❌ أدخل الأطوال كأرقام مفصولة بفاصلة")
                lengths = []

            if arabic and lengths:
                all_results = solve_scrambled(trie, arabic)

                if topic != "بدون":
                    all_results = filter_by_topic(all_results, topic)

                for target_len in sorted(lengths):
                    matched = [w for w in all_results if len(w) == target_len]
                    st.markdown(f"#### 📏 كلمات من {target_len} حروف:")
                    if matched:
                        chips = ''.join(
                            f'<span class="word-chip">{w}</span>'
                            for w in matched
                        )
                        st.markdown(chips, unsafe_allow_html=True)
                    else:
                        st.caption("لا توجد كلمات بهذا الطول")


# ═══════════════════════════════════
elif tool == "📚 استكشاف القاموس":
    st.markdown("### 📚 استكشاف القاموس")

    search = st.text_input("ابحث عن كلمة أو جزء منها", key="explore")

    if search:
        all_words = trie.get_all_words()
        matches = [w for w in all_words if search in w]

        if matches:
            st.success(f"✅ {len(matches)} كلمة تحتوي على **{search}**")
            chips = ''.join(
                f'<span class="word-chip">{w}</span>'
                for w in matches[:100]
            )
            st.markdown(chips, unsafe_allow_html=True)
            if len(matches) > 100:
                st.caption(f"... و {len(matches)-100} كلمة أخرى")
        else:
            st.info("لا توجد كلمات مطابقة")


# ═══════════════════════════════════
elif tool == "🏷️ استكشاف الموضوعات":
    st.markdown("### 🏷️ استكشاف الموضوعات")

    for topic_name, topic_words in TOPIC_WORDS.items():
        with st.expander(f"{topic_name} ({len(topic_words)} كلمة)"):
            chips = ''.join(
                f'<span class="word-chip">{w}</span>' for w in topic_words
            )
            st.markdown(chips, unsafe_allow_html=True)
