# اگر Actions چیزی نشان نداد

مشکل معمول، ساختار اشتباه پوشه است.

در صفحه اصلی Repository باید **مستقیماً** این را ببینی:

```text
.github/
  workflows/
    build-apk.yml
```

این ساختار اشتباه است:

```text
.github/
  workflows/
    .github/
      workflows/
        build-apk.yml
```

اسم Repository هر چیزی می‌تواند باشد؛ اسم خاص لازم نیست.

همچنین `build-apk.yml` باید روی **default branch** (معمولاً `main`) قرار گرفته باشد تا گزینه `Run workflow` دیده شود.
