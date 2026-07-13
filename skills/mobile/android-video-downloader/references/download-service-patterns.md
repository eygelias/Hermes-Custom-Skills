# Download Service Patterns for yt-dlp Android

## Complete DownloadService Template

```kotlin
class DownloadService : Service() {
    companion object {
        const val EXTRA_URL = "extra_url"
        const val EXTRA_CONVERT_AUDIO = "extra_convert_audio"
        const val ACTION_DOWNLOAD_COMPLETE = "com.app.DOWNLOAD_COMPLETE"
        const val ACTION_DOWNLOAD_FAILED = "com.app.DOWNLOAD_FAILED"
    }

    private suspend fun processDownload(url: String, convertToAudio: Boolean) {
        try {
            // 1. Init
            YoutubeDL.getInstance().init(this)

            // 2. Update (best effort)
            try { YoutubeDL.getInstance().updateYoutubeDL(this) } catch (_: Exception) {}

            // 3. Build request
            val timestamp = System.currentTimeMillis()
            val outputTemplate = "${downloadDir.absolutePath}/temp_${timestamp}.%(ext)s"
            
            val request = YoutubeDLRequest(url)
            request.addOption("-o", outputTemplate)
            request.addOption("--no-warnings")
            request.addOption("--no-check-certs")
            request.addOption("--no-playlist")
            request.addOption("-f", "best")

            // YouTube bypass
            if (url.contains("youtube.com") || url.contains("youtu.be")) {
                request.addOption("--extractor-args", "youtube:player_client=android")
                request.addOption("--geo-bypass")
                request.addOption("--force-ipv4")
            }

            // 4. Execute
            YoutubeDL.getInstance().execute(request) { progress, _, _ ->
                updateNotification("Descargando… ${progress.toInt()}%", progress.toInt())
            }

            // 5. Find file
            val file = downloadDir.listFiles()
                ?.filter { it.lastModified() >= timestamp - 10000 }
                ?.maxByOrNull { it.lastModified() }

            // 6. Convert if audio
            val finalFile = if (convertToAudio) {
                val audioFile = File(downloadDir, "audio_${timestamp}.mp3")
                FFmpegKit.execute("-i \"${file}\" -vn -acodec libmp3lame -q:a 2 \"${audioFile}\"")
                file?.delete()
                audioFile
            } else {
                file
            }

            // 7. Show completion
            notificationHelper.cancelProgressNotification()
            notificationHelper.showDownloadComplete(title, finalFile.absolutePath)

        } catch (e: YoutubeDLException) {
            notificationHelper.cancelProgressNotification()
            notificationHelper.showDownloadError("Error: ${e.message?.take(80)}")
        } finally {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }
    }
}
```

## Key Patterns

### File Discovery After Download
yt-dlp may change extensions. Always use prefix matching:
```kotlin
val file = downloadDir.listFiles()
    ?.filter { it.lastModified() >= timestamp - 10000 && it.name.startsWith("temp_") }
    ?.maxByOrNull { it.lastModified() }
```

### Progress Callback Signature
```kotlin
{ progress: Float, etaInSeconds: Long, line: String -> ... }
```
Three parameters, NOT two. Compilation error if wrong.

### Notification Lifecycle
```kotlin
// Progress: use PROGRESS_NOTIFICATION_ID
notificationManager.notify(PROGRESS_ID, progressNotif)

// Completion: cancel progress first, use different ID
notificationManager.cancel(PROGRESS_ID)
notificationManager.notify(COMPLETION_ID, completionNotif)

// Service stop: use REMOVE not DETACH
stopForeground(STOP_FOREGROUND_REMOVE)
```

### Audio Conversion with FFmpeg Kit
```kotlin
// MP3
"-i \"$in\" -vn -acodec libmp3lame -q:a 2 \"$out\""
// AAC
"-i \"$in\" -vn -acodec aac -b:a 192k \"$out\""
// WAV
"-i \"$in\" -vn -acodec pcm_s16le \"$out\""
// OGG
"-i \"$in\" -vn -acodec libvorbis -q:a 4 \"$out\""
```
