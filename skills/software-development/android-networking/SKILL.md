---
name: android-networking
description: "Android HTTP networking: cleartext traffic, network security config, HttpURLConnection vs OkHttp, diagnosing connectivity issues, and API response parsing."
trigger: "Android app making HTTP requests — connection refused, cleartext blocked, parsing API responses, or diagnosing network failures on device."
---

# Android Networking

Patterns for HTTP networking on Android, with pitfalls from production debugging.

## Cleartext HTTP Blocked (API 28+)

Android 9+ blocks cleartext (non-HTTPS) traffic by default. If your app connects to `http://` endpoints, you need explicit configuration.

### Fix: Network Security Config

**1. Create `res/xml/network_security_config.xml`:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">api.example.com</domain>
        <domain includeSubdomains="true">patch.example.net</domain>
    </domain-config>
</network-security-config>
```

**2. Add to AndroidManifest `<application>`:**
```xml
<application
    android:usesCleartextTraffic="true"
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### Pitfall: `usesCleartextTraffic` alone may not suffice
Some devices/OEM versions require BOTH `usesCleartextTraffic="true"` AND the `networkSecurityConfig`. Always add both.

### Pitfall: Browser works but app doesn't
The browser has its own network stack and may not be subject to the same cleartext restrictions. The app's `HttpURLConnection` or OkHttp IS restricted. Don't assume "works in browser = works in app".

## HttpURLConnection (Preferred for simplicity)

```kotlin
private fun httpGet(urlStr: String): String? {
    var conn: HttpURLConnection? = null
    try {
        conn = URL(urlStr).openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        conn.connectTimeout = 15_000
        conn.readTimeout = 15_000
        conn.setRequestProperty("User-Agent", "AppName/1.0")

        val code = conn.responseCode
        if (code == 200) {
            return BufferedReader(InputStreamReader(conn.inputStream)).readText()
        }
        return null
    } catch (e: Exception) {
        Log.e(TAG, "httpGet failed: ${e.javaClass.simpleName}: ${e.message}")
        return null
    } finally {
        conn?.disconnect()
    }
}
```

### Why HttpURLConnection over OkHttp:
- No extra dependency
- Same behavior across all Android versions
- Fewer edge cases with connection pooling
- Works identically to browser's network stack

## Diagnosing Network Issues on Device

When an HTTP request fails but the user says "internet works", check:

```kotlin
val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
val net = cm.activeNetwork
val caps = cm.getNetworkCapabilities(net)
val linkProps = cm.getLinkProperties(net)

// These tell you everything:
caps?.hasCapability(NET_CAPABILITY_INTERNET)     // has internet?
caps?.hasCapability(NET_CAPABILITY_VALIDATED)     // actually works?
caps?.hasCapability(NET_CAPABILITY_NOT_VPN)       // behind VPN?
linkProps?.dnsServers                              // which DNS?
linkProps?.interfaceName                           // wlan0 vs rmnet?
```

### Common causes when browser works but app doesn't:
1. **Cleartext blocked** — most common, see above
2. **VPN/proxy blocking app traffic** — check NOT_VPN capability
3. **Data Saver restricting app** — user must whitelist
4. **Firewall app (NetGuard, etc.)** — per-app blocking
5. **Different DNS resolution** — app may use system DNS vs browser's DoH

## API Response Parsing Pitfalls

### Pitfall: Assuming whitespace-delimited data
Many APIs (including Blizzard's agent API) use `|` or `\t` as delimiters, NOT spaces. Always check the actual response format before writing parsers.

**Blizzard agent API format:**
```
Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16
## seqn = 3815170
us|bc3b8e61b6ba9f06|2374bc9b22181d36||68101|2.5.5.68101|92cbb948...
eu|bc3b8e61b6ba9f06|2374bc9b22181d36||68101|2.5.5.68101|92cbb948...
```
- Lines starting with `##` are comments
- First non-comment line is header
- Data lines use `|` as separator
- Column indices: 0=Region, 1=BuildConfig, 2=CDNConfig, 3=KeyRing, 4=BuildId, 5=VersionsName

### Always log raw response before parsing
When debugging parse failures, always log the first 200 chars of the raw response. The parse error is almost always a format assumption mismatch.

## Cloudflare Worker Proxy (When Cleartext Config Fails)

Even with `usesCleartextTraffic` and `network_security_config.xml`, some OEM devices (Xiaomi, Samsung, Huawei) block cleartext at a deeper level. The cleanest fix is a **Cloudflare Worker** that proxies the HTTP API over HTTPS.

```
Android App → HTTPS (443) → Cloudflare Worker → HTTP (:1119) → Target API
```

Free tier: 100k requests/day. Works on all devices. No cleartext config needed.

**See:** `cloudflare-worker-fcm` skill for full Worker code template with FCM push, KV storage, Cron Triggers, and deployment steps.

## Pitfalls Summary

1. **Cleartext HTTP blocked (API 28+)** — Add both `usesCleartextTraffic` AND `networkSecurityConfig`
2. **Cleartext config still fails on some OEMs** — Use Cloudflare Worker proxy instead (see references/)
3. **OkHttp connection pooling can cause stale connections** — For simple polling apps, `HttpURLConnection` is more reliable
4. **`split("\\s+")` wrong for `|`-delimited data** — Check actual delimiter first
5. **Always close connections in `finally`** — Even on success path
6. **Show actual error to user** — Don't show generic "connection failed", show the exception class and message

## SSL Certificate Validation Failures

**Error:** `CertPathValidatorException: Trust anchor for certification path not found` or `SSLHandshakeException`

**Cause:** The device's certificate store doesn't include the server's CA certificate. Common on:
- Xiaomi devices (aggressive cert pinning)
- Huawei devices (custom cert store)
- Android 7-11 (missing intermediate CAs)
- Self-hosted/community API instances with non-standard certs

**Fix: Create an `HttpClientFactory` with permissive SSL:**

```kotlin
object HttpClientFactory {
    fun createPermissiveClient(): OkHttpClient {
        val trustAllCerts = arrayOf<TrustManager>(object : X509TrustManager {
            override fun checkClientTrusted(chain: Array<X509Certificate>, authType: String) {}
            override fun checkServerTrusted(chain: Array<X509Certificate>, authType: String) {}
            override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
        })
        val sslContext = SSLContext.getInstance("TLS")
        sslContext.init(null, trustAllCerts, SecureRandom())
        return OkHttpClient.Builder()
            .sslSocketFactory(sslContext.socketFactory, trustAllCerts[0] as X509TrustManager)
            .hostnameVerifier { _, _ -> true }
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    fun createDefaultClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    fun createDownloadClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(300, TimeUnit.SECONDS)
            .build()
    }
}
```

**When to use permissive client:**
- Third-party API calls (Cobalt, public instances)
- Downloading files from CDN URLs with cert chain issues
- Any HTTPS connection that fails with `CertPathValidatorException`

**When NOT to use:**
- Your own production APIs (use proper cert pinning)
- Payment/banking APIs (security critical)

**Pattern:** Create the permissive client once, reuse across all extractors/network calls. Don't create a new one per request.

## WebView Custom URL Scheme Crash

**Error:** `net::ERR_UNKNOWN_URL_SCHEME`

**Cause:** Social media sites (Facebook, Instagram, TikTok) redirect to app deep links:
- `fb://video/123456` (Facebook)
- `instagram://media?id=123` (Instagram)
- `tiktok://aweme/video/123` (TikTok)

WebView cannot load these schemes and throws `ERR_UNKNOWN_URL_SCHEME`.

**Fix: Override `shouldOverrideUrlLoading`:**

```kotlin
webViewClient = object : WebViewClient() {
    override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
        val url = request?.url?.toString() ?: return false
        // Block custom URL schemes that WebView can't handle
        if (url.startsWith("fb://") || url.startsWith("instagram://") ||
            url.startsWith("tiktok://") || url.startsWith("snssdk://") ||
            url.startsWith("whatsapp://") || url.startsWith("tg://")) {
            Log.d(TAG, "Blocked custom URL scheme: $url")
            return true // Don't load
        }
        return false // Allow http/https
    }
}
```

**Always add this** when using WebView to load social media pages.
