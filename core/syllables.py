"""
📝 حل مقاطع الكلمات
"""

from typing import List, Set, Optional
from itertools import permutations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def solve_syllables(
    trie, syllables: List[str],
    target_length: Optional[int] = None,
    max_results: int = None,
    use_all: bool = False
) -> List[str]:
    max_results = max_results or config.MAX_RESULTS
    found: Set[str] = set()

    if use_all:
        for perm in permutations(syllables):
            if len(found) >= max_results:
                break
            word = ''.join(perm)
            if target_length and len(word) != target_length:
                continue
            if trie.search(word):
                found.add(word)
    else:
        _combine(trie, syllables, [], found, target_length, max_results, set())

    return sorted(found, key=lambda w: (-len(w), w))


def _combine(trie, syllables, current, found, target_length, max_results, used):
    if len(found) >= max_results:
        return
    if current:
        word = ''.join(current)
        if target_length and len(word) > target_length:
            return
        if not trie.starts_with(word):
            return
        if trie.search(word):
            if not target_length or len(word) == target_length:
                found.add(word)
    for i, s in enumerate(syllables):
        if i not in used:
            current.append(s)
            used.add(i)
            _combine(trie, syllables, current, found, target_length, max_results, used)
            current.pop()
            used.discard(i)