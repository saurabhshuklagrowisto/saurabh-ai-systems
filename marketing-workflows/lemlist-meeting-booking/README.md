# Lemlist Multichannel Meeting Booking

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Channel](https://img.shields.io/badge/cadence-email_%2B_LinkedIn-7c3aed?style=flat-square)
![Goal](https://img.shields.io/badge/goal-in--person_founder_meetings-1e40af?style=flat-square)

An automated Lemlist multichannel sequence that books in-person US meetings for my company's founder with founders of US eCommerce brands. It is founder-to-founder outreach: a curated list, account-specific hooks, and a paced cadence that moves across email and LinkedIn so the request earns a reply instead of getting buried in one channel. Built at [Growisto](https://growisto.com).

## The outcome

| Metric | Value |
|---|---|
| Cadence | 6 touches across the sequence |
| Channels | 2 (email + LinkedIn), orchestrated together |
| Goal | In-person US meetings booked for the founder |
| Target | Founders of US eCommerce brands |

## The cadence

```
   Day 1   ┌──────────────────────────────┐
    ───────│  Email · founder-to-founder  │  Opens with a real, account-
           │  intro + the meeting ask     │  specific hook. Asks for a
           └──────────────┬───────────────┘  short in-person meeting.
                          │
   Day 2   ┌──────────────▼───────────────┐
    ───────│  LinkedIn · connection req   │  Personalised note, references
           │                              │  the same hook as the email.
           └──────────────┬───────────────┘
                          │
           ┌──────────────▼───────────────┐
    ───────│  Email · follow-up 1         │  Short nudge, adds a second
           │                              │  reason the meeting is worth it.
           └──────────────┬───────────────┘
                          │
           ┌──────────────▼───────────────┐
    ───────│  LinkedIn · message          │  Once connected, a direct
           │                              │  message continuing the thread.
           └──────────────┬───────────────┘
                          │
           ┌──────────────▼───────────────┐
    ───────│  Email · follow-up 2         │  Final email nudge with a
           │                              │  clear, low-friction ask.
           └──────────────┬───────────────┘
                          │
           ┌──────────────▼───────────────┐
    ───────│  LinkedIn · voice note       │  A short personal voice note.
           │                              │  Highest-signal, most human
           └──────────────────────────────┘  touch, saved for last.
                          │
                          v
                 Meeting booked → Zoho CRM
```

Each step is paced in Lemlist with delays and conditions, so a reply or a booked meeting stops the sequence. The voice note is deliberately last: it is the most personal, highest-effort touch, and it lands hardest once the founder has already seen the name a few times.

## Why this shape

1. **Multichannel beats single-channel.** A founder who ignores an email may accept a LinkedIn connection, and a connection who skims a message may stop for a voice note. Spreading six touches across two channels keeps the outreach present without being annoying in any one inbox.
2. **The voice note is the closer.** Most outreach never gets personal. A short, genuine LinkedIn voice note from one founder asking another for a quick in-person meeting is rare enough that it stands out, and it works best after a few lighter touches have built recognition.
3. **In-person is the real ask.** The whole sequence is built around a specific, concrete ask: a short in-person meeting while the founder is in the US. Concrete asks convert better than "hop on a call sometime."
4. **Founder-to-founder framing.** This is not an SDR pitching a service. It is positioned as one founder wanting to meet another, which is exactly why it earns the meeting.

## Where AI plugs in

- **Account-specific hooks** · Claude writes the opening hook for each founder, anchored to a real signal about their brand, so the first email and the LinkedIn note both feel researched.
- **Per-touch personalization** · the follow-ups and the LinkedIn message are tailored per account rather than reused verbatim.
- **Reply triage** · inbound replies are classified and the booked meetings are logged to Zoho CRM.

## The stack

`Lemlist` for the multichannel email + LinkedIn cadence and the voice-note step · `Apollo` for founder contact data · `Claude` for hooks and per-touch personalization · `LinkedIn` for the connection, message and voice-note touches · `Zoho CRM` for tracking booked meetings

## Related

This cadence is the delivery engine behind the [ABM Outbound to US eCommerce Founders](../us-ecom-founder-abm) motion.

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**
