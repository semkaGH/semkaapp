[app]

title = SemkaApp
package.name = semkaapp
package.domain = com.yourname

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

version = 0.1
requirements = python3,kivy

orientation = portrait

[buildozer]
log_level = 2

[android]
api = 33
minapi = 21
ndk = 25b
android.accept_sdk_license = True
android.permissions = INTERNET