// Website contact form -> Close CRM
// Deploy as a serverless function (Vercel: /api/lead.js, Netlify: netlify/functions/lead.js).
// Node 18+ (global fetch). No dependencies.

const CLOSE = "https://api.close.com/api/v1";

// ---- Close IDs. Do not change unless Close changes. ----
const STATUS_FRESH_LEAD = "stat_REPLACE_FRESH_LEAD";
const CF_LEAD_SOURCE = "cf_REPLACE_LEAD_SOURCE";
const CF_REFERRAL_SOURCE = "cf_REPLACE_REFERRAL_SOURCE";
const CF_COMPANY_WEBSITE = "cf_REPLACE_COMPANY_WEBSITE";
// Job Source (its own cf_ id) is the scraper views only. Inbound leads must never set it.

const LEAD_SOURCE_VALUE = "Website Form";
const REFERRAL_SOURCE_VALUE = "Website";

const FREE_EMAIL_DOMAINS = new Set([
  "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
  "icloud.com", "me.com", "live.com", "msn.com", "proton.me", "protonmail.com",
  "gmx.com", "mail.com", "yandex.com", "zoho.com"
]);

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

// 2125550147 -> +12125550147. Returns null if it does not look like a real number.
function toE164(raw) {
  if (!raw) return null;
  const trimmed = String(raw).trim();
  const digits = trimmed.replace(/\D/g, "");
  if (/^(\d)\1+$/.test(digits)) return null;        // 0000000000, 1111111111
  if (digits.length === 10) return "+1" + digits;
  if (digits.length === 11 && digits.startsWith("1")) return "+" + digits;
  if (trimmed.startsWith("+") && digits.length >= 8 && digits.length <= 15) return "+" + digits;
  return null;
}

function emailDomain(email) {
  const m = String(email || "").trim().toLowerCase().match(/^[^@\s]+@([^@\s]+\.[a-z]{2,})$/);
  return m ? m[1] : null;
}

// whitfieldgroup.com -> Whitfield Group is not safely derivable, so keep it honest:
// use the domain label as the company name and let the SDR correct it.
function companyNameFromDomain(domain) {
  const label = domain.split(".")[0].replace(/[-_]+/g, " ");
  return label.replace(/\b\w/g, c => c.toUpperCase());
}

function buildNote(form, domain, isFreeDomain) {
  const lines = [
    "SOURCE: website contact form.",
    `Submitted: ${form.submitted_at || new Date().toISOString()}`,
    "",
    "FORM SUBMISSION",
    `Name: ${form.name || "(not given)"}`,
    `Email: ${form.email}`,
    `Phone: ${form.phone || "(not given)"}`
  ];
  if (form.company) lines.push(`Company: ${form.company}`);
  if (form.request_type) lines.push(`Request type: ${form.request_type}`);
  if (form.message) lines.push("", "MESSAGE", form.message);
  lines.push("", "NOTES FOR SDR");
  lines.push("The form submitter is not a confirmed decision maker until someone checks. Title unknown.");
  lines.push(`Phone type was not stated on the form, stored as office.`);
  if (isFreeDomain) {
    lines.push(`Free email domain (${domain}), so the lead is named after the person, not a company. Fix the company name once known.`);
  }
  return lines.join("\n");
}

async function findLeadByDomain(domain) {
  const data = await closeApi(`/lead/?query=${encodeURIComponent(domain)}&_fields=id,name,contacts`);
  return (data.data && data.data[0]) || null;
}

function leadHasEmail(lead, email) {
  const wanted = String(email).trim().toLowerCase();
  return (lead.contacts || []).some(c =>
    (c.emails || []).some(e => String(e.email).toLowerCase() === wanted)
  );
}

async function handleSubmission(form) {
  if (!form || !form.email) throw new Error("email is required");
  const domain = emailDomain(form.email);
  if (!domain) throw new Error("email is not valid: " + form.email);

  const isFreeDomain = FREE_EMAIL_DOMAINS.has(domain);
  const phone = toE164(form.phone);
  const contact = {
    name: form.name || form.email,
    emails: [{ type: "office", email: form.email.trim() }],
    ...(phone ? { phones: [{ type: "office", phone }] } : {})
  };

  // Dedup by domain, never by person name.
  const existing = isFreeDomain ? null : await findLeadByDomain(domain);

  if (existing) {
    if (!leadHasEmail(existing, form.email)) {
      await closeApi("/contact/", {
        method: "POST",
        body: JSON.stringify({ lead_id: existing.id, ...contact })
      });
    }
    await closeApi("/activity/note/", {
      method: "POST",
      body: JSON.stringify({
        lead_id: existing.id,
        note: buildNote(form, domain, isFreeDomain)
      })
    });
    return { lead_id: existing.id, mode: "attached_to_existing", lead_name: existing.name };
  }

  const leadName = isFreeDomain
    ? (form.company || form.name || form.email)
    : (form.company || companyNameFromDomain(domain));

  const created = await closeApi("/lead/", {
    method: "POST",
    body: JSON.stringify({
      name: leadName,
      ...(isFreeDomain ? {} : { url: "https://" + domain }),
      status_id: STATUS_FRESH_LEAD,
      description: "Inbound website lead from the contact form.",
      contacts: [contact],
      [`custom.${CF_LEAD_SOURCE}`]: LEAD_SOURCE_VALUE,
      [`custom.${CF_REFERRAL_SOURCE}`]: REFERRAL_SOURCE_VALUE,
      ...(isFreeDomain ? {} : { [`custom.${CF_COMPANY_WEBSITE}`]: domain })
    })
  });

  await closeApi("/activity/note/", {
    method: "POST",
    body: JSON.stringify({
      lead_id: created.id,
      note: buildNote(form, domain, isFreeDomain)
    })
  });

  return { lead_id: created.id, mode: "created", lead_name: created.name };
}

// Vercel / Next.js API route style handler.
export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const secret = process.env.FORM_SHARED_SECRET;
  if (secret && req.headers["x-form-secret"] !== secret) {
    return res.status(401).json({ error: "bad or missing x-form-secret header" });
  }

  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
    const result = await handleSubmission(body);
    return res.status(200).json({ ok: true, ...result });
  } catch (err) {
    // Never swallow this. A failed push means a lost lead.
    console.error("close-website-lead failed:", err);
    return res.status(500).json({ ok: false, error: String(err.message || err) });
  }
}

export { handleSubmission, toE164, emailDomain };
