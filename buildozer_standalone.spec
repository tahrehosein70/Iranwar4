[app]

# نام نمایشی اپلیکیشن
title = جنگ منطقه‌ای ایران

# نام پکیج اپلیکیشن  
package.name = iranwargame

# دامنه پکیج (معکوس)
package.domain = ir.iranwargame

# فایل اصلی پایتون
source.main = standalone_apk_app.py

# شامل کردن فایل‌های اضافی
source.include_exts = py,png,jpg,kv,atlas,json,txt,gif,svg

# شامل کردن پوشه‌های اضافی
source.include_patterns = assets/*,static/*,templates/*

# فایل‌هایی که نباید شامل شوند
source.exclude_exts = spec

# فایل‌هایی که نباید کپی شوند
source.exclude_patterns = tests/*,__pycache__/*,*.pyc,bin/*,dist/*,*.egg-info/*

# نسخه اپلیکیشن
version = 1.0

# وابستگی‌های پایتون
requirements = python3,kivy,requests,flask

# آیکون اپلیکیشن (مربعی)
icon.filename = static/cyrus_logo.png

# عکس‌های اپلیکیشن در پلی استور
presplash.filename = static/cyrus_logo.png

# توجه شده اپلیکیشن
orientation = portrait

# سرویس‌های در پس‌زمینه
services = 

# اجازه‌های اندروید
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# معماری پردازنده
android.archs = arm64-v8a, armeabi-v7a

# API اندروید
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

# تنظیمات gradle
android.gradle_dependencies = 

# نام نمایشی در لانچر
android.launcher_name = جنگ ایران

# رنگ نوار وضعیت
android.theme = @android:style/Theme.NoTitleBar

# فعال‌سازی backup
android.allow_backup = True

# حالت fullscreen
fullscreen = 0

# نام APK خروجی
android.release_artifact = %(package.name)s-%(version)s-release.apk

[buildozer]

# مسیر log
log_level = 2

# استفاده از cache
use_cache = 1

# مسیر cache  
cache_dir = .buildozer_cache

# warn on root
warn_on_root = 1