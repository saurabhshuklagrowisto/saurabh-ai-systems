# Website lead intake and reply routing for Close CRM

Three serverless endpoints that close the loop between a website contact form, a CRM, and the
humans who work the pipeline. Running in production. Node 18+, no dependencies, no framework.

| File | Job |
|---|---|
| [`api/lead.js`](./api/lead.js) | Website form submission to a deduped Close lead |
| [`api/reply.js`](./api/reply.js) | Close webhook listener that classifies inbound replies and sets status |
| [`api/digest.js`](./api/digest.js) | One scheduled GET a day, groups yesterday's replies, posts to Slack |
| [`test/classify.test.mjs`](./test/classify.test.mjs) | Ten classifier cases including a real misread and a quoted email thread |

Account-specific Close status and custom field ids are replaced with `stat_REPLACE_*` and
`cf_REPLACE_*` placeholders. Everything else is the code as deployed.

## Why it exists

A CRM workflow can stop chasing someone when they reply. That is the goal criteria, and Close does
it well. What Close cannot do is act on the reply, because it has no inbound message trigger. So a
person who replies stops getting chased and then sits in "Called 2" forever. Nobody reads the
negative ones. Nobody notices the pattern in them.

That gap is where the expensive failure lived. One reply in the set was a director reading our
outbound as a job offer aimed at him personally. It was not a deliverability problem or a targeting
problem. The copy was ambiguous enough to read as recruitment, and no human saw the reply for days.

So the classifier has a dedicated `job_misread` class that is not about that one lead. It is a
smoke alarm. A spike in that row means the copy that went out this week reads as a job pitch again,
and the digest puts it in front of someone the next morning.

## Intake, `api/lead.js`

Per submission:

1. Validate the email, pull the domain from it.
2. Look for an existing lead on that domain. **Dedup is by domain, never by person name.**
3. Match found: add the person as a contact, only if that email is not already there, then post a note.
4. No match: create the lead with the contact, then post the full submission as a note.

Written fields: lead name (company from the form, else the domain label), status Fresh Lead, Lead
Source "Website Form", Referral Source "Website", Company Website the email domain.

**Job Source is left empty on purpose.** That field drives the scraper-output views. An inbound form
lead written into a scraper view corrupts the one number those views exist to report. The comment in
the code says not to helpfully add it, because the next person to read this file will want to.

Honest limits, stated in the file rather than hidden:

- A company name derived from a domain is a guess. `whitfieldgroup.com` becomes "Whitfieldgroup".
  Passing `company` from the form avoids it. An SDR fixes it on first touch.
- Free email domains skip domain dedup and name the lead after the person. The note flags it.
- The submitter is recorded as a contact, not as a confirmed decision maker. Nothing in the payload
  can tell the difference, so a human checks.
- A failed push returns 500 and logs. It never swallows the error. A silent failure here is a lost
  inbound lead, which is the most expensive kind.

## Reply routing, `api/reply.js`

| Reply reads as | Status set | In the digest |
|---|---|---|
| Opted out (stop, unsubscribe, remove me) | Do Not Contact | yes |
| Read our outbound as a job offer aimed at them | Not Interested | yes |
| Points at a different person | engaged | yes |
| Negative (not interested, role filled, all set) | Not Interested | yes |
| Positive (rates, book a time, send profiles) | engaged | no |
| Anything else with words in it | engaged | no |
| Out of office | untouched | no |
| Bounce | untouched | yes |

Two states it refuses to touch: a lead already in Do Not Contact, and one already in Discovery Call.
A human put it there, and a stray auto-reply must not undo a human decision.

Outbound activity is ignored, so our own sends never move a lead. Email replies are cut at the quoted
thread before classification, otherwise our own copy votes on the sentiment of the reply to it.

## Digest, `api/digest.js`

One GET a day, on a cron. It reads the listener's notes from the last 24 hours, groups them, posts to
a Slack webhook, and returns the same report as JSON.

The digest reports, it does not decide. Every status was already set in real time by the listener. A
digest that fails to send is a missing report, not a missing status change. That split is the whole
design: the thing that runs on a schedule is never the thing that holds the state.

## Running it

```bash
node test/classify.test.mjs
```

Ten cases, no framework, no install. Deploy `api/*.js` to any serverless host (Vercel `api/`,
Netlify `netlify/functions/`, or wrap the handler in a Next.js route export). Set the environment
variables from [`.env.example`](./.env.example) in the host, never in code.

Two secrets actually matter. `CLOSE_API_KEY` writes to live CRM data, so it lives in host env vars
and nowhere else. `CLOSE_WEBHOOK_SIGNATURE_KEY` is shown once by Close when the subscription is
created, and without it the reply endpoint accepts anything that can reach the URL.

Verification before you trust it: run the intake test twice. The second run must report
`attached_to_existing`, not create a twin lead.
