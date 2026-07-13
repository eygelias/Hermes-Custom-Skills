# POCO X3 NFC Debloat Session — 2026-06-21

Device: POCO X3 NFC (M2007J20CG), Android 12, MIUI
Connection: Wireless ADB (192.168.100.249)

## System Apps Removed (46)
com.miui.msa.global, com.miui.analytics, com.miui.bugreport, com.miui.weather2,
com.miui.compass, com.miui.fm, com.miui.fmservice, com.miui.cleaner,
com.miui.yellowpage, com.miui.touchassistant, com.miui.extraphoto, com.miui.misound,
com.miui.player, com.miui.videoplayer, com.miui.freeform, com.xiaomi.barrage,
com.xiaomi.discover, com.xiaomi.glgm, com.xiaomi.midrop, com.xiaomi.payment,
com.xiaomi.powerchecker, com.xiaomi.simactivate.service, com.mi.healthglobal,
com.milink.service, com.miui.cloudbackup, com.miui.cloudservice, com.miui.micloudsync,
com.miui.hybrid, com.miui.hybrid.accessory, com.miui.phrase, com.miui.daemon,
com.miui.notification, com.miui.wmsvc, com.miuix.editor, com.miui.audiomonitor,
com.google.android.apps.googleassistant, com.google.android.apps.turbo,
com.google.android.apps.wellbeing, com.google.android.apps.subscriptions.red,
com.google.android.apps.restore, com.google.android.gms.location.history,
com.google.android.marvin.talkback, com.google.android.tts,
com.google.android.feedback, com.google.android.printservice.recommendation,
com.google.android.projection.gearhead

## Third-Party Apps Removed (18)
com.ea.game.pvzfree_row (Plants vs Zombies), com.rovio.baba (Angry Birds),
com.halfbrick.dantheman (Dan the Man), com.geargames.warlegends.rts.strategy.game,
com.tiltingpoint.warhammer, com.farlightgames.samo.gp, com.funstick.gold.finfer.metaldetector,
com.g2g.www, com.amazon.appmanager, cn.wps.xiaomi.abroad.lite, com.uptodown,
com.medianet.oficinamovil, com.gars.recargasrbau, com.offline.bible, com.suno.android,
com.miui.android.fashiongallery, com.miui.mediaeditor, com.duokan.phone.remotecontroller

## Kept (user explicitly protected)
Facebook Lite, TikTok, Discord, ProtonVPN, Digitel, BNC, BDV, Banesco, Mercantil,
Binance, Bybit, PayPal, Zinli, VeMonedero, Notes MIUI, Screen Recorder, Xiaomi Account,
QR Scanner, YouTube, Google Maps, Gmail

## Failed
com.xiaomi.mipicks — SecurityException, protected by system

## Result
36 third-party apps remaining. Phone stable after reboot.
