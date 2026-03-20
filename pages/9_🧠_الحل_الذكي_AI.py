"""
🧠 الحل الذكي الشامل بالذكاء الاصطناعي
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- حل فوري من صورة الشاشة
- حل الأمثال من الإيموجي
- حل هجين (Trie + AI)
"""

import streamlit as st
import time
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.scrambler import solve_scrambled
from core.filter import filter_by_topic, get_available_topics
from utils.gemini_helper import (
    is_ai_available, ai_solve_from_image,
    ai_solve_scrambled, ai_solve_proverb,
    hybrid_solve
)


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


st.set_page_config(page_title="الحل الذكي AI", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif !important; }

.ai-header {
    text-align: center; padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    border-radius: 20px; color: white; margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(102,126,234,0.4);
}
.ai-header h1 { font-size: 2.5rem; margin: 0; }
.ai-header p { font-size: 1.1rem; opacity: 0.9; }

.word-chip {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; padding: 8px 18px; border-radius: 25px;
    margin: 4px; font-size: 1.1rem; font-weight: 600;
    box-shadow: 0 2px 8px rgba(102,126,234,0.3);
    transition: all 0.3s;
}
.word-chip:hover { transform: scale(1.08); }

.ai-word-chip {
    display: inline-block;
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white; padding: 8px 18px; border-radius: 25px;
    margin: 4px; font-size: 1.1rem; font-weight: 600;
    box-shadow: 0 2px 8px rgba(245,87,108,0.3);
}

.proverb-result {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    color: #1a1a2e; padding: 25px; border-radius: 15px;
    text-align: center; font-size: 1.6rem; font-weight: 700;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(67,233,123,0.3);
}

.confidence-bar {
    height: 8px; border-radius: 4px;
    background: #2a2d3e; margin: 5px 0;
}
.confidence-fill {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, #f5576c, #43e97b);
}

.solution-card {
    background: linear-gradient(135deg, #1e2130, #2a2d3e);
    border: 1px solid #3a3d4e; border-radius: 15px;
    padding: 1.5rem; margin: 0.8rem 0;
}

.mode-card {
    background: linear-gradient(135deg, #1e2130, #2a2d3e);
    border: 2px solid #3a3d4e; border-radius: 15px;
    padding: 2rem; text-align: center;
    transition: all 0.3s; cursor: pointer;
    height: 100%;
}
.mode-card:hover {
    border-color: #667eea;
    box-shadow: 0 8px 25px rgba(102,126,234,0.3);
    transform: translateY(-3px);
}
.mode-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.mode-title { font-size: 1.3rem; font-weight: 700; color: #667eea; }
.mode-desc { font-size: 0.9rem; color: #aaa; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

trie = get_trie()

# ═══ العنوان ═══
st.markdown("""
<div class="ai-header">
    <h1>🧠 الحل الذكي بالذكاء الاصطناعي</h1>
    <p>ارفع صورة أو أدخل إيموجي أو حروف — والذكاء الاصطناعي يحل لك فوراً!</p>
</div>
""", unsafe_allow_html=True)

# ═══ التحقق من AI ═══
ai_ready = is_ai_available()

if not ai_ready:
    st.error("""
    ⚠️ **مفتاح Gemini API غير مُعدّ**

    للتفعيل:
    1. اذهب إلى [Google AI Studio](https://aistudio.google.com/apikey)
    2. أنشئ مفتاح API مجاني
    3. في Streamlit Cloud: Settings → Secrets → أضف:
    ```
    GEMINI_API_KEY = "مفتاحك_هنا"
    ```
    أو أضفه في `.streamlit/secrets.toml` محلياً
    """)

    # عرض الحل التقليدي كبديل
    st.markdown("---")
    st.markdown("### ✏️ الحل التقليدي (بدون AI)")

    fallback_letters = st.text_input("أدخل الحروف", key="fallback")
    if fallback_letters and st.button("🔍 حل تقليدي"):
        arabic = ''.join(c for c in fallback_letters if '\u0600' <= c <= '\u06FF')
        if arabic:
            results = solve_scrambled(trie, arabic)
            if results:
                st.success(f"✅ {len(results)} كلمة")
                chips = ''.join(f'<span class="word-chip">{w}</span>' for w in results)
                st.markdown(chips, unsafe_allow_html=True)

    st.stop()

# ═══════════════════════════════════════════
#  اختيار وضع الحل
# ═══════════════════════════════════════════
st.markdown("## 🎯 اختر طريقة الحل")

mode = st.radio(
    "وضع الحل",
    [
        "📷 حل من صورة الشاشة (Vision AI)",
        "🔤 حل كلمات مبعثرة (Hybrid AI)",
        "📜 حل أمثال من إيموجي (AI)",
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")


# ═══════════════════════════════════════════
#  📷 الوضع 1: حل من صورة
# ═══════════════════════════════════════════
if mode == "📷 حل من صورة الشاشة (Vision AI)":

    st.markdown("### 📷 ارفع صورة الشاشة وسيحلها الذكاء الاصطناعي فوراً")

    uploaded = st.file_uploader(
        "📤 ارفع صورة المرحلة",
        type=["png", "jpg", "jpeg", "webp", "bmp"],
        key="vision_upload"
    )

    extra_info = st.text_input(
        "💡 معلومات إضافية (اختياري)",
        placeholder="مثال: المرحلة عن الحيوانات / المثل من 3 كلمات",
        key="vision_extra"
    )

    if uploaded:
        from PIL import Image
        image = Image.open(uploaded)

        col_img, col_sol = st.columns([1, 1.3])

        with col_img:
            st.image(image, caption="📸 صورة المرحلة", use_container_width=True)

        with col_sol:
            if st.button("🧠 حل المرحلة بالذكاء الاصطناعي", type="primary",
                        use_container_width=True, key="vision_solve"):

                with st.spinner("🤖 جاري تحليل الصورة وحل المرحلة..."):
                    start = time.time()
                    result = ai_solve_from_image(image, extra_info)
                    elapsed = time.time() - start

                if "error" in result:
                    st.error(f"❌ خطأ: {result['error']}")
                else:
                    confidence = result.get("confidence", 80)
                    st.success(f"✅ تم الحل في **{elapsed:.1f}** ثانية | الثقة: **{confidence}%**")

                    # شريط الثقة
                    st.markdown(f"""
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width:{confidence}%"></div>
                    </div>
                    """, unsafe_allow_html=True)

                    # نوع المرحلة
                    stage = result.get("stage_type", "غير محدد")
                    topic = result.get("topic", "")
                    desc = result.get("image_description", "")
                    letters = result.get("available_letters", "")

                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        st.info(f"📋 **نوع المرحلة:** {stage}")
                        if topic:
                            st.info(f"🏷️ **الموضوع:** {topic}")
                    with info_col2:
                        if desc:
                            st.info(f"🖼️ **وصف الصورة:** {desc}")
                        if letters:
                            st.info(f"🔤 **الحروف:** {letters}")

                    # المثل (إن وجد)
                    proverb = result.get("proverb", "")
                    if proverb:
                        st.markdown(f"""
                        <div class="proverb-result">📜 {proverb}</div>
                        """, unsafe_allow_html=True)

                    # الحل
                    solution = result.get("solution", {})
                    main_words = solution.get("main_words", [])
                    by_length = solution.get("by_length", {})
                    bonus = solution.get("bonus_words", [])

                    if main_words:
                        st.markdown("#### 🎯 الكلمات الرئيسية للحل:")
                        chips = ''.join(
                            f'<span class="word-chip">{w}</span>'
                            for w in main_words
                        )
                        st.markdown(chips, unsafe_allow_html=True)

                    if by_length:
                        st.markdown("#### 📏 حسب الطول:")
                        for length in sorted(by_length.keys(), reverse=True):
                            words = by_length[length]
                            if isinstance(words, list) and words:
                                with st.expander(f"📏 {length} حروف ({len(words)})"):
                                    chips = ''.join(
                                        f'<span class="word-chip">{w}</span>'
                                        for w in words
                                    )
                                    st.markdown(chips, unsafe_allow_html=True)

                    if bonus:
                        with st.expander(f"🌟 كلمات إضافية ({len(bonus)})"):
                            chips = ''.join(
                                f'<span class="ai-word-chip">{w}</span>'
                                for w in bonus
                            )
                            st.markdown(chips, unsafe_allow_html=True)

                    # الشرح
                    explanation = result.get("explanation", "")
                    tips = result.get("tips", [])

                    if explanation:
                        with st.expander("💡 شرح الحل"):
                            st.write(explanation)
                            if tips:
                                for tip in tips:
                                    st.write(f"  • {tip}")

                    # الاستجابة الخام
                    raw = result.get("raw_response", "")
                    if raw:
                        with st.expander("📝 الاستجابة الكاملة"):
                            st.text(raw)

                    # تصدير
                    st.markdown("---")
                    all_words = main_words + bonus
                    for ws in by_length.values():
                        if isinstance(ws, list):
                            all_words.extend(ws)
                    all_words = list(set(all_words))

                    st.download_button(
                        "💾 تحميل الحل",
                        json.dumps(result, ensure_ascii=False, indent=2),
                        "ai_solution.json",
                        "application/json",
                        use_container_width=True
                    )


# ═══════════════════════════════════════════
#  🔤 الوضع 2: حل هجين
# ═══════════════════════════════════════════
elif mode == "🔤 حل كلمات مبعثرة (Hybrid AI)":

    st.markdown("### 🔤 حل هجين: سرعة القاموس + ذكاء AI")

    col_in1, col_in2 = st.columns([2, 1])

    with col_in1:
        letters = st.text_input(
            "✏️ أدخل الحروف",
            placeholder="مثال: كتابلمعش",
            key="hybrid_letters"
        )

    with col_in2:
        topic = st.selectbox(
            "🏷️ الموضوع",
            ["بدون تصفية"] + get_available_topics(),
            key="hybrid_topic"
        )

    adv_col1, adv_col2 = st.columns(2)
    with adv_col1:
        image_desc = st.text_input(
            "🖼️ وصف صورة المرحلة (اختياري)",
            placeholder="مثال: حديقة حيوانات",
            key="hybrid_desc"
        )
    with adv_col2:
        word_lengths_str = st.text_input(
            "📏 أطوال الكلمات المطلوبة (اختياري)",
            placeholder="مثال: 3, 4, 5",
            key="hybrid_lengths"
        )

    if letters and st.button("🚀 حل هجين", type="primary",
                            use_container_width=True, key="hybrid_solve"):

        arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')

        if not arabic:
            st.error("❌ أدخل حروفاً عربية")
        else:
            with st.spinner("⚡ جاري الحل الهجين (Trie + AI)..."):
                start = time.time()

                topic_str = "" if topic == "بدون تصفية" else topic

                result = hybrid_solve(
                    trie, arabic,
                    topic=topic_str,
                    image_description=image_desc
                )

                elapsed = time.time() - start

            trie_results = result.get("trie_results", [])
            ai_extra = result.get("ai_extra", [])
            combined = result.get("combined", [])
            ai_topic = result.get("ai_topic", "")
            explanation = result.get("explanation", "")

            # إحصائيات
            st.success(
                f"✅ **{len(combined)}** كلمة "
                f"({len(trie_results)} قاموس + {len(ai_extra)} AI) "
                f"في **{elapsed:.2f}** ثانية"
            )

            if ai_topic:
                st.info(f"🏷️ الموضوع المكتشف بالـ AI: **{ai_topic}**")

            # تصفية حسب الطول المطلوب
            target_lengths = []
            if word_lengths_str:
                try:
                    target_lengths = [
                        int(x.strip()) for x in word_lengths_str.split(',')
                    ]
                except ValueError:
                    pass

            # عرض النتائج
            if target_lengths:
                st.markdown("#### 🎯 الكلمات بالأطوال المطلوبة:")
                for tl in sorted(target_lengths):
                    matched = [w for w in combined if len(w) == tl]
                    if matched:
                        st.markdown(f"**📏 {tl} حروف:**")
                        chips = ''.join(
                            f'<span class="word-chip">{w}</span>' for w in matched
                        )
                        st.markdown(chips, unsafe_allow_html=True)
                    else:
                        st.caption(f"📏 {tl} حروف: لا توجد كلمات")

            # كل النتائج
            st.markdown("#### 📚 كل الكلمات:")

            by_length = {}
            for w in combined:
                by_length.setdefault(len(w), []).append(w)

            tabs_labels = [
                f"📏 {l} حروف ({len(ws)})"
                for l, ws in sorted(by_length.items(), reverse=True)
            ]

            if tabs_labels:
                tabs = st.tabs(tabs_labels)
                for tab, (length, words) in zip(
                    tabs, sorted(by_length.items(), reverse=True)
                ):
                    with tab:
                        # تمييز كلمات AI
                        html = ""
                        for w in words:
                            if w in ai_extra:
                                html += f'<span class="ai-word-chip">🤖 {w}</span>'
                            else:
                                html += f'<span class="word-chip">{w}</span>'
                        st.markdown(html, unsafe_allow_html=True)

            # شرح AI
            if explanation:
                with st.expander("💡 تحليل الذكاء الاصطناعي"):
                    st.write(explanation)

            # تصدير
            st.markdown("---")
            export = {
                "letters": arabic,
                "topic": topic_str,
                "trie_count": len(trie_results),
                "ai_extra_count": len(ai_extra),
                "total": len(combined),
                "words": combined,
                "ai_extra": ai_extra,
            }
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    "📄 تحميل TXT",
                    '\n'.join(combined),
                    f"hybrid_{arabic}.txt",
                    "text/plain",
                    use_container_width=True
                )
            with dl_col2:
                st.download_button(
                    "📋 تحميل JSON",
                    json.dumps(export, ensure_ascii=False, indent=2),
                    f"hybrid_{arabic}.json",
                    "application/json",
                    use_container_width=True
                )


# ═══════════════════════════════════════════
#  📜 الوضع 3: حل أمثال
# ═══════════════════════════════════════════
elif mode == "📜 حل أمثال من إيموجي (AI)":

    st.markdown("### 📜 حل الأمثال بالذكاء الاصطناعي")
    st.markdown("أدخل الإيموجي الموجودة في المرحلة وسيكتشف المثل فوراً!")

    col_e, col_l = st.columns(2)

    with col_e:
        emojis = st.text_input(
            "🎭 أدخل الإيموجي",
            placeholder="مثال: 🐦✋🌳",
            key="proverb_emojis",
            help="انسخ الإيموجي من اللعبة والصقها هنا"
        )

    with col_l:
        proverb_letters = st.text_input(
            "🔤 الحروف المتاحة (اختياري)",
            placeholder="للتدقيق الإضافي",
            key="proverb_letters"
        )

    col_h, col_w = st.columns(2)
    with col_h:
        hint = st.text_input(
            "💡 تلميح (اختياري)",
            placeholder="مثال: عن الصبر",
            key="proverb_hint"
        )
    with col_w:
        word_count = st.number_input(
            "عدد كلمات المثل (0 = غير محدد)",
            0, 15, 0, key="proverb_wc"
        )

    # رفع صورة للمثل
    proverb_image = st.file_uploader(
        "📷 أو ارفع صورة المرحلة مباشرة",
        type=["png", "jpg", "jpeg", "webp"],
        key="proverb_img"
    )

    solve_proverb_btn = st.button(
        "🧠 اكتشف المثل",
        type="primary",
        use_container_width=True,
        key="proverb_solve"
    )

    if solve_proverb_btn:
        if proverb_image:
            # حل من الصورة مباشرة
            from PIL import Image
            img = Image.open(proverb_image)

            col_pi, col_pr = st.columns([1, 1.2])
            with col_pi:
                st.image(img, use_container_width=True)

            with col_pr:
                with st.spinner("🤖 جاري تحليل صورة المثل..."):
                    result = ai_solve_from_image(img, "هذه مرحلة أمثال عربية")

                proverb_text = result.get("proverb", "")
                if proverb_text:
                    st.markdown(f"""
                    <div class="proverb-result">📜 {proverb_text}</div>
                    """, unsafe_allow_html=True)

                sol = result.get("solution", {})
                main = sol.get("main_words", [])
                if main:
                    st.markdown("**كلمات الحل:**")
                    chips = ''.join(
                        f'<span class="word-chip">{w}</span>' for w in main
                    )
                    st.markdown(chips, unsafe_allow_html=True)

                explanation = result.get("explanation", "")
                if explanation:
                    with st.expander("💡 الشرح"):
                        st.write(explanation)

        elif emojis:
            with st.spinner("🤖 جاري تحليل الإيموجي واكتشاف المثل..."):
                start = time.time()
                result = ai_solve_proverb(
                    emojis=emojis,
                    letters=proverb_letters,
                    hint=hint,
                    word_count=word_count
                )
                elapsed = time.time() - start

            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                proverb = result.get("proverb", "")
                confidence = result.get("confidence", 0)
                meaning = result.get("meaning", "")
                analysis = result.get("emoji_analysis", "")
                alternatives = result.get("alternatives", [])

                # النتيجة الرئيسية
                st.markdown(f"""
                <div class="proverb-result">📜 {proverb}</div>
                """, unsafe_allow_html=True)

                # الثقة
                st.markdown(f"""
                <div style="text-align:center; margin:0.5rem 0;">
                    <span style="color:#aaa;">الثقة:</span>
                    <span style="color:{'#43e97b' if confidence > 70 else '#f5576c'};
                    font-weight:700; font-size:1.2rem;">{confidence}%</span>
                    <span style="color:#aaa;"> | الزمن: {elapsed:.1f} ث</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width:{confidence}%"></div>
                </div>
                """, unsafe_allow_html=True)

                # التفاصيل
                if meaning:
                    st.info(f"📖 **المعنى:** {meaning}")

                if analysis:
                    st.info(f"🔍 **تحليل الإيموجي:** {analysis}")

                # البدائل
                if alternatives:
                    st.markdown("#### 🔄 احتمالات أخرى:")
                    for alt in alternatives:
                        if isinstance(alt, dict):
                            alt_p = alt.get("proverb", "")
                            alt_c = alt.get("confidence", 0)
                            st.markdown(
                                f"  • **{alt_p}** "
                                f"<small style='color:#888;'>({alt_c}%)</small>",
                                unsafe_allow_html=True
                            )
                        elif isinstance(alt, str):
                            st.markdown(f"  • {alt}")
        else:
            st.warning("⚠️ أدخل الإيموجي أو ارفع صورة المرحلة")
