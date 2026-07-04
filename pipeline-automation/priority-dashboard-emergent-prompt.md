# Emergent Build Prompt: Pipeline Priority Engine Dashboard

Paste the prompt below into Emergent (app.emergent.sh) as a single message. It builds a working dashboard app that visualizes the Intent Priority Engine. Build time is usually 15 to 25 minutes. Deploy with the built-in hosting and keep the URL ready in a tab.

---

## THE PROMPT (copy everything below this line)

Build a single-page web app called "Pipeline Priority Engine" for a B2B marketing team at an AI sales enablement company (target customers: enterprise sales teams in insurance, banking, wealth management, fintech).

WHAT IT DOES
The app is an account prioritization dashboard. It ingests intent signals for target accounts, scores each account with weighted signals and 30-day time decay, sorts accounts into tiers, and shows the marketer exactly who to touch today.

DATA MODEL
Account: { id, name, domain, industry, employees, tier (T1/T2/T3), score (number), whyNow (string), signals: [Signal] }
Signal: { id, type (pricing_view | web_visit | content_download | webinar | job_change | funding | hiring_surge), detail (string), date (ISO), source (RB2B | Apollo | Form | Manual) }

SCORING RULES (implement exactly)
- Weights: pricing_view 4, web_visit 3, content_download 3, webinar 3, job_change 2, funding 2, hiring_surge 2
- Time decay: each signal's points are multiplied by (1 - ageInDays/30). Signals older than 30 days contribute 0 and show as "expired" in the UI
- Account score = sum of decayed signal points, rounded to 1 decimal
- Tiers: score 8+ is T1 (human 1:1 outreach), 4 to 7.9 is T2 (automated sequence), under 4 is T3 (ads-only nurture)
- Scores recalculate live whenever a signal is added or the page loads

UI (dark, clean, professional; navy background, blue accents, green for T1, amber for T2, neutral for T3)
1. Header: app name plus three stat chips: T1 count, T2 count, total active signals
2. Three-column tier board (T1 / T2 / T3). Each account card shows: name, industry chip, employee count, score with a small progress bar, "why now" line, and its signals as small tags with age (e.g. "pricing_view, 3d ago"). Expired signals render strikethrough
3. "Add Signal" panel (simulates a webhook from RB2B / Apollo / forms): dropdowns for account and signal type, text input for detail, date picker defaulting to today, submit button. On submit the account re-scores and animates to its new tier column if it changed
4. "Add Account" mini-form: name, domain, industry, employees
5. A "Daily Queue" strip at the top listing today's T1 accounts in score order, like a morning briefing

SEED DATA (load on first run)
Create 10 accounts with realistic mixed signals so all three tiers are populated:
- Northwestern Mutual (insurance, 7500 emp): pricing_view 2d ago, webinar 6d ago, job_change "New CRO joined" 10d ago
- Farmers Insurance (insurance, 12000 emp): web_visit 1d ago, content_download "AI roleplay guide" 4d ago
- Ameriprise Financial (wealth management, 14000 emp): web_visit 3d ago, hiring_surge "12 advisor roles posted" 8d ago
- Regions Bank (banking, 20000 emp): webinar 12d ago, job_change "New Head of Enablement" 15d ago
- Chime (fintech, 1500 emp): pricing_view 1d ago, web_visit 1d ago
- Lemonade (fintech insurance, 1300 emp): content_download 20d ago
- Synchrony (banking, 18000 emp): web_visit 25d ago
- Guardian Life (insurance, 8000 emp): funding "expansion announced" 9d ago
- SoFi (fintech, 4500 emp): webinar 2d ago, job_change "New VP Sales" 5d ago
- Truist (banking, 40000 emp): web_visit 29d ago, content_download 28d ago
Generate a sensible "why now" line for each from its strongest signal.

TECH
Frontend-only is fine (all state client-side with localStorage persistence). No auth. Make it look production-grade: consistent spacing, tabular numbers for scores, subtle hover states, and a small footer reading "Built by Saurabh Shukla, scoring logic: weighted intent signals with 30-day linear decay".

---
