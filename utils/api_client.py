"""
🌐 عميل API لتحديث القاموس
"""

import json
import urllib.request
import urllib.error
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def fetch_words_from_api(api_url: str, params=None, timeout=None):
    timeout = timeout or config.API_TIMEOUT
    try:
        if params:
            query = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{api_url}?{query}"
        else:
            url = api_url

        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'WordsCrushSolver/1.0', 'Accept': 'application/json'}
        )
        response = urllib.request.urlopen(request, timeout=timeout)
        data = json.loads(response.read().decode('utf-8'))

        if isinstance(data, list):
            return [str(i) for i in data if i]
        elif isinstance(data, dict):
            for key in ['words', 'data', 'results', 'items']:
                if key in data and isinstance(data[key], list):
                    return [str(i) for i in data[key] if i]
        return []
    except Exception:
        return []


def update_dictionary_from_api(trie, api_url=None, save_to_file=True):
    api_url = api_url or config.API_BASE_URL
    words = fetch_words_from_api(api_url)
    if not words:
        return 0
    count = 0
    for w in words:
        w = w.strip()
        if w and not trie.search(w):
            trie.insert(w)
            count += 1
    if save_to_file and count > 0:
        try:
            from core.trie import add_words_to_file
            add_words_to_file(words)
        except Exception:
            pass
    return count


def add_custom_words(trie, words, save=True):
    count = 0
    new_words = []
    for w in words:
        w = w.strip()
        if w and not trie.search(w):
            trie.insert(w)
            new_words.append(w)
            count += 1
    if save and new_words:
        try:
            from core.trie import add_words_to_file
            add_words_to_file(new_words)
        except Exception:
            pass
    return count