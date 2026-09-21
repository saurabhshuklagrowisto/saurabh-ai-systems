// Daily digest of what the reply listener did.
// Deploy alongside api/reply.js (Vercel: /api/digest.js) and hit it once a day from a cron.
// GET or POST, guarded by DIGEST_SECRET. Posts to SLACK_WEBHOOK_URL when it is set,
// and always returns the same report as JSON so it can be read without Slack.

import { NOTE_MARKER } from "./reply.js";

const CLOSE = "https://api.close.com/api/v1";

// Kinds worth a human's morning. Positive and neutral replies are already in MEL
// and sitting in someone's inbox, they do not need a report.
const DIGEST_KINDS = new Set(["negative", "opt_out", "job_misread", "referral", "bounce"]);

const KIND_LABEL = {
  negative: "Not interested",
  opt_out: "Opted out",
  job_misread: "Thought we were offering them a job",
  referral: "Pointed at someone else",
  bounce: "Bad address"
};

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

// The listener writes its verdict on line 1 of the note, after the marker.
function parseNote(note) {
  const body = String(note.note || note.note_html || "");
  if (!body.startsWith(NOTE_MARKER)) return null;
  const lines = body.split("\n");
  const kind = lines[0].slice(NOTE_MARKER.length).trim();
  const channel = (lines[1] || "").replace(/^Channel:\s*/i, "").trim();
  const replyIndex = lines.indexOf("REPLY");
  const reply = replyIndex === -1 ? "" : lines.slice(replyIndex + 1).join(" ").trim();
  return { kind, channel, reply, lead_id: note.lead_id, date: note.date_created };
}

async function fetchNotesSince(sinceIso) {
  const found = [];
  let skip = 0;
  // 5 pages is 500 notes in a day. Far past anything this pipeline produces.
  for (let page = 0; page < 5; page++) {
    const path = `/activity/note/?date_created__gt=${encodeURIComponent(sinceIso)}&_limit=100&_skip=${skip}`;
    const res = await closeApi(path);
    const batch = res.data || [];
    for (const note of batch) {
      const parsed = parseNote(note);
      if (parsed && DIGEST_KINDS.has(parsed.kind)) found.push(parsed);
    }
    if (!res.has_more) break;
    skip += batch.length;
  }
  return found;
}

async function addLeadNames(items) {
  const names = new Map();
  for (const item of items) {
    if (names.has(item.lead_id)) continue;
    try {
      const lead = await closeApi(`/lead/${item.lead_id}/?_fields=id,display_name,status_label`);
      names.set(item.lead_id, { name: lead.display_name, status: lead.status_label });
    } catch {
      // A deleted or merged lead should not kill the whole report.
      names.set(item.lead_id, { name: item.lead_id, status: "(unknown)" });
    }
  }
  return items.map(item => ({ ...item, ...(names.get(item.lead_id) || {}) }));
}

function buildSlackText(items, sinceIso) {
  if (items.length === 0) {
    return `*Outreach replies, last 24h*\nNothing negative came back.`;
  }
  const byKind = new Map();
  for (const item of items) {
    if (!byKind.has(item.kind)) byKind.set(item.kind, []);
    byKind.get(item.kind).push(item);
  }
  const lines = [`*Outreach replies, last 24h* (${items.length})`];
  for (const [kind, group] of byKind) {
    lines.push(`*${KIND_LABEL[kind] || kind}* (${group.length})`);
    for (const item of group.slice(0, 15)) {
      const quote = item.reply.slice(0, 120).replace(/\s+/g, " ");
      lines.push(`• ${item.name} [${item.channel}] now ${item.status}: "${quote}"`);
    }
    if (group.length > 15) lines.push(`• and ${group.length - 15} more`);
  }
  lines.push(`Since ${sinceIso}`);
  return lines.join("\n");
}

async function postToSlack(text) {
  const url = process.env.SLACK_WEBHOOK_URL;
  if (!url) return { posted: false, reason: "SLACK_WEBHOOK_URL is not set" };
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  if (!res.ok) throw new Error(`Slack ${res.status}: ${(await res.text()).slice(0, 300)}`);
  return { posted: true };
}

export default async function handler(req, res) {
  if (req.method !== "GET" && req.method !== "POST") {
    return res.status(405).json({ error: "GET or POST only" });
  }

  const secret = process.env.DIGEST_SECRET;
  const supplied = req.headers["x-digest-secret"] || (req.query && req.query.secret);
  if (secret && supplied !== secret) {
    return res.status(401).json({ error: "bad or missing digest secret" });
  }

  try {
    const hours = Number((req.query && req.query.hours) || 24);
    const sinceIso = new Date(Date.now() - hours * 3600 * 1000).toISOString();

    const items = await addLeadNames(await fetchNotesSince(sinceIso));
    const text = buildSlackText(items, sinceIso);
    const slack = await postToSlack(text);

    return res.status(200).json({ ok: true, since: sinceIso, count: items.length, slack, text, items });
  } catch (err) {
    // Never swallow this. A silent digest looks exactly like a quiet day.
    console.error("close-reply-digest failed:", err);
    return res.status(500).json({ ok: false, error: String(err.message || err) });
  }
}
