"""
📊 صفحة الإحصائيات
"""

import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.filter import TOPIC_WORDS


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


st.set_page_config(page_title="إحصائيات", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

</style>
""", unsafe_allow_html=True)

st.markdown("# 📊 إحصائيات القاموس")
st.markdown("---")

trie = get_trie()


# ===== إحصائيات عامة =====
all_words = trie.get_all_words()
total = len(all_words)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📚 إجمالي الكلمات", f"{total:,}")

if all_words:
    longest = max(all_words, key=len)
    shortest = min(all_words, key=len)
    avg_len = sum(len(w) for w in all_words) / total

    with col2:
        st.metric("📏 متوسط الطول", f"{avg_len:.1f}")
    with col3:
        st.metric("📐 أطول كلمة", f"{len(longest)} حرف")
    with col4:
        st.metric("📐 أقصر كلمة", f"{len(shortest)} حرف")

    st.markdown("---")

    # ===== توزيع حسب الطول =====
    st.markdown("### 📏 توزيع الكلمات حسب الطول")

    length_dist = {}
    for w in all_words:
        l = len(w)
        length_dist[l] = length_dist.get(l, 0) + 1

    try:
        import plotly.express as px
        import plotly.graph_objects as go

        lengths = sorted(length_dist.keys())
        counts = [length_dist[l] for l in lengths]

        fig = go.Figure(data=[
            go.Bar(
                x=[f"{l} حرف" for l in lengths],
                y=counts,
                marker_color=[
                    f'hsl({i * 30}, 70%, 60%)' for i in range(len(lengths))
                ],
                text=counts,
                textposition='auto',
            )
        ])

        fig.update_layout(
            xaxis_title="طول الكلمة",
            yaxis_title="العدد",
            template="plotly_dark",
            height=400,
            font=dict(family="Tajawal", size=14),
        )

        st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        for l in sorted(length_dist.keys()):
            c = length_dist[l]
            bar = "█" * min(c // 3, 40)
            st.text(f"  {l:2d} حرف: {c:5d} {bar}")

    # ===== المواضيع =====
    st.markdown("---")
    st.markdown("### 📂 الكلمات حسب الموضوع")

    topic_data = {
        topic: len(words) for topic, words in TOPIC_WORDS.items()
    }

    try:
        import plotly.express as px

        fig2 = px.pie(
            names=list(topic_data.keys()),
            values=list(topic_data.values()),
            hole=0.4,
        )
        fig2.update_layout(
            template="plotly_dark",
            height=500,
            font=dict(family="Tajawal", size=13),
        )
        st.plotly_chart(fig2, use_container_width=True)

    except ImportError:
        for topic, count in topic_data.items():
            st.write(f"  {topic}: {count} كلمة")

    # ===== أمثلة =====
    st.markdown("---")
    st.markdown("### 🔤 أمثلة من القاموس")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**أطول كلمة:** {longest}")
    with col_b:
        st.markdown(f"**أقصر كلمة:** {shortest}")

    # كلمات عشوائية
    import random
    if len(all_words) > 20:
        sample = random.sample(all_words, 20)
        st.markdown("**عينة عشوائية:**")
        st.write(", ".join(sample))