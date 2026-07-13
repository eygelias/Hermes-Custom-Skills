# Cobalt API — Social Media Video Extraction

Cobalt (https://cobalt.tools) is an open-source media downloader API that supports 20+ platforms. It's the same engine used by services like savefrom.net. **This is the most reliable extraction method** — use it as the primary strategy before HTTP or WebView fallbacks.

## API Endpoint

```
POST https://api.cobalt.tools/
Content-Type: application/json
Accept: application/json
```

**Note**: The official `api.cobalt.tools` has bot protection and may require authentication. Use community-hosted mirrors as fallbacks.

### Request Body

```json
{
    "url": "https://www.tiktok.com/@user/video/123456",
    "videoQuality": "1080",
    "audioFormat": "mp3",
    "downloadMode": "auto",
    "filenameStyle": "basic"
}
```

| Key | Type | Values | Default |
|-----|------|--------|---------|
| `url` | string | Source URL | **Required** |
| `videoQuality` | string | `max / 4320 / 2160 / 1440 / 1080 / 720 / 480 / 360 / 240 / 144` | `1080` |
| `audioFormat` | string | `best / mp3 / ogg / wav / opus` | `mp3` |
| `downloadMode` | string | `auto / audio / mute` | `auto` |
| `filenameStyle` | string | `classic / pretty / basic / nerdy` | `basic` |
| `audioBitrate` | string | `320 / 256 / 128 / 96 / 64 / 8` | `128` |

### Platform-Specific Options

| Key | Platform | Values | Default |
|-----|----------|--------|---------|
| `youtubeVideoCodec` | YouTube | `h264 / av1 / vp9` | `h264` |
| `youtubeVideoContainer` | YouTube | `auto / mp4 / webm / mkv` | `auto` |
| `tiktokFullAudio` | TikTok | `true / false` | `false` |
| `allowH265` | TikTok | `true / false` | `false` |
| `convertGif` | Twitter | `true / false` | `true` |

## Response Types

### Success — `tunnel` or `redirect`

```json
{
    "status": "tunnel",
    "url": "https://cobalt-instance.com/tunnel/...",
    "filename": "video.mp4"
}
```

### Multiple items — `picker`

```json
{
    "status": "picker",
    "picker": [
        {"type": "video", "url": "https://...", "thumb": "https://..."},
        {"type": "photo", "url": "https://..."}
    ]
}
```

### Error

```json
{
    "status": "error",
    "error": {
        "code": "error.code.here",
        "context": {"service": "youtube", "limit": 100}
    }
}
```

## Kotlin Implementation

```kotlin
class CobaltExtractor : BaseExtractor() {
    companion object {
        private val API_URLS = listOf(
            "https://api.cobalt.tools",
            "https://cobalt-api.kwiatekmiki.com",
            "https://co.eepy.today",
            "https://cobalt.api.timelessnesses.me"
        )
    }

    override suspend fun extract(url: String): MediaInfo {
        var lastError: Exception? = null
        
        for (apiUrl in API_URLS) {
            try {
                val result = callCobaltApi(apiUrl, url)
                if (result != null) return result
            } catch (e: Exception) {
                lastError = e
            }
        }
        throw lastError ?: Exception("No cobalt server available")
    }

    private fun callCobaltApi(apiUrl: String, url: String): MediaInfo? {
        val jsonBody = """{"url": "$url", "videoQuality": "1080", "audioFormat": "mp3"}"""
        
        val request = Request.Builder()
            .url("$apiUrl/")
            .post(jsonBody.toRequestBody("application/json".toMediaType()))
            .header("Accept", "application/json")
            .build()

        val response = client.newCall(request).execute()
        val json = JsonParser.parseString(response.body?.string()).asJsonObject
        
        return when (json.get("status")?.asString) {
            "tunnel", "redirect" -> {
                val downloadUrl = json.get("url")!!.asString
                val filename = json.get("filename")?.asString ?: "download"
                MediaInfo(directUrl = downloadUrl, fileName = filename, ...)
            }
            "picker" -> {
                val firstVideo = json.getAsJsonArray("picker")
                    ?.get(0)?.asJsonObject
                MediaInfo(directUrl = firstVideo?.get("url")?.asString ?: "", ...)
            }
            else -> null
        }
    }
}
```

## Supported Platforms

| Platform | Video | Audio | Images | Notes |
|----------|-------|-------|--------|-------|
| TikTok | ✅ | ✅ | ✅ | Watermark-free, original audio |
| YouTube | ✅ | ✅ | ❌ | Up to 8K, HDR, codec selection |
| Instagram | ✅ | ✅ | ✅ | Reels, stories, posts |
| Facebook | ✅ | ❌ | ❌ | Public videos only |
| Twitter/X | ✅ | ✅ | ✅ | Multi-media posts |
| Reddit | ✅ | ✅ | ✅ | Including v.redd.it |
| Pinterest | ✅ | ✅ | ✅ | |
| SoundCloud | ❌ | ✅ | ❌ | |
| Vimeo | ✅ | ✅ | ❌ | |
| Bilibili | ✅ | ✅ | ❌ | |
| Dailymotion | ✅ | ✅ | ❌ | |
| Snapchat | ✅ | ✅ | ❌ | |

## Recommended Extraction Strategy

```
1. Cobalt API (primary) — most reliable, 20+ platforms
   └─ Try multiple mirrors for redundancy
2. HTTP direct (fast fallback) — platform-specific parsers
   └─ Works for direct links, some TikTok URLs
3. WebView (universal fallback) — renders full page
   └─ Works when HTTP is blocked
```

## Pitfalls

1. **Rate limiting** — Cobalt instances may rate-limit. Try multiple mirrors.
2. **Authentication required** — Some instances need `Authorization: Api-Key <key>` header.
3. **YouTube restrictions** — Some videos are geo-restricted or age-gated.
4. **Private/protected content** — Cobalt only works with publicly accessible URLs.
5. **Response parsing** — Always check `status` field first. Handle `error`, `picker`, and `tunnel` differently.
6. **SSL certificate errors on Xiaomi/Huawei** — Community-hosted Cobalt mirrors often have cert chain issues. Use a permissive OkHttp client (accepts all certs) for Cobalt API calls. See `android-networking` skill for the `HttpClientFactory` pattern. Error: `CertPathValidatorException: Trust anchor for certification path not found`.
7. **Non-JSON responses from mirrors** — Community mirrors may return HTML error pages (502, 503) or plain text instead of JSON. Always check `responseBody.trimStart().startsWith("{")` before parsing. Wrap `JsonParser.parseString()` in try-catch. A `MalformedJsonException` means the server returned an error page, not a Cobalt response — skip to the next mirror.
