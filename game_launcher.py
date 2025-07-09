#!/usr/bin/env python3
"""
Game Launcher for Iran War Game
Allows users to choose between online and offline modes
"""

import subprocess
import socket
import sys
import os
import time
import signal
import threading
from datetime import datetime

class GameLauncher:
    def __init__(self):
        self.online_process = None
        self.offline_process = None
        self.current_mode = None
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def check_internet(self):
        """Check if internet connection is available"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def display_banner(self):
        """Display game banner"""
        print("""
    ═══════════════════════════════════════════════════════════
    🎮          جنگ منطقه‌ای ایران - مدیریت بازی            🏛️
    ═══════════════════════════════════════════════════════════
    
    🌟 انتخاب حالت بازی:
    
    [1] 🌐 آنلاین      - بازی از طریق اینترنت (Replit)
    [2] 🏠 آفلاین      - بازی روی WiFi محلی (بدون اینترنت)
    [3] 📋 راهنما      - نحوه استفاده و تنظیمات
    [4] ❌ خروج        - بستن برنامه
    
    ═══════════════════════════════════════════════════════════
        """)
    
    def display_status(self):
        """Display current system status"""
        internet = self.check_internet()
        local_ip = self.get_local_ip()
        
        print(f"""
    📊 وضعیت سیستم:
    ─────────────────────────────────────────────────────────────
    📡 اتصال اینترنت:    {'✅ موجود' if internet else '❌ قطع'}
    🖥️  آدرس محلی:      {local_ip}
    ⏰ زمان:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    🎮 حالت فعال:       {self.current_mode if self.current_mode else 'هیچکدام'}
    ─────────────────────────────────────────────────────────────
        """)
    
    def start_online_mode(self):
        """Start online mode server"""
        if self.offline_process:
            print("🛑 ابتدا حالت آفلاین را متوقف می‌کنیم...")
            self.stop_offline_mode()
        
        print("🌐 در حال راه‌اندازی سرور آنلاین...")
        try:
            self.online_process = subprocess.Popen([
                sys.executable, "simple_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.current_mode = "آنلاین (Port 5000)"
            
            print(f"""
    ✅ سرور آنلاین راه‌اندازی شد!
    
    🔗 لینک‌های دسترسی:
    ├─ محلی:    http://localhost:5000
    ├─ شبکه:    http://{self.get_local_ip()}:5000
    └─ Replit:  [آدرس Replit شما]
    
    📱 برای استفاده:
    ├─ لینک را در مرورگر باز کنید
    ├─ بازی ایجاد کنید یا به بازی بپیوندید
    └─ با دوستان از طریق اینترنت بازی کنید
    
    ⚠️  نوت: برای توقف Ctrl+C بزنید
            """)
            
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی سرور آنلاین: {e}")
    
    def start_offline_mode(self):
        """Start offline mode server"""
        if self.online_process:
            print("🛑 ابتدا حالت آنلاین را متوقف می‌کنیم...")
            self.stop_online_mode()
        
        print("🏠 در حال راه‌اندازی سرور آفلاین...")
        try:
            self.offline_process = subprocess.Popen([
                sys.executable, "offline_simple_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.current_mode = "آفلاین (Port 5001)"
            local_ip = self.get_local_ip()
            
            print(f"""
    ✅ سرور آفلاین راه‌اندازی شد!
    
    🔗 لینک‌های دسترسی:
    ├─ محلی:    http://localhost:5001
    └─ شبکه:    http://{local_ip}:5001
    
    📱 برای استفاده:
    ├─ همه گوشی‌ها به همان WiFi وصل شوند
    ├─ آدرس بالا را در مرورگر باز کنید
    ├─ بازی ایجاد کنید یا به بازی بپیوندید
    └─ بدون نیاز به اینترنت بازی کنید!
    
    📤 برای اشتراک‌گذاری در واتساپ:
    ┌─────────────────────────────────────────────┐
    │ 🎮 بازی جنگ منطقه‌ای ایران - آفلاین!      │
    │                                             │
    │ 📶 به WiFi من وصل شو و این آدرس رو باز کن: │
    │ http://{local_ip}:5001                      │
    │                                             │
    │ ⚡ بدون نیاز به اینترنت!                   │
    │ 👥 تا 8 نفر می‌تونیم بازی کنیم              │
    │                                             │
    │ بریم جنگ! ⚔️                               │
    └─────────────────────────────────────────────┘
    
    ⚠️  نوت: برای توقف Ctrl+C بزنید
            """)
            
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی سرور آفلاین: {e}")
    
    def stop_online_mode(self):
        """Stop online mode server"""
        if self.online_process:
            try:
                self.online_process.terminate()
                self.online_process.wait(timeout=5)
                print("✅ سرور آنلاین متوقف شد")
            except:
                self.online_process.kill()
                print("⚠️ سرور آنلاین به زور متوقف شد")
            finally:
                self.online_process = None
                if self.current_mode and "آنلاین" in self.current_mode:
                    self.current_mode = None
    
    def stop_offline_mode(self):
        """Stop offline mode server"""
        if self.offline_process:
            try:
                self.offline_process.terminate()
                self.offline_process.wait(timeout=5)
                print("✅ سرور آفلاین متوقف شد")
            except:
                self.offline_process.kill()
                print("⚠️ سرور آفلاین به زور متوقف شد")
            finally:
                self.offline_process = None
                if self.current_mode and "آفلاین" in self.current_mode:
                    self.current_mode = None
    
    def show_guide(self):
        """Show usage guide"""
        print("""
    📋 راهنمای استفاده:
    ═══════════════════════════════════════════════════════════
    
    🌐 حالت آنلاین:
    ├─ برای بازی از طریق اینترنت
    ├─ بازیکنان می‌تونن از هر جای دنیا بپیوندن
    ├─ نیاز به اتصال اینترنت پایدار
    └─ مناسب برای بازی از راه دور
    
    🏠 حالت آفلاین:
    ├─ برای بازی روی WiFi محلی
    ├─ بدون نیاز به اینترنت
    ├─ سرعت بالا و تاخیر کم
    ├─ مناسب برای جمع‌های دوستانه
    └─ قابل اجرا در مناطق بدون اینترنت
    
    📱 نصب روی گوشی:
    ├─ PWA: "Add to Home Screen" در مرورگر
    ├─ APK: ساخت با buildozer (راهنمای جداگانه)
    └─ فایل‌های راهنما: APK_GUIDE.md، PWA_SETUP.md
    
    🎮 نحوه بازی:
    ├─ حداقل 2 نفر، حداکثر 8 نفر
    ├─ میزبان بازی ایجاد می‌کند
    ├─ سایرین با Game ID می‌پیوندند
    ├─ بازی نوبتی روی نقشه ایران
    └─ هدف: تسخیر بیشترین مناطق
    
    🔧 تنظیمات پیشرفته:
    ├─ فایل config.py برای تغییر تنظیمات
    ├─ پورت‌ها: 5000 (آنلاین)، 5001 (آفلاین)
    ├─ لاگ‌ها در فایل‌های .log
    └─ بک‌آپ خودکار وضعیت بازی
    
    ═══════════════════════════════════════════════════════════
        """)
    
    def cleanup(self):
        """Cleanup running processes"""
        print("\n🧹 در حال تمیز کردن...")
        self.stop_online_mode()
        self.stop_offline_mode()
        print("✅ تمام پردازش‌ها متوقف شدند")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n\n🛑 درخواست توقف دریافت شد...")
        self.cleanup()
        print("👋 خداحافظ!")
        sys.exit(0)
    
    def run(self):
        """Main program loop"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                self.display_banner()
                self.display_status()
                
                try:
                    choice = input("    انتخاب کنید (1-4): ").strip()
                    
                    if choice == '1':
                        self.start_online_mode()
                        input("\n    ⏸️  برای بازگشت به منو Enter بزنید...")
                        
                    elif choice == '2':
                        self.start_offline_mode()
                        input("\n    ⏸️  برای بازگشت به منو Enter بزنید...")
                        
                    elif choice == '3':
                        self.show_guide()
                        input("\n    ⏸️  برای بازگشت به منو Enter بزنید...")
                        
                    elif choice == '4':
                        break
                        
                    else:
                        print("    ❌ انتخاب نامعتبر! لطفاً عدد 1 تا 4 وارد کنید.")
                        time.sleep(2)
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                    
        except Exception as e:
            print(f"❌ خطای غیرمنتظره: {e}")
        finally:
            self.cleanup()
            print("👋 خداحافظ!")

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()