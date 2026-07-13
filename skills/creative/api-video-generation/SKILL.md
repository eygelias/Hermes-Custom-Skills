---
name: api-video-generation
description: "Set up and use API-backed realistic video generation in Hermes without local model installs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [video-generation, api, fal, replicate, runway, kling, luma, minimax, xai, hermes]
    category: creative
---

# API Video Generation

Use this when the user wants realistic video generation by prompt using an API provider (FAL, Replicate, Runway, Kling, Luma, MiniMax, xAI, etc.), especially inside Hermes.

## Core rule

Do **not** assume local generation. If the user says they have an API/model or wants API-backed generation, avoid local installs unless explicitly requested.

Do not install ComfyUI, comfy-cli, FFmpeg, local models, CUDA/PyTorch stacks, or change PATH just to enable API video generation. Configure the API provider/tooling first.

## Hermes setup path

1. Check whether Hermes has `video_gen` available/enabled.
2. If disabled, enable it with `hermes tools enable video_gen`.
3. Identify provider and expected credential name from current Hermes docs or provider plugin docs.
   - Built-in provider pattern: `video_gen.provider` in `config.yaml` selects provider.
   - Model selection may use `video_gen.model`, `video_gen.<provider>.model`, or provider env var such as `<PROVIDER>_VIDEO_MODEL`.
4. Set only minimal config, e.g. provider/model, not unrelated local tooling.
5. Add API key only if the user provides it. Store credentials in Hermes `.env` or provider auth system, never in SKILL.md.
6. Tell user that enabling a new toolset often needs a fresh session (`/reset`) before `video_generate` appears in the current tool list.
7. Verify with `hermes tools list` and a cheap/short test generation if the tool is available.

## Provider questions

Ask for exactly what is missing, not a menu. Example:

> Pásame el API key de FAL o dime el nombre exacto del proveedor que ya pagaste. No voy a instalar modelos locales.

## Pitfalls

- User may say “instala lo necesario” but mean API integration, not local inference. Confirm provider/API intent before installing.
- ComfyUI skills are still useful for Comfy Cloud workflows, but local ComfyUI setup is a different path from Hermes `video_gen` API providers.
- Hardware checks are only relevant for local generation. They are unnecessary noise for pure API generation.
- If a provider plugin is missing, prefer adding/configuring a Hermes video-gen provider plugin over installing local model runtimes.

## Verification

Good completion evidence:

```text
hermes tools list  -> video_gen enabled
hermes config show -> video_gen.provider/model set as intended
fresh session      -> video_generate tool visible
small test         -> returns video URL/path or clear provider/API error
```

If the user asks to undo setup, reverse only changes made: disable toolsets changed, remove config/env keys added, uninstall packages installed, delete temporary files, and verify each removal.