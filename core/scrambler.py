"""
🔀 حل الكلمات المبعثرة
"""

import time
from collections import Counter
from typing import List, Set, Optional

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def solve_scrambled(
    trie, letters: str,
    min_len: int = None, max_len: int = None,
    max_results: int = None, timeout: float = None
) -> List[str]:
    min_len = min_len or config.DEFAULT_MIN_LEN
    max_len = max_len or min(len(letters), config.DEFAULT_MAX_LEN)
    max_results = max_results or config.MAX_RESULTS
    timeout = timeout or config.SEARCH_TIMEOUT

    letters = letters.strip().replace(" ", "")
    if not letters:
        return []

    available = Counter(letters)
    found: Set[str] = set()
    start_time = time.time()

    def backtrack(node, current, used):
        if len(found) >= max_results:
            return
        if time.time() - start_time > timeout:
            return

        current_len = len(current)
        if node.is_end and current_len >= min_len:
            found.add(''.join(current))
        if current_len >= max_len:
            return

        for char in set(available.keys()):
            if used[char] < available[char] and char in node.children:
                current.append(char)
                used[char] += 1
                backtrack(node.children[char], current, used)
                current.pop()
                used[char] -= 1

    backtrack(trie.root, [], Counter())
    return sorted(found, key=lambda w: (-len(w), w))


def find_anagrams(trie, word: str) -> List[str]:
    target = Counter(word)
    results = solve_scrambled(trie, word, min_len=len(word), max_len=len(word))
    return [w for w in results if Counter(w) == target and w != word]