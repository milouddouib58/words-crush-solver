"""
======================================
 🔀 حل الكلمات المبعثرة
======================================
يولد جميع الكلمات الممكنة من مجموعة
حروف معطاة باستخدام Backtracking
"""

import time
from collections import Counter
from typing import List, Optional, Set

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def solve_scrambled(
    trie,
    letters: str,
    min_len: int = None,
    max_len: int = None,
    max_results: int = None,
    timeout: float = None
) -> List[str]:
    """
    حل الكلمات المبعثرة - إيجاد جميع الكلمات الممكنة من الحروف

    Args:
        trie: شجرة Trie تحتوي على القاموس
        letters: الحروف المتاحة (مثل "كتابل")
        min_len: الحد الأدنى لطول الكلمة
        max_len: الحد الأقصى لطول الكلمة
        max_results: الحد الأقصى لعدد النتائج
        timeout: مهلة البحث بالثواني

    Returns:
        قائمة الكلمات الممكنة مرتبة حسب الطول تنازلياً
    """
    # الإعدادات الافتراضية
    min_len = min_len or config.DEFAULT_MIN_LEN
    max_len = max_len or min(len(letters), config.DEFAULT_MAX_LEN)
    max_results = max_results or config.MAX_RESULTS
    timeout = timeout or config.SEARCH_TIMEOUT

    # تنظيف الحروف
    letters = letters.strip().replace(" ", "")
    if not letters:
        return []

    # عدّاد الحروف المتاحة
    available = Counter(letters)
    found_words: Set[str] = set()
    start_time = time.time()

    def backtrack(node, current: list, used: Counter):
        """بحث بالتراجع مع تقليم ذكي"""
        # فحص المهلة وعدد النتائج
        if len(found_words) >= max_results:
            return
        if time.time() - start_time > timeout:
            return

        current_len = len(current)

        # إذا وصلنا لنهاية كلمة صالحة
        if node.is_end and current_len >= min_len:
            word = ''.join(current)
            found_words.add(word)

        # إذا وصلنا للحد الأقصى
        if current_len >= max_len:
            return

        # تجربة كل حرف متاح
        for char in set(available.keys()):
            if used[char] < available[char]:
                # التحقق من وجود هذا الحرف في الشجرة
                if char in node.children:
                    # تقليم: التحقق من أن البادئة قد تؤدي لكلمة
                    current.append(char)
                    used[char] += 1

                    backtrack(node.children[char], current, used)

                    current.pop()
                    used[char] -= 1

    # بدء البحث
    used = Counter()
    backtrack(trie.root, [], used)

    # ترتيب النتائج حسب الطول تنازلياً ثم أبجدياً
    result = sorted(found_words, key=lambda w: (-len(w), w))

    return result


def solve_scrambled_with_pattern(
    trie,
    letters: str,
    pattern: str,
    max_results: int = None
) -> List[str]:
    """
    حل كلمات مبعثرة مع نمط محدد (بعض الحروف معروفة)

    Args:
        trie: شجرة Trie
        letters: الحروف المتاحة
        pattern: النمط (مثل "ك??ب" حيث ? = حرف مجهول)
        max_results: الحد الأقصى للنتائج

    Returns:
        قائمة الكلمات المطابقة
    """
    max_results = max_results or config.MAX_RESULTS
    target_len = len(pattern)
    available = Counter(letters)
    found_words: Set[str] = set()

    def backtrack(node, pos: int, current: list, used: Counter):
        if len(found_words) >= max_results:
            return

        if pos == target_len:
            if node.is_end:
                found_words.add(''.join(current))
            return

        expected_char = pattern[pos]

        if expected_char == '?':
            # حرف مجهول - تجربة كل الحروف المتاحة
            for char in set(available.keys()):
                if used[char] < available[char] and char in node.children:
                    current.append(char)
                    used[char] += 1
                    backtrack(node.children[char], pos + 1, current, used)
                    current.pop()
                    used[char] -= 1
        else:
            # حرف معروف
            if expected_char in node.children:
                current.append(expected_char)
                backtrack(node.children[expected_char], pos + 1, current, used)
                current.pop()

    used = Counter()
    backtrack(trie.root, 0, [], used)

    return sorted(found_words)


def find_anagrams(trie, word: str) -> List[str]:
    """
    إيجاد جميع الجناسات (إعادة ترتيب الحروف) لكلمة

    Args:
        word: الكلمة المراد إيجاد جناساتها

    Returns:
        قائمة الكلمات التي تستخدم نفس الحروف بالضبط
    """
    target_counter = Counter(word)
    target_len = len(word)

    results = solve_scrambled(trie, word, min_len=target_len, max_len=target_len)

    # تصفية: فقط الكلمات التي تستخدم نفس الحروف بالضبط
    anagrams = [w for w in results if Counter(w) == target_counter and w != word]

    return anagrams


def format_results(words: List[str], show_count: bool = True) -> str:
    """
    تنسيق النتائج للعرض

    Args:
        words: قائمة الكلمات
        show_count: عرض العدد الإجمالي

    Returns:
        نص منسق
    """
    if not words:
        return "❌ لم يتم العثور على كلمات"

    output = []

    if show_count:
        output.append(f"📊 تم العثور على {len(words)} كلمة:\n")

    # تجميع حسب الطول
    by_length = {}
    for word in words:
        length = len(word)
        if length not in by_length:
            by_length[length] = []
        by_length[length].append(word)

    for length in sorted(by_length.keys(), reverse=True):
        group = by_length[length]
        output.append(f"  [{length} حروف] ({len(group)} كلمة):")
        # عرض الكلمات في صفوف
        row = "    "
        for i, word in enumerate(group):
            row += word + "  "
            if (i + 1) % 6 == 0:
                output.append(row)
                row = "    "
        if row.strip():
            output.append(row)
        output.append("")

    return '\n'.join(output)


# === اختبار ===
if __name__ == "__main__":
    from trie import load_trie

    print("=" * 50)
    print("   اختبار حل الكلمات المبعثرة")
    print("=" * 50)

    trie = load_trie()

    test_letters = "كتابلم"
    print(f"\nالحروف: {test_letters}")

    start = time.time()
    results = solve_scrambled(trie, test_letters)
    elapsed = time.time() - start

    print(format_results(results))
    print(f"⏱ زمن البحث: {elapsed:.3f} ثانية")