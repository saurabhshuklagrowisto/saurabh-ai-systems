#!/usr/bin/env python3
"""
Lead Nurture Sequencer -- stages leads and decides the next nurture touch.

Takes a list of leads with raw engagement signals (opens, clicks, replies,
meetings, unsubscribes, days since last touch) and returns, per lead: the
nurture stage, the next action, the channel, and how many days until the
next touch is due. No dependencies, no API keys.

Input schema:
{
  "brand": "YourBrand",
  "leads": [
    {
      "name": "Jordan Lee",
      "days_since_last_touch": 4,
      "email_opens": 2,
      "email_clicks": 1,
      "replied": false,
      "meeting_booked": false,
      "unsubscribed": false
    }
  ]
}

In production these signals come from the email platform / CRM webhook; the
demo generates a deterministic sample so the staging logic runs anywhere.
"""
import json, sys

# (stage, action, channel, cooldown_days) -- checked top to bottom, first match wins
STAGE_COOLDOWN = {
    "suppressed": None,
    "sales-qualified": None,
    "engaged": 0,
    "warm": 7,
    "curious": 10,
    "cold": 30,
    "nurture": 14,
}


def stage_lead(lead):
    if lead.get("unsubscribed"):
        return "suppressed", "Remove from every active sequence immediately. Do not re-add without explicit opt-in."
    if lead.get("meeting_booked"):
        return "sales-qualified", "Hand off to an AE and pause all nurture sends -- a human owns this thread now."
    if lead.get("replied"):
        return "engaged", "A rep replies personally within 24 hours. Do not let an automated touch follow a real reply."
    clicks = lead.get("email_clicks", 0)
    opens = lead.get("email_opens", 0)
    days = lead.get("days_since_last_touch", 0)
    if clicks > 0 and days < 7:
        return "warm", "Send a case-study or proof-point touch while interest is fresh."
    if opens > 0 and clicks == 0:
        return "curious", "Opening but not clicking -- vary the subject line and content type on the next touch."
    if opens == 0 and days > 30:
        return "cold", "No engagement in 30+ days -- send a breakup/re-engagement email before letting the lead go quiet."
    return "nurture", "Continue the standard nurture cadence -- no signal strong enough to change the plan yet."


def sequence(data):
    brand = data["brand"]
    leads = data["leads"]
    results = []
    for lead in leads:
        stage, action = stage_lead(lead)
        cooldown = STAGE_COOLDOWN[stage]
        days_since = lead.get("days_since_last_touch", 0)
        next_touch_in_days = None if cooldown is None else max(0, cooldown - days_since)
        results.append({
            "name": lead["name"],
            "stage": stage,
            "action": action,
            "next_touch_in_days": next_touch_in_days,
            "due_now": next_touch_in_days == 0,
        })

    due_now = [r["name"] for r in results if r["due_now"]]
    stage_counts = {}
    for r in results:
        stage_counts[r["stage"]] = stage_counts.get(r["stage"], 0) + 1

    if due_now:
        summary = f"{len(due_now)} of {len(results)} lead(s) are due for a touch right now: {', '.join(due_now)}."
    else:
        summary = f"{len(results)} lead(s) staged, none due for a touch today. Stage mix: {stage_counts}."

    return {"brand": brand, "leads": results, "stage_counts": stage_counts, "due_now": due_now, "summary": summary}


# --- deterministic sample so the demo runs with no keys ---
def _sample():
    return {
        "brand": "YourBrand",
        "leads": [
            {"name": "Jordan Lee", "days_since_last_touch": 4, "email_opens": 2, "email_clicks": 1,
             "replied": False, "meeting_booked": False, "unsubscribed": False},
            {"name": "Priya Shah", "days_since_last_touch": 1, "email_opens": 1, "email_clicks": 0,
             "replied": True, "meeting_booked": False, "unsubscribed": False},
            {"name": "Tom Rivera", "days_since_last_touch": 45, "email_opens": 0, "email_clicks": 0,
             "replied": False, "meeting_booked": False, "unsubscribed": False},
            {"name": "Ana Kim", "days_since_last_touch": 2, "email_opens": 3, "email_clicks": 0,
             "replied": False, "meeting_booked": False, "unsubscribed": False},
            {"name": "Sam Osei", "days_since_last_touch": 10, "email_opens": 0, "email_clicks": 0,
             "replied": False, "meeting_booked": False, "unsubscribed": True},
        ],
    }


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else _sample()
    print(json.dumps(sequence(data), indent=2))
