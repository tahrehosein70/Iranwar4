#!/bin/bash
echo "🎮 ساخت APK جنگ منطقه‌ای ایران"
echo "================================"
echo "📋 بررسی ابزارها..."

if ! command -v buildozer &> /dev/null; then
    echo "نصب buildozer..."
    pip3 install buildozer cython
fi

echo "🔧 شروع ساخت APK..."
buildozer android debug

if [ $? -eq 0 ]; then
    echo "✅ APK آماده است: bin/iranwargame-1.0-debug.apk"
else
    echo "❌ خطا در ساخت - راهنما در README.md"
fi
