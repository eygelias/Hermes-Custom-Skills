---
name: cloudflare-workers
description: Cloudflare Workers for API proxying, scheduled tasks (Cron Triggers), KV storage, FCM push from edge.
tags: [cloudflare, worker, edge, proxy, kv, cron]
triggers:
  - Cloudflare Worker
  - API proxy for mobile app
  - edge function
  - Cron Trigger
  - Worker KV
---

# Cloudflare Workers

## As HTTP Proxy (for mobile apps)

Mobile apps sometimes can't make direct HTTP requests (Android cleartext restrictions, non-standard ports, CORS). A Worker acts as an HTTPS proxy:

```
App (HTTPS:443) → Worker → Target API (HTTP:any-port)
```

### Pattern
```javascript
export default {
  async fetch(request) {
    const data = await fetch("http://internal-api:port/path");
    const json = await data.json();
    return Response.json(json, {
      headers: { "Access-Control-Allow-Origin": "*" }
    });
  }
};
```

## KV Storage

Key-value store for Worker state. Good for: tokens, config, last-known values.

### Setup
1. Cloudflare Dashboard → Workers & Pages → KV → Create namespace
2. Worker Settings → Variables → KV Namespace Bindings → Add
   - Variable name: `MY_KV`
   - Namespace: select your namespace

### Usage
```javascript
await env.MY_KV.put("key", JSON.stringify(value));
const data = await env.MY_KV.get("key", "json"); // auto-parse
await env.MY_KV.delete("key");
```

## Cron Triggers

Scheduled execution of Worker. Minimum interval: 1 minute (free plan).

### Setup
Worker Settings → Triggers → Cron Triggers → Add
- Expression: `*/1 * * * *` (every minute)

### Handler
```javascript
export default {
  async fetch(request, env, ctx) { /* HTTP handler */ },
  async scheduled(event, env, ctx) {
    // Runs on schedule
    const result = await doWork(env);
    console.log(JSON.stringify(result));
  }
};
```

## Environment Variables & Secrets

### Plain Variables
Worker Settings → Variables and secrets → Add variable

### Secrets (encrypted)
Same flow but mark as "Encrypt" 🔒. Value is hidden after save.

Access in code: `env.VARIABLE_NAME`

## Common Patterns

### CORS Proxy
```javascript
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};
if (request.method === "OPTIONS") {
  return new Response(null, { headers: corsHeaders });
}
```

### Multiple Endpoints
```javascript
const url = new URL(request.url);
if (url.pathname === "/fetch") { /* ... */ }
if (url.pathname === "/register") { /* ... */ }
// Always return 404 for unknown routes
```

## FCM Push from Worker (HTTP v1 API)

### OAuth2 JWT Signing with Web Crypto

Workers don't have Node.js `crypto`. Use `crypto.subtle` for JWT signing:

```javascript
// CRITICAL: Convert base64 to Uint8Array CORRECTLY
function base64ToUint8Array(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

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

  // Extract DER bytes from PEM
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

  const enc = new TextEncoder();
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(`${header}.${payload}`));

  const sigB64 = btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const jwt = `${header}.${payload}.${sigB64}`;

  const resp = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
  });
  const data = await resp.json();
  if (!data.access_token) throw new Error(`OAuth2: ${data.error} - ${data.error_description}`);
  return data.access_token;
}
```

### Sending FCM Message

```javascript
async function sendFCM(deviceToken, title, body, env) {
  const accessToken = await getAccessToken(env);
  const sa = JSON.parse(env.FIREBASE_SERVICE_ACCOUNT);

  const resp = await fetch(
    `https://fcm.googleapis.com/v1/projects/${sa.project_id}/messages:send`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          token: deviceToken,
          notification: { title, body },
          android: { priority: "high" },
        },
      }),
    }
  );
  return resp.ok;
}
```

## Pitfalls

1. **Worker code not updating** — After editing in dashboard, MUST click "Deploy" (blue button). The editor auto-saves but doesn't deploy.
2. **KV binding missing** — Code references `env.MY_KV` but binding not configured → runtime error. Always set up binding in Settings → Variables.
3. **Secret as Plaintext** — Forgetting to encrypt sensitive values. Always use "Encrypt" for API keys, tokens, credentials.
4. **Cron not firing** — Check Triggers section. Verify expression format. Check "View events" for execution logs.
6. **Free plan limits** — 100k requests/day, 1 min cron minimum, 1GB KV storage. **KV PUT limit: 1,000/day.** A cron every 1 min that writes to KV every time = 1,440 PUTs/day → exceeds limit. Fix: only write to KV when state actually changes:
```javascript
const isFirstRun = Object.keys(last).length === 0;
if (changes.length > 0 || isFirstRun) {
  await env.WOW_KV.put("last_versions", JSON.stringify(current));
}
```
6. **⚠️ FCM JWT signing: binary data corruption** — `TextEncoder.encode(atob(base64))` CORRUPTS binary key data. `atob()` returns a binary string; `TextEncoder.encode()` treats each byte as UTF-8, corrupting bytes > 127 into multi-byte sequences. MUST use `Uint8Array` with `charCodeAt()` loop instead. This caused `sent: 0, failed: 1` with no error message for hours.
7. **FCM Service Account role** — Default Service Account has "Firebase SDK Admin Service Agent" which is NOT enough for FCM. Must manually add **"Firebase Cloud Messaging API Admin"** role in Google Cloud Console → IAM. Without it, OAuth2 succeeds but FCM API returns 403/404.
8. **Testing FCM end-to-end** — To test push with app closed: (a) call `/simulate-update` to store fake old versions in KV, (b) Cron Trigger detects "change" within 1 min, (c) sends real FCM push. Verify each step: token registered (`/` shows registeredDevices > 0), simulate stored data, cron detected changes (`/check`), FCM send succeeded (`/test-fcm` shows sent > 0).
9. **Redeploy clears token state** — When you redeploy Worker code, the KV data persists but the in-memory state resets. If FCM tokens were stored in KV, they survive redeploy. If stored in a variable, they're lost.
10. **Dead token accumulation** — Multiple app reinstalls create multiple FCM tokens in KV. Old tokens cause `sent: N, failed: M`. Clean up by removing tokens that fail with specific FCM error codes, not on any failure.
11. **Cron consumes test data** — When using `/simulate-update` to store fake versions for testing, the next Cron Trigger detects the "change" and overwrites the fake data with real data. Always chain `simulate-update` + `/check` in < 30 seconds, or the Cron will eat the test data before the user sees the notification.
12. **Telegram Bot API from Worker** — Sending to Telegram channels is one `fetch` call. Store `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` as encrypted secrets. Bot must be channel admin with "Manage messages" permission. Channel ID is negative (e.g., `-1004240877348`). Get it by forwarding a channel message to the bot and calling `getUpdates`. Note: Telegram token gets redacted in terminal output — can't test directly from CLI, must test via Worker endpoint.
13. **MSYS path mangling on Windows** — Git Bash / MSYS converts paths starting with `/` to Windows paths. `/sdcard/Download/` becomes `C:/Users/.../sdcard/Download/`. Fix: use double slashes `//sdcard//Download//` for adb push commands.
