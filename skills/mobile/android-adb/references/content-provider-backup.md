# ADB Content Provider Backup Commands

Since `adb backup` is deprecated on Android 12+, use content providers to export data.

## Contacts
```bash
# List all contact names
adb shell content query --uri content://com.android.contacts/contacts --projection display_name

# Count contacts
adb shell content query --uri content://com.android.contacts/contacts --projection display_name | wc -l
```

## SMS Messages
```bash
# Export all SMS with address, body, date
adb shell content query --uri content://sms --projection address:body:date

# Count messages
adb shell content query --uri content://sms | wc -l
```

## Call Log
```bash
adb shell content query --uri content://call_log/calls --projection number:name:date:duration:type
```

## Calendar Events
```bash
adb shell content query --uri content://com.android.calendar/events --projection title:dtstart:dtend:description
```

## Notes (Google Keep backup)
Google Keep data is synced to cloud — no local content provider. User should verify Keep sync is on.

## Files (direct pull)
```bash
# Photos/Videos
adb pull /sdcard/DCIM/ ./backup/DCIM/

# Downloads
adb pull /sdcard/Download/ ./backup/Download/

# WhatsApp media
adb pull /sdcard/WhatsApp/Media/ ./backup/WhatsApp_Media/

# Telegram media
adb pull /sdcard/Telegram/ ./backup/Telegram/
```

## Important Notes
- `adb backup` still works on older Android but requires on-device confirmation tap
- Content provider exports are READ-ONLY and don't modify device data
- On MSYS/git-bash, wrap `adb shell` commands in quotes to prevent path mangling:
  ```bash
  adb shell "content query --uri content://sms --projection address:body:date"
  ```
- Date values in SMS are Unix timestamps in milliseconds
