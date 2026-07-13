# OpenAI/Hermes from Venezuela with Proton VPN

Session summary for future troubleshooting.

## Situation

User in Venezuela used Hermes Desktop with OpenAI OAuth (ChatGPT Plus). OpenAI auth showed connected, but model calls without VPN returned:

```text
HTTP 403 — HTML error page (title not found)
```

OpenAI support docs checked during session:

- ChatGPT supported countries page did not list Venezuela.
- OpenAI API supported countries page did not list Venezuela and said unsupported locations may be blocked/suspended.
- API and ChatGPT billing are separate; ChatGPT Plus does not include API credits.

## Practical explanation given

- Hermes OpenAI OAuth still sends model calls to OpenAI endpoints.
- If egress IP is Venezuela, OpenAI can reject request with `403`.
- OAuth “connected” only means login token exists; it does not guarantee model endpoint access from current IP.

## Proton split tunnel finding

Initial Proton mode included only `Hermes.exe`. Process inspection showed Hermes Desktop also spawned Python processes:

```text
C:\Users\ELY\AppData\Local\hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe
C:\Users\ELY\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe
C:\Users\ELY\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\python.exe
```

Same-session egress probe from Hermes runtime showed Proton/Miami when VPN route was active:

```text
IP: 134.82.68.70
City: Miami
Country: US
Org: AS208172 Proton AG
```

Durable lesson: with Electron/Python desktop agents, include-only split tunnels can miss child processes. Proton **exclusion mode** (all traffic via VPN except excluded apps) is safer for routing Hermes and its children through VPN.

## Recommended user-facing steps

1. Use Proton split tunnel exclusion mode.
2. Exclude apps that should not use VPN.
3. Do not exclude Hermes.
4. Fully quit/reopen Hermes after changing VPN rules.
5. If `403` persists, change Proton server (USA normal, Spain, or another supported country) and reconnect OpenAI OAuth with VPN active.

## Leaderboard sources discussed

- Artificial Analysis Intelligence Index: composite benchmark; agents/coding/science/general; good for capability.
- LMArena/Chatbot Arena: anonymous pairwise human votes; Elo/Bradley-Terry-style ranking; good for conversational preference.
- OpenRouter Rankings: real usage/tokens/spend; good for practical Hermes/OpenRouter model choice, not pure quality.
