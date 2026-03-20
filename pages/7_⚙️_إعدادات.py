"""
⚙️ صفحة الإعدادات
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie, add_words_to_file
import config


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


st.set_page_config(page_title="إعدادات", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
* { font-family: 'Tajawal', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("# ⚙️ الإعدادات")
st.markdown("---")

trie = get_trie()

# ===== إضافة كلمات =====
st.markdown("### ✏️ إضافة كلمات مخصصة")

new_words = st.text_area(
    "أدخل الكلمات الجديدة (كلمة في كل سطر أو مفصولة بمسافات)",
    placeholder="كلمة1\nكلمة2\nكلمة3",
    height=150
)

if st.button("➕ إضافة الكلمات", type="primary"):
    if new_words:
        words = new_words.replace('\n', ' ').split()
        arabic_words = [
            w.strip() for w in words
            if any('\u0600' <= c <= '\u06FF' for c in w)
        ]

        if arabic_words:
            count = 0
            for w in arabic_words:
                if not trie.search(w):
                    trie.insert(w)
                    count += 1

            if count > 0:
                try:
                    add_words_to_file(arabic_words)
                except Exception:
                    pass
                st.success(f"✅ تم إضافة {count} كلمة جديدة")
                st.cache_resource.clear()
            else:
                st.info("ℹ️ جميع الكلمات موجودة بالفعل")
        else:
            st.error("❌ لم يتم العثور على كلمات عربية")
    else:
        st.warning("⚠️ أدخل الكلمات أولاً")

st.markdown("---")

# ===== رفع ملف قاموس =====
st.markdown("### 📤 رفع ملف قاموس")

uploaded_dict = st.file_uploader(
    "ارفع ملف نصي يحتوي على كلمات",
    type=["txt"]
)

if uploaded_dict:
    content = uploaded_dict.read().decode('utf-8')
    words = [w.strip() for w in content.split('\n') if w.strip()]
    arabic_words = [
        w for w in words
        if any('\u0600' <= c <= '\u06FF' for c in w)
    ]

    st.info(f"📊 الملف يحتوي على {len(arabic_words)} كلمة عربية")

    if st.button("📥 استيراد الكلمات"):
        count = 0
        for w in arabic_words:
            if not trie.search(w):
                trie.insert(w)
                count += 1
        try:
            add_words_to_file(arabic_words)
        except Exception:
            pass
        st.success(f"✅ تم إضافة {count} كلمة جديدة")
        st.cache_resource.clear()

st.markdown("---")

# ===== تصدير القاموس =====
st.markdown("### 💾 تصدير القاموس")

if st.button("📋 تصدير القاموس الحالي"):
    all_words = trie.get_all_words()
    export_text = '\n'.join(sorted(all_words))
    st.download_button(
        "💾 تحميل القاموس",
        export_text,
        "arabic_dictionary.txt",
        "text/plain",
        use_container_width=True
    )
    st.info(f"📊 القاموس يحتوي على {len(all_words):,} كلمة")

st.markdown("---")

# ===== معلومات النظام =====
st.markdown("### ℹ️ معلومات النظام")

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    - **Python:** {sys.version.split()[0]}
    - **Streamlit:** {st.__version__}
    - **القاموس:** {len(trie):,} كلمة
    """)

with c2:
    try:
        from utils.ocr import check_ocr_deps
        deps = check_ocr_deps()
    except Exception:
        deps = {"cv2": False, "pytesseract": False, "PIL": False}

    st.markdown(f"""
    - **OpenCV:** {'✅' if deps['cv2'] else '❌ (اختياري)'}
    - **Tesseract:** {'✅' if deps['pytesseract'] else '❌ (اختياري)'}
    - **Pillow:** {'✅' if deps['PIL'] else '❌'}
    """)

st.markdown("---")

if st.button("🔄 مسح الذاكرة المؤقتة"):
    st.cache_resource.clear()
    st.rerun()
