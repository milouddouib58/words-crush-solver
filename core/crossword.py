"""
======================================
 ✝ حل الكلمات المتقاطعة
======================================
البحث عن كلمات تطابق نمطاً معيناً
مثل: "???ر?" أو "كتا?"
"""

from typing import List, Set

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def solve_crossword(trie, pattern: str, max_results: int = None) -> List[str]:
    """
    حل الكلمات المتقاطعة - إيجاد كلمات تطابق نمطاً

    Args:
        trie: شجرة Trie
        pattern: النمط (? = حرف مجهول، حرف = ثابت)
                 مثال: "???ر?" تعني كلمة من 5 حروف، الرابع 'ر'
        max_results: الحد الأقصى للنتائج

    Returns:
        قائمة الكلمات المطابقة
    """
    max_results = max_results or config.MAX_RESULTS
    target_len = len(pattern)
    found: Set[str] = set()

    def dfs(node, pos: int, current: list):
        """بحث بالعمق أولاً"""
        if len(found) >= max_results:
            return

        if pos == target_len:
            if node.is_end:
                found.add(''.join(current))
            return

        expected = pattern[pos]

        if expected in ('?', '_', '*', '.'):
            # حرف مجهول - تجربة كل الأبناء
            for char, child_node in node.children.items():
                current.append(char)
                dfs(child_node, pos + 1, current)
                current.pop()
        else:
            # حرف معروف
            if expected in node.children:
                current.append(expected)
                dfs(node.children[expected], pos + 1, current)
                current.pop()

    dfs(trie.root, 0, [])

    return sorted(found)


def solve_crossword_with_clue(
    trie,
    pattern: str,
    clue_words: List[str] = None,
    topic: str = None
) -> List[str]:
    """
    حل كلمات متقاطعة مع تلميح

    Args:
        trie: شجرة Trie
        pattern: النمط
        clue_words: كلمات مفتاحية من التلميح
        topic: الموضوع العام

    Returns:
        قائمة الكلمات المرشحة (مرتبة حسب الملاءمة)
    """
    from filter import filter_by_topic

    # الحصول على جميع الكلمات المطابقة للنمط
    matches = solve_crossword(trie, pattern)

    if not matches:
        return []

    # تصفية حسب الموضوع إذا كان متاحاً
    if topic:
        filtered = filter_by_topic(matches, topic)
        if filtered:
            return filtered

    return matches


def solve_multi_pattern(trie, patterns: List[str]) -> dict:
    """
    حل عدة أنماط دفعة واحدة

    Args:
        trie: شجرة Trie
        patterns: قائمة الأنماط

    Returns:
        قاموس {نمط: [كلمات]}
    """
    results = {}
    for pattern in patterns:
        results[pattern] = solve_crossword(trie, pattern)
    return results


# === اختبار ===
if __name__ == "__main__":
    from trie import load_trie

    print("=" * 50)
    print("   اختبار حل الكلمات المتقاطعة")
    print("=" * 50)

    trie = load_trie()

    patterns = ["??اب", "كت??", "???ر", "?لم"]

    for pattern in patterns:
        results = solve_crossword(trie, pattern)
        print(f"\n  النمط '{pattern}': {len(results)} نتيجة")
        if results:
            print(f"    {', '.join(results[:15])}")
            if len(results) > 15:
                print(f"    ... و {len(results) - 15} كلمة أخرى")