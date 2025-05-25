[app]
# App basic info
title = Vibrotactile Music App
package.name = vibrotactileapp
package.domain = org.example.vibrotactileapp

# Source code settings
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mid,midi

# Version
version = 0.1
version.regex = __version__ = ['"]([^'"]*)['"]
version.filename = %(source.dir)s/main.py

# Requirements - IMPORTANT: Matches your app's dependencies
requirements = python3,kivy,mido,jnius,android

# Android specific
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.sdk = 30
android.ndk = 23b
android.gradle_dependencies = 

# Icon (optional)
#icon.filename = %(source.dir)s/assets/icon.png

# Orientation
orientation = portrait

# Services (if needed for background tasks)
#android.add_src = 

[buildozer]
# Buildozer log level
log_level = 2

# Cache directory
#cache_dir = .buildozer_cache
