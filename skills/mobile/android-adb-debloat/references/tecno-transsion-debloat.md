# TECNO / Transsion (HiOS) Debloat Reference

Source: GitHub Gist spectrMeltdown/4bf5bbb03172acabe02721fd4c8729e1 + verified on TECNO BG7 (Android 13).

## ⛔ CRITICAL — NEVER REMOVE

| Package | Why |
|---------|-----|
| `tech.palm.id` | **Disables the Settings app entirely.** Phone becomes unusable. |
| `com.skyroam.silverhelper` | Causes app permissions to keep resetting. (Not on all models.) |
| `com.scorpio.securitycom` | TECNO security framework. `pm uninstall` fails, `pm disable-user` blocked by SecurityException. Restrict background instead. |

## Adware / Ad-Serving Apps (safe to remove — these generate full-screen ads)

| Package | Description |
|---------|-------------|
| `com.antivirus` | Fake antivirus, adware |
| `com.clean.mix.junk` | Fake cleaner, adware |
| `com.cleanerflow.flow` | Fake cleaner, sends resident notifications |
| `albums.gallery.photo.folder.picasa.app.web.gallery` | Fake gallery, FCM ad notifications |
| `com.easyapp.tool.picture.video.recovery` | Fake recovery tool |
| `com.easyrecovery.photorecovery.filerecover.restoredata` | Fake recovery tool |
| `com.store.photo.reskab` | Adware disguised as photo app |
| `com.funbase.xradio` | Radio app, runs background ads |
| `com.hoffnung` | Suspicious adware |
| `com.na.te.lithium.tt.rise` | Random-name adware |
| `com.reallytek.wg` | Suspicious adware |
| `com.sh.smart.caller` | Fake caller ID, adware |
| `com.teclinknet.corelink.apps` | Adware |
| `com.yaohuo.xingyu` | Chinese adware |
| `com.mztech.seeta` | Adware |
| `com.cartoonphoto.toonapp.cartoonavatar` | Photo app with aggressive ads |
| `photoeditor.layout.collagemaker` | Editor with aggressive ads |
| `net.bat.store` | AHA games pop-ups |
| `com.hazling.creditotal` | Loan/adware app |
| `com.extra.universe.eto.turbo.vpn` | VPN with aggressive ads |
| `com.scorpio.securitycom` | Cannot uninstall, restrict background only |

## Screen Blackout Pattern

Adware apps create fullscreen overlay windows. When user interrupts/dismisses the ad, the overlay gets stuck → screen goes black, phone requires reboot. **Symptoms**: screen goes black after dismissing an ad, must reboot to recover.

**Fix**: Force-stop all adware apps first (`am force-stop <pkg>`), then uninstall. The force-stop breaks the stuck overlay immediately.

## Safe to Remove — TECNO/Transsion Bloatware

| Package | Description |
|---------|-------------|
| `com.transsion.phonemaster` | Phone optimization (Android manages fine) |
| `com.transsion.phonemanager` | Phone manager bloat |
| `com.transsion.kolun.assistant` | AI assistant (empty APK) |
| `com.transsion.kolun.aiservice` | AI service |
| `com.transsion.magazineservice.hios` | Lock screen magazine ads |
| `com.transsnet.store` | Palm store (insecure apps) |
| `com.transsion.tecnospot` | Promotional/trackers |
| `com.transsion.letswitch` | Phone clone tool |
| `com.transsion.healthlife` | Health app |
| `com.transsion.trancare` | Telemetry |
| `com.transsion.carlcare` | After-sales/trackers |
| `com.transsion.quicktools` | Quick tools panel |
| `com.transsion.smartpanel` | Game mode/side panel (collects data) |
| `com.transsion.magicfont` | Font changer (questionable permissions) |
| `com.transsion.magicshow` | Bad media player |
| `com.transsion.manualguide` | User manual |
| `com.transsion.repaircard` | Repair info |
| `com.transsion.statisticalsales` | Telemetry |
| `com.transsion.theme.icon` | Icon themes |
| `com.transsion.os.typeface` | Font manager |
| `com.transsion.scanningrecharger` | QR scanner |
| `com.transsion.videocallenhancer` | Video call (talks to ads) |
| `com.transsion.batterylab` | Battery telemetry |
| `com.transsion.hamal` | Logging service |
| `com.transsion.agingfunction` | Factory aging test |
| `com.transsion.chromecustomization` | Chrome theme customization |
| `com.transsion.plat.appupdate` | App update service |
| `com.transsion.fmradio` | FM Radio |
| `com.transsion.zahooc` | Peek proof/theft alert |
| `com.transsion.tabe` | Cloud sync for Tecno account |
| `com.transsion.dualapp` | Dual app clone |
| `com.idea.questionnaire` | OS questionnaire/surveys |

## Safe to Remove — MediaTek (TECNO uses MediaTek SoC)

| Package | Description |
|---------|-------------|
| `com.mediatek.callrecorder` | Call recorder |
| `com.mediatek.engineermode` | Engineer mode (debug) |
| `com.mediatek.mdmconfig` | MDM config |
| `com.mediatek.mdmlsample` | MDM sample |
| `com.mediatek.ygps` | GPS test tool |

## Safe to Remove — Other

| Package | Description |
|---------|-------------|
| `com.rlk.weathers` | Weather app with ads |
| `com.talpa.hibrowser` | HiOS browser with ads |
| `com.android.bluetoothmidiservice` | Bluetooth MIDI (rarely used) |
| `com.android.egg` | Android easter egg |
| `com.android.traceur` | System tracing |
| `com.google.android.onetimeinitializer` | One-time setup |
| `com.google.android.partnersetup` | Partner setup |
| `com.google.android.printservice.recommendation` | Print service (printing still works) |
| `com.android.providers.partnerbookmarks` | Partner bookmarks |

## Safe to Remove — Facebook Bloat

If user keeps Facebook main app, these can still be removed:
| Package | Description |
|---------|-------------|
| `com.facebook.lite` | Facebook Lite (duplicate) |
| `com.facebook.services` | Background services |
| `com.facebook.system` | Facebook system manager |
| `com.facebook.appmanager` | App manager |

## Safe to Remove — Google

| Package | Description |
|---------|-------------|
| `com.google.android.apps.youtube.music` | YouTube Music |
| `com.google.android.apps.turbo` | Health services |
| `com.google.android.apps.restore` | Restore tool |
| `com.google.android.apps.nbu.files` | Files by Google (runs background) |
| `com.google.android.apps.safetyhub` | Safety Hub |
| `com.google.android.apps.tachyon` | Google Meet |
| `com.google.android.contactkeys` | Contact Keys |
| `com.google.android.videos` | Google Play Movies |
| `com.google.android.feedback` | Feedback |
| `com.google.android.gms.location.history` | Location history |
| `com.google.android.googlequicksearchbox` | Google App/Discover (~200MB RAM) |
| `com.google.android.marvin.talkback` | Accessibility |
| `com.google.android.projection.gearhead` | Android Auto |
| `com.google.android.apps.googleassistant` | Google Assistant |
| `com.google.android.adservices.api` | Ad services (disable, not uninstall) |
| `com.google.mainline.adservices` | Ad services module (disable) |
| `com.google.mainline.telemetry` | Telemetry (disable) |
| `com.google.android.sdksandbox` | SDK sandbox (disable) |

## NEVER REMOVE — Generic Android

These apply to ALL brands:
- `com.android.systemui` — System UI
- `com.android.settings` — Settings
- `com.android.phone` — Phone/dialer
- `com.android.providers.telephony` — Telephony provider
- `com.android.vending` — Play Store
- `com.google.android.gms` — Google Play Services
- `com.google.android.gsf` — Google Services Framework

## Optimization Commands (post-debloat)

```bash
# Restrict background for remaining heavy apps
for pkg in com.facebook.katana com.google.android.youtube com.google.android.apps.messaging; do
  adb shell "cmd appops set $pkg RUN_IN_BACKGROUND deny; cmd appops set $pkg RUN_ANY_IN_BACKGROUND deny"
done

# Disable ad tracking
adb shell settings put secure limit_ad_tracking 1

# Force-stop before uninstall (breaks stuck overlays)
adb shell am force-stop <package>
```

## Notes

- `pm uninstall --user 0` removes for current user only. Factory reset restores everything.
- Restore: `adb shell cmd package install-existing <package>`
- `pm clear --cache-only` is extremely slow via ADB (100+ apps = timeout). User should clear cache from Settings > Storage.
- TECNO BG7 tested: 70+ apps removed, 13GB freed, 367MB more RAM available.
