# OpenRouter Free Models (as of 2026-06)

## The `openrouter/free` Router

Special model ID that automatically selects from available free models based on the request's requirements. Use as delegation model for automatic fallback across all free models.

```bash
hermes config set delegation.provider openrouter
hermes config set delegation.model openrouter/free
```

## Top Free Models Available

| Model | Context | Best for |
|-------|---------|----------|
| Owl Alpha | 1M | Agentic workloads, tool use, code gen |
| NVIDIA Nemotron 3 Ultra | 1M | Deep research, coding agents, orchestration |
| Poolside Laguna M.1 | 262K | Complex software engineering (coding agent) |
| NVIDIA Nemotron 3 Super | 1M | Multi-token prediction, fast inference |
| OpenAI gpt-oss-120b | 131K | Configurable reasoning, tool use |
| Poolside Laguna XS.2 | 262K | Efficient coding agent |
| OpenAI gpt-oss-20b | 131K | Lower-latency inference |
| Google Gemma 4 31B | 262K | Multimodal (text+image), 140+ languages |
| NVIDIA Nemotron 3 Nano 30B | 256K | Small, compute-efficient |
| Cohere North Mini Code | 256K | Code generation, terminal tasks |
| NVIDIA Nemotron 3 Nano Omni | 256K | Multimodal (text+image+video+audio) |

## Notes

- Free models may log prompts/completions for model improvement
- Rate limits apply but are generous for delegation use
- Model availability changes — `openrouter/free` handles this automatically
- Source: https://openrouter.ai/collections/free-models
- Update this file periodically as new free models are added
