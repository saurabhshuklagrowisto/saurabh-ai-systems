# Sales Pipeline Digest

Two n8n workflows that generate a sales pipeline digest — a rolled-up,
AI-written summary of pipeline movement and sales signals, delivered by email.

| File | What it is |
|---|---|
| [daily_sales_pipeline_digest.json](./daily_sales_pipeline_digest.json) | Scheduled daily digest run. |
| [on_demand_sales_pipeline_digest.json](./on_demand_sales_pipeline_digest.json) | On-demand trigger for the same digest. |

Both are importable n8n exports. Credentials are referenced by name only —
no API keys, tokens, or internal email addresses are included (recipients are
placeholder addresses; wire your own credentials and recipients on import).
