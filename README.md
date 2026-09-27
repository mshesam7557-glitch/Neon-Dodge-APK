# Neon Dodge — Android

این پروژه برای ساخت APK با GitHub Actions آماده شده است.

## ساختار مهم

فایل Workflow **مستقیماً** در این مسیر است:

```text
.github/workflows/build-apk.yml
```

داخل Repository نباید `.github` تو در تو باشد.

ساختار باید دقیقاً شبیه این باشد:

```text
Neon-Dodge-APK/
├── main.py
├── buildozer.spec
├── data/
│   ├── icon.png
│   └── sounds/
└── .github/
    └── workflows/
        └── build-apk.yml
```

## GitHub

1. یک Repository معمولی بساز.
2. **محتویات همین ZIP را مستقیم در ریشه Repository آپلود کن.**
3. حتماً پوشه `.github` و فایل داخل آن آپلود شده باشد.
4. برو به **Actions**.
5. Workflow به نام **Build Neon Dodge APK** را باز کن.
6. روی **Run workflow** بزن.
7. بعد از اتمام، در قسمت Artifacts فایل `Neon-Dodge-APK` را بگیر و APK داخل آن را روی گوشی نصب کن.

نام برنامه روی گوشی: **Neon Dodge**

Fullscreen خاموش است و صفحه به صورت Landscape اجرا می‌شود. کنترل‌ها لمسی هستند.
