[app]

# اطلاعات اصلی اپلیکیشن
title = جنگ منطقه‌ای ایران
package.name = iranwargame
package.domain = ir.iranwargame.hotspot

# فایل اصلی 
source.main = hotspot_game_app.py

# شامل کردن فایل‌ها
source.include_exts = py,png,jpg,jpeg,txt,json

# حذف فایل‌های غیرضروری
source.exclude_exts = spec,pyc,pyo
source.exclude_patterns = tests/*,__pycache__/*,*.egg-info/*,dist/*,build/*

# نسخه اپلیکیشن
version = 2.0

# وابستگی‌های کم (فقط Python standard library)
requirements = python3

# تنظیمات ظاهری
icon.filename = static/cyrus_logo.png
presplash.filename = static/cyrus_logo.png
orientation = portrait

# اجازه‌های اندروید (حداقل ممکن)
android.permissions = ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,INTERNET

# تنظیمات اندروید
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.archs = arm64-v8a, armeabi-v7a

# نام در launcher
android.launcher_name = جنگ ایران

# تنظیمات اضافی
fullscreen = 0
android.allow_backup = True

# بهینه‌سازی
android.add_java_dir = java
android.gradle_dependencies = 
android.ant_dependencies =

# تنظیمات کیفیت
android.release_artifact = %(package.name)s-%(version)s-release.apk
android.debug_artifact = %(package.name)s-%(version)s-debug.apk

[buildozer]

# سطح log
log_level = 2

# استفاده از cache
cache_dir = .buildozer

# هشدار root
warn_on_root = 1