[app]
title = Habit Tracker
package.name = habittracker
package.domain = org.example
source.dir = .
source.include_exts = py,kv,png,jpg,db,json
version = 1.0
requirements = python3,kivy==2.3.0,kivymd==1.1.1,sqlite3
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.arch = armeabi-v7a
android.entrypoint = main.py
android.requirements = python3,kivy,kivymd,sqlite3
android.permissions = INTERNET,VIBRATE
