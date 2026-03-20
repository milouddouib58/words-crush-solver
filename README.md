# 🎮 حل كلمات كراش - Words Crush Solver

أداة ذكية ومتكاملة لحل جميع مراحل لعبة **كلمات كراش** العربية.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)

## ✨ الميزات

- 🔤 **حل الكلمات المبعثرة** - إيجاد جميع الكلمات الممكنة من حروف معطاة
- ✝️ **حل الكلمات المتقاطعة** - البحث بالأنماط (مثل `???ب`)
- 📝 **حل مقاطع الكلمات** - تركيب كلمات من مقاطع
- 📜 **حل الأمثال** - قاعدة بيانات أمثال عربية شاملة
- 📷 **دعم OCR** - استخراج الحروف من صور اللعبة
- 📱 **دعم ADB** - التقاط الشاشة والنقر التلقائي
- 🌐 **تحديث القاموس** - من API خارجي أو ملفات
- 🔍 **تصفية ذكية** - حسب الموضوع أو وصف الصورة
- 💾 **حفظ وتصدير** - النتائج في ملفات

## 📋 متطلبات النظام

- **Python** 3.8 أو أحدث
- **Tesseract OCR** (اختياري - لدعم قراءة الصور)
- **ADB** (اختياري - للتعامل مع الهاتف)

## 🚀 التثبيت

```bash
# استنساخ المشروع
git clone https://github.com/username/words-crush-solver.git
cd words-crush-solver

# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt
```

### تثبيت Tesseract OCR (اختياري)

**Windows:**
```bash
# تحميل من: https://github.com/UB-Mannheim/tesseract/wiki
# تأكد من تحديد اللغة العربية أثناء التثبيت
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # لدعم اللغة العربية
```

**Linux:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-ara
```

## 📖 كيفية الاستخدام

### الوضع التفاعلي
```bash
python main.py
```

### سطر الأوامر
```bash
# حل حروف مبعثرة
python main.py -l "كتابلم"

# حل نمط متقاطع
python main.py -p "???ب"

# من صورة
python main.py -i screenshot.png

# مع تصفية
python main.py -l "كتابلم" -t "حيوانات"
```

## 📁 هيكل المشروع

```
words_crush_solver/
├── main.py              # المدخل الرئيسي
├── config.py            # الإعدادات
├── core/                # المحرك الأساسي
│   ├── trie.py          # شجرة Trie والقاموس
│   ├── scrambler.py     # حل الكلمات المبعثرة
│   ├── crossword.py     # حل المتقاطعة
│   ├── syllables.py     # حل المقاطع
│   ├── proverbs.py      # حل الأمثال
│   └── filter.py        # تصفية النتائج
├── utils/               # أدوات مساعدة
│   ├── ocr.py           # قراءة الصور
│   ├── adb_helper.py    # التعامل مع ADB
│   ├── api_client.py    # عميل API
│   └── image_analyzer.py
├── data/                # البيانات
├── tests/               # الاختبارات
└── docs/                # الوثائق
```

## 🧪 تشغيل الاختبارات

```bash
python -m pytest tests/ -v
# أو
python tests/test_core.py
```

## 🤝 المساهمة

المساهمات مرحب بها! يرجى:

1. عمل Fork للمشروع
2. إنشاء فرع جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للفرع (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت [MIT License](LICENSE).

## ⭐ دعم المشروع

إذا أعجبك المشروع، لا تنسَ ⭐ على GitHub!