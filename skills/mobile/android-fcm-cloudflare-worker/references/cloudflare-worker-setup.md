# Cloudflare Worker Setup for FCM

## KV Namespace Setup
1. Cloudflare Dashboard → Workers & Pages → KV
2. "Create a namespace" → name it (e.g. `wow-kv`)
3. Copy the Namespace ID

## Bind KV to Worker
1. Worker → Settings → Variables → KV Namespace Bindings → Add binding
2. Variable name: `WOW_KV` (this becomes `env.WOW_KV` in code)
3. Select the KV namespace

## Add Secrets
1. Worker → Settings → Variables → Environment Variables → Add variable
2. Name: `FIREBASE_SERVICE_ACCOUNT`
3. Value: entire JSON content of the Service Account key file
4. Mark as 🔒 Encrypted
5. Save and deploy

## Cron Trigger
1. Worker → Settings → Triggers → Cron Triggers → Add
2. Expression: `*/1 * * * *` (every 1 minute — minimum on free plan)
3. Note: free plan minimum is 1 hour for Cron Triggers in some cases

## Common Issues
- KV binding must be set BEFORE deploying code that uses it
- Secrets are encrypted and not visible after saving
- Redeploying Worker code does NOT clear KV data
- But re-creating the Worker DOES lose bindings and secrets
- Cron Trigger minimum interval: 1 min (can vary by plan)
