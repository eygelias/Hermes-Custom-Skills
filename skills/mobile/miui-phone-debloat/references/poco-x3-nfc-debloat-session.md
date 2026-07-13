# POCO X3 NFC Debloat Session - 2026-06-21

## Device Info
- **Model:** POCO X3 NFC (M2007J20CG)
- **Android:** 12 (SDK 31)
- **MIUI:** Unknown version
- **Connection:** Wireless ADB (192.168.100.249)

## Apps Removed (64 total)

### System Bloatware (46 apps)
```
com.miui.msa.global           # MIUI Ads
com.miui.analytics            # Telemetry
com.miui.bugreport            # Bug reporting
com.miui.weather2             # Weather
com.miui.compass              # Compass
com.miui.fm                   # FM Radio
com.miui.fmservice            # FM Radio service
com.miui.cleaner              # Cleaner
com.miui.yellowpage           # Yellow pages
com.miui.touchassistant       # Touch assistant
com.miui.extraphoto           # Extra photos
com.miui.misound              # Sound
com.miui.player               # Music player
com.miui.videoplayer          # Video player
com.miui.freeform             # Floating windows
com.xiaomi.barrage            # Barrage
com.xiaomi.discover           # Discover
com.xiaomi.glgm               # Games
com.xiaomi.midrop             # Mi Drop
com.xiaomi.payment            # Payment
com.xiaomi.powerchecker       # Power checker
com.xiaomi.simactivate.service # SIM activation
com.mi.healthglobal           # Health
com.milink.service            # Mi Link
com.miui.cloudbackup          # Cloud backup
com.miui.cloudservice         # Cloud service
com.miui.micloudsync          # Cloud sync
com.miui.hybrid               # Hybrid apps
com.miui.hybrid.accessory     # Hybrid accessory
com.miui.phrase               # Phrases
com.miui.daemon               # Daemon
com.miui.notification         # Notifications
com.miui.wmsvc                # WM service
com.miuix.editor              # Editor
com.miui.audiomonitor         # Audio monitor
com.google.android.apps.googleassistant    # Google Assistant
com.google.android.apps.turbo             # Photo enhancer
com.google.android.apps.wellbeing         # Digital Wellbeing
com.google.android.apps.subscriptions.red # Google One
com.google.android.apps.restore           # Restore
com.google.android.gms.location.history   # Location history
com.google.android.marvin.talkback        # TalkBack
com.google.android.tts                    # TTS
com.google.android.feedback               # Feedback
com.google.android.printservice.recommendation  # Print
com.google.android.projection.gearhead    # Android Auto
```

### Third-Party Apps Removed (18 apps)
```
com.ea.game.pvzfree_row                    # Plants vs Zombies
com.rovio.baba                             # Angry Birds
com.halfbrick.dantheman                    # Dan the Man
com.geargames.warlegends.rts.strategy.game # War Legends
com.tiltingpoint.warhammer                 # Warhammer
com.farlightgames.samo.gp                  # SAMO Game
com.funstick.gold.finfer.metaldetector     # Metal Detector
com.g2g.www                                # G2G
com.amazon.appmanager                      # Amazon App Manager
cn.wps.xiaomi.abroad.lite                  # WPS Office
com.uptodown                               # Uptodown store
com.medianet.oficinamovil                  # Oficina Móvil
com.gars.recargasrbau                      # Recargas RBAU
com.offline.bible                          # Offline Bible
com.suno.android                           # Suno AI Music
com.miui.android.fashiongallery            # MIUI Fashion Gallery
com.miui.mediaeditor                       # MIUI Media Editor
com.duokan.phone.remotecontroller          # Mi Remote
```

### Google Apps Removed Later (7 apps)
```
com.google.android.apps.bard               # Google Bard
com.google.android.apps.magazines          # Google Magazines
com.google.android.apps.walletnfcrel       # Google Wallet
com.google.android.apps.youtube.creator    # YouTube Studio
com.google.android.apps.youtube.music      # YouTube Music
com.google.ar.core                         # ARCore
com.google.ar.lens                         # Google Lens
```

### Gallery Apps Removed (2 apps)
```
com.miui.gallery                           # MIUI Gallery
com.miui.mediaeditor                       # Gallery Editor (reinstalled then removed)
```

## Apps Kept (User Requested)
- Facebook Lite, TikTok, Discord, ProtonVPN
- Digitel App, BNC, BDV Digital, Banesco, Mercantil
- Binance, Bybit, PayPal, Zinli, VeMonedero
- Notes MIUI, Screen Recorder, Cuenta Xiaomi, Escáner QR
- YouTube, Google Maps, Gmail

## Default Apps Set
- **Photos/Videos:** Google Photos (com.google.android.apps.photos)

## Key Learnings
1. ADB pairing on Windows requires Python script (can't pipe input)
2. MIUI has extra install restrictions (INSTALL_FAILED_USER_RESTRICTED)
3. Xiaomi Gallery Editor AI features require Android 12L+ for latest versions
4. Samsung Gallery doesn't work on non-Samsung phones
5. Xiaomi AI photo features are cloud-based, not on-device
