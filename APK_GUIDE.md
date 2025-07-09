# راهنمای ساخت APK برای بازی جنگ منطقه‌ای ایران

## روش اول: استفاده از Buildozer (Linux/WSL)

### پیش‌نیازها
```bash
# نصب پیش‌نیازهای سیستم
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# نصب Android SDK
wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
mkdir -p ~/android-sdk/cmdline-tools
unzip commandlinetools-linux-8512546_latest.zip -d ~/android-sdk/cmdline-tools
mv ~/android-sdk/cmdline-tools/cmdline-tools ~/android-sdk/cmdline-tools/latest

# تنظیم متغیرهای محیطی
echo 'export ANDROID_SDK_ROOT=$HOME/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools' >> ~/.bashrc
source ~/.bashrc

# نصب NDK
$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager "platforms;android-33" "build-tools;33.0.0" "ndk;25.2.9519653"
```

### ساخت APK
```bash
# کلون کردن پروژه
git clone <repository-url>
cd iran-war-game

# نصب buildozer
pip install buildozer

# ویرایش آدرس سرور در mobile_app.py
# تغییر خط 285: self.server_url = "http://YOUR_SERVER_IP:5000"

# ساخت APK
buildozer android debug

# فایل APK در bin/iranwargame-1.0-debug.apk ایجاد می‌شود
```

## روش دوم: استفاده از GitHub Actions (آسان‌تر)

### گام‌ها:
1. پروژه را در GitHub آپلود کنید
2. فایل `.github/workflows/build.yml` ایجاد کنید:

```yaml
name: Build APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.9
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install buildozer
        sudo apt update
        sudo apt install -y git zip unzip openjdk-8-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
    
    - name: Build APK
      run: |
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: iran-war-game-apk
        path: bin/*.apk
```

3. کد را push کنید و APK را از Actions دانلود کنید

## روش سوم: استفاده از Replit APK Builder

### فایل‌های مورد نیاز:
- `main.py` (آماده شده)
- `mobile_app.py` (آماده شده)
- `buildozer.spec` (آماده شده)

### دستورات Replit:
```bash
# نصب buildozer
pip install buildozer

# ویرایش آدرس سرور
nano mobile_app.py
# خط 285 را به آدرس IP سرورتان تغییر دهید

# ساخت APK (ممکن است 20-30 دقیقه طول بکشد)
buildozer android debug
```

## روش چهارم: استفاده از Online APK Builders

### 1. Appetize.io
- فایل‌های پروژه را zip کنید
- در Appetize.io آپلود کنید
- APK دانلود خواهد شد

### 2. App Inventor (ساده‌تر)
- کد Python را به بلوک‌های App Inventor تبدیل کنید
- مستقیماً APK بسازید

## تنظیمات مهم قبل از ساخت APK

### 1. تغییر آدرس سرور
فایل `mobile_app.py` خط 285:
```python
self.server_url = "http://YOUR_SERVER_IP:5000"
```

مثال:
```python
self.server_url = "http://192.168.1.100:5000"  # آدرس کامپیوتر شما
# یا
self.server_url = "https://yourproject.replit.app"  # اگر در Replit deploy کردید
```

### 2. تنظیم مجوزها
در فایل `buildozer.spec`:
```ini
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE
```

### 3. آیکون و Splash Screen
```ini
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/splash.png
```

## نصب APK روی گوشی

### 1. فعال‌سازی نصب از منابع نامعلوم:
- تنظیمات > امنیت > منابع نامعلوم > فعال

### 2. نصب APK:
- فایل APK را روی گوشی کپی کنید
- روی فایل APK ضربه بزنید
- "نصب" را انتخاب کنید

### 3. اشتراک‌گذاری در واتساپ:
- APK نصب شده را در واتساپ به عنوان فایل ارسال کنید
- یا لینک دانلود APK را ارسال کنید

## عیب‌یابی

### خطای "buildozer command not found":
```bash
export PATH=$PATH:~/.local/bin
pip install --user buildozer
```

### خطای Android SDK:
```bash
export ANDROID_SDK_ROOT=$HOME/android-sdk
export ANDROID_NDK_ROOT=$ANDROID_SDK_ROOT/ndk/25.2.9519653
```

### خطای Java:
```bash
sudo apt install openjdk-8-jdk
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

## سایز فایل APK

APK نهایی حدود 15-25 مگابایت خواهد بود که برای ارسال در واتساپ مناسب است.

## نکات امنیتی

1. هرگز اطلاعات حساس (پسورد، کلید API) در کد قرار ندهید
2. از HTTPS برای ارتباط با سرور استفاده کنید
3. APK را از منابع معتبر دانلود کنید

## پشتیبانی

اگر در ساخت APK مشکل داشتید، می‌توانید:
1. از نسخه وب بازی استفاده کنید
2. از برنامه‌های شبیه‌ساز Android در کامپیوتر استفاده کنید
3. از خدمات آنلاین APK Builder استفاده کنید