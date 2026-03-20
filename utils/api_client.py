"""
======================================
 🌐 عميل API لتحديث القاموس
======================================
جلب كلمات جديدة من واجهات برمجة خارجية
"""

import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def fetch_words_from_api(
    api_url: str,
    params: dict = None,
    timeout: int = None
) -> list:
    """
    جلب كلمات من API خارجي

    Args:
        api_url: رابط الـ API
        params: معاملات الطلب (اختياري)
        timeout: مهلة الطلب

    Returns:
        قائمة الكلمات
    """
    timeout = timeout or config.API_TIMEOUT

    try:
        # بناء الرابط مع المعاملات
        if params:
            query = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{api_url}?{query}"
        else:
            url = api_url

        print(f"🌐 جاري جلب الكلمات من: {url}")

        # إنشاء الطلب
        request = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'WordsCrushSolver/1.0',
                'Accept': 'application/json'
            }
        )

        # إرسال الطلب
        response = urllib.request.urlopen(request, timeout=timeout)
        data = json.loads(response.read().decode('utf-8'))

        # استخراج الكلمات من الاستجابة
        words = []
        if isinstance(data, list):
            # الاستجابة هي قائمة مباشرة
            words = [str(item) for item in data if item]
        elif isinstance(data, dict):
            # البحث عن حقل الكلمات
            for key in ['words', 'data', 'results', 'items']:
                if key in data and isinstance(data[key], list):
                    words = [str(item) for item in data[key] if item]
                    break

        print(f"✅ تم جلب {len(words)} كلمة")
        return words

    except urllib.error.HTTPError as e:
        print(f"❌ خطأ HTTP: {e.code} - {e.reason}")
        return []
    except urllib.error.URLError as e:
        print(f"❌ خطأ في الاتصال: {e.reason}")
        return []
    except json.JSONDecodeError:
        print("❌ خطأ في تحليل JSON")
        return []
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return []


def update_dictionary_from_api(
    trie,
    api_url: str = None,
    save_to_file: bool = True,
    params: dict = None
) -> int:
    """
    تحديث القاموس من API خارجي

    Args:
        trie: شجرة Trie الحالية
        api_url: رابط الـ API
        save_to_file: حفظ الكلمات الجديدة في الملف
        params: معاملات الطلب

    Returns:
        عدد الكلمات الجديدة المضافة
    """
    api_url = api_url or config.API_BASE_URL

    # جلب الكلمات
    words = fetch_words_from_api(api_url, params)

    if not words:
        print("⚠️ لم يتم جلب أي كلمات")
        return 0

    # إضافة إلى Trie
    new_count = 0
    for word in words:
        word = word.strip()
        if word and not trie.search(word):
            trie.insert(word)
            new_count += 1

    print(f"📊 تم إضافة {new_count} كلمة جديدة إلى القاموس")

    # حفظ في الملف
    if save_to_file and new_count > 0:
        try:
            from core.trie import add_words_to_file
            added = add_words_to_file(words)
            print(f"💾 تم حفظ {added} كلمة جديدة في الملف")
        except Exception as e:
            print(f"⚠️ خطأ في الحفظ: {e}")

    return new_count


def fetch_words_from_multiple_sources(sources: list) -> list:
    """
    جلب كلمات من مصادر متعددة

    Args:
        sources: قائمة من القواميس [{url, params}]

    Returns:
        قائمة مجمعة من الكلمات
    """
    all_words = set()

    for source in sources:
        url = source.get('url', '')
        params = source.get('params', None)

        if url:
            words = fetch_words_from_api(url, params)
            all_words.update(words)

    return list(all_words)


def add_custom_words(trie, words: list, save: bool = True) -> int:
    """
    إضافة كلمات مخصصة يدوياً

    Args:
        trie: شجرة Trie
        words: قائمة الكلمات
        save: حفظ في الملف

    Returns:
        عدد الكلمات المضافة
    """
    new_count = 0
    new_words = []

    for word in words:
        word = word.strip()
        if word and not trie.search(word):
            trie.insert(word)
            new_words.append(word)
            new_count += 1

    if save and new_words:
        try:
            from core.trie import add_words_to_file
            add_words_to_file(new_words)
        except Exception:
            pass

    return new_count


# === اختبار ===
if __name__ == "__main__":
    print("=" * 50)
    print("   اختبار عميل API")
    print("=" * 50)

    # اختبار مع API تجريبي
    print("\n⚠️ ملاحظة: يحتاج API حقيقي للعمل")
    print("   يمكنك تعديل API_BASE_URL في config.py")