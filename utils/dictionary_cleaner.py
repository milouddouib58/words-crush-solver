import os

def clean_arabic_word(word: str) -> str:
    word = word.strip()
    if len(word) <= 3:
        return word
        
    for pref in ['وال', 'فال', 'بال', 'كال', 'لل']:
        if word.startswith(pref) and len(word) >= 6:
            word = word[3:]
            break
            
    if word.startswith('ال') and len(word) >= 5:
        word = word[2:]
        
    suffixes_3 = ['هما', 'كما', 'كمو', 'تهم', 'تها', 'تكم', 'تني', 'تون']
    suffixes_2 = ['هم', 'هن', 'كم', 'كن', 'ها', 'نا', 'وا', 'ين', 'ون', 'ات', 'ان', 'تم', 'تن', 'ني', 'تي']
    suffixes_1 = ['ه', 'ك', 'ي']
    
    for suf in suffixes_3:
        if word.endswith(suf) and len(word) - 3 >= 3:
            return word[:-3]
            
    for suf in suffixes_2:
        if word.endswith(suf) and len(word) - 2 >= 3:
            return word[:-2]
            
    for suf in suffixes_1:
        if word.endswith(suf) and len(word) - 1 >= 3:
            return word[:-1]
            
    return word

def refine_dictionary(filepath):
    import os
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
        
    print(f"Reading from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        words = f.read().splitlines()
        
    print(f"Loaded {len(words)} words. Refining...")
    cleaned = set()
    for w in words:
        w_clean = clean_arabic_word(w)
        if len(w_clean) >= 2: # اللعبة تقبل كلمات من حرفين كحد أدنى
            cleaned.add(w_clean)
            
    with open(filepath, 'w', encoding='utf-8') as f:
        for w in sorted(cleaned):
            f.write(w + "\n")
            
    print(f"SUCCESS: Refined dictionary. Shrunk from {len(words)} down to {len(cleaned)} pure lemmas/base words.")

if __name__ == '__main__':
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dict_path = os.path.join(base_dir, "data", "arabic_words.txt")
    refine_dictionary(dict_path)
