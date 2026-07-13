# Pre-Build Testing with yt-dlp CLI

Before building any APK, verify extraction works from the command line.

## Setup
```bash
pip install yt-dlp
```

## Test Commands

### Facebook
```bash
yt-dlp --no-warnings --no-check-certificates -f best \
  --print "%(title)s | %(format)s | %(ext)s" \
  "https://www.facebook.com/share/r/XXXXX/"
```

### YouTube (with anti-bypass)
```bash
yt-dlp --no-warnings --no-check-certificates -f best \
  --extractor-args "youtube:player_client=android" \
  --print "%(title)s | %(format)s | %(ext)s" \
  "https://youtube.com/shorts/XXXXX"
```

### TikTok
```bash
yt-dlp --no-warnings --no-check-certificates -f best \
  --print "%(title)s | %(format)s | %(ext)s" \
  "https://vt.tiktok.com/XXXXX/"
```

### Audio extraction
```bash
yt-dlp --no-warnings --no-check-certificates -f bestaudio \
  --print "%(title)s | %(ext)s" \
  "https://www.facebook.com/share/r/XXXXX/"
```

## Download Latest yt-dlp Binary for Android

```bash
mkdir -p app/src/main/assets/yt-dlp
curl -L -o app/src/main/assets/yt-dlp/yt-dlp \
  "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
echo "2026.6.9" > app/src/main/assets/yt-dlp/version.txt
ls -lh app/src/main/assets/yt-dlp/
```

## FFmpeg Kit AAR Download

FFmpeg Kit was archived April 2025. Download from Appodeal mirror:
```bash
curl -L -o app/libs/ffmpeg-kit.aar \
  "https://artifactory.appodeal.com/appodeal-public/com/arthenica/ffmpeg-kit-full-gpl/6.0-2.LTS/ffmpeg-kit-full-gpl-6.0-2.LTS.aar"
```
Size: ~70MB. Adds ~75MB to APK.
