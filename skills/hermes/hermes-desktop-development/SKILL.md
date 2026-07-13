---
name: hermes-desktop-development
description: "Patterns and internals of the Hermes Electron desktop app — i18n, themes, settings, components."
version: 1.0.0
author: hermes
metadata:
  hermes:
    tags: [hermes, desktop, electron, i18n, themes, settings]
---

# Hermes Desktop Development

Patterns for modifying the Hermes Electron desktop app (`apps/desktop/`).

## Project Structure

```
apps/desktop/
├── src/
│   ├── app/               # Feature pages (settings, chat, skills, cron, etc.)
│   ├── components/        # Shared UI components (shadcn-based)
│   ├── i18n/              # Internationalization system
│   ├── themes/            # Theme engine (VS Code theme compatible)
│   ├── store/             # Nanostores state management
│   ├── lib/               # Utilities, icons, haptics
│   └── main.tsx           # Entry point
├── electron/              # Electron main process
└── release/               # Built output (win-unpacked, etc.)
```

Tech stack: React + TypeScript + Vite + Nanostores + TanStack Query + shadcn/ui + Tailwind CSS.

## i18n (Internationalization)

Full guide: `references/desktop-i18n.md`

System lives at `src/i18n/`. Uses `defineLocale()` pattern — partial overrides merged onto English base. 4 locales currently: en, zh, zh-hant, ja.

Adding a locale: create `<locale>.ts` with `defineLocale()`, update `types.ts` Locale union, `languages.ts` LOCALE_OPTIONS + aliases, `catalog.ts` registry.

## Settings System

Settings pages live at `src/app/settings/`. Each section is a component:
- `appearance-settings.tsx` — themes, mode, translucency, tool view, pets
- `model-settings.tsx` — model config, fallback providers
- `gateway-settings.tsx` — local/remote gateway, auth
- `providers-settings.tsx` — provider accounts, API keys
- `notifications-settings.tsx` — native notification toggles
- `config-settings.tsx` — config.yaml editor
- `mcp-settings.tsx` — MCP server management

Primitives: `primitives.tsx` exports `SettingsContent`, `SectionHeading`, `ListRow`.

Field labels/descriptions: `constants.tsx` has `FIELD_LABELS` and `FIELD_DESCRIPTIONS` — typed config field metadata that gets translated via `defineFieldCopy()` in locale files.

## Theme Engine

Themes are VS Code-compatible. Can install from VS Code Marketplace via `installVscodeThemeFromMarketplace()`. User themes stored separately from built-in ones.

## Adding Translation Keys

1. Add to `Translations` interface in `types.ts`
2. Add English string in `en.ts`
3. Override in each locale file (`ja.ts`, `zh.ts`, etc.)
4. Use `useI18n()` hook: `const { t } = useI18n()` then `t.settings.appearance.title`

## Pitfalls

- `defineLocale()` does deep merge — objects recurse, strings/arrays/functions replace entirely
- Template functions (e.g., `count => \`${count} items\``) must be complete — can't partial-translate
- `LOCALE_OPTIONS.name` is endonym (native name), `englishName` is search-only
- Locale files are strictly typed against `src/i18n/types.ts`; stale extra keys in `src/i18n/es.ts` or other locales break `tsc -b`. Compare with `types.ts` + `en.ts`, remove obsolete keys, and verify with `npm run build`. See `references/desktop-i18n-build-failures.md`.
- When the user keeps a locale bundle/zip for future application (e.g. a Spanish UI pack), patch the source file **and** the bundle copy, create a backup zip, then verify the live project with `npm run build`; `npm run pack` can still be blocked by a running Desktop process (`EBUSY`) and is not required to prove TypeScript/i18n correctness.
- Built app at `release/win-unpacked/resources/app.asar` — changes need rebuild
- Desktop app binary: `C:\Users\ELY\AppData\Local\hermes\hermes-agent\apps\desktop\`
- Electron `Object has been destroyed` from hidden BrowserWindow timers usually means a delayed callback touched a destroyed `BrowserWindow`/`webContents`; guard both `window.isDestroyed()` and `webContents.isDestroyed()` and swallow teardown races in one helper. See `references/electron-destroyed-window.md`.
- `npm run pack`/`hermes desktop --force-build` can fail with `EBUSY ... v8_context_snapshot.bin` if Desktop is still open; close/kill `Hermes.exe`, then retry. Build success from `npm run build` still verifies TypeScript/i18n fixes.
