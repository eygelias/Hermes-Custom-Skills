---
name: android-video-downloader
description: Build Android video downloader apps using yt-dlp (youtubedl-android). Share-intent based — appears in Android share sheet for any app. Supports Facebook, TikTok, Instagram, YouTube, Twitter, Reddit, and 1000+ sites.
category: mobile
triggers:
  - "video downloader"
  - "download video from social media"
  - "descargar video"
  - "social media downloader"
  - "yt-dlp android"
---

# Android Video Downloader with yt-dlp

## Critical: Use yt-dlp, NOT custom extractors

After extensive failed attempts with:
- ❌ Cobalt API (instances are unreliable, require auth, go down frequently)
- ❌ Custom HTTP scrapers (social media platforms use JS-heavy pages)
- ❌ WebView-based extraction (times out, captures wrong URLs like fonts/CSS)
- ❌ FFmpeg Kit from Maven (archived/retired in 2025)

The ONLY reliable approach is **yt-dlp** via `youtubedl-android` library. This is what apps like Seal, NewPipe, and every successful downloader uses.

## Dependencies (build.gradle)

```groovy
// yt-dlp for Android
implementation 'io.github.junkfood02.youtubedl-android:library:0.18.1'
implementation 'io.github.junkfood02.youtubedl-android:ffmpeg:0.18.1'
// Note: NO separate FFmpeg Kit needed — yt-dlp bundles its own ffmpeg
```

Repository (settings.gradle):
```groovy
maven { url 'https://jitpack.io' }
```

## AndroidManifest Requirements

```xml
<application
    android:extractNativeLibs="true"  <!-- REQUIRED for yt-dlp native binaries -->
    android:requestLegacyExternalStorage="true"
    ...>
```

## Initialization (in Application or first Activity/Service)

```kotlin
try {
    YoutubeDL.getInstance().init(context)
} catch (e: Exception) {
    // Already initialized or init failed
}
```

## Downloading Videos

```kotlin
val request = YoutubeDLRequest(url)
request.addOption("-o", outputFile.absolutePath)
request.addOption("--no-warnings")
request.addOption("--no-check-certificates")
request.addOption("-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best")

YoutubeDL.getInstance().execute(request) { progress, etaInSeconds, line ->
    // Update progress notification
    // progress: Float (0-100), etaInSeconds: Long, line: String
}
```

## Extracting Audio (video → MP3)

**Do NOT use `-f bestaudio` or `-x`** — triggers `'NoneType' object has no attribute 'lower'` bug in bundled yt-dlp.

**Correct approach:** Download video with `-f best`, then convert with FFmpeg Kit:

```kotlin
// Step 1: Download video
val request = YoutubeDLRequest(url)
request.addOption("-o", tempTemplate)
request.addOption("-f", "best")
YoutubeDL.getInstance().execute(request) { progress, _, _ -> }

// Step 2: Convert to MP3 with FFmpeg Kit
val command = "-i \"$inputPath\" -vn -acodec libmp3lame -q:a 2 \"$outputPath\""
val session = FFmpegKit.execute(command)
val success = ReturnCode.isSuccess(session.returnCode)
// Then delete the temp video file
```

**FFmpeg Kit dependency** (Maven version retired April 2025 — use local AAR):
```gradle
implementation(files("libs/ffmpeg-kit.aar"))  // Download from Appodeal mirror
implementation("com.arthenica:smart-exception-java:0.2.1")  // REQUIRED companion dep
```
Download AAR: `https://artifactory.appodeal.com/appodeal-public/com/arthenica/ffmpeg-kit-full-gpl/6.0-2.LTS/ffmpeg-kit-full-gpl-6.0-2.LTS.aar`

## Getting Video Info Without Downloading

```kotlin
val request = YoutubeDLRequest(url)
request.addOption("--no-warnings")
val info = YoutubeDL.getInstance().getInfo(request)
// info.title, info.url, info.duration, etc.
```

## YouTube Anti-Bypass (403 Forbidden)

YouTube actively blocks yt-dlp. Bypass with Android player client:

```kotlin
if (url.contains("youtube.com") || url.contains("youtu.be")) {
    request.addOption("--extractor-args", "youtube:player_client=android")
    request.addOption("--user-agent", "com.google.android.youtube/19.09.37 (Linux; U; Android 14) gzip")
    request.addOption("--referer", "https://www.youtube.com/")
    request.addOption("--geo-bypass")
    request.addOption("--force-ipv4")
}
```

If still gets 403, YouTube is actively blocking — affects ALL downloaders (Seal, NewPipe, etc.). No workaround exists; try later or use VPN.

## Critical: Bundle latest yt-dlp binary in assets

The `youtubedl-android` library (0.18.1) bundles an OLD yt-dlp with bugs on Facebook, TikTok, YouTube. The library's `updateYoutubeDL()` **fails silently** on many devices. Do NOT rely on it.

**Correct approach — bundle the latest yt-dlp in assets:**

1. Download latest yt-dlp from GitHub:
   ```bash
   curl -L -o app/src/main/assets/yt-dlp/yt-dlp \
     "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
   ```
2. Create `app/src/main/assets/yt-dlp/version.txt` with version string
3. On first run, copy from assets to the library's expected location:

```kotlin
object YtdlpUpdater {
    fun installBundledYtdlp(context: Context) {
        val ytdlpDir = File(context.filesDir, "yt-dlp")
        if (!ytdlpDir.exists()) ytdlpDir.mkdirs()
        val ytdlpBin = File(ytdlpDir, "yt-dlp")
        
        val assetVersion = context.assets.open("yt-dlp/version.txt")
            .bufferedReader().readText().trim()
        val installedVersion = try {
            File(ytdlpDir, "version.txt").readText().trim()
        } catch (e: Exception) { "none" }
        
        if (assetVersion != installedVersion || !ytdlpBin.exists()) {
            context.assets.open("yt-dlp/yt-dlp").use { input ->
                FileOutputStream(ytdlpBin).use { output -> input.copyTo(output) }
            }
            ytdlpBin.setExecutable(true)
            File(ytdlpDir, "version.txt").writeText(assetVersion)
        }
    }
}
```

Then in DownloadService:
```kotlin
YtdlpUpdater.installBundledYtdlp(context)
YoutubeDL.getInstance().init(context)
```

**Test the bundled version first** before building APK:
```bash
yt-dlp --version  # Should match your bundled version
yt-dlp -f best --print "%(title)s" "https://www.facebook.com/share/r/XXXXX/"
```

## Critical: Use `execute()` directly, NOT `getInfo()` + download

For some platforms (Facebook, Instagram), `getInfo()` returns metadata but `info.url` is null. The URL field is only populated for simple direct-link platforms. ALWAYS use `execute()` to download directly — yt-dlp handles format selection and downloading internally.

```kotlin
// ❌ WRONG — info.url is null for Facebook
val info = YoutubeDL.getInfo(request)
// download(info.url) // CRASHES

// ✅ CORRECT — let yt-dlp handle everything
YoutubeDL.execute(request) { progress, _, _ -> ... }
```

## Critical: Audio extraction without ffmpeg

The `-x` flag requires ffmpeg to be found by yt-dlp. If ffmpeg isn't in PATH, you get: `ERROR: ffprobe and ffmpeg not found`. Use `-f bestaudio` instead:

```kotlin
// ❌ Requires ffmpeg
request.addOption("-x")
request.addOption("--audio-format", "mp3")

// ✅ Works without ffmpeg — downloads audio stream directly
request.addOption("-f", "bestaudio")
```

The downloaded file will be in the source format (M4A, WebM, etc.) which Android plays natively.

## TikTok Anti-Bypass

TikTok also needs specific extractor args:

```kotlin
if (url.contains("tiktok.com") || url.contains("vt.tiktok.com")) {
    request.addOption("--extractor-args", "tiktok:api_hostname=api-h2.tiktokv.com")
}
```

## Generic Anti-Bypass (all platforms)

Always add these for better success rates:
```kotlin
request.addOption("--geo-bypass")       // Bypass geo-restrictions
request.addOption("--force-ipv4")       // IPv4 is more compatible
request.addOption("--no-check-certificates")  // Avoid SSL errors
```

## Pitfalls

1. **Progress callback has 3 params**: `{ progress, etaInSeconds, line }` — NOT 2. Compilation error if you get this wrong.

2. **`info.isLive` may not exist**: The property might not be available in all versions. Don't rely on it.

3. **`info.url` is null for many platforms**: Facebook, Instagram, TikTok return null for the direct URL. Don't use getInfo() + download pattern.

4. **APK size ~197MB**: yt-dlp + ffmpeg binaries for all architectures. This is normal.

5. **First download is slow**: yt-dlp initializes AND updates on first use. Subsequent downloads are faster.

6. **File finding after download**: yt-dlp may change the file extension. Use `File.listFiles()` with prefix matching as fallback.

7. **FileProvider for notifications**: On Android 7+, use `FileProvider.getUriForFile()` not `file://` URIs in notification intents. Otherwise `FileUriExposedException`.

8. **extractNativeLibs="true"** is REQUIRED in the manifest. Without it, native binaries won't be extracted and yt-dlp will fail silently.

9. **Notification cleanup**: Cancel progress notification BEFORE showing completion. Use `stopForeground(STOP_FOREGROUND_REMOVE)` not `STOP_FOREGROUND_DETACH`. The "Descargando 100%" stuck notification is a common bug.

10. **Do NOT use `--merge-output-format`**: This triggers the NoneType bug on some platforms. Use `-f best` and let yt-dlp pick the format.

11. **Do NOT use `-f bestaudio` or `-x` for audio**: Triggers `NoneType` bug. Download with `-f best` then convert with FFmpeg Kit.

12. **YouTube 403 Forbidden**: YouTube blocks yt-dlp. Use `--extractor-args youtube:player_client=android` + Android User-Agent. May still fail — YouTube actively fights downloaders.

13. **Cobalt API is dead**: All public Cobalt instances are down or require auth (as of mid-2025). Do NOT use Cobalt API. Use yt-dlp directly.

14. **RadioButtons without RadioGroup**: Standalone RadioButtons don't auto-deselect. Use `setOnClickListener` on each button that manually sets `isChecked` on both buttons.

15. **Test BEFORE building APK**: Install yt-dlp on dev machine (`pip install yt-dlp`), test each platform with the exact same options. Don't make the user install/uninstall repeatedly — they will get exhausted and frustrated.

## Platform Test Results (June 2025)

| Platform | Status | Notes |
|:---------|:-------|:------|
| Facebook | ✅ Works | Videos, Reels, share links |
| YouTube | ✅ Works | With `player_client=android`. May get 403 on some videos |
| YouTube Shorts | ✅ Works | Same as YouTube |
| TikTok | ✅ Works | With `api_hostname=api-h2.tiktokv.com` |
| Instagram | ⚠️ Needs cookies | "empty media response" without login |
| Twitter/X | ⚠️ Region-dependent | May timeout, blocked in some regions |
| Reddit | ✅ Works | |
| SoundCloud | ✅ Works | |

## Pre-Build Testing Checklist

Before delivering APK to user:
1. `pip install yt-dlp` on dev machine
2. Test Facebook video: `yt-dlp -f best --print "%(title)s" <URL>`
3. Test YouTube: `yt-dlp -f best --extractor-args "youtube:player_client=android" --print "%(title)s" <URL>`
4. Test TikTok: `yt-dlp -f best --print "%(title)s" <URL>`
5. Test audio: `yt-dlp -f bestaudio --print "%(title)s" <URL>`
6. Only deliver APK after confirming all tests pass

## Share Intent Pattern

Register an activity with intent filter for `ACTION_SEND` with `text/plain`:

```xml
<activity android:name=".ShareActivity"
    android:theme="@style/Theme.Transparent"
    android:launchMode="singleTop"
    android:noHistory="true"
    android:excludeFromRecents="true">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="text/plain" />
    </intent-filter>
</activity>
```

## Material Chip Selection (visual feedback)

For format selection chips that need clear visual feedback:

```kotlin
chip.setOnCheckedChangeListener { buttonView, isChecked ->
    if (isChecked) {
        for (i in 0 until chipGroup.childCount) {
            val otherChip = chipGroup.getChildAt(i) as? Chip ?: continue
            val isSelected = (otherChip == buttonView)
            otherChip.chipBackgroundColor = ColorStateList.valueOf(
                resources.getColor(if (isSelected) R.color.primary else R.color.card_dark, null)
            )
            otherChip.chipStrokeColor = ColorStateList.valueOf(
                resources.getColor(if (isSelected) R.color.primary else R.color.divider, null)
            )
        }
    }
}
```

## MediaValidator (magic bytes)

Always validate downloaded files before saving. Check magic bytes to confirm the file is actually video/audio/image, not a font, HTML page, or error response. See `MediaValidator.kt` in SocialDownloader project for implementation.

## Reference Projects

- SocialDownloader: `C:\Users\ELY\Desktop\SocialDownloader`
- Seal (reference app): https://github.com/JunkFood02/Seal
- youtubedl-android: https://github.com/yausername/youtubedl-android
