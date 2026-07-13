# WhatsApp Baileys setup notes

Session-derived workflow for connecting Hermes to WhatsApp using the Baileys bridge on Windows/Hermes Desktop.

## Durable lessons

- Normalize Venezuelan numbers by removing `+` and trunk `0`: `+58 0412 245 7529` → `584122457529`.
- `hermes whatsapp` may print the QR in the background process output, not in the user-visible terminal pane. If user says "no lo veo", inspect/present the process output or generate a PNG QR.
- Incomplete bridge dependency installs can leave `node_modules` present while `@whiskeysockets/baileys` is missing. Run `npm install` inside `scripts/whatsapp-bridge` and retry.
- A temporary helper can save the Baileys `qr` string to a PNG using npm package `qrcode`. Clean up helper script and dependency after pairing.
- `hermes gateway install` on Windows can fall back to Startup folder when UAC/Scheduled Task elevation is skipped; this is acceptable for non-admin users.

## Verification signals

Successful pairing/gateway output includes lines like:

```text
✅ WhatsApp connected. Pairing complete.
[Whatsapp] Bridge ready (status: connected)
✓ Gateway is running
```

Test path: ask user to open WhatsApp → "Mensaje para ti" / "Message Yourself" and send `hola hermes`.
