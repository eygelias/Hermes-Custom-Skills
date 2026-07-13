---
name: android-background-tasks
description: "Android background execution: Foreground Service vs WorkManager vs AlarmManager vs FCM. Covers choosing the right mechanism, implementation patterns, auto-start on boot, and common pitfalls."
trigger: "Android app needs background work — polling, monitoring, scheduled checks, periodic sync, or push-like behavior without a persistent notification."
---

# Android Background Tasks

Guide for choosing the right background execution mechanism on Android, with pitfalls discovered in production.

## Choosing a Mechanism

| Mechanism | Min Interval | Notification | Survives Kill | Battery | Use When |
|-----------|-------------|--------------|---------------|---------|----------|
| **WorkManager** | 15 min (hard limit) | None | ✅ | Low | Periodic sync, data refresh |
| **AlarmManager** | Any (exact) | None | ✅ | Medium | Precise timing needed (<15min) |
| **Foreground Service** | Continuous | **Permanent** (required) | Partial | High | Real-time, user-visible |
| **FCM Push** | Server-driven | Only when needed | ✅ | Lowest | Server sends updates |

### Decision tree:
- Need <15 min interval? → AlarmManager
- Need ≥15 min interval? → WorkManager (simpler)
- Need continuous connection? → Foreground Service (accepts permanent notification)
- Have a server that can push? → FCM (like WhatsApp)

## AlarmManager Implementation

```kotlin
val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
val intent = Intent(context, AlarmReceiver::class.java)
val pending = PendingIntent.getBroadcast(context, REQUEST_CODE, intent,
    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)

if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
    alarmManager.setExactAndAllowWhileIdle(
        AlarmManager.ELAPSED_REALTIME_WAKEUP,
        android.os.SystemClock.elapsedRealtime() + delayMs,
        pending
    )
}
```

### Required permissions:
```xml
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />
```

### Pitfall: `goAsync()` returns null when called directly
`BroadcastReceiver.goAsync()` only works when the system delivers the broadcast. If you call `onReceive()` directly from code (e.g., from Activity for an immediate check), `goAsync()` returns null → NPE crash.

**Fix:** Create a separate static method for direct invocation:
```kotlin
class MyReceiver : BroadcastReceiver() {
    companion object {
        fun runNow(context: Context) {
            CoroutineScope(Dispatchers.IO).launch { doWork(context) }
        }
        private suspend fun doWork(context: Context) { /* actual logic */ }
    }
    override fun onReceive(context: Context, intent: Intent?) {
        val pending = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try { doWork(context) }
            finally { try { pending?.finish() } catch (_: Exception) {} }
        }
    }
}
```

## WorkManager Implementation

```kotlin
val request = PeriodicWorkRequestBuilder<MyWorker>(15, TimeUnit.MINUTES)
    .setConstraints(Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED).build())
    .build()
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "unique_name", ExistingPeriodicWorkPolicy.KEEP, request)
```

## Auto-start on Boot

```xml
<receiver android:name=".service.BootReceiver" android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

## FCM Push (Android-Side Setup)

When the server can push (e.g. Cloudflare Worker), FCM is the best option — no background service, no notification permanente, works with app closed.

### Dependencies

`build.gradle.kts` (project):
```kotlin
id("com.google.gms.google-services") version "4.4.0" apply false
```

`app/build.gradle.kts`:
```kotlin
plugins {
    id("com.google.gms.google-services") // at bottom
}
dependencies {
    implementation(platform("com.google.firebase:firebase-bom:32.7.0"))
    implementation("com.google.firebase:firebase-messaging-ktx")
}
```

Requires `google-services.json` in `app/` directory (download from Firebase Console).

### FCM Service

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        // POST token to your server
        registerTokenWithServer(token)
    }
    override fun onMessageReceived(message: RemoteMessage) {
        val title = message.notification?.title ?: message.data["title"] ?: "Update"
        val body = message.notification?.body ?: message.data["body"] ?: ""
        showNotification(title, body)
    }
}
```

### AndroidManifest.xml

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

### Token Registration

Get token and send to server on app open:
```kotlin
FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
    if (task.isSuccessful) {
        val token = task.result
        // POST to server /register-token
    }
}
```

### Pitfall: Dead tokens accumulate

When FCM send fails (e.g. token expired), remove the dead token from your server's storage. Otherwise future sends keep failing for that token.

### Pitfall: Token lost on Worker redeploy

If using Cloudflare Worker with KV, the token survives code redeployments. But if previous failed sends removed the token, user must reopen the app to re-register.

## Pitfalls

1. **Foreground Service REQUIRES visible notification** — Android policy, no workaround.
2. **Aggressive OEM battery optimization** — Samsung/Xiaomi/Huawei kill background services. User must: Settings → Battery → App → No restrictions.
3. **Cleartext HTTP blocked (API 28+)** — See `android-networking` skill.
4. **WorkManager minimum is 15 minutes** — Enforced by Android, no workaround. Use AlarmManager for shorter intervals.
5. **AlarmManager needs re-scheduling after each fire** — Unlike WorkManager, alarms are one-shot. Re-schedule in `onReceive()`.
6. **`goAsync()` null when calling `onReceive()` directly** — See implementation section above.
7. **FCM token needs re-registration after fixing server** — If server lost the token (dead token cleanup), user must reopen app.
