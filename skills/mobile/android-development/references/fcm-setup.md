# FCM Setup Guide — Server to Device Push

## Server-Side: FCM HTTP v1 API (Service Account)

### Getting Service Account JSON
1. Firebase Console → Project Settings → Service accounts
2. "Generate new private key" → downloads JSON file
3. This file contains: `client_email`, `private_key`, `project_id`

### Sending from Cloudflare Worker
The Worker uses Web Crypto API for JWT signing (no Node.js libraries):

```
1. Create JWT (RS256) with:
   - iss: service account client_email
   - scope: "https://www.googleapis.com/auth/firebase.messaging"
   - aud: "https://oauth2.googleapis.com/token"
   - iat/exp: current time ± 1 hour

2. Sign with private_key using crypto.subtle.importKey (pkcs8) + crypto.subtle.sign

3. POST to https://oauth2.googleapis.com/token with the JWT

4. Use returned access_token to POST to:
   https://fcm.googleapis.com/v1/projects/{project_id}/messages:send
```

### FCM Message Format
```json
{
  "message": {
    "token": "device_fcm_token",
    "notification": { "title": "...", "body": "..." },
    "data": { "key": "value" },
    "android": {
      "priority": "high",
      "notification": { "channel_id": "channel_name" }
    }
  }
}
```

## Client-Side: Android

### Getting FCM Token
```kotlin
FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
    if (task.isSuccessful) {
        val token = task.result
        // Send to server: POST /register-token { "token": token }
    }
}
```

### Token Lifecycle
- Token changes on app reinstall, data clear, or Firebase rotation
- `onNewToken()` is called — re-register with server
- Store tokens server-side (KV, database) for push delivery

### Notification Channels (Android 8+)
```kotlin
val channel = NotificationChannel("id", "Name", IMPORTANCE_HIGH)
getSystemService(NotificationManager::class.java).createNotificationChannel(channel)
```

### Manifest Metadata (default channel)
```xml
<meta-data
    android:name="com.google.firebase.messaging.default_notification_channel_id"
    android:value="your_channel_id" />
```

## Testing FCM
1. Register device token with server
2. Send test push from server (POST /test-fcm or Firebase Console)
3. Notification arrives even if app is fully closed
4. If notification doesn't arrive: check token validity, channel importance, battery optimization settings

## Common Issues
- **Token not registering**: Check INTERNET permission, server URL, network connectivity
- **No notification when app closed**: FCM handles this automatically — no service needed
- **Notification not showing**: Check channel importance level, POST_NOTIFICATIONS permission (Android 13+)
- **Service account auth fails**: Check private_key format (newlines must be \n), clock skew
