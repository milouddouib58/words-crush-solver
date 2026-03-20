import sys
from core.trie import load_trie

def main():
    try:
        trie = load_trie()
        word = "كتاب"
        exists = trie.search(word)
        words_prefix = trie.get_words_with_prefix(word[0])[:10]
        
        with open("test_out.txt", "w", encoding="utf-8") as f:
            f.write(f"Trie size: {len(trie)}\n")
            f.write(f"Exists '{word}': {exists}\n")
            f.write(f"Some words starting with '{word[0]}': {words_prefix}\n")
    except Exception as e:
        with open("test_out.txt", "w", encoding="utf-8") as f:
            f.write(f"Error: {str(e)}\n")

if __name__ == '__main__':
    main()
