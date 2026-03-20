"""
======================================
 🌳 بنية Trie للقاموس العربي
======================================
بنية بيانات شجرية للبحث السريع
عن الكلمات والبادئات العربية
"""

import os
import sys
import urllib.request
import re

# إضافة المسار الجذري
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class TrieNode:
    """عقدة في شجرة Trie"""

    __slots__ = ['children', 'is_end', 'word']

    def __init__(self):
        self.children = {}    # الأبناء: حرف -> TrieNode
        self.is_end = False   # هل هذه نهاية كلمة؟
        self.word = None      # الكلمة الكاملة (تُخزن عند نهاية الكلمة)


class Trie:
    """
    شجرة Trie للبحث السريع عن الكلمات العربية

    الاستخدام:
        trie = Trie()
        trie.insert("كتاب")
        print(trie.search("كتاب"))      # True
        print(trie.starts_with("كتا"))   # True
    """

    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    def insert(self, word: str) -> None:
        """إدراج كلمة في الشجرة"""
        if not word or not word.strip():
            return

        word = self._normalize(word)
        node = self.root

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        if not node.is_end:
            node.is_end = True
            node.word = word
            self.word_count += 1

    def search(self, word: str) -> bool:
        """البحث عن كلمة كاملة في الشجرة"""
        word = self._normalize(word)
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """التحقق من وجود كلمات تبدأ بهذه البادئة"""
        prefix = self._normalize(prefix)
        return self._find_node(prefix) is not None

    def get_words_with_prefix(self, prefix: str) -> list:
        """الحصول على جميع الكلمات التي تبدأ ببادئة معينة"""
        prefix = self._normalize(prefix)
        words = []
        node = self._find_node(prefix)

        if node:
            self._collect_words(node, words)

        return words

    def get_all_words(self) -> list:
        """الحصول على جميع الكلمات في الشجرة"""
        words = []
        self._collect_words(self.root, words)
        return words

    def _find_node(self, prefix: str) -> TrieNode:
        """البحث عن عقدة تمثل بادئة معينة"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _collect_words(self, node: TrieNode, words: list) -> None:
        """جمع كل الكلمات من عقدة معينة"""
        if node.is_end:
            words.append(node.word)

        for child in node.children.values():
            self._collect_words(child, words)

    @staticmethod
    def _normalize(word: str) -> str:
        """تنظيف الكلمة: إزالة التشكيل والمسافات"""
        if not word:
            return ""
        # إزالة التشكيل العربي
        word = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC]', '', word)
        return word.strip()

    def __len__(self):
        return self.word_count

    def __contains__(self, word):
        return self.search(word)

    def __repr__(self):
        return f"Trie(words={self.word_count})"


def download_dictionary(url: str, filepath: str) -> bool:
    """
    تحميل ملف القاموس من الإنترنت مع عرض التقدم

    Args:
        url: رابط التحميل
        filepath: مسار الحفظ المحلي

    Returns:
        True إذا تم التحميل بنجاح
    """
    try:
        print(f"📥 جاري تحميل القاموس من:\n   {url}")
        print("   يرجى الانتظار...")

        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # فتح الاتصال
        response = urllib.request.urlopen(url, timeout=30)
        total_size = response.headers.get('Content-Length')

        if total_size:
            total_size = int(total_size)

        # تحميل مع عرض التقدم
        downloaded = 0
        block_size = 8192
        data = b''

        while True:
            block = response.read(block_size)
            if not block:
                break
            data += block
            downloaded += len(block)

            if total_size:
                percent = (downloaded / total_size) * 100
                bar_len = 40
                filled = int(bar_len * downloaded // total_size)
                bar = '█' * filled + '░' * (bar_len - filled)
                print(f"\r   [{bar}] {percent:.1f}%", end='', flush=True)
            else:
                print(f"\r   تم تحميل {downloaded / 1024:.1f} KB", end='', flush=True)

        print()  # سطر جديد

        # حفظ الملف
        with open(filepath, 'wb') as f:
            f.write(data)

        print(f"✅ تم حفظ القاموس في: {filepath}")
        return True

    except urllib.error.URLError as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return False


def load_trie(dict_file: str = None, auto_download: bool = True) -> Trie:
    """
    تحميل القاموس العربي وبناء شجرة Trie

    Args:
        dict_file: مسار ملف القاموس (اختياري)
        auto_download: تحميل القاموس تلقائياً إذا لم يكن موجوداً

    Returns:
        كائن Trie يحتوي على الكلمات
    """
    trie = Trie()
    dict_path = dict_file or config.DICT_FILE
    loaded_from_file = False

    # محاولة تحميل من ملف محلي
    if os.path.exists(dict_path):
        print(f"📂 جاري تحميل القاموس من: {dict_path}")
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                line_count = 0
                for line in f:
                    word = line.strip()
                    # تصفية: فقط الكلمات العربية
                    if word and any('\u0600' <= c <= '\u06FF' for c in word):
                        trie.insert(word)
                        line_count += 1

                        if line_count % 10000 == 0:
                            print(f"\r   تم تحميل {line_count:,} كلمة...", end='', flush=True)

                if line_count > 0:
                    print(f"\r   تم تحميل {line_count:,} كلمة ✅          ")
                    loaded_from_file = True

        except Exception as e:
            print(f"⚠️ خطأ في قراءة الملف: {e}")

    # محاولة التحميل من الإنترنت
    if not loaded_from_file and auto_download:
        print("🌐 القاموس غير موجود محلياً، جاري التحميل...")

        urls = [config.DICT_URL] + config.BACKUP_DICT_URLS
        for url in urls:
            if download_dictionary(url, dict_path):
                # إعادة التحميل من الملف المحمّل
                return load_trie(dict_path, auto_download=False)

        print("⚠️ فشل تحميل القاموس من الإنترنت")

    # إذا لم يتم تحميل أي شيء، استخدم القاموس الافتراضي
    if trie.word_count == 0:
        print("📝 جاري تحميل القاموس الافتراضي المدمج...")
        for word in config.DEFAULT_WORDS:
            trie.insert(word)
        print(f"   تم تحميل {trie.word_count} كلمة من القاموس الافتراضي ✅")

        # حفظ القاموس الافتراضي في ملف
        try:
            with open(dict_path, 'w', encoding='utf-8') as f:
                for word in config.DEFAULT_WORDS:
                    f.write(word + '\n')
            print(f"   تم حفظ القاموس الافتراضي في: {dict_path}")
        except Exception:
            pass

    print(f"🌳 Trie جاهزة: {trie.word_count:,} كلمة")
    return trie


def add_words_to_file(words: list, filepath: str = None) -> int:
    """
    إضافة كلمات جديدة إلى ملف القاموس

    Returns:
        عدد الكلمات المضافة
    """
    filepath = filepath or config.DICT_FILE
    existing = set()

    # قراءة الكلمات الموجودة
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            existing = set(line.strip() for line in f)

    # إضافة الكلمات الجديدة
    new_words = [w for w in words if w.strip() and w.strip() not in existing]

    if new_words:
        with open(filepath, 'a', encoding='utf-8') as f:
            for word in new_words:
                f.write(word.strip() + '\n')

    return len(new_words)


# === اختبار سريع ===
if __name__ == "__main__":
    print("=" * 50)
    print("   اختبار وحدة Trie")
    print("=" * 50)

    trie = Trie()
    test_words = ["كتاب", "كتابة", "كاتب", "مكتبة", "قلم", "قراءة"]

    for w in test_words:
        trie.insert(w)

    print(f"\nعدد الكلمات: {len(trie)}")
    print(f"بحث 'كتاب': {trie.search('كتاب')}")
    print(f"بحث 'كتا': {trie.search('كتا')}")
    print(f"بادئة 'كتا': {trie.starts_with('كتا')}")
    print(f"كلمات تبدأ بـ 'كت': {trie.get_words_with_prefix('كت')}")

    print("\n" + "=" * 50)
    print("   تحميل القاموس الكامل")
    print("=" * 50)
    full_trie = load_trie()
    print(f"إجمالي الكلمات: {len(full_trie):,}")