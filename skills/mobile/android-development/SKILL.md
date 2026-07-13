---
name: android-development
description: Android app development — background processing, networking, FCM push notifications, Gradle builds, common pitfalls.
tags: [android, kotlin, mobile, fcm, gradle]
triggers:
  - building an Android app
  - Android notification
  - FCM or Firebase Cloud Messaging
  - Android background service
  - WorkManager or AlarmManager
---

# Android Development

## Background Processing — Three Approaches

| Approach | Min Interval | Notification Required | Survives App Kill | Use Case |
|----------|-------------|----------------------|-------------------|----------|
| **Foreground Service** | Continuous | ✅ Always visible | ❌ (some OEMs kill) | Real-time, always-on |
| **WorkManager** | 15 minutes | ❌ No | ✅ OS-managed | Periodic sync, best reliability |
| **AlarmManager** | ~1 minute | ❌ No | ✅ (with exact alarm perm) | Short-interval polling |

**Recommendation**: Use WorkManager for ≥15min intervals. Use AlarmManager for <15min. Foreground Service only if continuous processing needed.

### AlarmManager Setup
```kotlin
// Requires: SCHEDULE_EXACT_ALARM or USE_EXACT_ALARM permission
val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
val pending = PendingIntent.getBroadcast(context, REQUEST_CODE, intent, FLAG_IMMUTABLE)
alarmManager.setExactAndAllowWhileIdle(
    AlarmManager.ELAPSED_REALTIME_WAKEUP,
    SystemClock.elapsedRealtime() + delayMs,
    pending
)
```

### WorkManager Setup
```kotlin
val request = PeriodicWorkRequestBuilder<MyWorker>(15, TimeUnit.MINUTES)
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .build())
    .build()
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "unique_name", ExistingPeriodicWorkPolicy.KEEP, request
)
```

## HTTP Cleartext Traffic (Critical Pitfall)

**Android 9+ blocks HTTP (non-HTTPS) by default.** If your app connects to `http://` endpoints, requests will silently fail.

### Fix — Two files needed:

**1. `AndroidManifest.xml`** — in `<application>`:
```xml
android:usesCleartextTraffic="true"
android:networkSecurityConfig="@xml/network_security_config"
```

**2. `res/xml/network_security_config.xml`** — create this file:
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">your-domain.com</domain>
    </domain-config>
</network-security-config>
```

**Without both files, HTTP requests fail silently** — no error, no exception, just empty response.

## HTTP Client Choice

- **`HttpURLConnection`** (Android built-in) — most reliable, no dependencies
- **OkHttp** — popular but can have issues on some devices/configurations
- **Recommendation**: Start with `HttpURLConnection`. Only add OkHttp if you need interceptors, connection pooling, or HTTP/2.

## FCM Push Notifications

See `references/fcm-setup.md` for full setup guide.

## Venezuelan Exchange Rate APIs

See `references/venezuelan-exchange-rate-apis.md` — free APIs (ve.dolarapi.com, BCV scraping, Binance P2P) for building Venezuelan finance apps.

## Share Intent Handler

See `references/share-intent-pattern.md` for the transparent-activity share-receiver pattern (used by downloaders, translators, etc.).

### Quick Architecture
```
Server (Worker/Backend) → FCM HTTP v1 API → Google → Device
```

- App receives notifications even when closed — no background service needed
- Requires `google-services.json` in `app/` directory
- Requires `com.google.gms.google-services` Gradle plugin

### Gradle Setup
**Project-level `build.gradle.kts`:**
```kotlin
plugins {
    id("com.google.gms.google-services") version "4.4.0" apply false
}
```

**App-level `build.gradle.kts`:**
```kotlin
plugins {
    id("com.google.gms.google-services")
}
dependencies {
    implementation(platform("com.google.firebase:firebase-bom:32.7.0"))
    implementation("com.google.firebase:firebase-messaging-ktx")
}
```

### FCM Service
```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        // Send token to your server
    }
    override fun onMessageReceived(message: RemoteMessage) {
        // Show notification (only called when app is in foreground for notification payloads)
        // Background: system shows notification automatically for notification payloads
    }
}
```

### FCM history / in-app notification log pitfall

If the app must persist every push into local history ("latest notification", chat-style log, badges, update prompts), **do not rely on FCM `notification` payloads**. When the app is backgrounded/closed, Android may show the system notification without invoking `onMessageReceived()`, so app-side history can miss messages.

Use a **data-only high-priority** payload instead, put `title` and `body` inside `data`, and let `FirebaseMessagingService` both save history and show the notification manually:

```js
// Server / Worker payload
{
  message: {
    token,
    data: { title, body, type: "wow_update" },
    android: { priority: "high" }
  }
}
```

```kotlin
override fun onMessageReceived(message: RemoteMessage) {
    val title = message.data["title"] ?: "App"
    val body = message.data["body"] ?: ""
    saveNotification(this, title, body)
    showNotification(title, body)
}
```

For chat-style notification history UX:
- Store entries oldest → newest so newest renders at bottom.
- Use a fixed-height scroll container and scroll to bottom after render.
- Long-press a message bubble to show a small `PopupMenu` with `Eliminar` / delete.
- Avoid collapsible/dropdown history when user expects a chat-like log.

**AndroidManifest.xml:**
```xml
<service android:name=".service.MyFirebaseMessagingService" android:exported="false">
    <intent-filter>
        <action android:name="com.google.firebase.MESSAGING_EVENT" />
    </intent-filter>
</service>
```

## Social Media Content Extraction

For apps that download videos/images from social media (TikTok, Instagram, Facebook, YouTube, etc.), plain HTTP requests are blocked by anti-bot measures.

**Use yt-dlp via youtubedl-android library** — this is the ONLY reliable approach as of mid-2025.

**Do NOT use:**
- ❌ Cobalt API (all public instances are down or require auth as of mid-2025)
- ❌ Custom HTTP scrapers (social media platforms use JS-heavy pages)
- ❌ WebView-based extraction (times out, captures wrong URLs like fonts/CSS)
- ❌ FFmpeg Kit from Maven (archived/retired April 2025)

### yt-dlp Platform-Specific Options

These `--extractor-args` options are critical for bypassing platform anti-bot measures:

```kotlin
val request = YoutubeDLRequest(url)
request.addOption("-f", "best")

// YouTube: bypass 403 Forbidden
if (url.contains("youtube.com") || url.contains("youtu.be")) {
    request.addOption("--extractor-args", "youtube:player_client=android")
    request.addOption("--user-agent", "com.google.android.youtube/19.09.37 (Linux; U; Android 14) gzip")
}

// TikTok: use alternate API endpoint
if (url.contains("tiktok.com") || url.contains("vt.tiktok.com")) {
    request.addOption("--extractor-args", "tiktok:api_hostname=api-h2.tiktokv.com")
}

// Universal anti-bypass
request.addOption("--geo-bypass")
request.addOption("--force-ipv4")
request.addOption("--no-check-certificates")
```

**Without these options, YouTube returns 403 and TikTok returns "Unable to extract".**

### Audio Extraction

```kotlin
// Download audio only (requires FFmpeg Kit for conversion)
request.addOption("-f", "bestaudio")

// After download, convert to MP3 with FFmpeg Kit:
val cmd = "-i \"$inputPath\" -vn -acodec libmp3lame -q:a 2 \"$outputPath\""
val success = ReturnCode.isSuccess(FFmpegKit.execute(cmd).returnCode)
```

**Do NOT use `--extract-audio` flag** — it triggers a `NoneType` bug in some yt-dlp versions with Facebook. Use `-f bestaudio` + FFmpeg Kit conversion instead.

## ADB Wireless Pairing (Windows Pitfall)

`adb pair` does NOT accept piped input on Windows. `echo "code" | adb pair ...` silently fails.
Use Python subprocess or background PTY + submit. See `android-device-optimization` skill for full details and helper script.

## Build-from-Scratch Workflow (No Android Studio)

When user asks to build an Android app from terminal/CLI without Android Studio:

### Minimal project structure
```
project/
├── settings.gradle.kts
├── build.gradle.kts           # root — plugin versions only
├── gradle.properties
├── local.properties           # sdk.dir=C:\\Users\\ELY\\android-build\\android-sdk
├── gradlew                    # copy from existing project
├── gradlew.bat                # create if missing (see pitfall #10)
├── gradle/wrapper/
│   ├── gradle-wrapper.jar     # copy from existing project
│   └── gradle-wrapper.properties
└── app/
    ├── build.gradle.kts
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/pkg/app/
        │   └── MainActivity.kt
        └── res/
            ├── layout/activity_main.xml
            ├── values/colors.xml
            ├── values/strings.xml
            ├── values/themes.xml
            ├── xml/network_security_config.xml
            ├── mipmap-anydpi-v26/ic_launcher.xml   # adaptive icon
            └── mipmap-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/ic_launcher.png  # fallback
```

### Build command
```bash
cd PROJECT && export JAVA_HOME="/c/Users/ELY/android-build/jdk-17.0.19+10" && export ANDROID_HOME="/c/Users/ELY/android-build/android-sdk" && export PATH="$JAVA_HOME/bin:$PATH" && ./gradlew assembleDebug --no-daemon
```

Output APK: `app/build/outputs/apk/debug/app-debug.apk`

### Common first-build failures
- **"does not contain a Gradle build"** → `settings.gradle.kts` missing or not saved. Verify with `ls`.
- **"Unresolved reference: layout"** / **"Unresolved reference: id"** → layout XML file not written. Check `res/layout/` exists.
- **`execute_code` write_file with POSIX paths silently fails** → `write_file("/c/Users/ELY/...", content)` appears to succeed but file is NOT created. Must use Windows path: `write_file("C:/Users/ELY/...", content)`. When using `execute_code` to batch-create project files, always use `C:/` paths, never `/c/`. Verify with `ls` or `head` after batch operations.
- **`patch` tool can corrupt files via wrong fuzzy match** — The `patch` tool (mode='replace') uses fuzzy matching (9 strategies). If the `old_string` appears in multiple locations or the file was previously read with offset/limit pagination, it can match the WRONG section and silently corrupt the file. **Symptoms**: build fails with "Unresolved reference" for IDs that exist in layout but not in code (or vice versa), file size changes unexpectedly, imports change. **Prevention**: (1) After ANY `patch` call, verify with `head -5` and `wc -l` that the file still looks right. (2) If you previously read the file with `offset/limit`, re-read the FULL file before patching. (3) Prefer `write_file` for major rewrites — it's atomic and predictable. Use `patch` only for small, targeted, unambiguous edits. **This session**: patch matched a `val bcvSpread = 0.0` line but applied the replacement to a completely different section of MainActivity.kt, replacing `tvBcvRate.text` instead. It then cascaded — subsequent patches found the corrupted text and made it worse.

## Android Self-Updater Pattern

When an app needs to update itself without Play Store (internal distribution, kiosk devices, etc.):

### Requirements
```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />

<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.provider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

```xml
<!-- res/xml/file_paths.xml -->
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <external-files-path name="updates" path="." />
</paths>
```

### AppUpdater.kt (minimal)
```kotlin
object AppUpdater {
    fun save(context: Context, info: UpdateInfo) {
        context.getSharedPreferences("app_update", Context.MODE_PRIVATE).edit()
            .putInt("versionCode", info.versionCode)
            .putString("versionName", info.versionName)
            .putString("apkUrl", info.apkUrl)
            .putBoolean("required", info.required)
            .putString("message", info.message)
            .apply()
    }
    fun getSaved(context: Context): UpdateInfo? {
        val p = context.getSharedPreferences("app_update", Context.MODE_PRIVATE)
        val code = p.getInt("versionCode", 0)
        return if (code > 0) UpdateInfo(code, p.getString("versionName",""), p.getString("apkUrl",""), p.getBoolean("required",true), p.getString("message","")) else null
    }
    fun isNewer(context: Context, remoteCode: Int) = remoteCode > BuildConfig.VERSION_CODE
    fun download(context: Context, url: String, onComplete: (File) -> Unit) {
        Thread {
            val dir = context.getExternalFilesDir(null) ?: return@Thread
            val file = File(dir, "update.apk")
            val conn = java.net.URL(url).openConnection() as java.net.HttpURLConnection
            conn.inputStream.use { input -> file.outputStream().use { output -> input.copyTo(output) } }
            onComplete(file)
        }.start()
    }
    fun install(context: Context, file: File) {
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.provider", file)
        context.startActivity(Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
        })
    }
}
```

### Pitfalls
- **`buildFeatures { buildConfig = true }`** required in `app/build.gradle.kts` or `BuildConfig.VERSION_CODE` won't exist.
- **FileProvider authority** must match `${applicationId}.provider` in both manifest and code.
- **version.json** on server must have `versionCode` (integer) for comparison, not just `versionName` (string).

## Common Pitfalls

1. **`goAsync()` returns null** when calling `BroadcastReceiver.onReceive()` directly (not via system). Use a static method with coroutines instead.
2. **Region chip in `<include>` layout** — use `findViewById<ChipGroup>(R.id.chipGroup)` instead of binding reference.
3. **`split("\\\\s+")` vs `split("|")`** — always check the actual data format. `|` is a regex metacharacter in some contexts but works in `split()`.
4. **Unused variables** — Kotlin compiler warnings. Remove unused `val` declarations.

### Build & Resource Pitfalls

5. **Adaptive icon placement** — `<adaptive-icon>` XML must go in `mipmap-anydpi-v26/`, NOT in `mipmap-hdpi/`, `mipmap-mdpi/`, etc. Regular mipmap dirs expect PNG files. AAPT error: *"adaptive-icon elements require a sdk version of at least 26"*.
6. **Material3 Chip.Choice doesn't exist** — `Widget.Material3.Chip.Choice` is not a valid Material3 style. Use `Widget.Material3.Chip.Filter` instead for filterable chip groups. AAPT error: *"resource style/Widget.Material3.Chip.Choice not found"*.
7. **Escaped quotes in XML attributes** — Using `\"` inside `android:text="..."` causes AAPT parse errors. Use `&quot;` or avoid quotes entirely. Error: *"Element type must be followed by either attribute specifications, > or />"*.
8. **`settings.gradle` syntax** — Use `dependencyResolutionManagement` (not `dependencyResolution`). The former is the correct Gradle DSL name.
9. **FFmpeg Kit — RETIRED from Maven (April 2025)** — `com.arthenica:ffmpeg-kit-*` no longer resolves from Maven Central. The project was archived. **Working fix**: download the AAR from Appodeal's mirror and include locally:
   - URL: `https://artifactory.appodeal.com/appodeal-public/com/arthenica/ffmpeg-kit-full-gpl/6.0-2.LTS/ffmpeg-kit-full-gpl-6.0-2.LTS.aar` (~70MB)
   - Place in `app/libs/ffmpeg-kit.aar`
   - In `build.gradle`: `implementation(files("libs/ffmpeg-kit.aar"))` + `implementation("com.arthenica:smart-exception-java:0.2.1")` (the smart-exception dep is REQUIRED — use `0.2.1`, not `smart-exception-java9`)
   - For smaller APK: use `ffmpeg-kit-min` or `ffmpeg-kit-audio` variants from the same mirror
   - See `references/ffmpeg-kit-local-aar.md` for full details
10. **Gradle wrapper reuse** — On this Windows host, existing projects (e.g. `C:\Users\ELY\Desktop\WoWUpdateMonitor\`) have working `gradlew` and `gradle/wrapper/gradle-wrapper.jar`. Copy these instead of generating from scratch. Full sequence:
    ```bash
    mkdir -p NEWPROJECT/gradle/wrapper
    cp OLDPROJECT/gradlew NEWPROJECT/
    cp OLDPROJECT/gradle/wrapper/gradle-wrapper.jar NEWPROJECT/gradle/wrapper/
    cp OLDPROJECT/gradle/wrapper/gradle-wrapper.properties NEWPROJECT/gradle/wrapper/
    chmod +x NEWPROJECT/gradlew
    # Create gradlew.bat if missing (common — not all projects have it):
    cat > NEWPROJECT/gradlew.bat << 'BATCH'
    @rem Gradle startup script for Windows
    @if "%DEBUG%"=="" @echo off
    setlocal
    set DIRNAME=%~dp0
    set APP_BASE_NAME=%~n0
    set APP_HOME=%DIRNAME%
    set DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"
    set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar
    set JAVA_EXE=java.exe
    if defined JAVA_HOME set JAVA_EXE=%JAVA_HOME%/bin/java.exe
    "%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
    BATCH
    ```
    **Env vars required for terminal builds:**
    ```bash
    export JAVA_HOME="/c/Users/ELY/android-build/jdk-17.0.19+10"
    export ANDROID_HOME="/c/Users/ELY/android-build/android-sdk"
    export PATH="$JAVA_HOME/bin:$PATH"
    ```
    JDK 17 + Android SDK (platforms/android-34, build-tools/34.0.0) already installed at `C:\Users\ELY\android-build\`.
11. **Gson `JsonArray` has no `.getOrNull()`** — Gson's `JsonArray` is NOT a Kotlin `List`, so `.getOrNull(index)` won't compile. Use: `.let { if (it.size() > 0) it[0].asJsonObject else null }` instead of `.getOrNull(0)?.asJsonObject`. This catches you when chaining nullable Gson access like `json.getAsJsonArray("edges")?.getOrNull(0)` — Kotlin sees the Gson `JsonArray` type, not `List`.

### Error Logging Pattern

12. **Create an `ErrorLogger` utility for debugging** — When building apps that interact with external services (APIs, web scraping), errors are inevitable. Create a singleton `ErrorLogger` that:
    - Stores log entries in memory (last 100 entries)
    - Saves to a `.txt` file with device info, timestamps, and stack traces
    - Shares via `Intent.ACTION_SEND` + `FileProvider`
    - Add buttons in the main activity: "Export error log" and "Clear log"
    
    This lets users send you detailed error reports without needing ADB or logcat access. Critical for debugging remote APIs that may fail differently on different devices/networks.

13. **SSL certificate validation fails on some devices (Xiaomi, Huawei, older Android)** — Error: `CertPathValidatorException: Trust anchor for certification path not found`. This happens when the device's certificate store doesn't include the server's CA cert. Common with self-hosted or community-hosted API instances.
    
    **Fix: Create an `HttpClientFactory` with a permissive SSL client:**
    ```kotlin
    object HttpClientFactory {
        fun createPermissiveClient(): OkHttpClient {
            val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
                override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
                override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {}
                override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
            })
            val sslContext = SSLContext.getInstance("TLS")
            sslContext.init(null, trustAllCerts, SecureRandom())
            return OkHttpClient.Builder()
                .sslSocketFactory(sslContext.socketFactory, trustAllCerts[0] as X509TrustManager)
                .hostnameVerifier { _, _ -> true }
                .connectTimeout(15, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build()
        }
    }
    ```
    **Use this for:** API calls to third-party services, not for your own production APIs. Also use it for downloading files from CDN URLs that may have cert chain issues.

14. **WebView `net::ERR_UNKNOWN_URL_SCHEME` crash** — Apps like Facebook, Instagram, TikTok redirect to custom URL schemes (`fb://`, `instagram://`, `tiktok://`) that WebView cannot load. This causes `net::ERR_UNKNOWN_URL_SCHEME` and the page stops loading.
    
    **Fix: Override `shouldOverrideUrlLoading` to block custom schemes:**
    ```kotlin
    webViewClient = object : WebViewClient() {
        override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
            val url = request?.url?.toString() ?: return false
            if (url.startsWith("fb://") || url.startsWith("instagram://") ||
                url.startsWith("tiktok://") || url.startsWith("snssdk://")) {
                return true // Block custom schemes
            }
            return false // Allow http/https
        }
    }
    ```
    **Always add this** when using WebView to load social media pages. Without it, the WebView will fail silently when the page tries to redirect to the app's deep link.

15. **Facebook share URL resolution** — URLs like `facebook.com/share/r/XXXXX` or `fb.watch/XXXXX` are share redirects, not direct video pages. They must be resolved by following HTTP redirects first.
    
    **Pattern:**
    ```kotlin
    fun resolveShareUrl(url: String): String {
        val client = HttpClientFactory.createPermissiveClient()
        val request = Request.Builder().url(url).header("User-Agent", userAgent).build()
        val response = client.newCall(request).execute()
        val finalUrl = response.request.url.toString()
        response.close()
        return finalUrl
    }
    ```
    Then use the resolved URL for extraction. Also try variations: `/share/r/` → `/watch?v=`, `/reel/`, etc.

16. **`FileUriExposedException` on Android 7+ (API 24+)** — Sharing `file://` URIs via Intent crashes with `android.os.FileUriExposedException: file:///data/... exposed beyond app through Intent.getData()`. This happens in notifications, share intents, or any `Intent.ACTION_VIEW`.
    
    **Fix: Use FileProvider for `content://` URIs:**
    ```kotlin
    // In NotificationHelper or wherever you create the Intent:
    val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)
    val intent = Intent(Intent.ACTION_VIEW).apply {
        setDataAndType(uri, mimeType)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    ```
    **Also requires** `res/xml/file_paths.xml` and `<provider>` declaration in manifest. See `references/share-intent-pattern.md` for full setup. **Always use FileProvider** — never `Uri.fromFile()` for cross-process sharing.

17. **Media file validation after download** — When downloading from external APIs (Cobalt, web scraping), the URL may point to a font, CSS, HTML error page, or other non-media content. The file extension says `.mp4` but the content is a WOFF2 font or HTML page.
    
    **Fix: Validate with magic bytes (file signatures):**
    ```kotlin
    object MediaValidator {
        fun isValidMediaFile(file: File): Boolean {
            if (!file.exists() || file.length() < 16) return false
            val header = ByteArray(32)
            FileInputStream(file).use { it.read(header) }
            
            // Reject known non-media signatures
            // WOFF2: 0x77 0x4F 0x46 0x32 ("wOF2")
            // WOFF:  0x77 0x4F 0x46 0x46 ("wOFF")
            // TrueType: 0x00 0x01 0x00 0x00
            // HTML:  0x3C ('<')
            
            // Accept known media signatures
            // MP4: "ftyp" at various offsets
            // WebM/MKV: 0x1A 0x45 0xDF 0xA3
            // MP3: "ID3" or 0xFF 0xFB
            // JPEG: 0xFF 0xD8 0xFF
            // PNG: 0x89 0x50 0x4E 0x47
            
            return isVideoFile(header) || isAudioFile(header) || isImageFile(header)
        }
    }
    ```
    **Always validate** after downloading from external sources. Reject the file and show an error if it's not valid media. This prevents users from getting "corrupt" files that are actually fonts or HTML.

18. **Material Chip `setOnCheckedChangeListener` unreliable** — When using `Chip` with `isCheckable = true`, the `setOnCheckedChangeListener` can fire in unexpected order or not at all when programmatically unchecking other chips. This causes chips to appear selected but the value doesn't update.
    
    **Fix: Use `setOnClickListener` instead:**
    ```kotlin
    chip.setOnClickListener {
        selectedFormat = format.lowercase()
        // Manually uncheck all others
        for (i in 0 until chipGroup.childCount) {
            val other = chipGroup.getChildAt(i) as? Chip
            other?.isChecked = (other == chip)
        }
    }
    ```
    Also set unique `id` on each chip: `chip.id = index`. The `setOnClickListener` approach is more reliable than `setOnCheckedChangeListener` for single-selection chip groups.

19. **Cobalt API returns non-JSON responses** — Community-hosted Cobalt mirrors may return HTML error pages, 502 gateway errors, or plain text instead of JSON. Calling `JsonParser.parseString()` on non-JSON crashes with `MalformedJsonException`.
    
    **Fix: Check response format before parsing:**
    ```kotlin
    val responseBody = response.body?.string() ?: return null
    
    // Check if response is valid JSON
    if (!responseBody.trimStart().startsWith("{")) {
        Log.w(TAG, "Non-JSON response: ${responseBody.take(100)}")
        return null
    }
    
    val json = try {
        JsonParser.parseString(responseBody).asJsonObject
    } catch (e: Exception) {
        Log.w(TAG, "Invalid JSON: ${e.message}")
        return null
    }
    ```
    **Always wrap JSON parsing in try-catch** when consuming third-party APIs, especially community-hosted mirrors that may be down or misconfigured.

20. **Foreground service notification stuck at 100%** — When a foreground service shows a progress notification that reaches 100%, the notification often stays visible after the service stops. This happens because `stopForeground(STOP_FOREGROUND_DETACH)` only detaches the notification from the service but doesn't remove it.
    
    **Fix: Cancel progress notification explicitly, then use REMOVE:**
    ```kotlin
    // Cancel progress notification BEFORE showing completion
    notificationManager.cancel(PROGRESS_NOTIFICATION_ID)
    
    // Show separate completion notification
    notificationManager.notify(COMPLETION_NOTIFICATION_ID, completionNotification)
    
    // In finally block:
    stopForeground(STOP_FOREGROUND_REMOVE)  // NOT DETACH
    ```
    **Always use `STOP_FOREGROUND_REMOVE`** instead of `STOP_FOREGROUND_DETACH`. And cancel the progress notification explicitly before showing the completion one — they should be separate notification IDs.

21. **yt-dlp binary must be ARM for Android** — The `youtubedl-android` library manages its own yt-dlp binary internally. **Do NOT bundle your own yt-dlp binary from GitHub releases** — the default release is Linux x86_64, which will silently fail on Android ARM devices. The library downloads the correct ARM binary during `YoutubeDL.init()`.
    
    **If `updateYoutubeDL()` fails** (common on first run), the library falls back to its bundled version. Let the library handle this — don't try to manually download/replace the binary.
    
    **Pitfall**: Testing yt-dlp on your desktop (x86) confirms it works, but the same commands fail on the phone (ARM) with "Unable to extract" or "NoneType" errors. This is almost always because the bundled yt-dlp version is outdated, NOT because the commands are wrong.

22. **Content-Type check before saving downloads** — When downloading from URLs (especially from APIs or redirects), the response may be HTML (error page, login redirect) instead of the expected media file. The file gets saved as `.jpg` or `.mp4` but is actually HTML.
    
    **Fix: Check Content-Type header before writing:**
    ```kotlin
    val contentType = connection.contentType ?: ""
    if (contentType.contains("text/html")) {
        // This is an HTML page, not a media file
        // Fall back to yt-dlp or show error
        connection.disconnect()
        return
    }
    ```
    **Also applies to**: Cobalt API responses, web scraping results, any third-party download URL.

23. **Social media URLs vs direct file URLs** — Never use direct HTTP download for social media page URLs (facebook.com/posts/..., instagram.com/p/..., tiktok.com/...). These are HTML pages, not media files. Always route them through yt-dlp.

24. **MIUI `INSTALL_FAILED_USER_RESTRICTED` when installing APKs via ADB** — Xiaomi/MIUI devices have extra security even with "Install via USB" enabled in Developer Options. The install command succeeds in sending the APK but the device shows a confirmation dialog that the user must tap "Install" on.
    
    **Fix:** 
    - Ensure Settings → Developer Options → **Install via USB** is ON
    - Ensure Settings → Developer Options → **USB debugging (Security settings)** is ON
    - Run `adb install -r <apk>` — the phone will show a dialog
    - User MUST tap "Install" on the phone screen within the timeout
    - If the dialog doesn't appear, try: `adb shell settings put global verifier_verify_adb_installs 0`
    
    **Wireless ADB note:** After reboot, the wireless debugging port changes. Must get new IP:Port from phone settings.
    
    **Detection pattern:**
    ```kotlin
    fun isDirectFileUrl(url: String): Boolean {
        val lower = url.lowercase()
        val hasMediaExt = lower.matches(Regex(".*\\.(mp4|webm|jpg|png|gif|webp)(\\?.*)?$"))
        val isSocialMedia = lower.contains("facebook.com") || lower.contains("tiktok.com") ||
                lower.contains("instagram.com") || lower.contains("youtube.com") ||
                lower.contains("youtu.be") || lower.contains("twitter.com") || lower.contains("x.com")
        return hasMediaExt && !isSocialMedia
    }
    ```
    If `isDirectFileUrl` returns false, use yt-dlp. If true, download directly but still check Content-Type (see pitfall 22).
