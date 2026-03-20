"""
======================================
 📱 التعامل مع ADB (Android Debug Bridge)
======================================
التقاط صور الشاشة والنقر التلقائي
"""

import os
import sys
import time
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class ADBHelper:
    """
    فئة للتعامل مع أجهزة Android عبر ADB

    المتطلبات:
        - تثبيت ADB على الجهاز
        - تفعيل USB Debugging على الهاتف
        - توصيل الهاتف بالكمبيوتر
    """

    def __init__(self, serial: str = None, use_adbutils: bool = True):
        """
        Args:
            serial: رقم الجهاز (اختياري)
            use_adbutils: استخدام مكتبة adbutils أو سطر الأوامر
        """
        self.serial = serial
        self.use_adbutils = use_adbutils
        self.device = None

        if use_adbutils:
            try:
                import adbutils
                client = adbutils.AdbClient(host="127.0.0.1", port=5037)
                devices = client.device_list()

                if not devices:
                    print("⚠️ لا توجد أجهزة متصلة")
                    self.use_adbutils = False
                elif serial:
                    self.device = client.device(serial)
                else:
                    self.device = devices[0]
                    print(f"📱 تم الاتصال بالجهاز: {self.device.serial}")

            except ImportError:
                print("⚠️ مكتبة adbutils غير مثبتة، سيتم استخدام سطر الأوامر")
                self.use_adbutils = False
            except Exception as e:
                print(f"⚠️ خطأ في الاتصال بـ ADB: {e}")
                self.use_adbutils = False

    def _run_adb_command(self, command: str) -> str:
        """تنفيذ أمر ADB عبر سطر الأوامر"""
        try:
            cmd = f"adb {f'-s {self.serial} ' if self.serial else ''}{command}"
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=config.ADB_TIMEOUT
            )
            return result.stdout.strip()
        except FileNotFoundError:
            print("❌ ADB غير مثبت أو غير موجود في PATH")
            return ""
        except subprocess.TimeoutExpired:
            print("❌ انتهت مهلة أمر ADB")
            return ""
        except Exception as e:
            print(f"❌ خطأ في ADB: {e}")
            return ""

    def is_connected(self) -> bool:
        """التحقق من اتصال الجهاز"""
        if self.use_adbutils and self.device:
            try:
                self.device.shell("echo test")
                return True
            except Exception:
                return False
        else:
            result = self._run_adb_command("devices")
            return "device" in result

    def screenshot(self, filename: str = None) -> str:
        """
        التقاط صورة شاشة

        Args:
            filename: مسار حفظ الصورة

        Returns:
            مسار الصورة المحفوظة
        """
        filename = filename or config.ADB_LOCAL_SCREENSHOT

        try:
            if self.use_adbutils and self.device:
                # استخدام adbutils
                import io
                from PIL import Image

                png_data = self.device.shell("screencap -p", encoding=None)
                image = Image.open(io.BytesIO(png_data))
                image.save(filename)
            else:
                # استخدام سطر الأوامر
                remote = config.ADB_SCREENSHOT_PATH
                self._run_adb_command(f"shell screencap -p {remote}")
                self._run_adb_command(f"pull {remote} {filename}")
                self._run_adb_command(f"shell rm {remote}")

            if os.path.exists(filename):
                print(f"📸 تم حفظ لقطة الشاشة: {filename}")
                return filename
            else:
                print("❌ فشل في حفظ لقطة الشاشة")
                return ""

        except Exception as e:
            print(f"❌ خطأ في التقاط الشاشة: {e}")
            return ""

    def tap(self, x: int, y: int) -> bool:
        """
        النقر على نقطة على الشاشة

        Args:
            x: الإحداثي الأفقي
            y: الإحداثي العمودي

        Returns:
            True إذا تم النقر بنجاح
        """
        try:
            if self.use_adbutils and self.device:
                self.device.shell(f"input tap {x} {y}")
            else:
                self._run_adb_command(f"shell input tap {x} {y}")
            return True
        except Exception as e:
            print(f"❌ خطأ في النقر: {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int,
              duration: int = 300) -> bool:
        """سحب من نقطة إلى أخرى"""
        try:
            cmd = f"shell input swipe {x1} {y1} {x2} {y2} {duration}"
            if self.use_adbutils and self.device:
                self.device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")
            else:
                self._run_adb_command(cmd)
            return True
        except Exception as e:
            print(f"❌ خطأ في السحب: {e}")
            return False

    def get_screen_size(self) -> tuple:
        """الحصول على حجم الشاشة"""
        try:
            if self.use_adbutils and self.device:
                output = self.device.shell("wm size")
            else:
                output = self._run_adb_command("shell wm size")

            # تحليل "Physical size: 1080x1920"
            if "x" in output:
                parts = output.split(":")[-1].strip().split("x")
                return int(parts[0]), int(parts[1])
        except Exception:
            pass

        return 1080, 1920  # القيمة الافتراضية

    def get_letters_from_game(self) -> str:
        """
        التقاط صورة الشاشة واستخراج الحروف

        Returns:
            الحروف المستخرجة
        """
        from utils.ocr import extract_letters_from_image, manual_input_fallback

        # التقاط صورة الشاشة
        screenshot_path = self.screenshot()
        if not screenshot_path:
            print("⚠️ فشل التقاط الشاشة، يرجى إدخال الحروف يدوياً")
            return manual_input_fallback()

        # استخراج الحروف
        letters = extract_letters_from_image(screenshot_path)

        if not letters:
            print("⚠️ فشل استخراج الحروف، يرجى إدخال الحروف يدوياً")
            return manual_input_fallback()

        return letters

    def solve_and_tap(
        self,
        words: list,
        letter_positions: dict = None,
        delay: float = 0.5
    ) -> int:
        """
        النقر على الإجابات تلقائياً

        Args:
            words: قائمة الكلمات للنقر
            letter_positions: إحداثيات الحروف {حرف: (x, y)}
            delay: التأخير بين النقرات

        Returns:
            عدد الكلمات التي تم النقر عليها
        """
        if not letter_positions:
            print("⚠️ يجب تحديد إحداثيات الحروف على الشاشة")
            print("   يمكنك استخدام 'adb shell getevent' لتحديد الإحداثيات")
            return 0

        tapped = 0
        for word in words:
            print(f"   📝 جاري كتابة: {word}")
            for char in word:
                if char in letter_positions:
                    x, y = letter_positions[char]
                    self.tap(x, y)
                    time.sleep(0.1)  # تأخير قصير بين الحروف

            time.sleep(delay)  # تأخير بين الكلمات
            tapped += 1

        print(f"✅ تم النقر على {tapped} كلمة")
        return tapped


# === اختبار ===
if __name__ == "__main__":
    print("=" * 50)
    print("   اختبار وحدة ADB")
    print("=" * 50)

    adb = ADBHelper()

    if adb.is_connected():
        print("✅ الجهاز متصل")
        size = adb.get_screen_size()
        print(f"📐 حجم الشاشة: {size[0]}x{size[1]}")
    else:
        print("❌ لا يوجد جهاز متصل")
        print("   تأكد من:")
        print("   1. تثبيت ADB")
        print("   2. تفعيل USB Debugging")
        print("   3. توصيل الهاتف بالكمبيوتر")