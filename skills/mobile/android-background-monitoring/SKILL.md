---
name: android-background-monitoring
description: "Android background polling without persistent notifications — AlarmManager, WorkManager, Foreground Service tradeoffs. Covers HTTP cleartext issues, network diagnostics, BroadcastReceiver pitfalls, and testing patterns."
tags: [android, kotlin, background, alarmmanager, workmanager, notifications, network]
triggers:
  - "Android app needs to run periodically in the background"
  - "App has a persistent notification that user wants removed"
  - "Foreground Service migration to WorkManager or AlarmManager"
  - "Periodic API polling from Android app"
  - "App stops working when user clears recent apps"
  - "How does WhatsApp receive notifications without running"
  - "Android cannot connect to HTTP server"
  - "cleartext traffic blocked android"
---

# Android Background Monitoring (No Persistent Notification)

Build Android apps that poll a remote API periodically in the background WITHOUT showing a permanent notification.

## Architecture Decision Matrix

| Approach | Min Interval | Persistent Notif | Survives Kill | Battery |
|----------|-------------|-------------------|---------------|---------|
| **Foreground Service** | seconds | ✅ Required by Android | ❌ User can swipe | High (WakeLock) |
| **WorkManager** | 15 min (hard limit) | ❌ No | ✅ OS-managed | Low |
| **AlarmManager** | 1-5 min (practical) | ❌ No | ✅ Survives kill | Low |
| **FCM Push** | Instant | ❌ No | ✅ Yes | Zero | Needs server control |

**Recommendation**: Use AlarmManager for intervals < 15 min. Use WorkManager for ≥ 15 min.

### The WhatsApp myth
WhatsApp does NOT poll. It uses **FCM (Firebase Cloud Messaging)** — Google maintains a single persistent connection to all Android devices. The app doesn't run in background at all. When the WhatsApp server wants to notify you, it tells Google's servers, which deliver the push. **This requires server-side infrastructure** — you can't replicate it for a public API you don't control.

---

## AlarmManager Pattern (5-min polling, no notification)

### Core Components

1. **MonitorScheduler** (object) — schedules/cancels/checks alarms
2. **AlarmReceiver** (BroadcastReceiver) — executes the actual check, re-schedules next alarm
3. **BootReceiver** — re-schedules on device boot
4. **NotificationHelper** — sends alerts ONLY on detected changes

### MonitorScheduler — Scheduling Object

```kotlin
object MonitorScheduler {
    private const val REQUEST_CODE_PERIODIC = 7741
    private const val REQUEST_CODE_ONESHOT = 7742  // separate code for test alarms

    private val pendingIntentFlags = PendingIntent.FLAG_UPDATE_CURRENT or
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) PendingIntent.FLAG_IMMUTABLE else 0

    fun schedule(context: Context) {
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val intent = Intent(context, AlarmReceiver::class.java)
        val pending = PendingIntent.getBroadcast(context, REQUEST_CODE_PERIODIC, intent, pendingIntentFlags)

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                alarmManager.setExactAndAllowWhileIdle(
                    AlarmManager.ELAPSED_REALTIME_WAKEUP,
                    android.os.SystemClock.elapsedRealtime() + INTERVAL_MS,
                    pending
                )
            } else {
                alarmManager.setExact(AlarmManager.ELAPSED_REALTIME_WAKEUP,
                    android.os.SystemClock.elapsedRealtime() + INTERVAL_MS, pending)
            }
        } catch (e: SecurityException) {
            // Android 14+ can revoke SCHEDULE_EXACT_ALARM
            alarmManager.set(AlarmManager.ELAPSED_REALTIME_WAKEUP,
                android.os.SystemClock.elapsedRealtime() + INTERVAL_MS, pending)
        }
    }

    fun scheduleOneShot(context: Context, delayMs: Long) {
        // Same as schedule() but with REQUEST_CODE_ONESHOT and custom delay
    }

    fun isScheduled(context: Context): Boolean {
        return PendingIntent.getBroadcast(
            context, REQUEST_CODE_PERIODIC, intent,
            pendingIntentFlags or PendingIntent.FLAG_NO_CREATE
        ) != null
    }
}
```

### AlarmReceiver — The Worker

```kotlin
class AlarmReceiver : BroadcastReceiver() {
    companion object {
        // Direct invocation method (no goAsync)
        fun runCheckNow(context: Context) {
            CoroutineScope(Dispatchers.IO).launch {
                doCheck(context)
            }
        }

        private suspend fun doCheck(context: Context) {
            // fetch API → detect changes → send notifications
        }
    }

    override fun onReceive(context: Context, intent: Intent?) {
        MonitorScheduler.schedule(context)  // Re-schedule FIRST
        val pending = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try { doCheck(context) }
            catch (e: Exception) { Log.e(TAG, "Check failed", e) }
            finally { try { pending?.finish() } catch (_: Exception) {} }
        }
    }
}
```

### AndroidManifest

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />

<receiver android:name=".service.AlarmReceiver" android:exported="false" />
<receiver android:name=".service.BootReceiver" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

---

## WorkManager Pattern (≥15 min interval)

```kotlin
class MyWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    companion object {
        fun schedule(context: Context) {
            val request = PeriodicWorkRequestBuilder<MyWorker>(15, TimeUnit.MINUTES)
                .setConstraints(Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED).build())
                .build()
            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "my_periodic", ExistingPeriodicWorkPolicy.KEEP, request)
        }
        fun triggerNow(context: Context) {
            WorkManager.getInstance(context).enqueue(
                OneTimeWorkRequestBuilder<MyWorker>().build())
        }
    }
    override suspend fun doWork(): Result {
        return try { /* fetch, detect, notify */ Result.success() }
        catch (e: Exception) { Result.retry() }
    }
}
```

---

## Foreground Service → AlarmManager Migration Checklist

1. Delete `MonitorService.kt` (the Foreground Service)
2. Delete any `RestartReceiver.kt` (not needed — AlarmManager survives)
3. Create `MonitorScheduler.kt` (alarm scheduling object)
4. Create `AlarmReceiver.kt` (BroadcastReceiver with `goAsync()`)
5. Update `BootReceiver` — call `MonitorScheduler.schedule()` instead of `MonitorService.start()`
6. Update `MainActivity` — schedule alarm + trigger immediate check, no service start
7. Remove from manifest: `<service>`, `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_DATA_SYNC`, `WAKE_LOCK`
8. Add to manifest: `SCHEDULE_EXACT_ALARM`, `USE_EXACT_ALARM`, `<receiver>` for AlarmReceiver
9. Remove notification channel for service (keep version/update channels)
10. Remove `createServiceNotification()` from NotificationHelper
11. Remove `MonitorServiceRunningChecker` object if present
12. Search ALL files for references to deleted classes (grep for class name)

---

## Pitfalls

### PITFALL: goAsync() returns null when called directly
```
java.lang.NullPointerException: Attempt to invoke virtual method
'void android.content.BroadcastReceiver$PendingResult.finish()' on a null object reference
```
**Cause:** `goAsync()` only works when Android system delivers the broadcast. Calling `onReceive()` directly from Activity = no PendingResult = null.
**Fix:** Use companion object method `runCheckNow()` for direct invocation, and null-safe `pending?.finish()` in onReceive.

### PITFALL: Android blocks cleartext HTTP traffic (Android 9+)
```
java.net.ConnectException: Connection refused
// or silently returns null from HttpURLConnection
```
**Cause:** Android 9+ blocks non-HTTPS traffic by default. APIs on non-standard ports (like `http://server:1119`) are blocked even though the browser can access them.
**Fix — two parts:**

1. Create `res/xml/network_security_config.xml`:
```xml
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">your-api-domain.com</domain>
    </domain-config>
</network-security-config>
```

2. Add to `<application>` in AndroidManifest.xml:
```xml
android:usesCleartextTraffic="true"
android:networkSecurityConfig="@xml/network_security_config"
```

### PITFALL: OkHttp fails but browser works
On some devices/Android versions, OkHttp has issues with HTTP (non-HTTPS) connections to non-standard ports. **Use `HttpURLConnection` instead** — it's Android's native HTTP client and handles cleartext more reliably. Remove OkHttp dependency if not needed elsewhere.

### PITFALL: BroadcastReceiver has ~10 second limit
If work takes >10s, Android will ANR. Always use `goAsync()` + coroutine for network calls.

### PITFALL: Re-schedule FIRST in onReceive()
If the check crashes after re-scheduling, you still have the next alarm queued. If you re-schedule after the check and it crashes, you lose all future alarms.

### PITFALL: REQUEST_CODE must be unique per alarm type
Reusing request codes cancels previous alarms. Use separate codes for periodic (7741) vs one-shot test (7742) alarms.

### PITFALL: Samsung/Xiaomi/EMUI battery optimization
Some OEMs aggressively kill background work. User must set app to "Unrestricted" in battery settings:
**Settings → Battery → [App] → Unrestricted**

### PITFALL: setExactAndAllowWhileIdle SecurityException
Android 14+ can revoke `SCHEDULE_EXACT_ALARM` permission. Always wrap in try/catch, fall back to `set()`.

### PITFALL: FLAG_IMMUTABLE required on Android 12+
PendingIntents must use `FLAG_IMMUTABLE` on API 31+. Always include it.

### PITFALL: WorkManager 15-min minimum is a hard Android limit
Not configurable, not a WorkManager library limit. If you need <15 min, AlarmManager is the only non-service option.

---

## Testing Background Notifications

Insert a fake DB entry with a different build/version number, then schedule a one-shot alarm after 10-30 seconds. When the alarm fires, the change detector sees the difference and sends a real notification. This tests the full pipeline: alarm → fetch → detect → notify.

```kotlin
// In test button handler:
fun scheduleTest(seconds: Int) {
    // 1. Insert fake "old" entry with different build number
    val fakeEntry = existingEntry.copy(
        buildNumber = "99999", buildVersion = "9.9.9.99999",
        detectedAt = System.currentTimeMillis() - 60_000
    )
    db.versionDao().insert(fakeEntry)

    // 2. Schedule one-shot alarm
    MonitorScheduler.scheduleOneShot(context, seconds * 1000L)

    // 3. Start countdown UI
    // Shows "⏱️ Notification in Xs... minimize the app"
}
```

---

## Network Diagnostics

When an app can't connect but the browser can, use `ConnectivityManager` to diagnose:

```kotlin
val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
val net = cm.activeNetwork
val caps = cm.getNetworkCapabilities(net)
Log.d(TAG, "Active network: ${net != null}")
Log.d(TAG, "Internet: ${caps?.hasCapability(NET_CAPABILITY_INTERNET)}")
Log.d(TAG, "Validated: ${caps?.hasCapability(NET_CAPABILITY_VALIDATED)}")
val linkProps = cm.getLinkProperties(net)
Log.d(TAG, "DNS: ${linkProps?.dnsServers}")
Log.d(TAG, "Interface: ${linkProps?.interfaceName}")
```

Common causes when browser works but app doesn't:
1. Cleartext HTTP blocked (most common — see pitfall above)
2. OkHttp compatibility issue — switch to HttpURLConnection
3. VPN or firewall treating app differently than browser
4. App-level proxy configuration

---

## Cleartext HTTP Still Blocked After Config? Use a Cloudflare Worker Proxy

When `usesCleartextTraffic` + `network_security_config.xml` still fail (common on Xiaomi, Samsung, Huawei), deploy a Cloudflare Worker as an HTTPS proxy:

```
App (HTTPS/443) → Cloudflare Worker → HTTP API (any port)
```

Free tier: 100k requests/day. Works on all devices. See `references/cloudflare-worker-proxy.md` (in `android-networking` skill) for full Worker template and deployment steps.

## When to Use Foreground Service Instead

Keep Foreground Service when:
- Real-time streaming (WebSocket, SSE)
- Audio/video playback
- Fitness/health tracking with GPS
- User explicitly wants to see "active" status
