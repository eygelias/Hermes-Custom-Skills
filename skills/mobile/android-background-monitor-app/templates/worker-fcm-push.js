/**
 * Cloudflare Worker — API Proxy + FCM Push Notifications
 *
 * Features:
 *   - Proxies external API via HTTPS (avoids Android cleartext HTTP issues)
 *   - Cron Trigger checks for changes, sends FCM push if detected
 *   - Stores device tokens and last-known state in KV
 *   - Per-device region preferences in KV
 *
 * Required:
 *   - KV binding: WOW_KV
 *   - Secret: FIREBASE_SERVICE_ACCOUNT (JSON string)
 *   - Cron Trigger: */1 * * * * (every 1 minute, free plan minimum)
 *
 * Endpoints:
 *   GET  /                  — Status + device count
 *   GET  /fetch             — Proxy API data as JSON
 *   POST /register-token    — { token, regions } → register FCM token
 *   POST /unregister-token  — { token } → remove token
 *   GET  /check             — Manual change detection trigger
 */

// ─── CONFIG ─────────────────────────────────────────────
const API_BASE = "http://target-api.example.com:8080";

const ENDPOINTS = {
  item1: { path: "/api/item1", name: "Item One" },
  item2: { path: "/api/item2", name: "Item Two" },
};

const PREFERRED_ORDER = ["us", "eu", "cn"]; // display/notification order

// ─── API FETCH & PARSE ──────────────────────────────────

async function fetchAPI(path) {
  const resp = await fetch(`${API_BASE}${path}`);
  if (!resp.ok) return null;
  return await resp.text();
}

// Adapt parseXxx functions to your API's format
function parseResponse(text) {
  return text
    .split("\n")
    .filter((l) => l.trim() && !l.startsWith("#"))
    .map((line) => {
      const parts = line.split("|"); // or "\t" or "," — adapt to API
      return {
        region: parts[0]?.trim(),
        // ... map other fields
      };
    })
    .filter((r) => r.region);
}

async function fetchAll() {
  const results = {};
  await Promise.all(
    Object.entries(ENDPOINTS).map(async ([key, ep]) => {
      const raw = await fetchAPI(ep.path);
      if (!raw) return;
      const items = parseResponse(raw);
      items.sort((a, b) => {
        const ai = PREFERRED_ORDER.indexOf(a.region);
        const bi = PREFERRED_ORDER.indexOf(b.region);
        return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
      });
      results[key] = { key, name: ep.name, items };
    })
  );
  return results;
}

// ─── FCM (HTTP v1 API) ─────────────────────────────────

async function getAccessToken(env) {
  const sa = JSON.parse(env.FIREBASE_SERVICE_ACCOUNT);
  const now = Math.floor(Date.now() / 1000);

  const header = btoa(JSON.stringify({ alg: "RS256", typ: "JWT" }))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const payload = btoa(JSON.stringify({
    iss: sa.client_email,
    scope: "https://www.googleapis.com/auth/firebase.messaging",
    aud: "https://oauth2.googleapis.com/token",
    iat: now,
    exp: now + 3600,
  }))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

  const enc = new TextEncoder();
  const keyData = atob(sa.private_key.replace(/-----.*-----/g, "").replace(/\s/g, ""));
  const key = await crypto.subtle.importKey(
    "pkcs8",
    enc.encode(keyData),
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const sig = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    key,
    enc.encode(`${header}.${payload}`)
  );

  const jwt = `${header}.${payload}.${
    btoa(String.fromCharCode(...new Uint8Array(sig)))
      .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "")
  }`;

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
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
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

async function broadcast(env, title, body, data) {
  const tokensJson = await env.WOW_KV.get("fcm_tokens");
  if (!tokensJson) return { sent: 0 };
  const tokens = JSON.parse(tokensJson);
  let sent = 0;
  const dead = [];

  for (const token of tokens) {
    try {
      if (await sendFCM(token, title, body, data, env)) sent++;
      else dead.push(token);
    } catch {
      dead.push(token);
    }
  }

  if (dead.length > 0) {
    await env.WOW_KV.put(
      "fcm_tokens",
      JSON.stringify(tokens.filter((t) => !dead.includes(t)))
    );
  }
  return { sent, failed: dead.length };
}

// ─── CHANGE DETECTION ───────────────────────────────────

async function detectAndNotify(env) {
  const current = await fetchAll();
  if (!Object.keys(current).length) return { error: "API fetch failed" };

  const lastJson = await env.WOW_KV.get("last_versions");
  const last = lastJson ? JSON.parse(lastJson) : {};
  const changes = [];

  for (const [key, game] of Object.entries(current)) {
    const lastGame = last[key];
    if (!lastGame) continue;
    for (const item of game.items) {
      const lastItem = lastGame.items?.find((i) => i.region === item.region);
      if (lastItem && lastItem.buildNumber !== item.buildNumber) {
        changes.push({
          name: game.name,
          key,
          region: item.region,
          old: lastItem.buildVersion,
          new: item.buildVersion,
        });
      }
    }
  }

  await env.WOW_KV.put("last_versions", JSON.stringify(current));

  if (changes.length > 0) {
    const byGame = {};
    for (const c of changes) {
      if (!byGame[c.key]) byGame[c.key] = { name: c.name, list: [] };
      byGame[c.key].list.push(c);
    }
    for (const [, info] of Object.entries(byGame)) {
      const title = `🚨 ${info.name} UPDATED`;
      const body = `${info.list.length} region(s): ${info.list.map((c) => c.region.toUpperCase()).join(", ")}`;
      await broadcast(env, title, body, { type: "update", changes: JSON.stringify(info.list) });
    }
  }

  return { checked: Object.keys(current).length, changes: changes.length };
}

// ─── HTTP HANDLER ───────────────────────────────────────

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    if (url.pathname === "/") {
      const t = await env.WOW_KV.get("fcm_tokens");
      return Response.json({
        status: "ok",
        devices: t ? JSON.parse(t).length : 0,
      }, { headers: cors });
    }

    if (url.pathname === "/fetch") {
      return Response.json(await fetchAll(), { headers: cors });
    }

    if (url.pathname === "/register-token" && request.method === "POST") {
      const { token, regions } = await request.json();
      if (!token) return Response.json({ error: "token required" }, { status: 400, headers: cors });
      const tokens = JSON.parse(await env.WOW_KV.get("fcm_tokens") || "[]");
      if (!tokens.includes(token)) {
        tokens.push(token);
        await env.WOW_KV.put("fcm_tokens", JSON.stringify(tokens));
      }
      if (regions) await env.WOW_KV.put(`prefs_${token}`, JSON.stringify(regions));
      return Response.json({ ok: true }, { headers: cors });
    }

    if (url.pathname === "/unregister-token" && request.method === "POST") {
      const { token } = await request.json();
      const tokens = JSON.parse(await env.WOW_KV.get("fcm_tokens") || "[]");
      await env.WOW_KV.put("fcm_tokens", JSON.stringify(tokens.filter((t) => t !== token)));
      await env.WOW_KV.delete(`prefs_${token}`);
      return Response.json({ ok: true }, { headers: cors });
    }

    if (url.pathname === "/check") {
      return Response.json(await detectAndNotify(env), { headers: cors });
    }

    return Response.json({ error: "Not found" }, { status: 404, headers: cors });
  },

  async scheduled(event, env) {
    await detectAndNotify(env);
  },
};
