// Close inbound reply listener -> lead status routing
// Deploy as a serverless function alongside api/lead.js (Vercel: /api/reply.js).
// Node 18+ (global fetch, node:crypto). No dependencies.
//
// Why this exists: a Close workflow can STOP on a reply (goal criteria) but Close has no
// inbound-message trigger, so nothing inside Close can move the replier's status. This does that.

import crypto from "node:crypto";

const CLOSE = "https://api.close.com/api/v1";

// ---- Close lead status IDs. Do not change unless Close changes. ----
const STATUS_MEL = "stat_REPLACE_MEL";
const STATUS_NOT_INTERESTED = "stat_REPLACE_NOT_INTERESTED";
const STATUS_DNC = "stat_REPLACE_DNC";
const STATUS_DISCOVERY_CALL = "stat_REPLACE_DISCOVERY_CALL";

// A human already moved these forward or shut them down. A reply must not undo that.
const PROTECTED_STATUSES = new Set([STATUS_DNC, STATUS_DISCOVERY_CALL]);

// Marker so the daily digest can find what this file wrote.
const NOTE_MARKER = "[REPLY-CLASSIFIER]";

function authHeader() {
  const key = process.env.CLOSE_API_KEY;
  if (!key) throw new Error("CLOSE_API_KEY is not set");
  return "Basic " + Buffer.from(key + ":").toString("base64");
}

async function closeApi(path, options = {}) {
  const res = await fetch(CLOSE + path, {
    ...options,
    headers: {
      Authorization: authHeader(),
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`Close ${res.status} on ${path}: ${text.slice(0, 500)}`);
  return text ? JSON.parse(text) : {};
}

// ---- classification -------------------------------------------------------
// Rules, not a model. Every branch is readable, and a wrong call is visible in
// the note the listener leaves on the lead.

const RE_OPT_OUT = /\b(stop|stopall|unsubscribe|opt[\s-]?out|remove me|take me off|do not (contact|email|text)|dont (contact|email|text) me)\b/i;

const RE_AUTO_REPLY = /\b(out of (the )?office|automatic reply|auto[\s-]?repl(y|ies)|currently (away|on leave)|on (vacation|holiday|pto|leave)|away from my desk|limited access to email|respond when i return|maternity leave|paternity leave)\b/i;

const RE_BOUNCE = /\b(undeliverable|delivery (has )?failed|address not found|mailbox (is )?full|recipient .{0,20}rejected|550 5\.\d\.\d)\b/i;

// The expensive misread: they think we offered THEM a job.
const RE_JOB_MISREAD = /(my resume|not looking for (a )?(job|work)|i (already )?have a job|not applying|i did not apply|why would i want this)/i;

const RE_REFERRAL = /\b(wrong (person|number|department)|not the right person|i do ?n[o']?t handle|no longer (with|at)|has left the company|you (want|should) (to )?(talk|speak|reach)|reach out to|contact .{0,40}instead|forward(ing|ed) (this|you))\b/i;

const RE_NEGATIVE = /(not interested|no thanks|no thank you|we are (all set|good|covered)|were (all set|good|covered)|all set thanks|already (filled|hired|have someone)|(position|role) (is )?(filled|closed)|no need|not a (good )?fit|we do ?n[o']?t (need|use|outsource)|stop (emailing|texting|calling))/i;

const RE_POSITIVE = /\b(yes|yeah|sure|interested|sounds good|lets (talk|chat)|send (me )?(the )?(profiles|candidates|info|details|resumes)|what (are|is) (your|the) (rate|rates|pricing|cost)|how (does|would) (it|this) work|book|schedule|calendar|call me|available|works for me|tomorrow|next week)\b/i;

/**
 * Returns { kind, status_id, digest, reason }.
 * status_id null means leave the lead alone.
 * digest true means surface it in the daily report.
 */
function classifyReply(text) {
  const body = String(text || "").trim();
  if (!body) {
    return { kind: "empty", status_id: null, digest: false, reason: "no text in the reply" };
  }
  if (RE_BOUNCE.test(body)) {
    return { kind: "bounce", status_id: null, digest: true, reason: "looks like a bounce, the address needs a human" };
  }
  if (RE_AUTO_REPLY.test(body)) {
    return { kind: "auto_reply", status_id: null, digest: false, reason: "out of office, not a real reply, status untouched" };
  }
  if (RE_OPT_OUT.test(body)) {
    return { kind: "opt_out", status_id: STATUS_DNC, digest: true, reason: "explicit opt out" };
  }
  if (RE_JOB_MISREAD.test(body)) {
    return { kind: "job_misread", status_id: STATUS_NOT_INTERESTED, digest: true, reason: "read the offer as a job pitch aimed at them, check the copy that went out" };
  }
  if (RE_REFERRAL.test(body)) {
    return { kind: "referral", status_id: STATUS_MEL, digest: true, reason: "points at a different person, reroute before any more sends" };
  }
  if (RE_NEGATIVE.test(body)) {
    return { kind: "negative", status_id: STATUS_NOT_INTERESTED, digest: true, reason: "negative reply" };
  }
  if (RE_POSITIVE.test(body)) {
    return { kind: "positive", status_id: STATUS_MEL, digest: false, reason: "positive reply" };
  }
  return { kind: "neutral", status_id: STATUS_MEL, digest: false, reason: "replied, nothing negative in it" };
}

// ---- webhook plumbing -----------------------------------------------------

// Close signs webhooks with HMAC-SHA256 over (timestamp + raw body), keyed with the hex
// signature key it returns when the subscription is created.
function verifySignature(rawBody, headers, signatureKeyHex) {
  const hash = headers["close-sig-hash"];
  const timestamp = headers["close-sig-timestamp"];
  if (!hash || !timestamp) return { ok: false, error: "missing close-sig-hash or close-sig-timestamp" };

  const ageSeconds = Math.abs(Date.now() / 1000 - Number(timestamp));
  if (!Number.isFinite(ageSeconds) || ageSeconds > 300) {
    return { ok: false, error: "signature timestamp is more than 5 minutes off" };
  }

  const expected = crypto
    .createHmac("sha256", Buffer.from(signatureKeyHex, "hex"))
    .update(timestamp + rawBody)
    .digest("hex");

  const a = Buffer.from(expected, "utf8");
  const b = Buffer.from(String(hash), "utf8");
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
    return { ok: false, error: "signature mismatch" };
  }
  return { ok: true };
}

function htmlToText(html) {
  return String(html || "")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/(p|div|tr|li|h[1-6])>/gi, "\n")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/[ \t]+/g, " ")
    .trim();
}

// An email reply carries the whole quoted thread. Only the new text gets classified,
// otherwise our own copy ("you only pay if you hire") votes on the sentiment.
function stripQuotedThread(text) {
  const lines = String(text || "").split(/\r?\n/);
  const out = [];
  for (const line of lines) {
    if (/^\s*>/.test(line)) break;
    if (/^\s*On .{5,120}wrote:\s*$/i.test(line)) break;
    if (/^\s*(-{2,}\s*)?(Original Message|Forwarded message)/i.test(line)) break;
    if (/^\s*From:\s*.+@/i.test(line)) break;
    out.push(line);
  }
  const head = out.join("\n").trim();
  return head || String(text || "").trim();
}

// Pull (lead_id, text, channel) out of a Close webhook event. Returns null for anything
// that is not an inbound SMS or email, which is most of what a subscription can send.
function extractReply(payload) {
  const event = (payload && payload.event) || payload || {};
  const data = event.data || {};
  const objectType = event.object_type || data.object_type || "";
  const action = event.action || "";

  if (action && action !== "created" && action !== "updated") return null;

  const isSms = objectType === "activity.sms";
  const isEmail = objectType === "activity.email";
  if (!isSms && !isEmail) return null;

  const direction = String(data.direction || "").toLowerCase();
  if (direction !== "inbound" && direction !== "incoming") return null;

  const lead_id = event.lead_id || data.lead_id;
  if (!lead_id) return null;

  const raw = isSms
    ? data.text
    : (data.body_text || htmlToText(data.body_html) || data.subject);

  return {
    lead_id,
    activity_id: data.id || event.id || null,
    channel: isSms ? "sms" : "email",
    contact_id: data.contact_id || null,
    text: isEmail ? stripQuotedThread(raw) : String(raw || "").trim()
  };
}

function buildNote(reply, verdict, statusApplied, previousStatusName) {
  return [
    `${NOTE_MARKER} ${verdict.kind}`,
    `Channel: ${reply.channel}`,
    `Why: ${verdict.reason}`,
    `Status before: ${previousStatusName || "(unknown)"}`,
    statusApplied ? "Status set by the listener." : "Status left alone.",
    "",
    "REPLY",
    reply.text.slice(0, 2000)
  ].join("\n");
}

async function handleReply(payload) {
  const reply = extractReply(payload);
  if (!reply) return { handled: false, reason: "not an inbound sms or email" };

  const verdict = classifyReply(reply.text);
  const lead = await closeApi(`/lead/${reply.lead_id}/?_fields=id,name,status_id,status_label`);

  let statusApplied = false;
  if (verdict.status_id && !PROTECTED_STATUSES.has(lead.status_id) && lead.status_id !== verdict.status_id) {
    await closeApi(`/lead/${reply.lead_id}/`, {
      method: "PUT",
      body: JSON.stringify({ status_id: verdict.status_id })
    });
    statusApplied = true;
  }

  await closeApi("/activity/note/", {
    method: "POST",
    body: JSON.stringify({
      lead_id: reply.lead_id,
      note: buildNote(reply, verdict, statusApplied, lead.status_label)
    })
  });

  return {
    handled: true,
    lead_id: reply.lead_id,
    lead_name: lead.name,
    channel: reply.channel,
    kind: verdict.kind,
    status_applied: statusApplied,
    digest: verdict.digest
  };
}

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const rawBody = typeof req.body === "string" ? req.body : JSON.stringify(req.body || {});
  const signatureKey = process.env.CLOSE_WEBHOOK_SIGNATURE_KEY;

  if (signatureKey) {
    const check = verifySignature(rawBody, req.headers, signatureKey);
    if (!check.ok) return res.status(401).json({ error: check.error });
  } else {
    console.error("CLOSE_WEBHOOK_SIGNATURE_KEY is not set, this endpoint is unauthenticated");
  }

  try {
    const payload = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
    const result = await handleReply(payload);
    return res.status(200).json({ ok: true, ...result });
  } catch (err) {
    // Never swallow this. A dropped reply means someone keeps getting chased.
    console.error("close-reply-listener failed:", err);
    return res.status(500).json({ ok: false, error: String(err.message || err) });
  }
}

export {
  handleReply,
  classifyReply,
  extractReply,
  stripQuotedThread,
  verifySignature,
  NOTE_MARKER,
  STATUS_MEL,
  STATUS_NOT_INTERESTED,
  STATUS_DNC,
  STATUS_DISCOVERY_CALL
};
