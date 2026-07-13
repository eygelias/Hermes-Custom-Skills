# HTML Companion App for FCM Push Sender

Single-file HTML app that calls Worker's `/test-fcm` endpoint to send custom push notifications. Can be wrapped in a WebView APK for mobile use.

## HTML Features
- Dark theme matching the main app
- Emoji tray with categories (collapsible) and search
- Title + body inputs
- Send history in localStorage
- Direct fetch to Worker endpoint

## Wrapping in WebView APK

### Minimal Project Structure
```
WowPushSender/
├── app/
│   ├── src/main/
│   │   ├── assets/index.html          ← the HTML file
│   │   ├── java/.../MainActivity.kt   ← WebView wrapper
│   │   ├── res/
│   │   │   ├── drawable/ic_launcher_foreground.xml
│   │   │   ├── mipmap-anydpi-v26/ic_launcher.xml
│   │   │   ├── values/colors.xml
│   │   │   └── values/themes.xml
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
├── build.gradle.kts
├── settings.gradle.kts
└── local.properties
```

### MainActivity.kt
```kotlin
package com.wowpush.app

import android.os.Bundle
import android.webkit.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private lateinit var wv: WebView
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        wv = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            settings.allowFileAccess = true
            settings.allowContentAccess = true
            webViewClient = WebViewClient()
            webChromeClient = WebChromeClient()
        }
        setContentView(wv)
        wv.loadUrl("file:///android_asset/index.html")
    }
    override fun onBackPressed() {
        if (wv.canGoBack()) wv.goBack() else super.onBackPressed()
    }
}
```

### AndroidManifest.xml Pitfalls
- MUST use `AppCompatActivity` + Material theme (not `@android:style/Theme.NoTitleBar` — crashes on newer Android)
- NEEDS `android:usesCleartextTraffic="true"` for Worker HTTPS
- NEEDS `INTERNET` permission

### build.gradle.kts Dependencies
```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
}
```

### Custom Icon
- `res/drawable/ic_launcher_foreground.xml` — vector drawable (notification bell, signal waves, etc.)
- `res/mipmap-anydpi-v26/ic_launcher.xml` — adaptive icon referencing foreground + background color
- `res/values/colors.xml` — background color for icon

### settings.gradle.kts
Must include `dependencyResolutionManagement` with `repositories` block:
```kotlin
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
```

## Emoji Tray Pitfall
Splitting emoji strings with regex corrupts multi-byte characters. Use explicit arrays per category instead of `string.split(regex)`.

## CSS Overflow Pitfall
Emoji tray can overflow the card container on mobile. Fix:
- Add `overflow:hidden` to `.card` container
- Add `overflow-x:hidden` to `.emoji-tray`
- Add `word-break:break-all` to `.emoji-tray` as safety net

## Category Click Not Filtering
When clicking a category button, must pass the filtered emoji list (not ALL) to the render function and scroll tray to top:
```javascript
b.onclick = () => {
  cc = c.id;
  const l = cc === 'all' ? ALL : E[cc] || ALL;
  ren(l);
  $('tray').scrollTop = 0;
};
```

## Worker Endpoint
The HTML calls: `https://<worker>.workers.dev/test-fcm?title=...&body=...`
Returns: `{ ok: true, sent: N, failed: M }`
