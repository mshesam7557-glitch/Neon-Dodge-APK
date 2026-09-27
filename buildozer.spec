[app]
# (str) Title of your application
title = Neon Dodge

# (str) Package name
package.name = neondodge

# (str) Package domain (needed for android/ios packaging)
package.domain = org.neondodge

# (str) Source code where main.py live
source.dir = .

# (list) List of source files to include (let empty to include all the files)
source.include_exts = py,png,wav,json,txt

# (str) Application version
version = 1.0

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = landscape

# (bool) Fullscreen mode
fullscreen = 0

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Supported requirements
requirements = python3,kivy

# (str) Android API target
android.api = 35

# (str) Android minimum API
android.minapi = 23

# (str) Android NDK version
android.ndk = 28c

# (str) Android archs
android.archs = arm64-v8a, armeabi-v7a

# (bool) Indicate if the application should be fullscreen or not
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.apptheme = "@android:style/Theme.Material.Light.NoActionBar"

# (str) Python entrypoint
source.main = main.py

[buildozer]
# (str) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2
warn_on_root = 1
