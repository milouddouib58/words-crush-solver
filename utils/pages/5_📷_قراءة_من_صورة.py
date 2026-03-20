"""
📷 صفحة استخراج الحروف من صورة - محسّنة
"""

import streamlit as st
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.scrambler import solve_scrambled
from core.filter import (
    filter_by_topic, filter_by_length,
    get_available_topics, TOPIC_WORDS
)


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


st.set_page_config(page_title="قراءة من صورة", page_icon="📷", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif !important; }
.word-chip {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; padding: 8px 18px; border-radius: 25px;
    margin: 4px; font-size: 1.1rem; font-weight: 600;
    cursor: pointer; transition: all 0.3s;
    box-shadow: 0 2px 8px rgba(102,126,234,0.3);
}
.word-chip:hover { transform: scale(1.1); box-shadow: 0 4px 15px rgba(102,126,234,0.5); }
.upload-area {
    border: 3px dashed #667eea; border-radius: 20px;
    padding: 3rem; text-align: center;
    background: rgba(102,126,234,0.05);
    margin: 1rem 0;
}
.letter-display {
    font-size: 2.5rem; font-weight: 700;
    color: #667eea; text-align: center;
    padding: 1rem; letter-spacing: 15px;
    background: rgba(102,126,234,0.1);
    border-radius: 15px; margin: 1rem 0;
}
.step-box {
    background: linear-gradient(135deg, #1e2130, #2a2d3e);
    border: 1px solid #3a3d4e; border-radius: 12px;
    padding: 1.2rem; margin: 0.5rem 0;
    border-right: 4px solid #667eea;
}
.topic-btn {
    display: inline-block; background: #2a2d3e;
    color: #fafafa; padding: 8px 16px;
    border-radius: 10px; margin: 4px;
    border: 1px solid #3a3d4e;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📷 حل المرحلة من الصورة")
st.markdown("ارفع صورة المرحلة ← أدخل الحروف ← اختر الموضوع ← احصل على الحل!")
st.markdown("---")

trie = get_trie()

# ══════════════════════════════════════
#  الخطوة 1: رفع الصورة
# ══════════════════════════════════════
st.markdown("### 📌 الخطوة 1: ارفع صورة المرحلة")

uploaded = st.file_uploader(
    "اسحب الصورة هنا أو اضغط لاختيارها",
    type=["png", "jpg", "jpeg", "bmp", "webp"],
    help="ارفع لقطة شاشة من لعبة كلمات كراش"
)

extracted_letters = ""

if uploaded:
    col_img, col_info = st.columns([1, 1])

    with col_img:
        st.image(uploaded, caption="📸 صورة المرحلة", use_container_width=True)

    with col_info:
        # محاولة OCR
        ocr_result = ""
        try:
            from utils.ocr import check_ocr_deps, extract_from_pil_image
            deps = check_ocr_deps()
            if deps.get("pytesseract") and deps.get("PIL"):
                from PIL import Image
                image = Image.open(uploaded)
                with st.spinner("🤖 جاري التعرف على الحروف تلقائياً..."):
                    ocr_result = extract_from_pil_image(image)
                if ocr_result:
                    st.success(f"✅ تم التعرف تلقائياً: **{ocr_result}**")
                else:
                    st.info("💡 لم يتم التعرف تلقائياً - أدخل الحروف يدوياً")
            else:
                st.info("💡 أدخل الحروف التي تراها في الصورة")
        except Exception:
            st.info("💡 أدخل الحروف التي تراها في الصورة")

        st.markdown("""
        <div class="step-box">
            <b>💡 نصيحة:</b> انظر إلى الدوائر أو المربعات
            في الصورة واكتب الحروف التي تراها
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ══════════════════════════════════════
    #  الخطوة 2: إدخال/تعديل الحروف
    # ══════════════════════════════════════
    st.markdown("### 📌 الخطوة 2: أدخل الحروف")

    letters_col, info_col = st.columns([2, 1])

    with letters_col:
        letters = st.text_input(
            "✏️ اكتب الحروف التي تراها في الصورة",
            value=ocr_result,
            placeholder="مثال: ك ت ا ب ل م ع",
            key="image_letters",
            help="اكتب كل الحروف الموجودة في دوائر اللعبة"
        )

    with info_col:
        if letters:
            arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')
            if arabic:
                st.markdown(f"""
                <div class="letter-display">{arabic}</div>
                """, unsafe_allow_html=True)
                st.caption(f"🔢 عدد الحروف: {len(arabic)}")

    st.markdown("---")

    # ══════════════════════════════════════
    #  الخطوة 3: الموضوع والتصفية
    # ══════════════════════════════════════
    st.markdown("### 📌 الخطوة 3: حدد الموضوع (اختياري)")
    st.caption("اختيار الموضوع يساعد في تصفية النتائج وإظهار الكلمات الأنسب")

    topic_cols = st.columns(4)
    topics = get_available_topics()

    selected_topic = st.selectbox(
        "🏷️ اختر موضوع الصورة",
        ["الكل - بدون تصفية"] + topics,
        key="image_topic"
    )

    # إعدادات إضافية
    with st.expander("⚙️ إعدادات متقدمة"):
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        with adv_col1:
            min_len = st.number_input("أقل طول", 2, 10, 2, key="img_min")
        with adv_col2:
            max_len = st.number_input("أكثر طول", 3, 15, 10, key="img_max")
        with adv_col3:
            exact_len = st.number_input("طول محدد (0=الكل)", 0, 15, 0, key="img_exact")

    st.markdown("---")

    # ══════════════════════════════════════
    #  الخطوة 4: البحث والنتائج
    # ══════════════════════════════════════
    st.markdown("### 📌 الخطوة 4: احصل على الحل!")

    solve_btn = st.button(
        "🚀 حل المرحلة",
        type="primary",
        use_container_width=True,
        key="solve_image"
    )

    if solve_btn:
        if not letters:
            st.error("❌ أدخل الحروف أولاً!")
        else:
            arabic = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')

            if not arabic:
                st.error("❌ أدخل حروفاً عربية!")
            else:
                with st.spinner("🔍 جاري حل المرحلة..."):
                    progress = st.progress(0, "تحضير البحث...")

                    progress.progress(20, "البحث في القاموس...")
                    start = time.time()
                    results = solve_scrambled(
                        trie, arabic,
                        min_len=min_len,
                        max_len=max_len
                    )
                    elapsed = time.time() - start

                    progress.progress(60, "تطبيق التصفية...")

                    # تصفية حسب الموضوع
                    if selected_topic != "الكل - بدون تصفية":
                        topic_filtered = filter_by_topic(results, selected_topic)
                        remaining = [w for w in results if w not in topic_filtered]
                    else:
                        topic_filtered = results
                        remaining = []

                    # تصفية حسب الطول
                    if exact_len > 0:
                        topic_filtered = filter_by_length(
                            topic_filtered, exact_len=exact_len
                        )

                    progress.progress(100, "اكتمل!")
                    time.sleep(0.3)
                    progress.empty()

                # ═══ عرض النتائج ═══
                if topic_filtered:
                    st.success(
                        f"🎉 تم العثور على **{len(topic_filtered)}** كلمة "
                        f"في **{elapsed:.3f}** ثانية!"
                    )

                    # عرض الكلمات المرشحة (الأنسب)
                    if selected_topic != "الكل - بدون تصفية":
                        st.markdown("#### 🌟 الكلمات الأنسب للموضوع")

                    # تجميع حسب الطول
                    by_length = {}
                    for w in topic_filtered:
                        by_length.setdefault(len(w), []).append(w)

                    for length in sorted(by_length.keys(), reverse=True):
                        group = by_length[length]
                        with st.expander(
                            f"📏 كلمات من {length} حروف — {len(group)} كلمة",
                            expanded=(length >= 3)
                        ):
                            chips = ''.join(
                                f'<span class="word-chip">{w}</span>'
                                for w in group
                            )
                            st.markdown(chips, unsafe_allow_html=True)

                    # كلمات أخرى (غير مصفاة)
                    if remaining:
                        with st.expander(
                            f"📝 كلمات أخرى ممكنة ({len(remaining)})"
                        ):
                            other_chips = ''.join(
                                f'<span class="word-chip" '
                                f'style="background:#4a4d5e;">{w}</span>'
                                for w in remaining[:50]
                            )
                            st.markdown(other_chips, unsafe_allow_html=True)
                            if len(remaining) > 50:
                                st.caption(
                                    f"... و {len(remaining)-50} كلمة أخرى"
                                )

                    # ═══ التصدير ═══
                    st.markdown("---")
                    st.markdown("### 💾 تصدير النتائج")

                    dl_col1, dl_col2, dl_col3 = st.columns(3)

                    with dl_col1:
                        st.download_button(
                            "📄 ملف نصي",
                            '\n'.join(topic_filtered),
                            f"حل_{arabic}.txt",
                            "text/plain",
                            use_container_width=True
                        )

                    with dl_col2:
                        import json
                        export = {
                            "الحروف": arabic,
                            "الموضوع": selected_topic,
                            "العدد": len(topic_filtered),
                            "الكلمات": topic_filtered
                        }
                        st.download_button(
                            "📋 ملف JSON",
                            json.dumps(export, ensure_ascii=False, indent=2),
                            f"حل_{arabic}.json",
                            "application/json",
                            use_container_width=True
                        )

                    with dl_col3:
                        csv_text = "الكلمة,الطول\n"
                        csv_text += '\n'.join(
                            f"{w},{len(w)}" for w in topic_filtered
                        )
                        st.download_button(
                            "📊 ملف CSV",
                            csv_text,
                            f"حل_{arabic}.csv",
                            "text/csv",
                            use_container_width=True
                        )

                else:
                    st.warning("❌ لم يتم العثور على كلمات بهذه المعايير")
                    st.info("💡 جرب تغيير الموضوع أو تقليل الحد الأدنى للطول")

else:
    # ═══ بدون صورة ═══
    st.markdown("""
    <div class="upload-area">
        <h2>📤</h2>
        <h3>ارفع صورة المرحلة هنا</h3>
        <p style="color:#888;">
            التقط لقطة شاشة من اللعبة وارفعها<br>
            أو اسحب الصورة وأفلتها هنا
        </p>
    </div>
    """, unsafe_allow_html=True)

    # حل بدون صورة
    st.markdown("---")
    st.markdown("### ✏️ أو أدخل الحروف مباشرة بدون صورة")

    quick_col1, quick_col2 = st.columns([3, 1])

    with quick_col1:
        direct = st.text_input(
            "الحروف",
            placeholder="اكتب الحروف هنا...",
            key="direct_no_img"
        )
    with quick_col2:
        direct_topic = st.selectbox(
            "الموضوع",
            ["الكل"] + get_available_topics(),
            key="direct_topic"
        )

    if direct and st.button("🔍 حل", key="direct_solve"):
        arabic = ''.join(c for c in direct if '\u0600' <= c <= '\u06FF')
        if arabic:
            results = solve_scrambled(trie, arabic)
            if direct_topic != "الكل":
                results = filter_by_topic(results, direct_topic)
            if results:
                st.success(f"✅ {len(results)} كلمة")
                chips = ''.join(
                    f'<span class="word-chip">{w}</span>' for w in results
                )
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.warning("❌ لم يتم العثور على كلمات")
