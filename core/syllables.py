"""
======================================
 📝 حل مقاطع الكلمات
======================================
تركيب كلمات من مقاطع (أجزاء) معطاة
"""

from typing import List, Set, Optional
from itertools import permutations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def solve_syllables(
    trie,
    syllables: List[str],
    target_length: Optional[int] = None,
    max_results: int = None,
    use_all: bool = False
) -> List[str]:
    """
    تركيب كلمات من مقاطع معطاة

    Args:
        trie: شجرة Trie
        syllables: قائمة المقاطع (مثل ["كتا", "ب"])
        target_length: الطول المطلوب للكلمة (اختياري)
        max_results: الحد الأقصى للنتائج
        use_all: يجب استخدام جميع المقاطع

    Returns:
        قائمة الكلمات الممكنة
    """
    max_results = max_results or config.MAX_RESULTS
    found: Set[str] = set()

    if use_all:
        # تجربة كل ترتيبات المقاطع
        for perm in permutations(syllables):
            if len(found) >= max_results:
                break
            word = ''.join(perm)
            if target_length and len(word) != target_length:
                continue
            if trie.search(word):
                found.add(word)
    else:
        # تجربة تركيبات مختلفة (1 إلى كل المقاطع)
        _combine_syllables(trie, syllables, [], found,
                          target_length, max_results, set())

    return sorted(found, key=lambda w: (-len(w), w))


def _combine_syllables(
    trie,
    syllables: List[str],
    current: List[str],
    found: Set[str],
    target_length: Optional[int],
    max_results: int,
    used_indices: set
):
    """دالة مساعدة للتركيب التراجعي"""
    if len(found) >= max_results:
        return

    # التحقق من الكلمة الحالية
    if current:
        word = ''.join(current)

        # فحص الطول
        if target_length and len(word) > target_length:
            return

        # التحقق من البادئة (تقليم)
        if not trie.starts_with(word):
            return

        # إذا كانت كلمة صالحة
        if trie.search(word):
            if not target_length or len(word) == target_length:
                found.add(word)

    # تجربة إضافة مقطع جديد
    for i, syllable in enumerate(syllables):
        if i not in used_indices:
            current.append(syllable)
            used_indices.add(i)

            _combine_syllables(trie, syllables, current, found,
                             target_length, max_results, used_indices)

            current.pop()
            used_indices.discard(i)


def split_into_syllables(word: str) -> List[str]:
    """
    تقسيم كلمة عربية إلى مقاطع (تقريبي)

    Args:
        word: الكلمة المراد تقسيمها

    Returns:
        قائمة المقاطع
    """
    # حروف العلة العربية
    vowels = set('اوي')
    syllables = []
    current = ""

    for i, char in enumerate(word):
        current += char

        # قاعدة بسيطة: قطع بعد حرف العلة
        if char in vowels and i < len(word) - 1:
            syllables.append(current)
            current = ""

    if current:
        if syllables:
            syllables[-1] += current
        else:
            syllables.append(current)

    return syllables


# === اختبار ===
if __name__ == "__main__":
    from trie import load_trie

    print("=" * 50)
    print("   اختبار حل مقاطع الكلمات")
    print("=" * 50)

    trie = load_trie()

    test_cases = [
        (["مدر", "سة"], None),
        (["كتا", "ب"], None),
        (["مع", "لم"], None),
    ]

    for syllables, target in test_cases:
        results = solve_syllables(trie, syllables, target)
        print(f"\n  المقاطع {syllables}: {len(results)} نتيجة")
        if results:
            print(f"    {', '.join(results[:10])}")