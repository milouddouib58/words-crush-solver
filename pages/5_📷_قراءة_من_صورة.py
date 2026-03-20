"""
📷 صفحة استخراج الحروف من صورة
"""

import streamlit as st
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.scrambler import solve_scrambled


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
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    margin: 4px;
    font-size: 1.05rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 📷 قراءة الحروف من صورة")
st.markdown("ارفع صورة المرحلة واستخرج الحروف أو أدخلها يدوياً")
st.markdown("---")

trie = get_trie()

# === التحقق من OCR ===
ocr_available = False
try:
    from utils.ocr import check_ocr_deps, extract_from_pil_image
    deps = check_ocr_deps()
    ocr_available = deps.get("pytesseract", False) and deps.get("PIL", False)
except Exception:
    deps = {"cv2": False, "pytesseract": False, "PIL": False}

# عرض حالة المكتبات
with st.expander("🔧 حالة مكتبات OCR"):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("✅ OpenCV" if deps["cv2"] else "❌ OpenCV")
    with c2:
        st.write("✅ Tesseract" if deps["pytesseract"] else "❌ Tesseract")
    with c3:
        st.write("✅ Pillow" if deps["PIL"] else "❌ Pillow")

    if not ocr_available:
        st.info("💡 OCR غير متاح حالياً - يمكنك إدخال الحروف يدوياً بعد رفع الصورة")

st.markdown("---")

# === رفع الصورة ===
uploaded = st.file_uploader(
    "📤 ارفع صورة المرحلة",
    type=["png", "jpg", "jpeg", "bmp", "webp"],
    help="ارفع لقطة شاشة من اللعبة"
)

if uploaded:
    col_img, col_result = st.columns(2)

    with col_img:
        st.image(uploaded, caption="الصورة المرفوعة", use_container_width=True)

    with col_result:
        extracted = ""

        # محاولة OCR إذا متاح
        if ocr_available:
            try:
                from PIL import Image
                image = Image.open(uploaded)
                with st.spinner("🔍 جاري استخراج الحروف..."):
                    extracted = extract_from_pil_image(image)
                if extracted:
                    st.success(f"✅ تم استخراج: **{extracted}**")
                else:
                    st.warning("⚠️ لم يتم استخراج حروف تلقائياً")
            except Exception as e:
                st.warning(f"⚠️ خطأ في OCR: {e}")
        else:
            st.info("📝 أدخل الحروف يدوياً من الصورة")

        # إدخال / تعديل يدوي
        letters = st.text_input(
            "✏️ أدخل أو عدّل الحروف",
            value=extracted,
            placeholder="أدخل الحروف التي تراها في الصورة",
            key="ocr_letters"
        )

        min_len = st.slider("أقل طول", 2, 8, 2, key="ocr_min")

        if st.button("🔍 ابحث عن الكلمات", type="primary", key="ocr_search"):
            if letters:
                arabic = ''.join(
                    c for c in letters if '\u0600' <= c <= '\u06FF'
                )
                if arabic:
                    with st.spinner("🔍 جاري البحث..."):
                        start = time.time()
                        results = solve_scrambled(trie, arabic, min_len=min_len)
                        elapsed = time.time() - start

                    if results:
                        st.success(
                            f"✅ {len(results)} كلمة ({elapsed:.3f} ث)"
                        )

                        # تجميع حسب الطول
                        by_length = {}
                        for w in results:
                            by_length.setdefault(len(w), []).append(w)

                        for length in sorted(by_length.keys(), reverse=True):
                            group = by_length[length]
                            with st.expander(
                                f"📏 {length} حروف ({len(group)} كلمة)"
                            ):
                                chips = ''.join(
                                    f'<span class="word-chip">{w}</span>'
                                    for w in group
                                )
                                st.markdown(chips, unsafe_allow_html=True)

                        # تحميل
                        st.download_button(
                            "💾 تحميل النتائج",
                            '\n'.join(results),
                            f"results_{arabic}.txt",
                            "text/plain"
                        )
                    else:
                        st.warning("❌ لم يتم العثور على كلمات")
                else:
                    st.error("❌ أدخل حروفاً عربية")
            else:
                st.warning("⚠️ أدخل الحروف أولاً")

else:
    # بدون صورة - إدخال يدوي فقط
    st.markdown("### ✏️ أو أدخل الحروف مباشرة")
    direct_letters = st.text_input(
        "الحروف",
        placeholder="أدخل الحروف هنا",
        key="direct_input"
    )

    if direct_letters and st.button("🔍 بحث", key="direct_search"):
        arabic = ''.join(
            c for c in direct_letters if '\u0600' <= c <= '\u06FF'
        )
        if arabic:
            results = solve_scrambled(trie, arabic)
            if results:
                st.success(f"✅ {len(results)} كلمة")
                chips = ''.join(
                    f'<span class="word-chip">{w}</span>' for w in results
                )
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.warning("❌ لم يتم العثور على كلمات")
