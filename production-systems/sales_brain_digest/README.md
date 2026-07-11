# Sales Brain Digest

Two n8n workflows that generate a "Sales Brain" digest — a rolled-up
summary of pipeline and sales signals delivered by email.

| File | What it is |
|---|---|
| [daily_sales_brain_digest.json](./daily_sales_brain_digest.json) | Scheduled daily digest run. |
| [on_demand_sales_brain_digest.json](./on_demand_sales_brain_digest.json) | On-demand trigger for the same digest. |

Both are importable n8n exports. Credentials are referenced by name only —
no API keys, tokens, or internal email addresses are included (recipients are
placeholder addresses; wire your own credentials and recipients on import).
