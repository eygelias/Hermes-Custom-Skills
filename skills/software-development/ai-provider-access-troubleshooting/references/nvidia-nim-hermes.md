# NVIDIA NIM in Hermes

Session-derived setup notes for configuring NVIDIA NIM as a Hermes model provider, including free-preview filtering for the desktop model picker.

## Known-good config

```bash
# Store secret in active profile (default profile shown)
printf '\nNVIDIA_API_KEY=YOUR_NVAPI_KEY\n' >> "$HOME/AppData/Local/hermes/.env"

hermes config set model.provider nvidia
hermes config set model.base_url https://integrate.api.nvidia.com/v1
hermes config set model.default nvidia/nemotron-3-super-120b-a12b
hermes config set model.context_length 1048576
rm -f "$HOME/AppData/Local/hermes/provider_models_cache.json"
```

Verify:

```bash
hermes chat -q 'Responde solo: hola desde NVIDIA' --provider nvidia -m nvidia/nemotron-3-super-120b-a12b
```

Observed successful response: `hola desde NVIDIA`.

## Model discovery behavior

`https://integrate.api.nvidia.com/v1/models` with Bearer auth returned 121 model IDs for the user's key, including NVIDIA, Meta, Mistral, Qwen, DeepSeek, OpenAI OSS, Z.ai, MiniMax, Moonshot, StepFun, and utility models.

Hermes `provider_model_ids('nvidia', force_refresh=True)` normally merges curated fallback entries with live `/models` results. Clear `provider_models_cache.json` when the desktop picker still shows old entries.

## Free Endpoint / preview filtering

NVIDIA's API model list does **not** expose pricing/free metadata. NVIDIA Build does expose the UI filter:

```text
https://build.nvidia.com/models?filters=nimType%3Anim_type_preview&page=1
```

In browser/a11y text, this appears as `Free Endpoint`. In page data, matching resources carry a `nimType` label with unresolved value `nim_type_preview` and often attribute `PREVIEW=true`.

Observed extraction result from pages 1–4:

- `Free Endpoint` resources on NVIDIA Build: 77
- Free endpoint rows that were also in `/v1/models` and had `playgroundType=chat`: 50
- Other free endpoint rows were non-chat services (TTS, rerank, embeddings, video, safety, biology, etc.) or page slugs that needed API-ID normalization.

For Hermes model picker, use only the 50 chat/API-available IDs. Tested working through Hermes:

```text
nvidia/nemotron-3-super-120b-a12b -> ok nemotron
deepseek-ai/deepseek-v4-flash -> ok deepseek
openai/gpt-oss-20b -> ok gptoss
```

## Picker override pattern

To show **only** NVIDIA free-preview chat models in the picker, do not edit Hermes core. Use a user model-provider override:

```text
$HERMES_HOME/plugins/model-providers/nvidia/plugin.yaml
$HERMES_HOME/plugins/model-providers/nvidia/__init__.py
```

Minimal `plugin.yaml`:

```yaml
name: nvidia-free-preview-provider
kind: model-provider
version: 1.0.0
description: NVIDIA NIM free preview chat models only
author: local
```

In `__init__.py`, subclass/instantiate `ProviderProfile` named `nvidia` and override `fetch_models()` to return the curated free-preview chat IDs. User plugins override bundled provider profiles on name collision, so this survives Hermes updates better than patching the install tree.

Important: the built-in `_PROVIDER_MODELS["nvidia"]` curated entries are still prepended by `provider_model_ids()`, but they are also free-preview chat models in the current set. If future curated entries become non-free, update the local override or upstream logic.

After writing the override:

```bash
rm -f "$HOME/AppData/Local/hermes/provider_models_cache.json"
# then /reset or restart Hermes Desktop/TUI
```

## Re-runnable helper

Use `scripts/nvidia_free_preview_models.py` to re-fetch NVIDIA Build free endpoint pages, intersect with `/v1/models`, keep chat rows, and print a Python tuple suitable for the provider override.

## Caveat wording

Use: “NVIDIA Build marks these as Free Endpoint / preview and your `NVIDIA_API_KEY` can call these API IDs.”

Avoid: “permanently free forever.” NVIDIA can change preview/free availability or quota limits account-side.
