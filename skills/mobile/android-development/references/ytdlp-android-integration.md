# yt-dlp Android Integration Guide

## Library Setup

```gradle
// settings.gradle
dependencyResolutionManagement {
    repositories {
        mavenCentral()
        maven { url 'https://jitpack.io' }
    }
}

// app/build.gradle
dependencies {
    implementation 'io.github.junkfood02.youtubedl-android:library:0.18.1'
    implementation 'io.github.junkfood02.youtubedl-android:ffmpeg:0.18.1'
}
```

**AndroidManifest.xml:**
```xml
<application android:extractNativeLibs="true" ...>
```

## Initialization

```kotlin
// Must be called before any yt-dlp operations
try {
    YoutubeDL.getInstance().init(context)
} catch (e: Exception) { }

// Optional: update to latest version
try {
    YoutubeDL.getInstance().updateYoutubeDL(context)
    YoutubeDL.getInstance().init(context) // re-init after update
} catch (e: Exception) { }
```

## Download Video

```kotlin
val request = YoutubeDLRequest(url)
request.addOption("-o", outputTemplate) // e.g. "/path/%(title)s.%(ext)s"
request.addOption("--no-warnings")
request.addOption("--no-check-certificates")
request.addOption("--no-playlist")
request.addOption("-f", "best")

// Platform-specific bypasses (CRITICAL)
if (url.contains("youtube.com") || url.contains("youtu.be")) {
    request.addOption("--extractor-args", "youtube:player_client=android")
}
if (url.contains("tiktok.com")) {
    request.addOption("--extractor-args", "tiktok:api_hostname=api-h2.tiktokv.com")
}
request.addOption("--geo-bypass")
request.addOption("--force-ipv4")

YoutubeDL.getInstance().execute(request) { progress, etaInSeconds, line ->
    // progress: 0-100, line: yt-dlp output text
}
```

## Extract Audio → MP3

```kotlin
// Step 1: Download best audio
request.addOption("-f", "bestaudio")

// Step 2: Convert with FFmpeg Kit
val cmd = "-i \"$inputPath\" -vn -acodec libmp3lame -q:a 2 \"$outputPath\""
val success = ReturnCode.isSuccess(FFmpegKit.execute(cmd).returnCode)

// Other formats:
// AAC: "-i ... -vn -acodec aac -b:a 192k ..."
// WAV: "-i ... -vn -acodec pcm_s16le ..."
// OGG: "-i ... -vn -acodec libvorbis -q:a 4 ..."
```

**Do NOT use `--extract-audio` flag** — triggers NoneType bug on Facebook.

## Get Video Info (without downloading)

```kotlin
val info = YoutubeDL.getInstance().getInfo(request)
val title = info.title
val url = info.url // May be null for some platforms (Facebook)
```

**Pitfall:** `info.url` is null for Facebook and some other platforms. Use `execute()` for direct download instead of `getInfo()` + manual download.

## Platform Support Matrix

| Platform | Video | Audio | Image | Notes |
|----------|-------|-------|-------|-------|
| Facebook | ✅ | ✅ | ❌ | Needs `player_client` for some videos |
| YouTube | ✅ | ✅ | ❌ | Needs `player_client=android` to avoid 403 |
| TikTok | ✅ | ✅ | ❌ | Needs `api_hostname` override |
| Instagram | ⚠️ | ⚠️ | ⚠️ | Requires authentication (cookies) |
| Twitter/X | ⚠️ | ⚠️ | ⚠️ | May timeout due to regional blocks |
| Reddit | ✅ | ✅ | ✅ | Works without special options |
| Direct URLs | ✅ | ✅ | ✅ | Any direct .mp4/.jpg/.mp3 URL |

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `HTTP Error 403: Forbidden` | YouTube anti-bot | Add `--extractor-args youtube:player_client=android` |
| `'NoneType' object has no attribute 'lower'` | Old yt-dlp version or `--extract-audio` flag | Use `-f bestaudio` instead, or update yt-dlp |
| `Unable to extract webpage video data` | TikTok anti-bot | Add `--extractor-args tiktok:api_hostname=api-h2.tiktokv.com` |
| `Instagram sent an empty media response` | Requires login | Not fixable without cookies |
| `failed to update youtube-dl` | Network issue or blocked | Library falls back to bundled version |

## FFmpeg Kit (for audio conversion)

FFmpeg Kit was retired from Maven in April 2025. Use local AAR:

1. Download from: `https://artifactory.appodeal.com/appodeal-public/com/arthenica/ffmpeg-kit-full-gpl/6.0-2.LTS/ffmpeg-kit-full-gpl-6.0-2.LTS.aar`
2. Place in `app/libs/ffmpeg-kit.aar`
3. In build.gradle: `implementation(files("libs/ffmpeg-kit.aar"))` + `implementation("com.arthenica:smart-exception-java:0.2.1")`
