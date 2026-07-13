# WebView-Based Content Extraction (Android)

Social media platforms (Facebook, Instagram, TikTok, YouTube) block plain HTTP requests with anti-bot measures. The reliable approach is to use Android WebView to render pages and extract media URLs via JavaScript injection.

## Architecture: Dual Extraction Strategy

```
Share Intent → Extract URL
  ├─ Try HTTP extraction (fast, ~1s)
  │   └─ OkHttp + HTML parsing + regex
  │   └─ Works for: direct links, simple pages, TikTok (sometimes)
  └─ Fallback: WebView extraction (reliable, ~5-15s)
      └─ Renders page with JavaScript
      └─ Intercepts network requests for media URLs
      └─ Injects JS to find <video>, og:video, etc.
      └─ Works for: Facebook, Instagram, YouTube, most platforms
```

## WebViewExtractor Implementation

```kotlin
class WebViewExtractor(private val context: Context) {
    companion object {
        private const val TIMEOUT_SECONDS = 15L
    }

    suspend fun extract(url: String): MediaInfo = withContext(Dispatchers.Main) {
        val deferred = CompletableDeferred<MediaInfo>()
        val handler = Handler(Looper.getMainLooper())

        val webView = WebView(context.applicationContext).apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                userAgentString = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"
            }

            webViewClient = object : WebViewClient() {
                private val foundUrls = mutableListOf<String>()

                // Intercept resource requests to capture media URLs
                override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
                    val reqUrl = request?.url?.toString() ?: return null
                    if (isVideoUrl(reqUrl)) foundUrls.add(reqUrl)
                    return super.shouldInterceptRequest(view, request)
                }

                override fun onPageFinished(view: WebView?, url: String?) {
                    // Check captured URLs first
                    val capturedVideo = foundUrls.firstOrNull { isVideoUrl(it) }
                    if (capturedVideo != null) {
                        deferred.complete(createMediaInfo(url!!, capturedVideo))
                        return
                    }

                    // Inject JavaScript to find media in DOM
                    val js = """
                        (function() {
                            var result = {videos: [], images: [], title: '', thumbnail: ''};
                            
                            // Check <video> elements
                            document.querySelectorAll('video').forEach(v => {
                                if (v.src) result.videos.push(v.src);
                                if (v.currentSrc) result.videos.push(v.currentSrc);
                                v.querySelectorAll('source').forEach(s => {
                                    if (s.src) result.videos.push(s.src);
                                });
                            });
                            
                            // Check og:video meta tags
                            document.querySelectorAll('meta[property*="og:video"]').forEach(m => {
                                var c = m.getAttribute('content');
                                if (c) result.videos.push(c);
                            });
                            
                            // Regex scan page HTML for video URLs
                            var html = document.documentElement.outerHTML;
                            var patterns = [
                                /https?:\/\/[^\s"']+\.mp4[^\s"']*/g,
                                /https?:\/\/[^\s"']*fbcdn[^\s"']*\.mp4[^\s"']*/g,
                                /https?:\/\/[^\s"']*tiktokcdn[^\s"']*/g
                            ];
                            patterns.forEach(p => {
                                var m = html.match(p);
                                if (m) result.videos.push(...m);
                            });
                            
                            // og:image + og:title
                            var ogImg = document.querySelector('meta[property="og:image"]');
                            if (ogImg) result.images.push(ogImg.content);
                            var ogTitle = document.querySelector('meta[property="og:title"]');
                            result.title = ogTitle ? ogTitle.content : document.title;
                            
                            // Deduplicate
                            result.videos = [...new Set(result.videos.filter(v => 
                                v && !v.includes('.js') && !v.includes('.css')))];
                            
                            return JSON.stringify(result);
                        })();
                    """.trimIndent()

                    view?.evaluateJavascript(js) { json ->
                        // Parse result, find best video URL, complete deferred
                    }
                }
            }
        }

        webView.loadUrl(url)

        try {
            withTimeout(TimeUnit.SECONDS.toMillis(TIMEOUT_SECONDS + 5)) { deferred.await() }
        } finally {
            webView.stopLoading()
            webView.destroy()
        }
    }

    private fun isVideoUrl(url: String): Boolean {
        val lower = url.lowercase()

        // Exclude non-media file types (CRITICAL — fonts, assets cause false positives)
        val excludedExtensions = listOf(
            ".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
            ".woff", ".woff2", ".ttf", ".eot", ".otf",  // Fonts!
            ".json", ".xml", ".html", ".htm", ".php",
            ".ico", ".manifest", ".appcache"
        )
        for (ext in excludedExtensions) {
            if (lower.contains(ext)) return false
        }

        // Exclude common CDN/asset paths
        val excludedPaths = listOf(
            "/assets/", "/static/", "/css/", "/js/", "/fonts/", "/images/",
            "cdnjs.", "jsdelivr.", "unpkg.", "googleapis."
        )
        for (path in excludedPaths) {
            if (lower.contains(path)) return false
        }

        // Must contain video indicators
        val videoIndicators = listOf(
            ".mp4", ".webm", ".m3u8", ".ts",
            "video", "fbcdn", "tiktokcdn", "videoplayback",
            "media", "stream", "clip"
        )
        return videoIndicators.any { lower.contains(it) }
    }
}
```

## Key Pitfalls

1. **WebView must run on Main thread** — Use `withContext(Dispatchers.Main)` in the suspend function. The WebView is created with `context.applicationContext` so it works from a Service.

2. **Always destroy WebView** — Use `try/finally` to call `webView.stopLoading()` and `webView.destroy()`. Leaked WebViews cause memory issues.

3. **Timeout is critical** — Pages may never finish loading (infinite scroll, lazy loading). Use `withTimeout` + a handler-based timeout in `onPageStarted`.

4. **`shouldInterceptRequest` captures network-level URLs** — This catches video URLs that load via XHR/fetch, not just those in the HTML. Facebook videos especially load this way.

5. **JavaScript regex for URL extraction** — Scan `document.documentElement.outerHTML` with patterns for `.mp4`, platform CDN domains. Filter out `.js`, `.css` false positives.

6. **URL cleaning** — Social media URLs often contain `\\u002F` (escaped `/`) and `\\u0026` (escaped `&`). Always `.replace("\\u002F", "/").replace("\\u0026", "&")` before using.

7. **Extraction timeout in Service** — In DownloadService, wrap extraction in `withTimeout(30_000L)` to prevent indefinite hanging. Catch `TimeoutCancellationException` separately for a clear error message.

8. **Custom URL scheme crash (CRITICAL)** — Social media sites redirect to app deep links (`fb://`, `instagram://`, `tiktok://`, `snssdk://`). WebView cannot load these and throws `net::ERR_UNKNOWN_URL_SCHEME`. **Always override `shouldOverrideUrlLoading` to block custom schemes:**
   ```kotlin
   override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
       val url = request?.url?.toString() ?: return false
       if (url.startsWith("fb://") || url.startsWith("instagram://") ||
           url.startsWith("tiktok://") || url.startsWith("snssdk://") ||
           url.startsWith("whatsapp://") || url.startsWith("tg://")) {
           return true // Block
       }
       return false // Allow http/https
   }
   ```
   Without this, the WebView fails silently when Facebook/Instagram tries to redirect to the native app.

## Platform-Specific Notes

| Platform | HTTP Works? | WebView Works? | Notes |
|----------|------------|----------------|-------|
| TikTok | Sometimes | ✅ | Short URLs (vm.tiktok.com) redirect to full URLs |
| YouTube | ❌ | Partial | Heavy JS, streaming data encrypted. May need yt-dlp |
| Instagram | ❌ | ✅ | Requires JS rendering, og:meta extraction works |
| Facebook | ❌ | ✅ | `shouldInterceptRequest` catches fbcdn.net video URLs |
| Twitter/X | Sometimes | ✅ | video.twimg.com URLs captured in network requests |
| Direct links | ✅ | N/A | .mp4/.webm URLs work directly |

## Saving Downloads (MediaStore)

```kotlin
// Android 10+ uses MediaStore
val collection = MediaStore.Video.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
val values = ContentValues().apply {
    put(MediaStore.MediaColumns.DISPLAY_NAME, fileName)
    put(MediaStore.MediaColumns.MIME_TYPE, "video/mp4")
    put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/YourAppName")
}
val uri = contentResolver.insert(collection, values)
uri?.let { contentResolver.openOutputStream(it)?.use { out -> inputStream.copyTo(out) } }
```

## FFmpeg Conversion (when FFmpeg Kit available)

```kotlin
// Extract audio from video
FFmpegKit.execute("-i \"$input\" -vn -acodec libmp3lame -q:a 2 \"$output\"")

// Convert video format
FFmpegKit.execute("-i \"$input\" -c:v mpeg4 -c:a mp3 \"$output\"")  // to AVI
FFmpegKit.execute("-i \"$input\" -c copy \"$output\"")               // remux (fast)
```
