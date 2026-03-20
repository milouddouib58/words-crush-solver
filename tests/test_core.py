"""
======================================
 🧪 اختبارات الوحدات الأساسية
======================================
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.trie import Trie, TrieNode
from core.scrambler import solve_scrambled, find_anagrams
from core.crossword import solve_crossword
from core.syllables import solve_syllables
from core.proverbs import solve_proverb, complete_proverb
from core.filter import filter_by_topic, filter_by_length


class TestTrie(unittest.TestCase):
    """اختبارات شجرة Trie"""

    def setUp(self):
        """تهيئة Trie للاختبارات"""
        self.trie = Trie()
        self.words = ["كتاب", "كتابة", "كاتب", "مكتبة", "قلم", "قراءة", "قرأ"]
        for word in self.words:
            self.trie.insert(word)

    def test_insert_and_search(self):
        """اختبار الإدراج والبحث"""
        for word in self.words:
            self.assertTrue(self.trie.search(word), f"يجب أن توجد '{word}'")

    def test_search_nonexistent(self):
        """اختبار البحث عن كلمة غير موجودة"""
        self.assertFalse(self.trie.search("حصان"))
        self.assertFalse(self.trie.search("كتا"))

    def test_starts_with(self):
        """اختبار البحث بالبادئة"""
        self.assertTrue(self.trie.starts_with("كتا"))
        self.assertTrue(self.trie.starts_with("كا"))
        self.assertTrue(self.trie.starts_with("قل"))
        self.assertFalse(self.trie.starts_with("حص"))

    def test_word_count(self):
        """اختبار عدد الكلمات"""
        self.assertEqual(len(self.trie), len(self.words))

    def test_get_words_with_prefix(self):
        """اختبار استرجاع كلمات ببادئة"""
        words = self.trie.get_words_with_prefix("كت")
        self.assertIn("كتاب", words)
        self.assertIn("كتابة", words)
        self.assertNotIn("كاتب", words)

    def test_empty_insert(self):
        """اختبار إدراج كلمة فارغة"""
        count_before = len(self.trie)
        self.trie.insert("")
        self.trie.insert("   ")
        self.assertEqual(len(self.trie), count_before)

    def test_duplicate_insert(self):
        """اختبار إدراج كلمة مكررة"""
        count_before = len(self.trie)
        self.trie.insert("كتاب")
        self.assertEqual(len(self.trie), count_before)

    def test_contains(self):
        """اختبار عامل in"""
        self.assertIn("كتاب", self.trie)
        self.assertNotIn("حصان", self.trie)


class TestScrambler(unittest.TestCase):
    """اختبارات حل الكلمات المبعثرة"""

    def setUp(self):
        self.trie = Trie()
        words = ["كتب", "كتاب", "بكت", "أكل", "لعب", "كلب", "قلب", "بلد"]
        for w in words:
            self.trie.insert(w)

    def test_basic_scramble(self):
        """اختبار حل بسيط"""
        results = solve_scrambled(self.trie, "كتب")
        self.assertIn("كتب", results)

    def test_find_multiple(self):
        """اختبار إيجاد عدة كلمات"""
        results = solve_scrambled(self.trie, "كلب")
        # يجب أن يجد "كلب" على الأقل
        self.assertTrue(len(results) >= 1)

    def test_min_length(self):
        """اختبار الحد الأدنى للطول"""
        results = solve_scrambled(self.trie, "كتاب", min_len=4)
        for word in results:
            self.assertGreaterEqual(len(word), 4)

    def test_max_length(self):
        """اختبار الحد الأقصى للطول"""
        results = solve_scrambled(self.trie, "كتابلم", max_len=3)
        for word in results:
            self.assertLessEqual(len(word), 3)

    def test_empty_letters(self):
        """اختبار حروف فارغة"""
        results = solve_scrambled(self.trie, "")
        self.assertEqual(results, [])

    def test_sorted_by_length(self):
        """اختبار الترتيب حسب الطول"""
        results = solve_scrambled(self.trie, "كتابل")
        for i in range(len(results) - 1):
            self.assertGreaterEqual(len(results[i]), len(results[i + 1]))


class TestCrossword(unittest.TestCase):
    """اختبارات الكلمات المتقاطعة"""

    def setUp(self):
        self.trie = Trie()
        words = ["كتاب", "حساب", "جواب", "باب", "كلب", "قلم"]
        for w in words:
            self.trie.insert(w)

    def test_pattern_end(self):
        """اختبار نمط ينتهي بحرف معين"""
        results = solve_crossword(self.trie, "???ب")
        self.assertIn("كتاب", results)

    def test_pattern_start(self):
        """اختبار نمط يبدأ بحرف معين"""
        results = solve_crossword(self.trie, "ك???")
        self.assertIn("كتاب", results)

    def test_exact_match(self):
        """اختبار نمط كامل"""
        results = solve_crossword(self.trie, "كتاب")
        self.assertEqual(results, ["كتاب"])

    def test_all_unknown(self):
        """اختبار كل الحروف مجهولة"""
        results = solve_crossword(self.trie, "???")
        # يجب أن يجد كلمات من 3 حروف
        for word in results:
            self.assertEqual(len(word), 3)


class TestSyllables(unittest.TestCase):
    """اختبارات مقاطع الكلمات"""

    def setUp(self):
        self.trie = Trie()
        words = ["مدرسة", "كتاب", "معلم"]
        for w in words:
            self.trie.insert(w)

    def test_basic_combine(self):
        """اختبار تركيب بسيط"""
        results = solve_syllables(self.trie, ["كتا", "ب"])
        self.assertIn("كتاب", results)

    def test_use_all(self):
        """اختبار استخدام جميع المقاطع"""
        results = solve_syllables(self.trie, ["كتا", "ب"], use_all=True)
        self.assertIn("كتاب", results)


class TestProverbs(unittest.TestCase):
    """اختبارات الأمثال"""

    def test_search_by_keyword(self):
        """اختبار البحث بكلمة مفتاحية"""
        results = solve_proverb(hint="صبر")
        self.assertTrue(len(results) > 0)

    def test_complete(self):
        """اختبار إكمال مثل"""
        results = complete_proverb("العلم")
        self.assertTrue(len(results) > 0)


class TestFilter(unittest.TestCase):
    """اختبارات التصفية"""

    def test_filter_by_topic(self):
        """اختبار التصفية حسب الموضوع"""
        words = ["قط", "تفاح", "طبيب", "أسد"]
        filtered = filter_by_topic(words, "حيوانات")
        self.assertIn("قط", filtered)
        self.assertIn("أسد", filtered)
        self.assertNotIn("تفاح", filtered)

    def test_filter_by_length(self):
        """اختبار التصفية حسب الطول"""
        words = ["قط", "كتاب", "مدرسة", "قلم"]
        filtered = filter_by_length(words, exact_len=4)
        self.assertIn("كتاب", filtered)
        self.assertNotIn("قط", filtered)

    def test_unknown_topic(self):
        """اختبار موضوع غير معروف"""
        words = ["قط", "كلب"]
        filtered = filter_by_topic(words, "موضوع_غريب")
        # يجب إرجاع الكل
        self.assertEqual(len(filtered), len(words))


if __name__ == "__main__":
    print("=" * 60)
    print("   🧪 تشغيل اختبارات مشروع حل كلمات كراش")
    print("=" * 60)

    # تشغيل الاختبارات مع تفاصيل
    unittest.main(verbosity=2)