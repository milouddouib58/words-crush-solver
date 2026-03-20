"""
╔═══════════════════════════════════════════════╗
║   🎮 حل كلمات كراش - Words Crush Solver      ║
║         Streamlit Web Application             ║
╚═══════════════════════════════════════════════╝
"""

import streamlit as st
import sys
import os
import time

# ===== إعداد المسارات =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.trie import load_trie


# ═══════════════════════════════════════
#  تحميل القاموس (مع التخزين المؤقت)
# ═══════════════════════════════════════
@st.cache_resource(show_spinner=False)
def get_trie():
    """تحميل وتخزين شجرة Trie في الذاكرة"""
    return load_trie()


# ═══════════════════════════════════════
#  إعداد الصفحة
# ═══════════════════════════════════════
st.set_page_config(
    page_title="حل كلمات كراش",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# 🎮 حل كلمات كراش\nأداة ذكية لحل جميع مراحل اللعبة"
    }
)

# ===== CSS مخصص =====
st.markdown("""
<style>
    /* خط عربي */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

    * {
        font-family: 'Tajawal', sans-serif !important;
    }

    /* العنوان الرئيسي */
    .main-title {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .main-title h1 {
        font-size: 2.5rem;
        margin: 0;
    }

    .main-title p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }

    /* بطاقات الميزات */
    .feature-card {
        background: linear-gradient(135deg, #1e2130 0%, #2a2d3e 100%);
        border: 1px solid #3a3d4e;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
        height: 100%;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    .feature-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        font-size: 0.9rem;
        color: #a0a0a0;
    }

    /* إحصائيات */
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        color: white;
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
    }

    .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }

    /* نتائج الكلمات */
    .word-chip {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        margin: 3px;
        font-size: 1rem;
        font-weight: 500;
    }

    /* الشريط الجانبي */
    .sidebar-info {
        background: #1e2130;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid #3a3d4e;
    }

    /* إخفاء عناصر Streamlit الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
#  الشريط الجانبي
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎮 كلمات كراش")
    st.markdown("---")

    # تحميل Trie
    with st.spinner("⏳ جاري تحميل القاموس..."):
        trie = get_trie()

    st.success(f"✅ القاموس: {len(trie):,} كلمة")

    st.markdown("---")
    st.markdown("### 📌 التنقل السريع")
    st.markdown("""
    استخدم القائمة الجانبية للتنقل
    بين صفحات الأدوات المختلفة:

    - 🔤 **حل كلمات مبعثرة**
    - ✝️ **كلمات متقاطعة**
    - 📝 **مقاطع كلمات**
    - 📜 **أمثال عربية**
    - 📷 **قراءة من صورة**
    - 📊 **إحصائيات**
    - ⚙️ **إعدادات**
    """)

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#888; font-size:0.8rem;'>"
        "صُنع بـ ❤️ بواسطة Python + Streamlit<br>"
        "الإصدار 1.0.0"
        "</div>",
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════
#  المحتوى الرئيسي
# ═══════════════════════════════════════

# العنوان
st.markdown("""
<div class="main-title">
    <h1>🎮 حل كلمات كراش</h1>
    <p>أداة ذكية لحل جميع مراحل لعبة كلمات كراش العربية</p>
</div>
""", unsafe_allow_html=True)

# ===== الحل السريع =====
st.markdown("## ⚡ حل سريع")

col_input, col_settings = st.columns([3, 1])

with col_input:
    quick_letters = st.text_input(
        "أدخل الحروف هنا",
        placeholder="مثال: كتابلم",
        help="أدخل الحروف المتاحة في المرحلة بدون مسافات",
        key="quick_input"
    )

with col_settings:
    quick_min = st.number_input("أقل طول", 2, 10, 2, key="quick_min")

if quick_letters:
    # تصفية الحروف العربية
    arabic = ''.join(c for c in quick_letters if '\u0600' <= c <= '\u06FF')

    if arabic:
        from core.scrambler import solve_scrambled

        with st.spinner("🔍 جاري البحث..."):
            start = time.time()
            results = solve_scrambled(trie, arabic, min_len=quick_min)
            elapsed = time.time() - start

        if results:
            st.success(f"✅ تم العثور على **{len(results)}** كلمة في **{elapsed:.3f}** ثانية")

            # تجميع حسب الطول
            by_length = {}
            for w in results:
                l = len(w)
                by_length.setdefault(l, []).append(w)

            for length in sorted(by_length.keys(), reverse=True):
                group = by_length[length]
                with st.expander(
                    f"📏 {length} حروف — {len(group)} كلمة",
                    expanded=(length == max(by_length.keys()))
                ):
                    chips_html = ''.join(
                        f'<span class="word-chip">{w}</span>' for w in group
                    )
                    st.markdown(chips_html, unsafe_allow_html=True)

            # تصدير
            all_text = '\n'.join(results)
            st.download_button(
                "💾 تحميل النتائج",
                all_text,
                f"results_{arabic}.txt",
                mime="text/plain"
            )
        else:
            st.warning("❌ لم يتم العثور على كلمات")
    else:
        st.error("❌ أدخل حروفاً عربية")

st.markdown("---")

# ===== بطاقات الميزات =====
st.markdown("## 🧩 الأدوات المتاحة")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔤</div>
        <div class="feature-title">كلمات مبعثرة</div>
        <div class="feature-desc">
            أدخل الحروف المتاحة وسنجد
            لك جميع الكلمات الممكنة
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">✝️</div>
        <div class="feature-title">كلمات متقاطعة</div>
        <div class="feature-desc">
            أدخل النمط مع ? للحروف
            المجهولة وسنجد المطابقات
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📝</div>
        <div class="feature-title">مقاطع كلمات</div>
        <div class="feature-desc">
            ركّب كلمات من مقاطع
            معطاة بترتيبات مختلفة
        </div>
    </div>
    """, unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📜</div>
        <div class="feature-title">أمثال عربية</div>
        <div class="feature-desc">
            ابحث في قاعدة بيانات
            الأمثال والحكم العربية
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📷</div>
        <div class="feature-title">قراءة من صورة</div>
        <div class="feature-desc">
            ارفع صورة المرحلة
            واستخرج الحروف تلقائياً
        </div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">إحصائيات</div>
        <div class="feature-desc">
            عرض إحصائيات القاموس
            والرسوم البيانية
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
# أضف هذا الكود بعد بطاقات الميزات الموجودة في app.py
# (بعد col4, col5, col6)

# ═══ بطاقة AI ═══
st.markdown("---")

from utils.gemini_helper import is_ai_available
ai_ok = is_ai_available()

if ai_ok:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 15px; padding: 2rem; text-align: center;
        box-shadow: 0 8px 32px rgba(102,126,234,0.4);
    ">
        <h2 style="color:white; margin:0;">🧠 الذكاء الاصطناعي مفعّل!</h2>
        <p style="color:rgba(255,255,255,0.9); font-size:1.1rem;">
            يمكنك الآن حل المراحل من الصور مباشرة، واكتشاف الأمثال من الإيموجي
        </p>
        <p style="color:rgba(255,255,255,0.7); font-size:0.9rem;">
            اذهب إلى صفحة "🧠 الحل الذكي AI" من القائمة الجانبية
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e2130, #2a2d3e);
        border: 2px dashed #667eea;
        border-radius: 15px; padding: 2rem; text-align: center;
    ">
        <h2 style="color:#667eea; margin:0;">🧠 فعّل الذكاء الاصطناعي!</h2>
        <p style="color:#aaa; font-size:1rem;">
            أضف مفتاح Gemini API المجاني لتفعيل الحل الذكي من الصور والإيموجي
        </p>
        <p style="color:#888; font-size:0.85rem;">
            اذهب إلى صفحة ⚙️ الإعدادات للتفعيل
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===== إحصائيات سريعة =====
st.markdown("## 📈 نظرة سريعة")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">{len(trie):,}</div>
        <div class="stat-label">كلمة في القاموس</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">12</div>
        <div class="stat-label">موضوع للتصفية</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-number">30+</div>
        <div class="stat-label">م��ل عربي</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">6</div>
        <div class="stat-label">أدوات حل</div>
    </div>
    """, unsafe_allow_html=True)

# ===== التعليمات =====
st.markdown("---")

with st.expander("📖 كيفية الاستخدام", expanded=False):
    st.markdown("""
    ### طريقة الاستخدام

    1. **الحل السريع**: أدخل الحروف أعلاه مباشرة
    2. **الأدوات المتقدمة**: استخدم القائمة الجانبية للتنقل

    ### أنواع المراحل المدعومة

    | النوع | الوصف | الصفحة |
    |-------|-------|--------|
    | كلمات مبعثرة | إيجاد كلمات من حروف | 🔤 |
    | كلمات متقاطعة | البحث بنمط مثل `???ب` | ✝️ |
    | مقاطع | تركيب كلمات من أجزاء | 📝 |
    | أمثال | البحث في الأمثال | 📜 |
    | OCR | قراءة من صورة | 📷 |

    ### نصائح
    - 💡 استخدم **التصفية بالموضوع** لتضييق النتائج
    - 💡 يمكنك **تحميل النتائج** كملف نصي
    - 💡 جرب **أطوال مختلفة** للحد الأدنى
    """)
