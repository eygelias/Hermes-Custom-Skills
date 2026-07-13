# Migration Examples

## Example 1: Foreground Service → WorkManager (15-min interval)

### Context
App monitoring WoW update APIs. Originally used Foreground Service with 60-second polling. User complained about persistent notification and app getting killed by cleaner apps. 15-minute interval acceptable.

### Before
- `MonitorService` — Foreground Service, 60s polling, WakeLock, persistent notification
- `MonitorWorker` — WorkManager that only checked if service was alive
- `RestartReceiver` — BroadcastReceiver to restart service on kill
- 3 notification channels: service (persistent), versions, cdns

### After
- `MonitorWorker` — WorkManager doing ALL work: fetch → detect → notify
- `BootReceiver` — Only schedules WorkManager on boot
- 2 notification channels: versions, cdns

### Files Deleted
- `MonitorService.kt`, `RestartReceiver.kt`

### Files Modified
- `MonitorWorker.kt` — rewritten to do fetch + detect + notify
- `NotificationHelper.kt` — removed `createServiceNotification()`
- `WowMonitorApp.kt` — removed `CHANNEL_SERVICE`
- `BootReceiver.kt` — `MonitorWorker.schedule()` instead of `MonitorService.start()`
- `MainActivity.kt` — `schedule()` + `triggerNow()`, no service start
- `AndroidManifest.xml` — removed `<service>`, FOREGROUND_SERVICE, WAKE_LOCK

---

## Example 2: Foreground Service → AlarmManager (5-min interval)

### Context
Same app, but user wanted 5-minute polling. WorkManager's 15-min minimum was too slow. Switched to AlarmManager.

### Additional Changes (on top of Example 1)
- Replaced `MonitorWorker` with `MonitorScheduler` (object) + `AlarmReceiver` (BroadcastReceiver)
- Added `SCHEDULE_EXACT_ALARM` + `USE_EXACT_ALARM` permissions
- Added `AlarmReceiver` to manifest with `exported="false"`
- Added network_security_config.xml for cleartext HTTP (Blizzard uses port 1119, non-HTTPS)
- Added `usesCleartextTraffic="true"` to manifest
- Replaced OkHttp with HttpURLConnection (more reliable for HTTP on some devices)

### Key Pattern: Separate direct invocation from system broadcast
```kotlin
class AlarmReceiver : BroadcastReceiver() {
    companion object {
        fun runCheckNow(context: Context) { /* no goAsync */ }
    }
    override fun onReceive(context: Context, intent: Intent?) {
        MonitorScheduler.schedule(context)  // re-schedule FIRST
        val pending = goAsync()             // null-safe
        // ...
    }
}
```

### Testing
Added "Test Background Notification" buttons (10s/20s/30s):
- Insert fake DB entry with different build number
- Schedule one-shot alarm with separate REQUEST_CODE
- Countdown UI shows "minimize the app"
- When alarm fires → change detector sees difference → real notification sent

---

## Example 3: Cleartext HTTP → Cloudflare Worker Proxy

### Context
Same WoW monitoring app. Even with `usesCleartextTraffic="true"` and `network_security_config.xml`, the app couldn't connect to `http://us.patch.battle.net:1119` on the user's device. Browser worked fine. Root cause: OEM-level cleartext blocking that overrides Android config.

### Solution
Deployed a Cloudflare Worker that:
1. Receives HTTPS requests from the app
2. Fetches from Blizzard's HTTP API server-side
3. Parses the `|`-delimited text response
4. Returns clean JSON

### Architecture
```
App (HTTPS/443) → Cloudflare Worker → Blizzard API (HTTP/1119)
```

### Changes
- `NetworkMonitor.kt` — rewrote to fetch single HTTPS URL (`WorkerUrl/fetch`) and parse JSON
- `MainActivity.kt` — dialog fetches from Worker, parses JSON with `org.json.JSONObject`
- Removed OkHttp dependency (no longer needed)
- Removed `network_security_config.xml` and `usesCleartextTraffic` (not needed with HTTPS Worker)
- Created `worker.js` — Cloudflare Worker code (deployed to Cloudflare dashboard)

### Why This Is Better Than Cleartext Config
- Works on ALL devices (no OEM overrides)
- Standard HTTPS (port 443) — never blocked
- No permission prompts for cleartext
- Worker can cache responses (reduces load on target API)
- Worker can do server-side parsing (simpler Android client)
- Free tier: 100k requests/day
