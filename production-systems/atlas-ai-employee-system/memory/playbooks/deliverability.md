# Deliverability SOP (non-negotiable)

Updated: 2026-07-10 · Applies to Scribe and all outbound.

1. **Never send cold email from the main company domain.** Use 2–3 lookalike sending domains (e.g. try-{brand}.com, get{brand}.com).
2. Each domain: Google Workspace inboxes, SPF + DKIM + DMARC configured, forwarding to the main domain.
3. **Warmup 2–3 weeks** in Smartlead/Instantly before any real send. Keep warmup running permanently.
4. Volume caps: ≤ 30–50 cold sends per inbox per day, ramp slowly.
5. Plain text, no links/images in early touches, spintax where the sequencer supports it.
6. CAN-SPAM: physical postal address + working unsubscribe in every email; honor opt-outs immediately (suppression list lives in lead-history/).
7. Watch: spam complaint rate < 0.1–0.2%, bounce rate < 3% (verify emails in Clay before sending).
8. If a domain's reputation degrades: pause it, keep warmup only, rotate in a fresh domain.
