[app]
# Neon Dodge - Android build
# Build with Kivy + Buildozer in GitHub Actions.

title = Neon Dodge
package.name = neondodge
package.domain = org.neondodge
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav
source.include_patterns = data/*,data/sounds/*
version = 1.0.0
requirements = python3,kivy
orientation = landscape
fullscreen = 0
icon.filename = %(source.dir)s/data/neondodge_icon.png
presplash.filename = %(source.dir)s/data/presplash.png

# Build for common Android phones.
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# No permissions are needed for this offline game.

[buildozer]
log_level = 2
warn_on_root = 0
