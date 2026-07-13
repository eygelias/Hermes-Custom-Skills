---
name: android-background-monitor-app
description: "Build Android apps that monitor APIs and send push notifications — covers background execution (AlarmManager/WorkManager/FCM), Cloudflare Worker proxies, and Android networking pitfalls."
trigger:
  - "Android app that monitors an API or endpoint"
  - "Push notifications from a server to Android"
  - "Background polling without persistent notification"
  - "Cloudflare Worker as API proxy for mobile apps"
  - "FCM integration with Worker"
---

# Android Background Monitor App

Build Android apps that poll external APIs, detect changes, and notify users — with or without the app open.

## Architecture Decision Tree

| Need | Solution | Min Interval | Needs App Open? |
|------|----------|-------------|-----------------|
| Check every 15+ min | **WorkManager** | 15 min (hard Android limit) | No |
| Check every 1-5 min | **AlarmManager** | ~1 min (practical) | No |
| Instant push on change | **FCM** | Instant (server-side) | No |
| Legacy foreground monitoring | **Foreground Service** | Any | Shows persistent notification |

**Best practice**: Use FCM for instant notifications + AlarmManager for manual/test checks. No persistent notification.

## Cloudflare Worker Proxy Pattern

Use when the target API uses non-standard ports or HTTP (Android 9+ blocks cleartext HTTP by default).

```
App (HTTPS:443) → Cloudflare Worker → Target API (HTTP:any-port)
```

Worker endpoints:
- `GET /fetch` — proxy the API data
- `POST /register-token` — receive FCM device tokens
- `GET /check` — manual trigger for change detection

### Worker + FCM Push Flow

1. **Cron Trigger** (min 1 min on free plan) checks API for changes
2. Compares with stored last-known version in **KV**
3. If changed → sends FCM push to all registered device tokens
4. App receives push → shows notification (works when app is closed)

### FCM Auth in Worker (HTTP v1 API)

Requires **Service Account JSON** from Firebase Console → Project Settings → Service Accounts → Generate new private key.

Store as Worker secret: `FIREBASE_SERVICE_ACCOUNT`.

**⚠️ Service Account Role**: Default role "Firebase SDK Admin Service Agent" is NOT sufficient for FCM. Must add **"Firebase Cloud Messaging API Admin"** role in Google Cloud Console → IAM → find the service account → edit → add role.

OAuth2 flow with Web Crypto API (no Node.js libs available in Workers):
1. Create JWT with RS256 signing
2. Exchange for access token at `oauth2.googleapis.com/token`
3. POST to `fcm.googleapis.com/v1/projects/{project_id}/messages:send`

**Critical pitfall**: See `cloudflare-workers` skill for the JWT binary data corruption issue with `TextEncoder.encode()`.

### KV Namespaces

- `fcm_tokens` — JSON array of device FCM tokens
- `last_versions` — JSON of last-known game versions (for change detection)
- `prefs_{token}` — per-device region preferences

## Android Networking Pitfalls

### Cleartext HTTP Blocked (Android 9+)

**Symptom**: `http://` URLs work in browser but app gets `ConnectException` or timeout.

**Fix** (both required):
1. `AndroidManifest.xml`:
   ```xml
   android:usesCleartextTraffic="true"
   android:networkSecurityConfig="@xml/network_security_config"
   ```
2. `res/xml/network_security_config.xml`:
   ```xml
   <network-security-config>
       <domain-config cleartextTrafficPermitted="true">
           <domain includeSubdomains="true">target-domain.com</domain>
       </domain-config>
   </network-security-config>
   ```

### Use HttpURLConnection over OkHttp

For simple GET requests, `java.net.HttpURLConnection` is more reliable across devices than OkHttp. It's the native Android HTTP client — the same one browsers use internally.

## Blizzard Patch API Specifics

Endpoint: `http://us.patch.battle.net:1119/{game}/versions` and `.../cdns`

**Critical**: Data uses `|` (pipe) as separator, NOT spaces:
```
us|buildConfig|cdnPath|keyRing|buildId|versionsName|productConfig
```

First line is header with type annotations: `Region!STRING:0|BuildConfig!HEX:16|...`

Parse: `line.split("|")` → `[0]`=region, `[4]`=buildId, `[5]`=versionsName

Games: `/wow_anniversary` (TBC/Anniversary), `/wow_classic` (MOP), `/wow_classic_era` (Era)

## Region Display Order

WoW players prefer: **US → EU → CN → TW → KR → SG**

## Android Build Environment (Windows/MSYS)

```
export JAVA_HOME="/c/Users/<user>/android-build/jdk-17.x"
export ANDROID_SDK_ROOT="/c/Users/<user>/android-build/android-sdk"
export PATH="$JAVA_HOME/bin:$PATH"
cd project && ./gradlew assembleDebug --no-daemon
```

Requires `google-services.json` in `app/` for Firebase builds.

## Testing FCM End-to-End

To verify push notifications work with the app **closed**:

1. **Register token**: Open app → FCM token gets sent to Worker
2. **Simulate update**: Call Worker `/simulate-update` → stores fake old versions (build "99999") in KV
3. **Wait for Cron**: Cron Trigger (every 1 min) fetches real versions, compares with fake → detects "change"
4. **FCM push sent**: Worker sends notification to all registered tokens
5. **Verify arrives**: Notification should appear even with app closed

Debug each step:
- `GET /` → check `registeredDevices > 0`
- `GET /check` → check `changes > 0`
- `GET /test-fcm` → check `sent > 0` (if `failed > 0`, check Service Account role)

## Version Transition Display (old ➡️ new)

To show version transitions in the app's history:

1. Add `previousVersion: String? = null` field to the Room entity
2. In `ChangeDetector.detectChanges()`, when a version change is detected, set `previousVersion = existing.buildVersion` on the new entry
3. In the history adapter, display: `"📌 ${item.previousVersion} ➡️ ${item.buildVersion}"` when `previousVersion` is not null
4. Bump Room database version (destructive migration will clear old data)

The `ChangeDetector` must be called BOTH from the AlarmReceiver (background checks) AND from the download dialog (manual fetches) to ensure transitions are recorded.

**Note**: First download on fresh install creates baseline entries with `previousVersion = buildVersion` (shows "📌 version" without arrow). Transitions (old ➡️ new) only appear when a REAL version change is detected against existing data.

To test transitions on fresh install: use Worker's `/fetch?fake=1` endpoint to seed fake old versions into local DB first, then fetch real data to see transitions.

## Last Notification Display (FCM apps)

Save the last received FCM notification to SharedPreferences so the user can see it even after dismissing. Display at the top of the main activity:

```kotlin
// In MyFirebaseMessagingService.onMessageReceived():
fun saveLastNotification(context: Context, title: String, body: String) {
    val prefs = context.getSharedPreferences("wow_last_notification", Context.MODE_PRIVATE)
    val time = SimpleDateFormat("dd MMM HH:mm:ss", Locale.getDefault()).format(Date())
    prefs.edit().putString("last_title", title).putString("last_body", body)
        .putString("last_time", time).apply()
}

// In MainActivity.onResume():
fun loadLastNotification() {
    val (title, body, time) = MyFirebaseMessagingService.getLastNotification(this)
    if (title.isNotEmpty()) {
        binding.lastNotifTitle.text = title
        binding.lastNotifBody.text = body
        binding.lastNotifTime.text = time
    }
}
```

## Expandable Game Cards (Collapsible Sections)

For apps with multiple game/version categories, use collapsible cards:

1. `card_game.xml`: Add clickable header with expand icon (▶/▼)
2. `regionsContainer` starts as `visibility="gone"`
3. Toggle on header click
4. Sort regions inside: `sortedBy { regionOrder.indexOf(it.region) }`

```kotlin
cardBinding.gameHeader.setOnClickListener {
    if (cardBinding.regionsContainer.visibility == View.GONE) {
        cardBinding.regionsContainer.visibility = View.VISIBLE
        cardBinding.expandIcon.text = "▼"
    } else {
        cardBinding.regionsContainer.visibility = View.GONE
        cardBinding.expandIcon.text = "▶"
    }
}
```

## Guiding Non-Technical Users

When walking someone through UI setup (Firebase Console, Cloudflare Dashboard, etc.):
- **NEVER use multiple-choice questions** — they confuse non-technical users and frustrate them. User explicitly complained: "no me gusta como me estas guiando, me dejas preguntas, vamos paso por paso"
- Guide **step by step**, one action at a time
- Let them **send screenshots** after each step
- Use **numbered steps** with exact button names to click
- Say "mándame captura" after each step
- If they get lost, ask them to send a screenshot — don't guess what they see
- For Spanish-speaking users: use "Haz click en X" not "¿Ves X?"
- **Do the work for them** when possible — don't ask "do you want X or Y?", just do the right thing
- After giving instructions, **wait for confirmation** before proceeding to next step
- User language follows user's language — if they write Spanish, respond Spanish

## File Structure Reference

```
app/src/main/
├── java/com/wowmonitor/app/
│   ├── WowMonitorApp.kt          # Application class, notification channels
│   ├── data/
│   │   ├── NetworkMonitor.kt     # HTTP client (HttpURLConnection)
│   │   ├── ChangeDetector.kt     # Compare old vs new versions
│   │   ├── AppDatabase.kt        # Room database
│   │   ├── VersionDao.kt         # Database queries
│   │   └── Models.kt             # Data classes
│   ├── service/
│   │   ├── MonitorScheduler.kt   # AlarmManager scheduling
│   │   ├── AlarmReceiver.kt      # BroadcastReceiver for alarms
│   │   ├── NotificationHelper.kt # Build and show notifications
│   │   ├── MyFirebaseMessagingService.kt # FCM token + message handling
│   │   ├── RegionPrefs.kt        # SharedPreferences for region selection
│   │   └── BootReceiver.kt       # Re-register FCM token on boot
│   └── ui/
│       └── MainActivity.kt       # Main UI with cards, tools, region chips
└── res/
    ├── layout/
    │   ├── activity_main.xml
    │   ├── card_game.xml
    │   ├── dialog_versions.xml
    │   └── section_regions.xml
    ├── xml/
    │   └── network_security_config.xml
    └── values/
        ├── colors.xml, themes.xml, strings.xml
```
