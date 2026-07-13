// Cloudflare Worker: API Proxy + FCM Push + Cron Trigger
// Requires: KV binding (WOW_KV), env var (FIREBASE_SERVICE_ACCOUNT)

const API_BASE = "http://your-internal-api.com";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

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
  const pemBody = sa.private_key.replace(/-----.*-----/g, "").replace(/\s/g, "");
  const key = await crypto.subtle.importKey("pkcs8", base64ToUint8Array(pemBody),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key,
    new TextEncoder().encode(`${header}.${payload}`));
  const jwt = `${header}.${payload}.${btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")}`;
  const resp = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion=${jwt}`,
  });
  return (await resp.json()).access_token;
}

async function sendFCM(token, title, body, data, env) {
  const accessToken = await getAccessToken(env);
  const sa = JSON.parse(env.FIREBASE_SERVICE_ACCOUNT);
  const resp = await fetch(`https://fcm.googleapis.com/v1/projects/${sa.project_id}/messages:send`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      message: {
        token, notification: { title, body }, data: data || {},
        android: { priority: "high", notification: { channel_id: "default" } },
      },
    }),
  });
  if (!resp.ok) { console.error(`FCM ${resp.status}:`, await resp.text()); return false; }
  return true;
}

async function broadcastToTokens(env, title, body, data) {
  const tokensJson = await env.WOW_KV.get("fcm_tokens");
  if (!tokensJson) return { sent: 0, failed: 0 };
  const tokens = JSON.parse(tokensJson);
  let sent = 0, failed = 0;
  const dead = [];
  for (const t of tokens) {
    try { if (await sendFCM(t, title, body, data, env)) sent++; else { failed++; dead.push(t); } }
    catch { failed++; dead.push(t); }
  }
  if (dead.length) await env.WOW_KV.put("fcm_tokens", JSON.stringify(tokens.filter(t => !dead.includes(t))));
  return { sent, failed };
}

// HTTP Handler
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    if (request.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

    if (path === "/") {
      const tokens = JSON.parse(await env.WOW_KV.get("fcm_tokens") || "[]");
      return Response.json({ status: "ok", devices: tokens.length }, { headers: corsHeaders });
    }
    if (path === "/register-token" && request.method === "POST") {
      const { token } = await request.json();
      const tokens = JSON.parse(await env.WOW_KV.get("fcm_tokens") || "[]");
      if (!tokens.includes(token)) { tokens.push(token); await env.WOW_KV.put("fcm_tokens", JSON.stringify(tokens)); }
      return Response.json({ ok: true }, { headers: corsHeaders });
    }
    if (path === "/test-fcm") {
      const title = url.searchParams.get("title") || "Test";
      const body = url.searchParams.get("body") || "FCM works!";
      return Response.json({ ok: true, ...(await broadcastToTokens(env, title, body, { type: "test" })) }, { headers: corsHeaders });
    }
    return Response.json({ error: "Not found" }, { status: 404, headers: corsHeaders });
  },

  async scheduled(event, env, ctx) {
    // Add your change detection + notification logic here
    console.log("Cron triggered");
  },
};
