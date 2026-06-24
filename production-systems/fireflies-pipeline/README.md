# Fireflies Summary Pipeline

An n8n automation that catches every external meeting via the Fireflies webhook, runs Claude through a brand disambiguation step against the existing Drive folder structure, and files the transcript and an English summary to the right brand folder. Multi-language friendly. Live in production at [Growisto](https://growisto.com).

## What problem it solves

Sales teams take 30+ external calls a week across many accounts. Fireflies records and transcribes them, but the default storage is a flat list. Two months later, when an AE asks "what did we discuss with [brand] in March", finding the transcript means scrolling Fireflies looking for a meeting title that may or may not include the brand name.

This pipeline files every transcript into the right brand folder automatically. The brand disambiguation step is the hard part — and it is done by Claude, not by string-match.

## The architecture

```
   Fireflies webhook fires
            │
            v
   ┌─────────────────────────────┐
   │  Fetch transcript           │  POST api.fireflies.ai
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Internal call?             │  All participants @growisto.com?
   │  (decision diamond)         │
   └────────┬───────────┬────────┘
            │ Yes       │ No (external)
            v           v
       Skip & stop      │
       no storage       │
                        v
                ┌───────────────────────────────┐
                │  Extract raw brand hint       │
                │  1. From meeting title        │
                │  2. Fallback: non-Growisto    │
                │     participant email domain  │
                └────────────┬──────────────────┘
                             │
                             v
                ┌───────────────────────────────┐
                │  List all existing brand      │  Google Drive API
                │  folders in Drive             │
                └────────────┬──────────────────┘
                             │
                             v
                ┌───────────────────────────────┐
                │  Claude · Brand               │  Given: raw hint + folder list
                │  Disambiguation               │  Identify exact brand entity
                │                               │  Detect sub-brand conflicts
                │                               │  Example handling:
                │                               │  "Dove (Chocolate)" ≠ "Dove (Personal Care)"
                │                               │  "boAt" ≈ "boAt Logistics" → same folder
                └────────┬──────────────────────┘
                         │
                         v
                ┌──────────────────────────────┐
                │  Exact / fuzzy match in      │
                │  Drive?                      │
                └─────┬────────────────┬───────┘
                      │ Yes            │ No (new brand)
                      v                v
                Use existing       Create new brand
                folder             folder in Drive
                      │                │
                      └────────┬───────┘
                               v
                ┌──────────────────────────────┐
                │  Search subfolders:          │
                │  - Transcripts/              │
                │  - Summaries/                │
                │  Missing? Create them.       │
                └──────────────┬───────────────┘
                               │
                               v
                ┌──────────────────────────────┐
                │  Upload transcript           │  Stored as-is (any language)
                │  to Transcripts/             │  Hindi / English / mix — no change
                └──────────────┬───────────────┘
                               │
                               v
                ┌──────────────────────────────┐
                │  Read transcript             │
                │  → Claude generates          │  Translate if needed
                │     English summary          │  Key points + action items
                └──────────────┬───────────────┘
                               │
                               v
                ┌──────────────────────────────┐
                │  Upload English summary      │
                │  to Summaries/               │
                └──────────────┬───────────────┘
                               │
                               v
                ┌──────────────────────────────┐
                │  Filter recipients           │
                │  Keep only @growisto.com     │
                │  attendees from the call     │
                └──────────────┬───────────────┘
                               │
                               v
                ┌──────────────────────────────┐
                │  Send email                  │
                │  Body: English summary +     │
                │  Drive link                  │
                │  Clients excluded            │
                └──────────────────────────────┘
```

## The architecture choices that matter

**Claude does the brand disambiguation.** The naive approach is to string-match the meeting title against folder names. That breaks the moment a meeting is titled "Quick sync" or when a brand has subsidiaries ("Dove Chocolate" vs "Dove Personal Care"). Claude gets the raw hint, the full existing folder list, and decides which existing brand matches or whether a new brand folder is warranted. The disambiguation prompt is short and tight: "Given a raw hint and an existing folder list, return the canonical brand identity, with a confidence rating and your reasoning."

**Internal calls are silently skipped.** If all participants are `@growisto.com`, the meeting is internal and not stored as client intel. The check is done at the start of the workflow before any expensive operations run.

**Transcript stored as-is, summary always in English.** The transcript keeps the original language (Hindi, English, mix). The summary is always translated to English so anyone on the team can search and skim it. This costs more in tokens than English-only would, but the trade-off is right for an India-USA team where half the team prefers English-skim.

**Clients excluded from the summary email.** The summary email goes only to internal `@growisto.com` attendees of the call. Clients are filtered out. This is a real guardrail — accidentally summarising a client's own meeting back to them with internal notes would be embarrassing at best, brand-damaging at worst.

**Pre-existing summary refinement (rolled back).** A version tried to use n8n's "simple memory" to take an existing brand's prior summary and produce a refined cumulative summary on each new meeting. It did not work well in production — the cumulative summary drifted off-topic over time. Rolled back to per-meeting summaries with the brand folder as the natural organising structure. Documented in the project tracker as a real research-and-development cycle that closed with "this path does not work here".

## Numbers

- **Coverage** · 100% of external Fireflies meetings get processed (internal meetings auto-skipped at the start)
- **Multi-language** · Hindi, English, and Hindi-English mixed meetings all process correctly
- **Brand disambiguation accuracy** · Manually spot-checked; the Claude step matches the correct brand folder above 95% of the time. Mistakes (when they happen) trigger an email alert to the AI tools group so a human can move the file.
- **Manual time saved** · Approximately 3 to 4 hours per week of file-organising work that the team used to do by hand

## Why this pattern transfers

Any workflow that needs to file documents into a canonical structure across a messy human-titled stream fits this shape:

- Calendar invites filed into project folders
- Support tickets routed to product teams
- Job applications filed by role
- Inbound contracts filed by client
- Press mentions filed by brand

In every case the architecture is the same. Webhook fires, extract raw hint, list existing canonical structure, Claude does the disambiguation, file accordingly. The Claude step is the only part that has to be smart. The rest is plumbing.

## Stack

n8n · the orchestrator
Fireflies · meeting recording, transcript and webhook
Google Drive · storage of canonical brand folders, each with Transcripts and Summaries subfolders
Claude · brand disambiguation + summary generation
Email · sent from n8n SMTP node to the internal `@growisto.com` recipients of the call only

## What is in scope, what is not

In scope · Auto-file external meeting transcripts and summaries. Auto-create brand folders for new brands. Translate non-English transcripts to English in the summary step. Email summary to internal attendees.

Not in scope · Auto-deleting old meetings (handled separately). Auto-tagging speakers by name beyond what Fireflies provides. Cross-meeting brand summaries (the rolled-back R&D — kept as per-meeting only).
