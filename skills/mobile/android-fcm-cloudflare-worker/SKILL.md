---
name: android-fcm-cloudflare-worker
description: Push notifications for Android via Cloudflare Worker + FCM HTTP v1 API
tags: [android, fcm, firebase, cloudflare, push-notifications, worker]
triggers:
  - fcm push notifications
  - cloudflare worker fcm
  - android push without server
  - push notifications cloudflare
---

# Android FCM Push via Cloudflare Worker

Architecture: Android app receives push notifications via FCM, with a Cloudflare Worker as the backend that detects changes and sends pushes.

```
App → HTTPS → Cloudflare Worker → Blizzard API (or any source)
Worker (Cron Trigger) → detects change → FCM HTTP v1 → App receives push
```

## Components

### 1. Cloudflare Worker
- Proxies external API calls (solves Android cleartext HTTP blocking)
- Stores FCM tokens in KV namespace
- Stores last-known state in KV for change detection
- Cron Trigger checks for changes periodically (min 1 min on free plan)
- Sends push via FCM HTTP v1 API with Service Account JWT

### 2. Android App
- Firebase SDK for FCM token retrieval
- `FirebaseMessagingService` subclass for receiving messages
- Registers token with Worker via POST `/register-token`
- Region/topic preferences synced with Worker

## Critical Pitfalls

### Binary data in Workers — use Uint8Array, NOT TextEncoder
```javascript
// ❌ WRONG — TextEncoder corrupts binary data from atob()
enc.encode(atob(base64String))

// ✅ CORRECT — manual byte conversion
function base64ToUint8Array(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}
```

### Service Account needs FCM Admin role
Default Firebase Service Account roles are NOT enough. Must add:
- **"Firebase Cloud Messaging API Admin"** role in Google Cloud Console IAM
- Path: Google Cloud Console → IAM → find `firebase-adminsdk-*` → Edit → Add role

### Dead token cleanup removes valid tokens on transient failures
If `sendFCM` returns false for a token, it gets removed from KV. Transient network errors can cause valid tokens to be deleted. Consider retry logic or only removing tokens on specific FCM error codes (messaging/registration-token-not-registered).

### Android cleartext HTTP blocking (API 28+)
If app connects to HTTP (not HTTPS) endpoints:
1. Create `res/xml/network_security_config.xml` with domain exceptions
2. Add `android:usesCleartextTraffic="true"` and `android:networkSecurityConfig` to manifest

### FCM token re-registration
Tokens can expire or change. App should re-register on:
- Every app open (in `onCreate`)
- `onNewToken` callback in `FirebaseMessagingService`
- After app update

## Worker JWT Signing (FCM HTTP v1)

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
    iat: now,
    exp: now + 3600,
  })).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  // CRITICAL: Use Uint8Array, not TextEncoder
  const pemBody = sa.private_key
    .replace(/[REDACTED PRIVATE KEY]/, "")
    .replace(/\s/g, "");
  const keyBytes = base64ToUint8Array(pemBody);

  const key = await crypto.subtle.importKey(
    "pkcs8", keyBytes,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["sign"]
  );

  const enc = new TextEncoder();
  const sig = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5", key,
    enc.encode(`${header}.${payload}`)
  );

  const sigBase64 = btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const resp = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${header}.${payload}.${sigBase64}`,
  });

  return (await resp.json()).access_token;
}
```

## Testing Endpoints Pattern

For debugging and user testing, include these Worker endpoints:

| Endpoint | Purpose |
|---|---|
| `/test-fcm?title=...&body=...` | Direct FCM push with custom message |
| `/simulate-update` | Store fake old versions in KV so next Cron detects "change" |
| `/check` | Force immediate change detection + FCM send |
| `/fetch?fake=1` | Return fake old version data (for app-side transition testing) |

### Timing Pitfall
Cron clears fake versions after detecting changes. `simulate-update` + `check` must happen in quick succession (< 30s). If user waits for Cron, the fake versions may already be consumed. Always chain: `curl /simulate-update && curl /check`.

### Dead Token Cleanup
When `sendFCM` fails, the token is removed from KV. Transient failures can delete valid tokens. Multiple reinstalls accumulate dead tokens (response shows `sent: N, failed: M`). Consider only removing on FCM error code `messaging/registration-token-not-registered`.

### WebView Companion App Pattern
For admin/test tools (e.g., custom message sender), wrap HTML in a WebView APK:
- Single `MainActivity` with `WebView` loading `file:///android_asset/index.html`
- Needs `INTERNET` permission, `usesCleartextTraffic="true"`
- Theme must use `AppCompatActivity` + Material theme (not `@android:style/Theme.NoTitleBar` — crashes on newer Android)
- Custom icon via `res/drawable/ic_launcher_foreground.xml` + `mipmap-anydpi-v26/ic_launcher.xml`
- Call Worker's `/test-fcm?title=...&body=...` directly from JS fetch

## Cloudflare Free Plan Limits

| Resource | Limit |
|---|---|
| Requests/day | 100,000 |
| KV GETs/day | 100,000 |
| KV PUTs/day | **1,000** ← easy to exceed |
| KV namespace count | 5 |
| CPU time (Cron <1hr) | 10ms |
| Cron minimum interval | 1 minute |

### KV PUT Optimization (Critical)
Free plan: 1,000 KV PUTs/day. Cron every 1 min = 1,440 writes/day if writing unconditionally. Fix: only write when state changes:
```javascript
const isFirstRun = Object.keys(last).length === 0;
if (changes.length > 0 || isFirstRun) {
  await env.WOW_KV.put("last_versions", JSON.stringify(current));
}
```
Reduces daily PUTs from ~1,440 to ~0 (only when actual changes detected). Without this fix, Cloudflare sends "Daily Workers KV put limit exceeded" email and returns 429 errors.

## Cloudflare Setup Checklist

### "Install via USB" required for ADB
- Settings → Additional Settings → Developer Options → "Install via USB"
- Must be RE-ENABLED after uninstalling the app (MIUI resets it)
- May require Mi account login on first enable

### Wireless ADB Debugging
1. Developer Options → Wireless Debugging → enable
2. "Pair device with pairing code" → shows IP:port + 6-digit code
3. `adb pair <ip:port>` → enter code when prompted
4. `adb connect <ip:port>` — NOTE: connection port ≠ pairing port
5. `adb devices` to verify
6. `adb install -r <apk>` or `adb uninstall <pkg> && adb install <apk>`

### Battery Optimization
- Settings → Battery → App → No restrictions
- Required for AlarmManager to fire reliably

## Blizzard Patch API Format

Data uses `|` (pipe) as separator, NOT spaces:
```
us|bc3b8e61b6ba9f06|2374bc9b22181d36||68101|2.5.5.68101|92cbb948
```
Header: `Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16`

Parse with `split("|")`, not `split("\\s+")`.

## Room Database Migration

When adding columns to existing entities:
1. Bump `@Database(version = N+1)`
2. Add `.fallbackToDestructiveMigration()` to builder
3. DB will be recreated (data lost on update — acceptable for debug builds)

## Android UI Patterns

### Collapsible Expandable Cards
- Use `LinearLayout` with `visibility=GONE` for content
- Toggle `visibility` and arrow icon (▶/▼) on header click
- Default state: collapsed

### Notification History Storage
- Store in SharedPreferences as JSON array
- Latest entry first, max 20 entries
- Display: latest in green (`status_green` color), older in default text color
- Collapsible section for older notifications

## User Guidance (Non-Technical Users)
When guiding through Cloudflare/Firebase setup:
- Give numbered steps: "1. Haz click en X. 2. Escribe Y. 3. Mándame captura."
- Do NOT use multiple-choice clarify tool during multi-step setup flows — user explicitly complained: "no me gusta como me estas guiando, me dejas preguntas, vamos paso por paso, y yo te voy pasando los captures, no me hagas preguntas por selecion aqui en el chat"
- User will send screenshots after each step — respond with next step only
- Keep instructions in user's language (Spanish for this user)
- If user says "me perdi" (I'm lost), show them exactly where they are with a screenshot reference
- Never ask "which option do you prefer?" mid-setup — just pick the correct one and tell them to click it
- When user says "paso por paso" — ONE instruction per message, wait for confirmation/screenshot before next step
- If user sends a screenshot showing they're on the right page, give the NEXT step immediately without asking

## Telegram Bot Integration (alongside FCM)
Worker can send to both FCM and Telegram with minimal extra code. Same `broadcastToTokens` flow, one additional `fetch` to Telegram API.

### Setup
1. User creates bot via @BotFather → gets token
2. User creates Telegram channel
3. User adds bot as admin with "Manage messages" permission
4. Store bot token as Worker secret: `TELEGRAM_TOKEN`
5. Get channel ID: forward a channel message to bot, then `getUpdates` API → `forward_from_chat.id`

### Worker Code Addition
```javascript
async function sendTelegram(env, text) {
  const token = env.TELEGRAM_TOKEN;
  const chatId = env.TELEGRAM_CHAT_ID; // e.g. "-1004240877348"
  if (!token || !chatId) return;
  await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text }),
  });
}
```
Call `sendTelegram(env, messageText)` alongside FCM in `detectAndNotify`.

### Pitfalls
- Bot MUST be admin of channel with "Manage messages" (Gestionar mensajes) permission
- Channel chat ID is negative (starts with -100...) — get via `getUpdates` after forwarding a message
- Telegram token in Worker env var must be marked as secret (encrypted)
- Token gets redacted in terminal output — can't test directly from CLI, must test via Worker

### ADB Path Issue on Windows (MSYS/Git Bash)
`/sdcard/Download/` gets converted by MSYS to a local Windows path. Use double slashes:
```bash
adb push file.apk //sdcard//Download//file.apk
```

## Cloudflare Setup Checklist
1. Create KV namespace
2. Bind KV to Worker (`WOW_KV` variable name)
3. Add `FIREBASE_SERVICE_ACCOUNT` as encrypted secret
4. Deploy Worker code
5. Set Cron Trigger (`*/1 * * * *` for every minute)

## Android Setup Checklist
1. Firebase Console → Create project → Add Android app → Download `google-services.json`
2. Place `google-services.json` in `app/` directory
3. Add `com.google.gms.google-services` plugin to build.gradle
4. Add Firebase BOM + messaging-ktx dependency
5. Create `FirebaseMessagingService` subclass
6. Register in AndroidManifest with `com.google.firebase.MESSAGING_EVENT`
7. Set default notification channel via meta-data
8. Generate Service Account key in Google Cloud Console (JSON)
9. Add FCM Admin role to Service Account in IAM

## Companion HTML Sender App
See `references/companion-html-sender.md` for WebView APK wrapper pattern — useful for admin/test tools that call the Worker's `/test-fcm` endpoint from a mobile-friendly UI.
