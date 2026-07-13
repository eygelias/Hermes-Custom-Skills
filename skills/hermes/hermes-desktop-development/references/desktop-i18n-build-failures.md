# Desktop i18n build failures

## Symptom

`hermes desktop --force-build` or `npm run build` fails in `apps/desktop` with TypeScript errors like:

```text
src/i18n/es.ts:169:5 - error TS2353: Object literal may only specify known properties, and 'dismiss' does not exist...
src/i18n/es.ts:706:7 - error TS2353: ... 'or' does not exist...
src/i18n/es.ts:991:5 - error TS2561: ... 'tokensK' does not exist...
src/i18n/es.ts:2251:7 - error TS2353: ... 'shortcutSuffix' does not exist...
```

## Cause

Locale override files (`src/i18n/es.ts`, `ja.ts`, `zh.ts`, etc.) are typed against `Translations` from `src/i18n/types.ts`. Extra/stale keys that are not in the interface fail `tsc -b`.

This often happens after upstream i18n schema changes: English/base and `types.ts` move forward, but a locale file still carries removed keys.

## Fix pattern

1. Compare failing locale block against `src/i18n/types.ts` and `src/i18n/en.ts`.
2. Remove keys not present in `Translations`.
3. If a replacement key exists, rename to the current key.
   - Example: old clarify keys `send/back/shortcutSuffix` were replaced by `continueLabel`.
4. Run focused verification:

```bash
cd apps/desktop
npm run build
```

Expected output includes:

```text
✓ built
✓ assert-dist-built: dist/index.html + assets present
```

## Packaging blocker

If build passes but `npm run pack` / `hermes desktop --force-build` fails with:

```text
EBUSY: resource busy or locked, unlink '...release\\win-unpacked\\v8_context_snapshot.bin'
```

Hermes Desktop is still running from `release/win-unpacked`. Close Desktop or kill `Hermes.exe`, then retry packaging. This is not an i18n error.
