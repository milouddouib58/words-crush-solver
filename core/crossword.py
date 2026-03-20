"""
✝ حل الكلمات المتقاطعة
"""

from typing import List, Set
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def solve_crossword(trie, pattern: str, max_results: int = None) -> List[str]:
    max_results = max_results or config.MAX_RESULTS
    target_len = len(pattern)
    found: Set[str] = set()

    def dfs(node, pos, current):
        if len(found) >= max_results:
            return
        if pos == target_len:
            if node.is_end:
                found.add(''.join(current))
            return
        expected = pattern[pos]
        if expected in ('?', '_', '*', '.'):
            for char, child in node.children.items():
                current.append(char)
                dfs(child, pos + 1, current)
                current.pop()
        else:
            if expected in node.children:
                current.append(expected)
                dfs(node.children[expected], pos + 1, current)
                current.pop()

    dfs(trie.root, 0, [])
    return sorted(found)