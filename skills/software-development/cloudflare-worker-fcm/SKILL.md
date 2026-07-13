---
name: cloudflare-worker-fcm
description: "Cloudflare Worker as API proxy + FCM push notifications for mobile apps. Covers: Worker setup, KV storage, Cron Triggers, FCM HTTP v1 from Workers, Android FCM integration."
category: software-development
tags: [cloudflare, fcm, android, push-notifications, worker, firebase]
---

# Cloudflare Worker + FCM Push Notifications

Architecture: Mobile app → HTTPS → Cloudflare Worker → internal API → detect changes → FCM push → device receives notification (app closed OK).

## When to Use

- Mobile app needs to monitor an internal/HTTP API that can't be reached directly
- Push notifications needed without keeping app alive
- Replace polling (AlarmManager/WorkManager) with server-side push

## Prerequisites

- Cloudflare account (free plan works)
- Firebase project with Android app registered
- `google-services.json` in Android project

## Setup Flow (in order)

### 1. Cloudflare Worker

Create Worker in dashboard → "Start with Hello World" → Deploy → Edit code.

### 2. KV Namespace

Workers & Pages → KV → Create namespace → Copy ID → Worker Settings → Variables → KV Namespace Bindings → Add: name=`WOW_KV`, namespace=selected.

### 3. Firebase Service Account

Firebase Console → Project Settings → Service Accounts → Generate new private key → Download JSON.

Google Cloud Console → IAM → Find `firebase-adminsdk-*` → Edit → Add role: **"Firebase Cloud Messaging API Admin"** → Save.

Worker Settings → Variables → Add variable: name=`FIREBASE_SERVICE_ACCOUNT`, value=full JSON content, Encrypt=ON.

### 4. Cron Trigger

Worker Settings → Triggers → Cron Triggers → Add: `*/1 * * * *` (every 1 min, free plan minimum).

### 5. Android App

Dependencies in `app/build.gradle.kts`:
```kotlin
plugins {
    id("com.google.gms.google-services") // at bottom
}
// In dependencies:
implementation(platform("com.google.firebase:firebase-bom:32.7.0"))
implementation("com.google.firebase:firebase-messaging-ktx")
```

Project `build.gradle.kts`:
```kotlin
id("com.google.gms.google-services") version "4.4.0" apply false
```

### 6. FCM Service (Android)

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        // POST token to Worker /register-token
    }
    override fun onMessageReceived(message: RemoteMessage) {
        // Show notification
    }
}
```

AndroidManifest.xml:
```xml
<service android:name=".service.MyFirebaseMessagingService" android:exported="false">
    <intent-filter>
        <action android:name="com.google.firebase.MESSAGING_EVENT" />
    </intent-filter>
</service>
<meta-data
    android:name="com.google.firebase.messaging.default_notification_channel_id"
    android:value="your_channel_id" />
```

## FCM HTTP v1 from Cloudflare Worker

### Critical Pitfall: Binary Key Corruption

`TextEncoder.encode(atob(base64))` CORRUPTS binary data. `atob()` returns a binary string, and `TextEncoder` encodes it as UTF-8 multi-byte, breaking the DER key bytes.

**Correct approach — base64 → Uint8Array:**
```javascript
function base64ToUint8Array(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

// Extract DER from PEM:
const pemBody = sa.private_key
  .replace(/-----BEGIN PRIVATE KEY-----/, "")
  .replace(/-----END PRIVATE KEY-----/, "")
  .replace(/\s/g, "");
const keyBytes = base64ToUint8Array(pemBody);

const key = await crypto.subtle.importKey(
  "pkcs8", keyBytes,
  { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
  false, ["sign"]
);
```

### JWT Signing for OAuth2

```javascript
async function getAccessToken(env) {
  const sa = JSON.parse(env.FIREBASE_SERVICE_ACCOUNT);
  const now = Math.floor(Date.now() / 1000);

  const header = btoa(JSON.stringify({ alg: "RS256", typ: "JWT" }))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const payload = btoa(JSON.stringify({
    iss: sa.client_email,
    scope: "https://www.googleapis.com/auth/firebase.messaging",
    aud: "https://oauth2.googleapis.com/token",
    iat: now, exp: now + 3600,
  })).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  // ... importKey + sign (see pitfall above) ...

  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(`${header}.${payload}`));
  const jwt = `${header}.${payload}.${btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")}`;

  const resp = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
  });
  return (await resp.json()).access_token;
}
```

### Sending FCM

```javascript
const resp = await fetch(
  `https://fcm.googleapis.com/v1/projects/${sa.project_id}/messages:send`,
  {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      message: {
        token: deviceToken,
        notification: { title, body },
        data: { type: "version_change" },
        android: { priority: "high", notification: { channel_id: "your_channel" } },
      },
    }),
  }
);
```

## Pitfalls

1. **FCM token cleanup**: When `sendFCM` fails, remove the dead token. Otherwise `broadcastToTokens` keeps trying dead tokens and all future sends fail silently.
2. **Service Account roles**: Must have "Firebase Cloud Messaging API Admin" — the default "Firebase SDK Admin Service Agent" is NOT sufficient.
3. **KV binding lost on redeploy**: KV namespace bindings survive code redeployments, but always verify after deploy.
4. **Android cleartext HTTP**: If Worker connects to HTTP endpoints, ensure `network_security_config.xml` + `usesCleartextTraffic="true"` in manifest. Better: use Worker as HTTPS proxy so app never touches HTTP directly.
5. **Cron Trigger minimum**: Free plan = **1 minute** (`*/1 * * * *`). Paid plan also 1 min but with more CPU (30s vs 10ms). Free plan CPU limit for <1hr interval is 10ms; network fetch/KV reads do NOT count toward CPU time.
6. **Dead token accumulation**: Previous failed sends remove tokens from KV (the `broadcastToTokens` function adds failed tokens to `deadTokens` and removes them). After fixing FCM auth issues, user MUST reopen the app to re-register their token. Call `GET /` to verify `registeredDevices > 0` before testing.
7. **Testing with `/simulate-update`**: Store fake old versions in KV so the next Cron Trigger detects "changes" and sends real FCM push. Flow: call `/simulate-update` → wait 1 min → Cron detects change → FCM sent. Verify with `GET /check` (returns `changes > 0` and `fcmResult`). ⚠️ **Timing window**: The Cron runs every ~1 min and overwrites `last_versions` with real data. If you call `/simulate-update` and then wait too long (>1 min) before the Cron runs, the fake versions get cleared. For reliable testing, call `/simulate-update` followed immediately by `/check`.
8. **Custom test notifications**: `/test-fcm?title=Custom&body=Message` sends a custom push to all registered devices. URL-encode the parameters.
9. **Fake data for UI testing**: `/fetch?fake=1` returns the real game structure but with fake version numbers (e.g., "2.5.4.67000" instead of "2.5.5.68101"). Use this to seed the app's local DB with "old" versions, then fetch real data to test version transition display (old ➡️ new) in the UI.
10. **Token re-registration after FCM fix**: After fixing FCM auth issues (Service Account role, Worker code), the old token may have been removed from KV by the dead-token cleanup logic. User MUST reopen the app to re-register. Call `GET /` to verify `registeredDevices > 0` before testing.
11. **KV PUT limit (free plan = 1,000/day)**: If Cron Trigger runs every 1 min and writes to KV unconditionally, that's 1,440 PUTs/day → exceeds limit → 429 errors. **Fix**: only `KV.put()` when data actually changed or on first run:
```javascript
const isFirstRun = Object.keys(last).length === 0;
if (changes.length > 0 || isFirstRun) {
  await env.WOW_KV.put("last_versions", JSON.stringify(current));
}
```
KV GET operations are free (unlimited on free plan). The bottleneck is PUT/DELETE only.
12. **Custom test notifications**: `/test-fcm?title=Custom&body=Message` endpoint sends a push to all registered devices. URL-encode params. Useful for verifying FCM pipeline end-to-end without waiting for real data changes.
13. **HTML push sender tool**: A single-file HTML page can call the Worker's `/test-fcm` endpoint directly from the browser. Include emoji picker (with search + categories), send history in localStorage. Can be wrapped in a WebView Android APK for mobile use. Useful for quick custom notifications without touching terminal. Place HTML in `assets/index.html` of a minimal WebView app.

## Notification History (Multiple Entries)

For showing multiple recent notifications in-app (not just the last one):

```kotlin
// SharedPreferences with JSON array
fun saveNotification(context: Context, title: String, body: String) {
    val prefs = context.getSharedPreferences("wow_notifications", Context.MODE_PRIVATE)
    val arr = JSONArray(prefs.getString("history", "[]") ?: "[]")
    val entry = JSONObject().apply {
        put("title", title); put("body", body)
        put("time", SimpleDateFormat("dd MMM HH:mm:ss", Locale.getDefault()).format(Date()))
    }
    val newArr = JSONArray(); newArr.put(entry)
    for (i in 0 until minOf(arr.length(), 19)) newArr.put(arr.getJSONObject(i))
    prefs.edit().putString("history", newArr.toString()).apply()
}

fun getNotifications(context: Context): List<Triple<String, String, String>> {
    val arr = JSONArray(context.getSharedPreferences("wow_notifications", Context.MODE_PRIVATE)
        .getString("history", "[]") ?: "[]")
    return (0 until arr.length()).map { arr.getJSONObject(it) }
        .map { Triple(it.optString("title",""), it.optString("body",""), it.optString("time","")) }
}
```

Display: latest in green at top, older ones hidden behind expand toggle. Color latest with `status_green` color for identification.

## Telegram Channel Integration (alongside FCM)

Same Worker, one extra `fetch` call. Zero additional KV usage.

### Worker Setup

1. Create bot via @BotFather → get token
2. Create Telegram channel → add bot as admin with "Manage messages" permission
3. Add `TELEGRAM_TOKEN` as encrypted env variable in Worker
4. Get channel ID: forward a channel message to the bot → `GET /getUpdates` → find `chat.id` (negative number like `-1004240877348`)

### Worker Code

```javascript
async function sendTelegram(env, text) {
  const token = env.TELEGRAM_TOKEN;
  if (!token) return;
  try {
    await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: "-100XXXXXXXXXX", text }),
    });
  } catch (e) {
    console.error("Telegram send failed:", e.message);
  }
}
```

Call after FCM in `detectAndNotify`:
```javascript
await sendTelegram(env, `${title}\n${body}`);
```

Also add to `/test-fcm` endpoint so custom messages from push sender go to both.

### Pitfall: Bot needs admin rights
Bot must be channel admin with at least "Manage messages" permission. Without it: `400 Bad Request: need administrator rights`.

### Pitfall: Token redaction in terminal
Some environments redact bot tokens in terminal output. Store token in Worker env variable, not in shell commands.

## Version Transition Display (old ➡️ new)

When showing version changes in-app (history, expandable cards), display the transition:

```
📌 5.5.3.67000 ➡️ 5.5.4.68159
```

Implementation: add `previousVersion` field to the database entry. When ChangeDetector finds an existing entry, copy `existing.buildVersion` → new entry's `previousVersion`. Display logic: if `previousVersion != buildVersion`, show transition; else show current version.

This applies to both:
- Expandable game cards (VersionAdapter)
- History list (HistoryAdapter)

## References

- [FCM HTTP v1 API](https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages/send)
- [Cloudflare Workers Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/)
- [Cloudflare Workers KV](https://developers.cloudflare.com/kv/)
- [Web Crypto API - importKey](https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/importKey)
