name: Build APK

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:  # Allows manual trigger

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          build-essential \
          git \
          ffmpeg \
          libsdl2-dev \
          libsdl2-image-dev \
          libsdl2-mixer-dev \
          libsdl2-ttf-dev \
          libportmidi-dev \
          libswscale-dev \
          libavformat-dev \
          libavcodec-dev \
          zlib1g-dev \
          libgstreamer1.0-dev \
          libgstreamer-plugins-base1.0-dev
    
    - name: Install Java (required for Android build)
      uses: actions/setup-java@v3
      with:
        distribution: 'temurin'
        java-version: '11'
    
    - name: Setup Android SDK
      uses: android-actions/setup-android@v2
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install buildozer cython
        pip install -r requirements.txt
    
    - name: Cache Buildozer dependencies
      uses: actions/cache@v3
      with:
        path: |
          .buildozer
          ~/.buildozer
        key: ${{ runner.os }}-buildozer-${{ hashFiles('buildozer.spec') }}
        restore-keys: |
          ${{ runner.os }}-buildozer-
    
    - name: Build APK with Buildozer
      run: |
        buildozer android debug
    
    - name: Upload APK artifact
      uses: actions/upload-artifact@v3
      with:
        name: vibrotactile-app-debug
        path: bin/*.apk
        retention-days: 30
    
    - name: Create Release (on tag push)
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: bin/*.apk
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
