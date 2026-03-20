import os
from core.dictionary_builder import get_massive_dictionary

def main():
    words = get_massive_dictionary()
    path = "data/arabic_words.txt"
    os.makedirs("data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for w in words:
            f.write(w + "\n")
    print(f"Successfully wrote {len(words)} words to {path}")

if __name__ == '__main__':
    main()
