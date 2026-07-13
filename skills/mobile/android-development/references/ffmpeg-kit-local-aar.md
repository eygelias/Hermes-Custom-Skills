# FFmpeg Kit for Android — Local AAR Setup

## Problem
FFmpegKit was **archived April 2025** by its maintainer. The Maven Central artifacts (`com.arthenica:ffmpeg-kit-*`) are no longer reliably available. Gradle builds fail with:
```
Could not find com.arthenica:ffmpeg-kit-full:6.0-2
```

## Solution — Local AAR from Appodeal Mirror

### Step 1: Download AAR
```bash
curl -L -o app/libs/ffmpeg-kit.aar \
  "https://artifactory.appodeal.com/appodeal-public/com/arthenica/ffmpeg-kit-full-gpl/6.0-2.LTS/ffmpeg-kit-full-gpl-6.0-2.LTS.aar"
```
Size: ~70MB (includes native libs for arm64-v8a, armeabi-v7a, x86_64, x86)

### Step 2: build.gradle (app level)
```groovy
android {
    defaultConfig {
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a', 'x86_64', 'x86'
        }
    }
}

dependencies {
    implementation(files("libs/ffmpeg-kit.aar"))
    implementation("com.arthenica:smart-exception-java:0.2.1")  // REQUIRED companion dep
}
```

**Critical**: Use `smart-exception-java:0.2.1`, NOT `smart-exception-java9`. The Java 9 variant causes class loading issues.

### Step 3: Use in Code
```kotlin
import com.arthenica.ffmpegkit.FFmpegKit
import com.arthenica.ffmpegkit.ReturnCode

// Convert video to MP3
val session = FFmpegKit.execute("-i input.mp4 -vn -acodec libmp3lame -q:a 2 output.mp3")
val success = ReturnCode.isSuccess(session.returnCode)

// Extract audio as AAC
FFmpegKit.execute("-i input.mp4 -vn -acodec aac -b:a 192k output.aac")

// Convert video container (fast, no re-encode)
FFmpegKit.execute("-i input.mp4 -c copy output.mkv")
```

## Variants Available at Appodeal Mirror
- `ffmpeg-kit-full-gpl` — all codecs with GPL (~70MB)
- `ffmpeg-kit-full` — all codecs LGPL only
- `ffmpeg-kit-min` — minimal codecs
- `ffmpeg-kit-audio` — audio codecs only (smaller)

## APK Size Impact
The full GPL variant adds ~70MB to APK (native libs for 4 ABIs). To reduce:
1. Filter ABIs: `ndk { abiFilters 'arm64-v8a', 'armeabi-v7a' }` (drops x86)
2. Use `ffmpeg-kit-audio` or `ffmpeg-kit-min` instead of full
3. Use Android App Bundle (AAB) for Play Store — only ships needed ABI per device

## Alternative: Build from Source
If the mirror goes down, build from the archived repo:
```bash
git clone https://github.com/arthenica/ffmpeg-kit.git
cd ffmpeg-kit
export ANDROID_SDK_ROOT=/path/to/sdk
export ANDROID_NDK_ROOT=/path/to/ndk
./android.sh --lts
```
Requires matching NDK version — check FFmpegKit wiki for compatibility.
