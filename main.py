#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║       🎮 حل كلمات كراش - Words Crush Solver     ║
║                  الإصدار 1.0.0                   ║
╚══════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime

# إضافة مسار المشروع
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from core.trie import load_trie, Trie
from core.scrambler import solve_scrambled, format_results, find_anagrams
from core.crossword import solve_crossword
from core.syllables import solve_syllables
from core.proverbs import solve_proverb, complete_proverb, get_all_proverbs
from core.filter import (
    filter_by_topic,
    filter_by_image_description,
    filter_by_length,
    get_available_topics
)


# ═══════════════════════════════════════════
#  🎨 واجهة المستخدم
# ═══════════════════════════════════════════

def clear_screen():
    """مسح الشاشة"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """طباعة شعار البرنامج"""
    banner = """
╔══════════════════════════════════════════════════════╗
║                                                      ║
║     🎮  حل كلمات كراش  -  Words Crush Solver  🎮    ║
║                                                      ║
║     أداة ذكية لحل جميع مراحل لعبة كلمات كراش       ║
║     ─────────────────────────────────────────        ║
║     📖 قاموس عربي شامل  |  🔍 بحث سريع             ║
║     📷 دعم OCR          |  📱 دعم ADB               ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """طباعة القائمة الرئيسية"""
    menu = """
┌──────────────────────────────────────────┐
│           📋 القائمة الرئيسية            │
├──────────────────────────────────────────┤
│                                          │
│  1️⃣  إدخال الحروف يدوياً               │
│  2️⃣  قراءة الحروف من صورة (OCR)        │
│  3️⃣  استخدام ADB (من الهاتف)           │
│  4️⃣  حل كلمات متقاطعة (نمط)           │
│  5️⃣  حل مقاطع كلمات                    │
│  6️⃣  البحث عن أمثال                     │
│  7️⃣  تحديث القاموس من API              │
│  8️⃣  إضافة كلمات مخصصة                 │
│  9️⃣  إحصائيات القاموس                   │
│  0️⃣  خروج                               │
│                                          │
└──────────────────────────────────────────┘
"""
    print(menu)


def save_results(words: list, letters: str = "", topic: str = "") -> str:
    """
    حفظ النتائج في ملف

    Returns:
        مسار الملف المحفوظ
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results_{timestamp}.txt"
    filepath = os.path.join(config.EXPORT_DIR, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"نتائج حل كلمات كراش\n")
            f.write(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if letters:
                f.write(f"الحروف: {letters}\n")
            if topic:
                f.write(f"الموضوع: {topic}\n")
            f.write(f"عدد الكلمات: {len(words)}\n")
            f.write("=" * 40 + "\n\n")

            for word in words:
                f.write(f"{word}\n")

        print(f"💾 تم حفظ النتائج في: {filepath}")
        return filepath

    except Exception as e:
        print(f"❌ خطأ في الحفظ: {e}")
        return ""


def post_results_menu(words: list, letters: str = "", trie: Trie = None):
    """قائمة ما بعد النتائج"""
    while True:
        print("\n┌─────────────────────────────┐")
        print("│   ماذا تريد أن تفعل؟       │")
        print("├─────────────────────────────┤")
        print("│  1. تصفية حسب الموضوع      │")
        print("│  2. تصفية حسب وصف الصورة   │")
        print("│  3. تصفية حسب الطول         │")
        print("│  4. حفظ النتائج             │")
        print("│  5. العودة للقائمة الرئيسية │")
        print("└─────────────────────────────┘")

        choice = input("\n  اختيارك ← ").strip()

        if choice == "1":
            print(f"\n  المواضيع المتاحة: {', '.join(get_available_topics())}")
            topic = input("  أدخل الموضوع ← ").strip()
            filtered = filter_by_topic(words, topic)
            print(f"\n  📊 {len(filtered)} كلمة بعد التصفية:")
            for w in filtered:
                print(f"    • {w}")

        elif choice == "2":
            from utils.image_analyzer import get_image_description_from_user
            desc = get_image_description_from_user()
            filtered = filter_by_image_description(words, desc)
            print(f"\n  📊 {len(filtered)} كلمة بعد التصفية:")
            for w in filtered:
                print(f"    • {w}")

        elif choice == "3":
            try:
                length = int(input("  أدخل الطول المطلوب ← ").strip())
                filtered = filter_by_length(words, exact_len=length)
                print(f"\n  📊 {len(filtered)} كلمة بطول {length}:")
                for w in filtered:
                    print(f"    • {w}")
            except ValueError:
                print("❌ أدخل رقماً صحيحاً")

        elif choice == "4":
            save_results(words, letters)

        elif choice == "5":
            break


# ═══════════════════════════════════════════
#  🔧 وظائف الحل
# ═══════════════════════════════════════════

def option_manual_input(trie: Trie):
    """الخيار 1: إدخال الحروف يدوياً"""
    print("\n" + "─" * 40)
    print("  📝 إدخال الحروف يدوياً")
    print("─" * 40)

    letters = input("\n  أدخل الحروف (بدون مسافات) ← ").strip()

    if not letters:
        print("❌ لم يتم إدخال حروف")
        return

    # تصفية الحروف العربية
    arabic_letters = ''.join(c for c in letters if '\u0600' <= c <= '\u06FF')
    if not arabic_letters:
        print("❌ لم يتم العثور على حروف عربية")
        return

    print(f"\n  الحروف: {arabic_letters} ({len(arabic_letters)} حرف)")

    # خيارات إضافية
    min_len = input("  الحد الأدنى للطول (Enter = 2) ← ").strip()
    min_len = int(min_len) if min_len.isdigit() else config.DEFAULT_MIN_LEN

    # البحث
    print("\n  🔍 جاري البحث...")
    start_time = time.time()

    results = solve_scrambled(trie, arabic_letters, min_len=min_len)

    elapsed = time.time() - start_time

    # عرض النتائج
    print(format_results(results))
    print(f"  ⏱ زمن البحث: {elapsed:.3f} ثانية")

    if results:
        post_results_menu(results, arabic_letters, trie)


def option_ocr_input(trie: Trie):
    """الخيار 2: قراءة الحروف من صورة"""
    print("\n" + "─" * 40)
    print("  📷 قراءة الحروف من صورة (OCR)")
    print("─" * 40)

    image_path = input("\n  أدخل مسار الصورة ← ").strip()

    if not image_path:
        print("❌ لم يتم إدخال مسار")
        return

    # إزالة علامات الاقتباس
    image_path = image_path.strip('"').strip("'")

    if not os.path.exists(image_path):
        print(f"❌ الملف غير موجود: {image_path}")
        return

    from utils.ocr import extract_letters_from_image, manual_input_fallback

    letters = extract_letters_from_image(image_path)

    if not letters:
        print("⚠️ فشل في استخراج الحروف")
        choice = input("  هل تريد إدخالها يدوياً؟ (نعم/لا) ← ").strip()
        if choice in ("نعم", "ن", "y", "yes"):
            letters = manual_input_fallback()

    if letters:
        print(f"\n  الحروف المستخرجة: {letters}")
        confirm = input("  هل الحروف صحيحة؟ (Enter = نعم، أو أدخل التصحيح) ← ").strip()

        if confirm:
            letters = confirm

        print("\n  🔍 جاري البحث...")
        start_time = time.time()
        results = solve_scrambled(trie, letters)
        elapsed = time.time() - start_time

        print(format_results(results))
        print(f"  ⏱ زمن البحث: {elapsed:.3f} ثانية")

        if results:
            post_results_menu(results, letters, trie)


def option_adb_input(trie: Trie):
    """الخيار 3: استخدام ADB"""
    print("\n" + "─" * 40)
    print("  📱 قراءة الحروف من الهاتف (ADB)")
    print("─" * 40)

    from utils.adb_helper import ADBHelper

    adb = ADBHelper()

    if not adb.is_connected():
        print("\n❌ لا يوجد جهاز متصل")
        print("  تأكد من:")
        print("  1. تثبيت ADB")
        print("  2. تفعيل USB Debugging")
        print("  3. توصيل الهاتف")
        return

    print("✅ الجهاز متصل")

    letters = adb.get_letters_from_game()

    if letters:
        print(f"\n  الحروف: {letters}")

        confirm = input("  هل الحروف صحيحة؟ (Enter = نعم، أو أدخل التصحيح) ← ").strip()
        if confirm:
            letters = confirm

        print("\n  🔍 جاري البحث...")
        results = solve_scrambled(trie, letters)

        print(format_results(results))

        if results:
            post_results_menu(results, letters, trie)


def option_crossword(trie: Trie):
    """الخيار 4: حل كلمات متقاطعة"""
    print("\n" + "─" * 40)
    print("  ✝ حل كلمات متقاطعة")
    print("─" * 40)
    print("  استخدم ? للحروف المجهولة")
    print("  مثال: ???ب = كلمة من 4 حروف تنتهي بـ 'ب'")

    pattern = input("\n  أدخل النمط ← ").strip()

    if not pattern:
        print("❌ لم يتم إدخال نمط")
        return

    print("\n  🔍 جاري البحث...")
    start_time = time.time()

    results = solve_crossword(trie, pattern)

    elapsed = time.time() - start_time

    if results:
        print(f"\n  📊 تم العثور على {len(results)} كلمة:")
        for i, word in enumerate(results, 1):
            print(f"    {i:3d}. {word}")
            if i >= 50:
                print(f"    ... و {len(results) - 50} كلمة أخرى")
                break
    else:
        print("  ❌ لم يتم العثور على كلمات مطابقة")

    print(f"\n  ⏱ زمن البحث: {elapsed:.3f} ثانية")

    if results:
        post_results_menu(results, pattern, trie)


def option_syllables(trie: Trie):
    """الخيار 5: حل مقاطع كلمات"""
    print("\n" + "─" * 40)
    print("  📝 حل مقاطع كلمات")
    print("─" * 40)
    print("  أدخل المقاطع مفصولة بمسافات")
    print("  مثال: مدر سة")

    syllables_input = input("\n  أدخل المقاطع ← ").strip()

    if not syllables_input:
        print("❌ لم يتم إدخال مقاطع")
        return

    syllables = syllables_input.split()
    print(f"\n  المقاطع: {syllables}")

    print("\n  🔍 جاري البحث...")
    start_time = time.time()

    results = solve_syllables(trie, syllables)

    elapsed = time.time() - start_time

    if results:
        print(f"\n  📊 تم العثور على {len(results)} كلمة:")
        for word in results:
            print(f"    • {word}")
    else:
        print("  ❌ لم يتم العثور على كلمات")

    print(f"\n  ⏱ زمن البحث: {elapsed:.3f} ثانية")


def option_proverbs(trie: Trie):
    """الخيار 6: البحث عن أمثال"""
    print("\n" + "─" * 40)
    print("  📜 البحث عن أمثال")
    print("─" * 40)
    print("  1. البحث بكلمة مفتاحية")
    print("  2. إكمال مثل")
    print("  3. عرض جميع الأمثال")

    choice = input("\n  اختيارك ← ").strip()

    if choice == "1":
        keyword = input("  أدخل الكلمة المفتاحية ← ").strip()
        results = solve_proverb(hint=keyword)

        if results:
            print(f"\n  📊 تم العثور على {len(results)} مثل:")
            for p in results:
                print(f"    📜 {p}")
        else:
            print("  ❌ لم يتم العثور على أمثال")

    elif choice == "2":
        start = input("  أدخل بداية المثل ← ").strip()
        results = complete_proverb(start)

        if results:
            print(f"\n  📊 أمثال مطابقة:")
            for p in results:
                print(f"    📜 {p}")
        else:
            print("  ❌ لم يتم العثور على أمثال")

    elif choice == "3":
        proverbs = get_all_proverbs()
        print(f"\n  📚 جميع الأمثال ({len(proverbs)}):")
        for i, p in enumerate(proverbs, 1):
            print(f"    {i:2d}. {p}")


def option_update_api(trie: Trie):
    """الخيار 7: تحديث القاموس"""
    print("\n" + "─" * 40)
    print("  🌐 تحديث القاموس")
    print("─" * 40)
    print("  1. تحديث من API")
    print("  2. تحديث من ملف")
    print("  3. تحميل القاموس من الإنترنت")

    choice = input("\n  اختيارك ← ").strip()

    if choice == "1":
        from utils.api_client import update_dictionary_from_api
        url = input("  أدخل رابط API (Enter للافتراضي) ← ").strip()
        url = url or config.API_BASE_URL
        count = update_dictionary_from_api(trie, url)
        print(f"  تم إضافة {count} كلمة جديدة")

    elif choice == "2":
        filepath = input("  أدخل مسار الملف ← ").strip()
        if os.path.exists(filepath):
            count = 0
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not trie.search(word):
                        trie.insert(word)
                        count += 1
            print(f"  تم إضافة {count} كلمة جديدة")
        else:
            print("❌ الملف غير موجود")

    elif choice == "3":
        from core.trie import download_dictionary
        url = input("  أدخل الرابط (Enter للافتراضي) ← ").strip()
        url = url or config.DICT_URL
        if download_dictionary(url, config.DICT_FILE):
            print("  ✅ تم التحميل، أعد تشغيل البرنامج لتحميل القاموس الجديد")


def option_add_words(trie: Trie):
    """الخيار 8: إضافة كلمات مخصصة"""
    print("\n" + "─" * 40)
    print("  ✏️ إضافة كلمات مخصصة")
    print("─" * 40)
    print("  أدخل الكلمات مفصولة بمسافات")
    print("  أو اكتب 'انتهى' للتوقف")

    words_input = input("\n  أدخل الكلمات ← ").strip()

    if words_input:
        words = words_input.split()
        from utils.api_client import add_custom_words
        count = add_custom_words(trie, words)
        print(f"  ✅ تم إضافة {count} كلمة جديدة")
        print(f"  📊 إجمالي الكلمات: {len(trie):,}")


def option_stats(trie: Trie):
    """الخيار 9: إحصائيات القاموس"""
    print("\n" + "─" * 40)
    print("  📊 إحصائيات القاموس")
    print("─" * 40)

    all_words = trie.get_all_words()
    total = len(all_words)

    print(f"\n  إجمالي الكلمات: {total:,}")

    if all_words:
        # توزيع حسب الطول
        length_dist = {}
        for word in all_words:
            l = len(word)
            length_dist[l] = length_dist.get(l, 0) + 1

        print("\n  توزيع حسب الطول:")
        for length in sorted(length_dist.keys()):
            count = length_dist[length]
            bar = "█" * min(count // 5, 30)
            print(f"    {length:2d} حرف: {count:5d} {bar}")

        # أطول وأقصر كلمة
        longest = max(all_words, key=len)
        shortest = min(all_words, key=len)
        print(f"\n  أطول كلمة: {longest} ({len(longest)} حرف)")
        print(f"  أقصر كلمة: {shortest} ({len(shortest)} حرف)")

    # حجم ملف القاموس
    if os.path.exists(config.DICT_FILE):
        size = os.path.getsize(config.DICT_FILE)
        if size > 1024 * 1024:
            print(f"\n  حجم الملف: {size / (1024*1024):.2f} MB")
        else:
            print(f"\n  حجم الملف: {size / 1024:.2f} KB")


# ═══════════════════════════════════════════
#  🚀 الدالة الرئيسية
# ═══════════════════════════════════════════

def main():
    """الدالة الرئيسية للبرنامج"""
    # تحليل الوسائط
    parser = argparse.ArgumentParser(
        description="حل كلمات كراش - Words Crush Solver"
    )
    parser.add_argument(
        '-l', '--letters',
        help='الحروف المراد حلها مباشرة'
    )
    parser.add_argument(
        '-p', '--pattern',
        help='نمط الكلمات المتقاطعة'
    )
    parser.add_argument(
        '-i', '--image',
        help='مسار صورة لاستخراج الحروف'
    )
    parser.add_argument(
        '-t', '--topic',
        help='الموضوع للتصفية'
    )
    parser.add_argument(
        '--min-len',
        type=int,
        default=config.DEFAULT_MIN_LEN,
        help='الحد الأدنى لطول الكلمة'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=config.MAX_RESULTS,
        help='الحد الأقصى للنتائج'
    )

    args = parser.parse_args()

    # عرض الشعار
    clear_screen()
    print_banner()

    # تحميل القاموس
    print("⏳ جاري تحميل القاموس...")
    trie = load_trie()
    print()

    # ─── الوضع المباشر (سطر الأوامر) ───
    if args.letters:
        print(f"  الحروف: {args.letters}")
        results = solve_scrambled(trie, args.letters, min_len=args.min_len)
        if args.topic:
            results = filter_by_topic(results, args.topic)
        print(format_results(results))
        return

    if args.pattern:
        print(f"  النمط: {args.pattern}")
        results = solve_crossword(trie, args.pattern)
        print(f"\n  النتائج: {', '.join(results[:30])}")
        return

    if args.image:
        from utils.ocr import extract_letters_from_image
        letters = extract_letters_from_image(args.image)
        if letters:
            results = solve_scrambled(trie, letters)
            print(format_results(results))
        return

    # ─── الوضع التفاعلي ───
    while True:
        print_menu()
        choice = input("  اختيارك ← ").strip()

        if choice == "1":
            option_manual_input(trie)
        elif choice == "2":
            option_ocr_input(trie)
        elif choice == "3":
            option_adb_input(trie)
        elif choice == "4":
            option_crossword(trie)
        elif choice == "5":
            option_syllables(trie)
        elif choice == "6":
            option_proverbs(trie)
        elif choice == "7":
            option_update_api(trie)
        elif choice == "8":
            option_add_words(trie)
        elif choice == "9":
            option_stats(trie)
        elif choice in ("0", "q", "خروج"):
            print("\n  👋 شكراً لاستخدام حل كلمات كراش!")
            print("  ⭐ لا تنسَ تقييم المشروع على GitHub\n")
            break
        else:
            print("  ❌ خيار غير صالح، حاول مجدداً")

        input("\n  اضغط Enter للمتابعة...")
        clear_screen()
        print_banner()


if __name__ == "__main__":
    main()