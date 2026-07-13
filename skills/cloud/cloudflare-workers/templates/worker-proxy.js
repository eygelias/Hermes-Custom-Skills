/**
 * Cloudflare Worker — API Proxy with KV + Cron + FCM Push
 *
 * Features:
 *   - HTTP proxy to backend API
 *   - KV storage for tokens/state
 *   - Cron Trigger for periodic checks
 *   - FCM push notifications (Service Account auth)
 *
 * Required setup:
 *   - KV Namespace binding: WOW_KV
 *   - Secret: FIREBASE_SERVICE_ACCOUNT (JSON string)
 *   - Cron Trigger: */1 * * * * (or desired interval)
 */

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

// ─── FCM Auth ──────────────────────────────────────────

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

  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "pkcs8",
    enc.encode(atob(sa.private_key.replace(/-----.*-----/g, "").replace(/\s/g, ""))),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false, ["sign"]
  );
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(`${header}.${payload}`));
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
  const resp = await fetch(
    `https://fcm.googleapis.com/v1/projects/${sa.project_id}/messages:send`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          token,
          notification: { title, body },
          data: data || {},
          android: { priority: "high" },
        },
      }),
    }
  );
  return resp.ok;
}

// ─── HTTP Handler ──────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    // Add your routes here
    if (url.pathname === "/") {
      return Response.json({ status: "ok" }, { headers: corsHeaders });
    }

    return Response.json({ error: "Not found" }, { status: 404, headers: corsHeaders });
  },

  async scheduled(event, env, ctx) {
    // Add your periodic logic here
    console.log("Cron triggered");
  },
};
