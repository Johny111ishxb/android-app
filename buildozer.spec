[app]

title = VibrotactileApp
package.name = vibrotactile
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,mid
version = 1.0
requirements = python3==3.10.12,kivy==2.2.1,mido==1.2.10,android,jnius,hostpython3,pygame
orientation = portrait
android.permissions = INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE, ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.ndk = 23b
android.ndk_path = /opt/android-ndk-r23b
android.sdk_path = /opt/android-sdk
android.arch = arm64-v8a
p4a.branch = develop