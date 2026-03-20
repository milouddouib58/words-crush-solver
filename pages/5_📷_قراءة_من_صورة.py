"""
📷 صفحة استخراج الحروف من صورة
"""

import streamlit as st
import time
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie
from core.scrambler import solve_scrambled
from utils.ocr import check_ocr_deps, extract_from_pil_image


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
st.markdown("ارفع صورة المرحلة واستخرج الحروف تلقائياً باستخدام OCR")
st.markdown("---")

trie = get_trie()

# التحقق من المتطلبات
deps = check_ocr_deps()
dep_col1, dep_col2, dep_col3 = st.columns(3)

with dep_col1:
    if deps["cv2"]:
        st.success("✅ OpenCV")
    else:
        st.error("❌ OpenCV")

with dep_col2:
    if deps["pytesseract"]:
        st.success("✅ Tesseract")
    else:
        st.error("❌ Tesseract")

with dep_col3:
    if deps["PIL"]:
        st.success("✅ Pillow")
    else:
        st.error("❌ Pillow")

st.markdown("---")

# رفع الصورة
uploaded = st.file_uploader(
    "📤 ارفع صورة المرحلة",
    type=["png", "jpg", "jpeg", "bmp"],
    help="ارفع لقطة شاشة من اللعبة"
)

if uploaded:
    col_img, col_result = st.columns(2)

    with col_img:
        st.image(uploaded, caption="الصورة المرفوعة", use_container_width=True)

    with col_result:
        if all(deps.values()):
            from PIL import Image
            image = Image.open(uploaded)

            with st.spinner("🔍 جاري استخراج الحروف..."):
                letters = extract_from_pil_image(image)

            if letters:
                st.success(f"✅ تم استخراج: **{letters}**")
            else:
                st.warning("⚠️ لم يتم استخراج حروف")
                letters = ""

            # تعديل يدوي
            edited = st.text_input(
                "✏️ تعديل الحروف (إذا لزم)",
                value=letters,
                key="ocr_edit"
            )

            if edited and st.button("🔍 ابحث", type="primary"):
                arabic = ''.join(
                    c for c in edited if '\u0600' <= c <= '\u06FF'
                )
                if arabic:
                    with st.spinner("🔍 جاري البحث..."):
                        results = solve_scrambled(trie, arabic)

                    if results:
                        st.success(f"✅ {len(results)} كلمة")
                        chips = ''.join(
                            f'<span class="word-chip">{w}</span>'
                            for w in results
                        )
                        st.markdown(chips, unsafe_allow_html=True)
                    else:
                        st.warning("❌ لم يتم العثور على كلمات")
        else:
            st.error("""
            ❌ المكتبات المطلوبة غير مكتملة

            لاستخدام OCR تحتاج:
            ```
            pip install pytesseract opencv-python-headless Pillow
            ```

            وتثبيت Tesseract OCR مع دعم العربية
            """)

            # إدخال يدوي كبديل
            manual = st.text_input("✏️ أو أدخل الحروف يدوياً")
            if manual and st.button("🔍 ابحث", key="manual_search"):
                arabic = ''.join(
                    c for c in manual if '\u0600' <= c <= '\u06FF'
                )
                if arabic:
                    results = solve_scrambled(trie, arabic)
                    if results:
                        st.success(f"✅ {len(results)} كلمة")
                        for w in results:
                            st.write(f"  • {w}")