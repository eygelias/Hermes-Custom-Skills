# Manual GitHub APK update flow

Use when user wants Android app update notices without extra polling/cron spend.

## Architecture

- GitHub public repo stores release APKs plus a fixed `version.json` on `main`.
- Cloudflare Worker exposes:
  - `GET /app-version` — reads fixed GitHub raw `version.json` (cache-busted), fallback to KV `latest_app_version` if GitHub fails.
  - `GET|POST /notify-app-update` — manual trigger from admin UI; reads `version.json`, stores KV `latest_app_version`, broadcasts FCM with `data.type = "app_update"`.
- Sender UI (HTML/WebView APK) has buttons:
  - `Leer versión GitHub` → call `/app-version` and show `appName versionName`.
  - `Avisar nueva versión` → call `/notify-app-update`.
- Android app handles `app_update` FCM and also checks `/app-version` on launch.
- If installed `versionCode < remote.versionCode` and `required=true`, block main UI until update.
- App downloads APK from `apkUrl` inside app storage, then opens Android package installer via `FileProvider`.

## version.json shape

```json
{
  "versionCode": 3,
  "versionName": "v3.0.0",
  "appName": "WoWUpdateMonitor",
  "apkName": "WoWUpdateMonitor v3.0.0.apk",
  "apkUrl": "https://github.com/<user>/<repo>/releases/download/v3.0.0/WoWUpdateMonitor-v3.0.0.apk",
  "required": true,
  "message": "Actualización obligatoria disponible"
}
```

Fixed raw URL pattern:

```text
https://raw.githubusercontent.com/<user>/<repo>/main/version.json
```

## Worker snippets

```js
const APP_VERSION_URL = "https://raw.githubusercontent.com/<user>/<repo>/main/version.json";

async function fetchAppVersion() {
  const resp = await fetch(`${APP_VERSION_URL}?t=${Date.now()}`, {
    headers: { "Cache-Control": "no-cache" },
  });
  if (!resp.ok) throw new Error(`GitHub version fetch failed: ${resp.status}`);
  return await resp.json();
}

async function notifyAppUpdate(env) {
  const v = await fetchAppVersion();
  await env.WOW_KV.put("latest_app_version", JSON.stringify(v));
  const title = "🔔 Nueva versión disponible";
  const body = `${v.appName || "App"} ${v.versionName} ya está lista. ${v.message || "Actualización obligatoria."}`;
  const result = await broadcastToTokens(env, title, body, {
    type: "app_update",
    versionCode: String(v.versionCode || ""),
    versionName: String(v.versionName || ""),
    appName: String(v.appName || "App"),
    apkName: String(v.apkName || ""),
    apkUrl: String(v.apkUrl || ""),
    required: String(v.required !== false),
    message: String(v.message || ""),
  });
  return { ok: true, version: v, fcm: result };
}
```

## Android limitation

Normal sideloaded APKs cannot silently update themselves. Silent install only works with Play Store in-app updates, Device Owner/MDM, root, or system app. For GitHub APKs, app can download internally but Android must show the package installer and user must tap Update.

## Manual Cloudflare deploy fallback

If Cloudflare dashboard blocks automation with human verification, edit manually:

1. Worker → Edit code.
2. Open local `worker.js`.
3. Copy all content.
4. In Cloudflare editor: select all, paste, Deploy.
5. Verify with `GET /app-version` and root endpoint endpoints list.
