---
name: hermes-messaging-gateway
description: "Configure and troubleshoot Hermes Gateway messaging platforms, especially WhatsApp/WhatsApp Cloud, Telegram, and delivery targets."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [hermes, gateway, messaging, whatsapp, telegram, setup, troubleshooting]
---

# Hermes Messaging Gateway

Use this skill when the user asks to connect Hermes to messaging platforms (WhatsApp, Telegram, Discord, Slack, Signal, etc.), run the gateway, make cron jobs deliver to chat apps, or troubleshoot gateway delivery.

Authoritative docs still win: check `hermes-agent` skill and live docs when commands or platform requirements may have changed. This skill captures practical setup workflow and pitfalls from real sessions.

## Default workflow

1. Identify platform and path:
   - WhatsApp quick/personal: Baileys bridge (`hermes whatsapp`) with QR scan.
   - WhatsApp production/business: Cloud API (`hermes whatsapp-cloud`) with Meta Business + webhook URL.
   - Other platforms: `hermes gateway setup` unless platform has a dedicated helper.
2. Configure access control before starting gateway. For WhatsApp Baileys, write phone numbers with country code and no `+` or trunk `0`.
   - Venezuelan `+58 0412...` becomes `58412...`.
3. Pair/auth the platform.
4. Start gateway and verify with real status/log output:
   - `hermes gateway run` for foreground/manual run.
   - `hermes gateway status` to verify.
   - On Windows, `hermes gateway install` can install a login item/Startup fallback if Scheduled Task elevation is skipped.
5. Test from the actual messaging app, then inspect gateway logs if no reply.

## WhatsApp Baileys bridge checklist

Use for personal/quick setup, not official Business API.

```bash
# Configure mode/allowlist via wizard
hermes whatsapp

# Or set env directly before pairing
WHATSAPP_ENABLED=true
WHATSAPP_MODE=self-chat
WHATSAPP_ALLOWED_USERS=58412XXXXXXX
```

Then scan from phone:

1. WhatsApp → Ajustes/Settings.
2. Dispositivos vinculados / Linked Devices.
3. Vincular dispositivo / Link a Device.
4. Scan QR.

Session credentials live under the Hermes home WhatsApp session directory (`~/.hermes/whatsapp/session` or profile-equivalent). Treat like a password.

## Windows / Hermes Desktop QR visibility pitfall

If the user says they cannot see the QR:

- Background process output is not the same as the visible in-app terminal. Use the background process log/poll output to inspect whether the QR was printed.
- Terminal-rendered QR can be off-screen, garbled, or hard to scan in TUI/desktop contexts. Prefer generating a PNG QR on the Desktop when guiding a non-dev user.
- If a previous pairing process is waiting, kill it before starting a new pairing attempt to avoid rotating QRs.

Minimal temporary PNG method if needed:

```bash
cd "$HERMES_HOME/hermes-agent/scripts/whatsapp-bridge"  # or actual source path
npm install qrcode --no-fund --no-audit --progress=false
# create a temporary Node pairing script that uses Baileys + qrcode.toFile()
# save QR to ~/Desktop/hermes-whatsapp-qr.png, then remove script and uninstall qrcode after pairing
```

Do not leave temporary helper scripts/dependencies behind unless the user asks for a permanent tool.

## Troubleshooting WhatsApp bridge

See `references/whatsapp-baileys-windows.md` for a condensed Windows/Desktop pairing runbook and verification signals.

- `ERR_MODULE_NOT_FOUND: Cannot find package '@whiskeysockets/baileys'` while bridge says dependencies exist usually means incomplete `node_modules`. Fix by running `npm install` in `scripts/whatsapp-bridge`, then rerun pairing.
- If gateway prints bridge decode/Unicode errors but then `Bridge ready (status: connected)`, verify with `hermes gateway status` before treating it as fatal.
- For self-chat mode, user must message their own "Mensaje para ti / Message Yourself" chat.
- If no response, check `~/.hermes/logs/gateway.log` and platform adapter logs, then verify `WHATSAPP_ALLOWED_USERS` normalization.

## User guidance preference

For Carlos/Ely-style setup flows: act directly when safe, give one current step plus screenshot/capture request. Avoid multiple-choice branching unless the platform choice genuinely changes required credentials or risk.
