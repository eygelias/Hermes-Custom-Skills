# Cloudflare Worker as HTTPS Proxy for Android

When an Android app needs to connect to an HTTP API on a non-standard port (like Blizzard's `http://server:1119`), and adding cleartext exceptions doesn't work on all devices, use a Cloudflare Worker as an HTTPS proxy.

## Architecture

```
Android App  →  HTTPS (443)  →  Cloudflare Worker  →  HTTP (:1119)  →  Target API
```

- App connects via standard HTTPS — no cleartext issues, no network security config needed
- Worker fetches from the HTTP API server-side (no Android restrictions)
- Worker returns clean JSON — no client-side parsing of raw text formats
- Free tier: 100,000 requests/day (more than enough for polling)

## Worker Code Template (fetch + parse + return JSON)

```javascript
const API_BASE = "http://api-server:1119";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    // GET / — status
    if (url.pathname === "/") {
      return new Response(JSON.stringify({ status: "ok" }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // GET /fetch — proxy the API
    if (url.pathname === "/fetch") {
      const resp = await fetch(`${API_BASE}/some-endpoint`);
      if (!resp.ok) {
        return new Response(JSON.stringify({ error: `HTTP ${resp.status}` }), {
          status: 502,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      const text = await resp.text();
      // Parse and return as JSON
      const parsed = parseResponse(text);
      return new Response(JSON.stringify(parsed), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response("Not found", { status: 404 });
  },
};
```

## Deployment Steps (Cloudflare Dashboard)

1. Go to **Workers & Pages** in sidebar
2. Click **Create application** → **Create Worker**
3. Name it (e.g., `my-api-proxy`) → **Deploy** (creates Hello World)
4. Click **Edit code** (top right of Worker dashboard)
5. Select all (Ctrl+A) → paste Worker code → **Deploy**
6. Test: visit `https://<name>.<subdomain>.workers.dev/fetch` in browser

## Android Client — Simple HttpURLConnection

```kotlin
companion object {
    const val WORKER_URL = "https://<name>.<subdomain>.workers.dev/fetch"
}

fun fetchFromWorker(): String? {
    var conn: HttpURLConnection? = null
    try {
        conn = URL(WORKER_URL).openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        conn.connectTimeout = 15_000
        conn.readTimeout = 15_000
        val code = conn.responseCode
        if (code == 200) {
            return BufferedReader(InputStreamReader(conn.inputStream)).readText()
        }
        return null
    } catch (e: Exception) {
        Log.e(TAG, "Worker fetch failed: ${e.message}")
        return null
    } finally {
        conn?.disconnect()
    }
}
```

Then parse JSON with `org.json.JSONObject` (built into Android, no dependency needed).

## Why This Works When Cleartext Config Doesn't

Even with `usesCleartextTraffic="true"` and `network_security_config.xml`, some devices (Xiaomi, Samsung, Huawei) enforce cleartext blocking at a deeper level. The Cloudflare Worker approach eliminates the problem entirely by:
- Using HTTPS (port 443) which is never blocked
- Moving the HTTP fetch to Cloudflare's servers (not subject to Android restrictions)
- Returning standard JSON over HTTPS

## Blizzard Agent API — Worker Reference

See the complete Worker code for Blizzard's patch API at:
`C:\Users\ELY\Desktop\WoWUpdateMonitor\worker.js`

Key parsing detail: Blizzard's agent API uses `|` as delimiter, not spaces.
Format: `Region|BuildConfig|CDNConfig|KeyRing|BuildId|VersionsName|ProductConfig`
