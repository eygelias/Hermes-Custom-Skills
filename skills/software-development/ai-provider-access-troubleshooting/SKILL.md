---
name: ai-provider-access-troubleshooting
description: Troubleshoot AI provider access failures in Hermes and other clients, especially 403/regional blocks, OAuth vs API differences, VPN split tunneling, and model leaderboard selection.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ai-providers, hermes, openai, oauth, api, vpn, split-tunnel, troubleshooting]
---

# AI Provider Access Troubleshooting

Use when user reports model calls failing in Hermes, ChatGPT OAuth, OpenAI API, OpenRouter, or another AI provider; especially `HTTP 403`, unsupported-country errors, regional blocks, VPN/proxy behavior, or confusion between ChatGPT Plus and API billing.

## Fast triage

1. Identify client surface: Hermes Desktop/TUI, browser ChatGPT, OpenAI API key, OpenRouter, provider OAuth.
2. Identify auth type:
   - ChatGPT Plus / OpenAI OAuth: browser-style subscription credentials.
   - OpenAI API: separate platform billing and API key; Plus does not include API credits.
   - Aggregator (OpenRouter/Nous/etc.): separate provider with its own routing and country/payment rules.
3. For current facts, check provider support docs before making claims about country availability or policy.
4. If `403` appears only without VPN, treat regional/IP block as primary suspect.
5. Verify egress IP from the same runtime/process when possible, not only from the browser.

## Hermes + VPN split tunnel on Windows

Hermes Desktop is not only `Hermes.exe`. It launches Python child processes that may make model/API requests.

When using Proton VPN split tunneling:

- Prefer **exclusion mode**: send all traffic through VPN except apps user explicitly excludes. This catches Hermes child processes automatically.
- If using **include-only mode**, include all relevant executables, not just `Hermes.exe`:
  - `C:\Users\ELY\AppData\Local\hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe`
  - `C:\Users\ELY\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe`
  - `C:\Users\ELY\AppData\Roaming\uv\python\cpython-*-windows-x86_64-none\python.exe`
- After changing split tunnel rules, fully quit and relaunch Hermes so child processes inherit the route.
- If OAuth login opens a browser, that browser may also need VPN temporarily for login/verification.

## Regional/provider guidance

- `HTTP 403` from OpenAI with a Venezuela IP usually means OpenAI rejected the request based on location/IP or policy.
- ChatGPT Plus does not override country support restrictions.
- OpenAI API and ChatGPT subscriptions are billed separately and may share similar country-support restrictions.
- For users in unsupported regions, recommend a provider/aggregator that works for them (often OpenRouter) as primary, with OpenAI OAuth/API only when VPN is active and compliant with provider terms.
- Avoid promising VPN bypass safety. Explain practical behavior and account-risk caveat clearly.

## Model leaderboard guidance

For choosing models, do not rely on one leaderboard:

- **Artificial Analysis Intelligence Index**: best for capability. Composite benchmark over agents, coding, scientific reasoning, and general tasks. Also compares cost/speed/token use.
- **LMArena / Chatbot Arena**: best for human preference and conversational feel. Anonymous pairwise battles; ranking from Elo/Bradley-Terry-style preference data.
- **OpenRouter Rankings**: best for practical availability/popularity/cost in Hermes/OpenRouter. Based on real usage/token/spend data, not pure intelligence.

Recommended decision flow:

1. Use Artificial Analysis for raw quality.
2. Use OpenRouter for availability/price in user's actual provider.
3. Use LMArena for conversational preference check.

## Z.ai / GLM setup in Hermes

Use this path when the user wants GLM models in Hermes, especially a separate free-trial/coding-plan profile:

1. Create or clone a profile instead of overwriting the default model if the user wants to test safely:
   ```bash
   hermes profile create glm --clone
   ```
2. Configure the profile for Z.ai GLM Coding endpoint:
   ```bash
   hermes -p glm config set model.default "glm-5.2"
   hermes -p glm config set model.provider "zai"
   hermes -p glm config set model.base_url "https://api.z.ai/api/coding/paas/v4"
   hermes -p glm config set model.context_length 1000000
   ```
3. Store the key in that profile's `.env`, not only the default profile:
   ```bash
   printf '\nGLM_API_KEY=YOUR_KEY_HERE\n' >> "$HOME/AppData/Local/hermes/profiles/glm/.env"
   ```
4. Verify with a real chat call:
   ```bash
   hermes -p glm chat -q "di hola"
   ```

If `/models` works but `/chat/completions` returns `HTTP 429` with `Insufficient balance or no resource package. Please recharge.`, the key is syntactically valid but the Z.ai account has no active quota/trial/resource package. Fix is account-side activation or recharge, not Hermes config.

## NVIDIA NIM setup in Hermes

Use this path when the user provides an NVIDIA `nvapi-...` key and wants NVIDIA/NIM models in the Hermes model picker:

1. Store the key in the active profile `.env` using `NVIDIA_API_KEY`:
   ```bash
   printf '\nNVIDIA_API_KEY=YOUR_KEY_HERE\n' >> "$HOME/AppData/Local/hermes/.env"
   ```
2. Configure Hermes for the built-in NVIDIA provider:
   ```bash
   hermes config set model.provider nvidia
   hermes config set model.base_url https://integrate.api.nvidia.com/v1
   hermes config set model.default nvidia/nemotron-3-super-120b-a12b
   hermes config set model.context_length 1048576
   ```
3. Clear provider model cache when the picker still shows old entries:
   ```bash
   rm -f "$HOME/AppData/Local/hermes/provider_models_cache.json"
   ```
4. Verify with a real call:
   ```bash
   hermes chat -q "Responde solo: hola desde NVIDIA" --provider nvidia -m nvidia/nemotron-3-super-120b-a12b
   ```

NVIDIA's `/v1/models` endpoint lists models accessible to the key, but does not include pricing/free metadata. If the user asks for “only free,” use NVIDIA Build's `Free Endpoint` filter (`filters=nimType%3Anim_type_preview`) as the free/preview source, then intersect those rows with `/v1/models` and keep only `playgroundType=chat` for Hermes. In the observed workflow, that reduced 121 API-listed models to 50 free preview chat models. See `references/nvidia-nim-hermes.md` and runnable helper `scripts/nvidia_free_preview_models.py`.

To make the desktop picker show only free NVIDIA chat models without editing Hermes core, create a user model-provider override under `$HERMES_HOME/plugins/model-providers/nvidia/` whose `ProviderProfile.fetch_models()` returns the curated free-preview chat list. User plugins override bundled provider profiles, so this is update-safe compared with patching `plugins/model-providers/nvidia` in the install tree. Clear `provider_models_cache.json` and restart/reset Hermes after writing the plugin.

## Pitfalls

- Do not say “Hermes is connected to ChatGPT, so network is fine.” OAuth connected only proves login succeeded; model calls still go to provider endpoints and can be blocked by IP.
- Do not diagnose split tunneling from the visible app list alone. Electron apps commonly spawn helper/child processes.
- Do not equate “most used” with “best model.” Usage rankings can be driven by price/free tiers.
- Do not confuse OpenRouter GLM availability with free Z.ai trial access. `z-ai/glm-5.2` on OpenRouter may be paid even when Z.ai/BigModel offers a short trial or coding-plan quota.
- Do not store one-off IPs/server names as durable truth; only capture the diagnostic pattern.

## References

- `references/openai-venezuela-proton-hermes.md` — session notes: OpenAI 403 from Venezuela, Proton split tunnel modes, Hermes child processes, and leaderboard sources.
- `references/zai-glm-hermes.md` — GLM 5.2 profile setup, endpoints, and quota/balance error interpretation.
- `references/nvidia-nim-hermes.md` — NVIDIA NIM provider setup, model discovery behavior, cache refresh, free-preview filtering, and local provider override pattern.
- `scripts/nvidia_free_preview_models.py` — re-fetch NVIDIA Build Free Endpoint pages, intersect with `/v1/models`, and print the free-preview chat tuple for a picker override.