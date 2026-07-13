/**
 * Complete Cloudflare Worker example with FCM push, KV storage, Cron Triggers.
 * 
 * Setup:
 * 1. Create KV namespace → bind as WOW_KV
 * 2. Add FIREBASE_SERVICE_ACCOUNT secret (JSON from Firebase Console)
 * 3. Add Cron Trigger: */1 * * * * (every 1 min)
 * 4. Grant Service Account "Firebase Cloud Messaging API Admin" role in GCP IAM
 */

// ─── FCM Auth ───────────────────────────────────────────

function base64ToUint8Array(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

async function getAccessToken(env) {
  const sa = JSON.parse(env.FIREBASE_SERVICE_ACCOUNT);
  const now = Math.floor(Date.now() / 1000);

  const header = btoa(JSON.stringify({ alg: "RS256", typ: "JWT" }))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const payload = btoa(JSON.stringify({
    iss: sa.client_email,
    scope: "https://www.googleapis.com/auth/firebase.messaging",
    aud: "https://oauth2.googleapis.com/token",
    iat: now, exp: now + 3600,
  })).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const pemBody = sa.private_key.replace(/[REDACTED PRIVATE KEY]/, "").replace(/\s/g, "");
  const keyBytes = base64ToUint8Array(pemBody);

  const key = await crypto.subtle.importKey(
    "pkcs8", keyBytes,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["sign"]
  );

  const enc = new TextEncoder();
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(`${header}.${payload}`));
  const sigB64 = btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const resp = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${header}.${payload}.${sigB64}`,
  });
  const data = await resp.json();
  if (!data.access_token) throw new Error(`OAuth2: ${data.error}`);
  return data.access_token;
}

async function sendFCM(deviceToken, title, body, data, env) {
  const accessToken = await getAccessToken(env);
  const sa = JSON.parse(env.FIREBASE_SERVICE_ACCOUNT);
  const resp = await fetch(
    `https://fcm.googleapis.com/v1/projects/${sa.project_id}/messages:send`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          token: deviceToken,
          notification: { title, body },
          data: data || {},
          android: { priority: "high" },
        },
      }),
    }
  );
  if (!resp.ok) console.error("FCM failed:", resp.status, await resp.text());
  return resp.ok;
}

async function broadcastToTokens(env, title, body, data) {
  const tokensJson = await env.WOW_KV.get("fcm_tokens");
  if (!tokensJson) return { sent: 0, failed: 0, reason: "no tokens" };
  const tokens = JSON.parse(tokensJson);
  let sent = 0, failed = 0;
  const dead = [];
  for (const token of tokens) {
    try {
      if (await sendFCM(token, title, body, data, env)) sent++;
      else { failed++; dead.push(token); }
    } catch (e) { failed++; dead.push(token); }
  }
  if (dead.length > 0) {
    await env.WOW_KV.put("fcm_tokens", JSON.stringify(tokens.filter(t => !dead.includes(t))));
  }
  return { sent, failed };
}

// ─── Token Registration ─────────────────────────────────

async function registerToken(env, token) {
  const tokensJson = await env.WOW_KV.get("fcm_tokens");
  const tokens = tokensJson ? JSON.parse(tokensJson) : [];
  if (!tokens.includes(token)) {
    tokens.push(token);
    await env.WOW_KV.put("fcm_tokens", JSON.stringify(tokens));
  }
  return tokens.length;
}

// ─── HTTP Handler ───────────────────────────────────────

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

    if (url.pathname === "/register-token" && request.method === "POST") {
      const { token } = await request.json();
      const count = await registerToken(env, token);
      return Response.json({ ok: true, totalDevices: count }, { headers: corsHeaders });
    }

    if (url.pathname === "/test-fcm") {
      const result = await broadcastToTokens(env, "Test", "FCM works!", { type: "test" }, env);
      return Response.json({ ok: true, ...result }, { headers: corsHeaders });
    }

    return Response.json({ error: "Not found" }, { status: 404, headers: corsHeaders });
  },

  async scheduled(event, env, ctx) {
    // Your change detection + notification logic here
    console.log("Cron triggered");
  },
};
