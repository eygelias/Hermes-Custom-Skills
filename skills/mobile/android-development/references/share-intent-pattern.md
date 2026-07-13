# Share Intent Handler Pattern (Android)

Receives URLs/content from any app's "Share" button. Used for downloaders, translators, note-takers, etc.

## Architecture

```
User taps Share → Android share sheet → Your app's transparent Activity → Process → Finish
```

## Manifest Setup

```xml
<!-- Transparent activity that handles share intents -->
<activity
    android:name=".ShareActivity"
    android:exported="true"
    android:theme="@style/Theme.Transparent"
    android:launchMode="singleTop"
    android:noHistory="true"
    android:excludeFromRecents="true"
    android:taskAffinity="">

    <!-- Receive shared text (URLs) from ANY app -->
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="text/plain" />
    </intent-filter>

    <!-- Receive shared images -->
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="image/*" />
    </intent-filter>

    <!-- Receive shared videos -->
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="video/*" />
    </intent-filter>
</activity>
```

## Transparent Theme

```xml
<style name="Theme.Transparent" parent="Theme.Material3.Dark.NoActionBar">
    <item name="android:windowIsTranslucent">true</item>
    <item name="android:windowBackground">@android:color/transparent</item>
    <item name="android:windowNoTitle">true</item>
    <item name="android:windowContentOverlay">@null</item>
    <item name="android:backgroundDimEnabled">true</item>
    <item name="android:statusBarColor">@android:color/transparent</item>
    <item name="android:navigationBarColor">@color/surface_dark</item>
</style>
```

## Kotlin Handler

```kotlin
private fun handleIntent(intent: Intent?) {
    when (intent?.action) {
        Intent.ACTION_SEND -> {
            val type = intent.type ?: ""
            when {
                type.startsWith("text/") -> {
                    val url = intent.getStringExtra(Intent.EXTRA_TEXT) ?: ""
                }
                type.startsWith("image/") -> {
                    val uri = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        intent.getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
                    } else {
                        @Suppress("DEPRECATION")
                        intent.getParcelableExtra(Intent.EXTRA_STREAM)
                    }
                }
            }
        }
    }
}
```

## Key Pitfalls

- `android:noHistory="true"` + `android:excludeFromRecents="true"` keeps the share handler out of recents
- `android:taskAffinity=""` prevents it from grouping with the main app task
- Always extract URL from `Intent.EXTRA_TEXT` — some apps put the URL in EXTRA_TEXT, others in EXTRA_SUBJECT
- Use `ExtractorFactory` pattern to find URLs in text that may contain surrounding description text
- For Android 13+ parcelable extras, use the typed `getParcelableExtra(key, Class)` overload

## "Quick Mode" Pattern

For downloaders: if user has a default format configured, start download immediately without showing UI. Show a Toast, start a foreground service, and finish the activity after 2-3 seconds. This keeps the user in their social media app without interruption.
