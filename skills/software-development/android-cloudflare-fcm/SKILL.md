---
name: android-cloudflare-fcm
description: Android app with Cloudflare Worker backend and Firebase Cloud Messaging push notifications
tags: [android, cloudflare, fcm, firebase, push-notifications, kotlin, worker]
triggers:
  - Android app with push notifications
  - Cloudflare Worker as API proxy
  - FCM setup for Android
  - Serverless backend for mobile app
---

# Android + Cloudflare Worker + FCM Architecture

## Architecture Overview

```
Android App → HTTPS → Cloudflare Worker → HTTP → External API
                          ↓
                    Cron Trigger (1 min)
                          ↓
                    Detect changes → FCM Push → Device
```

**Why this pattern**: Android blocks cleartext HTTP by default. A Cloudflare Worker proxies HTTP API calls over HTTPS. Worker's Cron Trigger checks for changes periodically and sends FCM push notifications — no Foreground Service needed.

## Step-by-Step Setup

### 1. Firebase Project Setup

1. Create project at `console.firebase.google.com`
2. Add Android app with correct package name
3. Download `google-services.json` → place in `app/` directory
4. Go to **Project Settings → Service Accounts → Generate new private key** (JSON file)
5. Go to **Google Cloud Console → IAM** → add role **"Firebase Cloud Messaging API Admin"** to the service account

### 2. Cloudflare Worker Setup

1. Create Worker at `dash.cloudflare.com → Workers & Pages`
2. Create KV namespace for storing tokens and version state
3. Bind KV to Worker: **Settings → Variables → KV Namespace Bindings**
4. Add Service Account JSON as environment variable: **Settings → Variables → Environment Variables** (name: `FIREBASE_SERVICE_ACCOUNT`, mark as Encrypt)
5. Set Cron Trigger: **Settings → Triggers → Cron Triggers** → `*/1 * * * *`

### 3. Android Dependencies

```kotlin
// app/build.gradle.kts
plugins {
    id("com.google.gms.google-services")  // add to app level
}

dependencies {
    implementation(platform("com.google.firebase:firebase-bom:32.7.0"))
    implementation("com.google.firebase:firebase-messaging-ktx")
}
```

```kotlin
// build.gradle.kts (project level)
plugins {
    id("com.google.gms.google-services") version "4.4.0" apply false
}
```

### 4. AndroidManifest.xml

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />

<application
    android:usesCleartextTraffic="true"
    android:networkSecurityConfig="@xml/network_security_config">

    <service android:name=".service.MyFirebaseMessagingService" android:exported="false">
        <intent-filter>
            <action android:name="com.google.firebase.MESSAGING_EVENT" />
        </intent-filter>
    </service>

    <meta-data
        android:name="com.google.firebase.messaging.default_notification_channel_id"
        android:value="your_channel_id" />
</application>
```

### 5. Network Security Config (for any HTTP calls)

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">your-api-domain.com</domain>
    </domain-config>
</network-security-config>
```

### 6. FCM Service (Kotlin)

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        // Send token to Worker's /register-token endpoint
        registerToken(this, token)
    }

    override fun onMessageReceived(message: RemoteMessage) {
        val title = message.notification?.title ?: message.data["title"] ?: ""
        val body = message.notification?.body ?: message.data["body"] ?: ""
        // Save to SharedPreferences for in-app display
        // Show system notification
    }
}
```

### 7. Worker FCM Send (JavaScript)

**Critical: Use `Uint8Array` for private key, NOT `TextEncoder.encode()`**

```javascript
function base64ToUint8Array(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return bytes;
}

async function getAccessToken(env) {
    const sa = JSON.parse(env.FIREBASE_SERVICE_ACCOUNT);
    const now = Math.floor(Date.now() / 1000);
    // Build JWT header + payload
    // Extract DER bytes from PEM
    const pemBody = sa.private_key.replace(/-----.*-----/g, "").replace(/\s/g, "");
    const keyBytes = base64ToUint8Array(pemBody);  // NOT enc.encode(atob(...))
    const key = await crypto.subtle.importKey("pkcs8", keyBytes,
        { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
    // Sign JWT, exchange for access token
}
```

## GitHub Release update distribution

For sideloaded APK update notices, use GitHub Releases + a fixed raw `version.json` URL + a manual Worker trigger from the sender app. Do not add GitHub polling cron when user wants manual publish control. The Android app can download the APK in-app and then open Android's installer, but cannot silently install/replace itself unless Play Store in-app updates, Device Owner/MDM, root, or system-app privileges are used.

Worker pattern:
- `GET /app-version` reads GitHub raw `version.json` and falls back to KV cache.
- `GET|POST /notify-app-update` reads `version.json`, stores `latest_app_version`, broadcasts FCM `data.type = "app_update"`.
- Sender HTML/WebView APK should have "Leer versión GitHub" and "Avisar nueva versión" buttons; do not send update notices before the target app can handle `app_update`.

See `references/github-release-app-updates.md` and `references/manual-github-apk-updates.md` for the full pattern, Worker endpoints, Android behavior, and GitHub release workflow.

## Pitfalls

- **`TextEncoder.encode(atob(...))` corrupts binary key data** — use `Uint8Array` with `charCodeAt()` instead
- **MIUI/Xiaomi "Install via USB"** must be re-enabled after each uninstall
- **MSYS path conversion** — use `//sdcard//` instead of `/sdcard/` for adb push on Windows/Git Bash
- **FCM tokens get deleted** after failed sends — the Worker's dead token cleanup removes them. Always re-register on app open
- **Cron Trigger runs every 1 min** (free plan minimum) — if simulation and Cron race, the fake versions get cleared before notification arrives
- **KV PUT limit (free plan = 1,000/day)** — writing to KV every cron run (1,440/day) exceeds limit. Fix: only write when changes detected or first run
- **Sideloaded APK auto-updates are two-step** — app can download APK in-app, but Android installer confirmation is mandatory unless Play Store/Device Owner/root/system-app
- **`BuildConfig.VERSION_CODE` may be unavailable on newer AGP** — enable `buildFeatures { buildConfig = true }` before using it for update comparisons
- **Release asset URL must match `version.json` exactly** — verify it downloads an APK before sending `/notify-app-update`; old apps without `app_update` handling only show a normal notification
- **`SCHEDULE_EXACT_ALARM`** needs user consent on Android 12+
- **`android:usesCleartextTraffic="true"`** required for any HTTP (non-HTTPS) calls from the app
