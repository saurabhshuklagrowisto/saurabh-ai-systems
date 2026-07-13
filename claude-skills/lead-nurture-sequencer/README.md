# Lead Nurture Sequencer

Stages leads by real engagement signal and decides the next nurture action for each -- with suppression rules that hard-stop automation the moment a human should own the thread (a reply, a booked meeting, an unsubscribe).

## Why this shape

Most nurture bugs are suppression bugs: a lead replies or books a meeting and the sequence keeps emailing them anyway, or an unsubscribe doesn't fully propagate. This skill checks those conditions first, before any engagement scoring runs, so they can't be overridden by a clever heuristic downstream.

## Run it

```bash
python scripts/nurture_sequencer.py         # built-in sample
python scripts/nurture_sequencer.py in.json # your own brand + leads
```

## Sample output

```json
{
  "leads": [
    { "name": "Jordan Lee", "stage": "warm", "next_touch_in_days": 3, "due_now": false },
    { "name": "Priya Shah", "stage": "engaged", "next_touch_in_days": 0, "due_now": true },
    { "name": "Tom Rivera", "stage": "cold", "next_touch_in_days": 0, "due_now": true },
    { "name": "Ana Kim", "stage": "curious", "next_touch_in_days": 8, "due_now": false },
    { "name": "Sam Osei", "stage": "suppressed", "next_touch_in_days": null, "due_now": false }
  ],
  "due_now": ["Priya Shah", "Tom Rivera"],
  "summary": "2 of 5 lead(s) are due for a touch right now: Priya Shah, Tom Rivera."
}
```

## How it composes

Feed it a daily/weekly CRM or email-platform export of lead signals; it returns exactly who is due for a touch today and what that touch should be. Pair with a scheduled n8n flow (same pattern as `pipeline-automation/aeo-geo-improvement-loop.json`) to post the `due_now[]` list to a rep's task queue automatically.
