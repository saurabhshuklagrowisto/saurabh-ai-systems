// Run: node test/classify.test.mjs
// No framework. Exits non zero on the first failure.

import { classifyReply, stripQuotedThread, extractReply } from "../api/reply.js";

const cases = [
  ["I am in a director position, what about my resume makes you think I want this", "job_misread"],
  ["wrong person, you want Dana in HR", "referral"],
  ["Not interested, we already filled the role", "negative"],
  ["STOP", "opt_out"],
  ["Sure, what are your rates?", "positive"],
  ["I am out of the office until Monday with limited access to email", "auto_reply"],
  ["Your message could not be delivered, address not found", "bounce"],
  ["Who is this", "neutral"]
];

let failed = 0;
for (const [text, expected] of cases) {
  const got = classifyReply(text).kind;
  const ok = got === expected;
  if (!ok) failed++;
  console.log(`${ok ? "pass" : "FAIL"}  ${expected.padEnd(12)} got ${got.padEnd(12)} ${text.slice(0, 50)}`);
}

// A quoted thread must not vote on the sentiment.
const threaded = [
  "Not interested, thanks.",
  "",
  "On Tue, Sep 15, 2026 at 9:02 AM Norman <norman@example.com> wrote:",
  "> If the seat can run remote it is $10/hr and you only pay when you hire. Worth 15 min?"
].join("\n");
const stripped = stripQuotedThread(threaded);
const threadOk = stripped === "Not interested, thanks." && classifyReply(stripped).kind === "negative";
if (!threadOk) failed++;
console.log(`${threadOk ? "pass" : "FAIL"}  quoted thread stripped, classified negative`);

// Outbound sends must be ignored, otherwise our own copy moves the lead.
const outbound = extractReply({
  event: { object_type: "activity.sms", action: "created", lead_id: "lead_1", data: { direction: "outbound", text: "hi" } }
});
const inbound = extractReply({
  event: { object_type: "activity.sms", action: "created", lead_id: "lead_1", data: { direction: "inbound", text: "not interested" } }
});
const extractOk = outbound === null && inbound && inbound.channel === "sms" && inbound.lead_id === "lead_1";
if (!extractOk) failed++;
console.log(`${extractOk ? "pass" : "FAIL"}  outbound ignored, inbound extracted`);

console.log(failed === 0 ? "\nall green" : `\n${failed} failing`);
process.exit(failed === 0 ? 0 : 1);
