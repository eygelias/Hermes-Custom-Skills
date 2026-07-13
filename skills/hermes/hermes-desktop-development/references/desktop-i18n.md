# Hermes Desktop i18n System

Location: `apps/desktop/src/i18n/`

## Architecture

- **Base locale**: `en.ts` (~2229 lines, ~94KB) — full `Translations` interface
- **Override locales**: `ja.ts`, `zh.ts`, `zh-hant.ts` — use `defineLocale()` which merges partial overrides on top of English
- **Type**: `types.ts` — `Locale` union type, full `Translations` interface (~1800 lines)
- **Catalog**: `catalog.ts` — `TRANSLATIONS: Record<Locale, Translations>` registry
- **Language picker**: `languages.ts` — `LOCALE_OPTIONS` array (id, name, englishName, configValue), `LOCALE_ALIASES` map for OS locale normalization
- **Context**: `context.tsx` — React context providing `useI18n()` hook with `t` (translations) and `isSavingLocale`

## Adding a New Locale (step by step)

1. **Create `<locale>.ts`**:
   ```ts
   import { defineFieldCopy } from '@/app/settings/field-copy'
   import { defineLocale } from './define-locale'
   export const es = defineLocale({ /* partial overrides only */ })
   ```
   Untranslated keys fall back to English automatically.

2. **Update `types.ts`**: Add to `Locale` union type, e.g. `'en' | 'zh' | 'zh-hant' | 'ja' | 'es'`

3. **Update `languages.ts`**:
   - Add to `LOCALE_OPTIONS`: `{ id: 'es', name: 'Español', englishName: 'Spanish', configValue: 'es' }`
   - Add aliases to `LOCALE_ALIASES`: `es: 'es', 'es-es': 'es', es_es: 'es', 'es-mx': 'es', es_mx: 'es'`

4. **Update `catalog.ts`**: Import and add to `TRANSLATIONS` record

## Key Translation Sections in `Translations` Interface

- `common` — ~40 button/label strings (Apply, Save, Cancel, etc.)
- `fileMenu` — context menu items (reveal, copy path, rename, delete)
- `boot` — startup/loading/error messages, failure recovery
- `notifications` — toasts, native OS notifications, voice errors
- `titlebar` — sidebar toggles, haptics, search
- `keybinds` — keyboard shortcut categories + action labels
- `language` — language picker labels
- `settings.nav` — sidebar navigation labels
- `settings.notifications` — notification type toggles
- `settings.sections` — section headings (Model, Chat, Appearance, etc.)
- `settings.appearance` — theme, mode, translucency, tool view, pet settings
- `settings.fieldLabels` — config field labels (uses `defineFieldCopy()`)
- `settings.fieldDescriptions` — config field descriptions
- `settings.about` — version, updates, branch info
- `settings.gateway` — local/remote gateway, auth, diagnostics
- `settings.mcp` — MCP server management
- `settings.sessions` — archived chat management
- `settings.chat`, `settings.model`, `settings.workspace`, `settings.safety`, `settings.memory`, `settings.voice`, `settings.advanced` — per-section settings
- `tools` — tool display names (ToolTitleKey union: terminal, read_file, etc.)
- `commandCenter` — command palette, theme install
- `sidebar` — session list, new session, projects
- `composer` — input area, attachments, model picker, voice
- `chat` — message display, tool calls, approvals, diffs

## `defineLocale()` Merge Behavior

```ts
// define-locale.ts
function mergeTranslations<T>(base: T, overrides: TranslationOverride<T> | undefined): T
```

- **Objects**: deep-merge (recurse into keys)
- **Strings/primitives**: override replaces entirely
- **Arrays**: override replaces entirely
- **Functions** (template strings): override replaces entirely — must provide complete function

## Pitfalls

- String interpolation functions must be complete: `count => \`${count} items\`` — can't partial-translate
- `fieldLabels`/`fieldDescriptions` use `defineFieldCopy()` helper from `@/app/settings/field-copy`
- `LOCALE_OPTIONS.name` = endonym (native name, shown in picker); `englishName` = search-only
- Built app at `release/win-unpacked/resources/app.asar` — source changes need `npm run build`
- Desktop source path on this machine: `C:\Users\ELY\AppData\Local\hermes\hermes-agent\apps\desktop\`
