"""
⚙️ صفحة الإعدادات - محدثة مع إعدادات AI
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.trie import load_trie, add_words_to_file
from utils.gemini_helper import is_ai_available, get_api_key
import config


@st.cache_resource(show_spinner=False)
def get_trie():
    return load_trie()


st.set_page_config(page_title="إعدادات", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
*:not(.material-symbols-rounded):not(.material-icons):not(.stIcon):not([class*="icon"]) { font-family: 'Tajawal', sans-serif !important; }
.status-ok { color: #43e97b; font-weight: 700; }
.status-no { color: #f5576c; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.markdown("# ⚙️ الإعدادات")
st.markdown("---")

trie = get_trie()

# ═══════════════════════════════════
#  حالة النظام
# ═══════════════════════════════════
st.markdown("### 📊 حالة النظام")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📚 القاموس", f"{len(trie):,} كلمة")

with col2:
    ai_ok = is_ai_available()
    if ai_ok:
        st.markdown("🧠 **الذكاء الاصطناعي:** <span class='status-ok'>✅ مفعّل</span>",
                    unsafe_allow_html=True)
    else:
        st.markdown("🧠 **الذكاء الاصطناعي:** <span class='status-no'>❌ غير مفعّل</span>",
                    unsafe_allow_html=True)

with col3:
    try:
        from utils.ocr import check_ocr_deps
        deps = check_ocr_deps()
        ocr_ok = deps.get("pytesseract", False)
    except Exception:
        ocr_ok = False

    if ocr_ok:
        st.markdown("📷 **OCR:** <span class='status-ok'>✅ متاح</span>",
                    unsafe_allow_html=True)
    else:
        st.markdown("📷 **OCR:** <span class='status-no'>❌ غير متاح</span>",
                    unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════
#  إعداد Gemini API
# ═══════════════════════════════════
st.markdown("### 🧠 إعداد الذكاء الاصطناعي (Gemini API)")

if ai_ok:
    st.success("✅ مفتاح API مُعدّ وجاهز للعمل")

    # اختبار الاتصال
    if st.button("🔍 اختبار الاتصال بـ AI"):
        with st.spinner("جاري الاختبار..."):
            try:
                from utils.gemini_helper import get_model
                model = get_model()
                response = model.generate_content("قل: مرحباً أنا جاهز!")
                st.success(f"✅ الاتصال ناجح: {response.text.strip()}")
            except Exception as e:
                st.error(f"❌ خطأ: {e}")
else:
    st.warning("""
    ⚠️ **مفتاح API غير مُعدّ**

    للحصول على مفتاح مجاني:
    1. اذهب إلى [Google AI Studio](https://aistudio.google.com/apikey)
    2. سجل دخولك بحساب Google
    3. اضغط **"Create API Key"**
    4. انسخ المفتاح
    """)

    st.markdown("#### طريقة الإضافة:")

    st.markdown("""
    **على Streamlit Cloud:**
    1. اذهب إلى إعدادات التطبيق (⚙️)
    2. اختر **Secrets**
    3. أضف:
    ```toml
    GEMINI_API_KEY = "مفتاحك_هنا"
    ```

    **محلياً:**
    أنشئ ملف `.streamlit/secrets.toml`:
    ```toml
    GEMINI_API_KEY = "مفتاحك_هنا"
    ```
    """)

st.markdown("---")

# ═══════════════════════════════════
#  إضافة كلمات
# ═══════════════════════════════════
st.markdown("### ✏️ إضافة كلمات مخصصة")

new_words = st.text_area(
    "أدخل الكلمات الجديدة",
    placeholder="كلمة1\nكلمة2\nكلمة3",
    height=120
)

if st.button("➕ إضافة", type="primary"):
    if new_words:
        words = new_words.replace('\n', ' ').split()
        arabic = [w.strip() for w in words if any('\u0600' <= c <= '\u06FF' for c in w)]
        if arabic:
            count = 0
            for w in arabic:
                if not trie.search(w):
                    trie.insert(w)
                    count += 1
            if count > 0:
                try:
                    add_words_to_file(arabic)
                except Exception:
                    pass
                st.success(f"✅ تم إضافة {count} كلمة")
                st.cache_resource.clear()
            else:
                st.info("ℹ️ الكلمات موجودة بالفعل")

st.markdown("---")

# ═══════════════════════════════════
#  رفع ملف قاموس
# ═══════════════════════════════════
st.markdown("### 📤 رفع ملف قاموس")

uploaded = st.file_uploader("ملف نصي (كلمة في كل سطر)", type=["txt"])
if uploaded:
    content = uploaded.read().decode('utf-8')
    words = [w.strip() for w in content.split('\n') if w.strip()]
    arabic = [w for w in words if any('\u0600' <= c <= '\u06FF' for c in w)]
    st.info(f"📊 {len(arabic)} كلمة عربية")

    if st.button("📥 استيراد"):
        count = 0
        for w in arabic:
            if not trie.search(w):
                trie.insert(w)
                count += 1
        try:
            add_words_to_file(arabic)
        except Exception:
            pass
        st.success(f"✅ {count} كلمة جديدة")
        st.cache_resource.clear()

st.markdown("---")

# ═══════════════════════════════════
#  تصدير ومعلومات
# ═══════════════════════════════════
st.markdown("### 💾 تصدير القاموس")

if st.button("📋 تصدير"):
    all_words = trie.get_all_words()
    st.download_button(
        "💾 تحميل",
        '\n'.join(sorted(all_words)),
        "arabic_dictionary.txt",
        "text/plain",
        use_container_width=True
    )
    st.info(f"📊 {len(all_words):,} كلمة")

st.markdown("---")

st.markdown("### ℹ️ معلومات النظام")
st.markdown(f"""
- **Python:** {sys.version.split()[0]}
- **Streamlit:** {st.__version__}
- **القاموس:** {len(trie):,} كلمة
- **AI:** {'✅ Gemini' if ai_ok else '❌'}
- **OCR:** {'✅' if ocr_ok else '❌ (اختياري)'}
- **النظام:** {os.name}
""")

if st.button("🔄 مسح الذاكرة المؤقتة"):
    st.cache_resource.clear()
    st.rerun()
