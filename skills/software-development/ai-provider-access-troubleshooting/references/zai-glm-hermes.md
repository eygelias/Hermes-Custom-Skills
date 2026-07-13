# Z.ai / GLM in Hermes

## When to use

User wants to run GLM 5.x / GLM 5.2 in Hermes, especially via the free Z.ai/BigModel trial or GLM Coding Plan.

## Known-good Hermes profile setup

Safer than replacing the default model: make a dedicated profile.

```bash
hermes profile create glm --clone
hermes -p glm config set model.default "glm-5.2"
hermes -p glm config set model.provider "zai"
hermes -p glm config set model.base_url "https://api.z.ai/api/coding/paas/v4"
hermes -p glm config set model.context_length 1000000
```

Store the API key in the profile env:

```bash
printf '\nGLM_API_KEY=YOUR_KEY_HERE\n' >> "$HOME/AppData/Local/hermes/profiles/glm/.env"
```

Then verify with:

```bash
hermes -p glm chat -q "di hola"
```

## Endpoints

Z.ai docs distinguish two OpenAI-compatible API bases:

- Coding-plan endpoint: `https://api.z.ai/api/coding/paas/v4`
- General/resource-package endpoint: `https://api.z.ai/api/paas/v4`

For GLM Coding Plan/free-trial coding usage, prefer the coding endpoint.

## Diagnostic pattern

`GET /models` can succeed even when chat calls fail. If model listing works but chat returns:

```text
HTTP 429
Insufficient balance or no resource package. Please recharge.
code: 1113
```

Interpretation: API key is accepted and endpoint/model are reachable, but account has no active trial/quota/resource package for inference. Fix is in Z.ai/BigModel account/subscription/quota, not Hermes config.

## OpenRouter caveat

OpenRouter lists GLM models, including `z-ai/glm-5.2`, but that does not mean free Z.ai trial quota is available through OpenRouter. Check OpenRouter pricing live before telling user it is free.
