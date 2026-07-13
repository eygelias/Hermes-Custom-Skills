# GitHub Releases app-update pattern

Use when an Android APK distributed outside Play Store needs update notices without polling GitHub.

## Architecture

```
GitHub public repo
  ├─ version.json (fixed raw URL)
  └─ Releases / APK assets
        ↓
WowPushSender manual button
        ↓
Cloudflare Worker endpoint (/notify-app-update)
        ↓
FCM data message type=app_update
        ↓
Android app blocks old version, downloads APK in-app, opens Android installer
```

## version.json

Keep one fixed raw URL, e.g.

```
https://raw.githubusercontent.com/<owner>/<repo>/main/version.json
```

Example:

```json
{
  "versionCode": 3,
  "versionName": "v3.0.0",
  "appName": "WoWUpdateMonitor",
  "apkName": "WoWUpdateMonitor v3.0.0.apk",
  "apkUrl": "https://github.com/<owner>/<repo>/releases/download/v3.0.0/WoWUpdateMonitor-v3.0.0.apk",
  "required": true,
  "message": "Actualización obligatoria disponible"
}
```

## Worker endpoints

- `GET /app-version` returns the current `version.json` from GitHub raw URL; fall back to cached KV `latest_app_version` if GitHub fetch fails.
- `GET|POST /notify-app-update` reads `version.json`, stores latest app version metadata in KV, and sends FCM data:

```json
{
  "type": "app_update",
  "versionCode": "3",
  "versionName": "v3.0.0",
  "appName": "WoWUpdateMonitor",
  "apkName": "WoWUpdateMonitor v3.0.0.apk",
  "apkUrl": "https://github.com/...apk",
  "required": "true",
  "message": "Actualización obligatoria disponible"
}
```

Do **not** cron-poll GitHub if the user wants manual control. Let WowPushSender trigger the notification.

## Android implementation checklist

1. Bump `versionCode`/`versionName`. If using `BuildConfig.VERSION_CODE`, ensure `buildFeatures { buildConfig = true }` is enabled on newer AGP projects.
2. Add permissions/providers:

```xml
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

`res/xml/file_paths.xml`:

```xml
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <external-files-path name="updates" path="." />
</paths>
```

3. Add an `AppUpdater` helper that:
   - parses `version.json` into `AppUpdateInfo`;
   - persists update metadata to SharedPreferences when FCM arrives;
   - calls `/app-version` on app launch so missed FCM still enforces update;
   - downloads APK to `context.getExternalFilesDir(null)`;
   - opens installer via `FileProvider.getUriForFile(...)`, `Intent.ACTION_VIEW`, MIME `application/vnd.android.package-archive`, and flags `FLAG_GRANT_READ_URI_PERMISSION | FLAG_ACTIVITY_NEW_TASK`.
4. In `FirebaseMessagingService.onMessageReceived`, if `message.data["type"] == "app_update"`, save update metadata before showing notification.
5. In `MainActivity.onCreate`/`onResume`, call update check/enforcement. If `remote.versionCode > BuildConfig.VERSION_CODE` and `required=true`, show a non-cancelable dialog/screen.
6. Button states:
   - if APK not downloaded: `Descargar` → show progress → save file;
   - if APK exists: `Instalar` → open Android installer;
   - after download succeeds, swap button text/listener to `Instalar`.

Android cannot silently install a normal sideloaded APK. User must tap Android installer confirmation unless Play Store in-app updates, Device Owner/MDM, root, or system app is used.

## Sender app behavior

The sender HTML/WebView APK should expose a separate app-update section:

- `Leer versión GitHub` → calls `/app-version` and displays `<appName> <versionName>`.
- `Avisar nueva versión` → calls `/notify-app-update` and shows `sent` count from Worker.

Do not send update notices before the target app version can handle `app_update`; older installed APKs will only show a normal notification.

## GitHub release workflow for user

1. Create public repo, e.g. `WoWUpdateMonitor-Releases`.
2. Keep `version.json` in repo root.
3. For each version, create Release tag `vX.Y.Z` and upload APK asset named consistently with `apkUrl`.
4. Edit `version.json` with new `versionCode`, `versionName`, `apkName`, and `apkUrl`.
5. Verify the release asset URL downloads an APK before notifying devices.
6. In WowPushSender, click the manual app-update notify button.

## Verification

- Android build must pass (`assembleDebug` or release build).
- Verify `output-metadata.json` has intended `versionCode` and `versionName`.
- Verify release URL downloads an Android package, not a 404/HTML response.
- Verify Worker `/app-version` returns the same `apkUrl` and version metadata.
