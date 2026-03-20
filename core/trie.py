"""
🌳 بنية Trie للقاموس العربي
"""

import os
import re
import urllib.request
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class TrieNode:
    __slots__ = ['children', 'is_end', 'word']
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = None


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    def insert(self, word: str) -> None:
        if not word or not word.strip():
            return
        word = self._normalize(word)
        if not word:
            return
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
        word = self._normalize(word)
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        prefix = self._normalize(prefix)
        return self._find_node(prefix) is not None

    def get_words_with_prefix(self, prefix: str) -> list:
        prefix = self._normalize(prefix)
        words = []
        node = self._find_node(prefix)
        if node:
            self._collect_words(node, words)
        return words

    def get_all_words(self) -> list:
        words = []
        self._collect_words(self.root, words)
        return words

    def _find_node(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _collect_words(self, node, words):
        if node.is_end and node.word:
            words.append(node.word)
        for child in node.children.values():
            self._collect_words(child, words)

    @staticmethod
    def _normalize(word: str) -> str:
        if not word:
            return ""
        word = re.sub(
            r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u0640]',
            '', word
        )
        return word.strip()

    def __len__(self):
        return self.word_count

    def __contains__(self, word):
        return self.search(word)


def load_trie(dict_file=None, auto_download=True):
    """تحميل القاموس العربي الضخم وبناء شجرة Trie"""
    trie = Trie()
    dict_path = dict_file or config.DICT_FILE
    loaded = False

    # === 1. من ملف محلي ===
    if os.path.exists(dict_path):
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and any('\u0600' <= c <= '\u06FF' for c in word):
                        trie.insert(word)
            if trie.word_count > 0:
                loaded = True
        except Exception:
            pass

    # === 3. القاموس المدمج الضخم ===
    if trie.word_count == 0:
        try:
            from core.dictionary_builder import get_massive_dictionary
            all_words = get_massive_dictionary()
        except ImportError:
            all_words = config.DEFAULT_WORDS

        for word in all_words:
            trie.insert(word)

        # حفظ في ملف
        try:
            os.makedirs(os.path.dirname(dict_path), exist_ok=True)
            with open(dict_path, 'w', encoding='utf-8') as f:
                for word in all_words:
                    f.write(word + '\n')
        except Exception:
            pass

    return trie


def add_words_to_file(words, filepath=None):
    filepath = filepath or config.DICT_FILE
    existing = set()
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            existing = set(line.strip() for line in f)
    new_words = [w for w in words if w.strip() and w.strip() not in existing]
    if new_words:
        with open(filepath, 'a', encoding='utf-8') as f:
            for word in new_words:
                f.write(word.strip() + '\n')
    return len(new_words)
