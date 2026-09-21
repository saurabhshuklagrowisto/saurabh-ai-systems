# Cold email infrastructure at 152 mailboxes

An audit and rebuild of a B2B outbound sending estate: three lookalike sending domains, 152
Microsoft 365 mailboxes, full DNS authentication, and a launch that did not happen on schedule for
two reasons nobody had written down.

This is an architecture and diagnosis write-up. The artifacts it describes hold live mailbox
credentials and a client contact list, so none of them are in this repo.

## The estate

| Thing | State |
|---|---|
| Sending domains | 3 live lookalikes, registered 11 to 13 months earlier. The root business domain is never used to send. |
| Mailboxes | 152 across the three, provisioned by a third-party domain and mailbox vendor |
| MX | Microsoft 365 on all three |
| SPF | One record per domain, `-all` hard fail. Exactly one, because two SPF records is an automatic fail. |
| DKIM | `selector1` and `selector2` both resolving to Microsoft, so a full two-key rotation set |
| DMARC | `p=quarantine; pct=100` with `rua` reporting, aggressive from day one |
| Blacklists | 45 of 45 DNSBL and URIBL families returned not listed, on all three domains |
| Landing behaviour | All three redirect to the real business website |

That last row is the one most cold setups get wrong. When a spam filter or a curious recipient
resolves the sending domain, it should land on a real company, not a parked "domain for sale" page.
It costs one redirect and it moves inbox placement.

## What the audit actually changed

The account had been assumed healthy and assumed to be warming. Both were checked directly rather
than read off a dashboard summary, and the second one was false.

**Nothing had been warming.** The provisioning vendor's product is domain registration, DNS and
authentication records, and mailbox creation. It does not warm mailboxes. Its own analytics page
said so, in the form of an empty state asking to connect a sending tool. The earlier claim of native
AI warmup came from third-party review-site marketing copy, not from the account. Twelve months of
assumed warmup was twelve months of nothing.

**Auto-renew was off** on domain registration for the live domains. A sending estate with a year of
age on it is the asset. Silent expiry would have destroyed the only thing that cannot be bought back
quickly, with no warning louder than a modal nobody had clicked through.

**Nineteen more provisioned domains were sitting unpaid**, carrying between 50 and 103 mailboxes
each. That reframes the capacity question: the reinstatement decision is worth several times the
live estate, not a marginal top-up.

**All 152 mailboxes were one persona**, local-part permutations of a single name. Fine for
provisioning, wrong for send rotation, because one persona across 152 mailboxes means one reputation
event lands everywhere at once.

## The failure worth reading

Warmup was wired by building a bulk sender import: all 152 mailboxes converted into the sending
tool's exact CSV template, SMTP and IMAP hosts set, warmup enabled, ramp from 5 with a daily
increment, daily cap pre-set at 25 so the rows were inert until a sequence existed.

All 152 rows imported. Every single one failed warmup connection with the same generic error.
Retrying one by hand reproduced it exactly, so it was not transient.

The cause was not in the tool. Microsoft has been retiring Basic Authentication for SMTP and IMAP,
and a bulk CSV of mailbox passwords is Basic Authentication by definition. The corroborating detail
was in the provisioning vendor's own help center: its supported integration path names three specific
sending tools and nothing else. There is no generic SMTP credential path any more, and there was not
going to be one.

The fallback existed and was also wrong: the sending tool's Microsoft OAuth connector would very
likely have worked, and requires an interactive browser sign-in per mailbox. At 152 mailboxes that is
not a fallback, it is a different project.

The lesson I took: at this scale, authentication method is an architecture decision, not a setup step.
Choosing the sending tool before checking how it authenticates to the mailbox provider is how a
twelve-month-old estate ends up unable to send.

## The blocker nobody expects

While the mailbox side was being fixed, the recipient side was quietly the harder constraint.

The qualified account list ran to 52 companies. Usable decision-maker email addresses: about seven.

The enrichment pipeline had been built to return **phone numbers**, because the CRM push rules
required a named decision maker and a phone. So the contact sheet held 591 entries and zero email
addresses. The handful of addresses that did exist were `hr@`, `humanresources@` and
`candidatequestions@`, which are application inboxes. Sending cold pitches to a careers inbox is a
direct route to a domain reputation problem.

At a 25-per-mailbox daily cap, the estate could send 400 emails a day. The campaign had seven
addresses. **Capacity was never the constraint. It had been the only thing measured.**

There was a second-order finding in the title distribution. The registry source used for enrichment
returns registry-official titles: owner, president, CEO. It structurally cannot return an office
manager. Benchmark reply rates put practice and office managers at roughly two to three times the
reply rate of the owner titles, and the list held about 14 of the former against 124 of the latter.
The enrichment source was selecting against the segment most likely to answer.

## Settings that were right, and left alone

Plain text only. Bounce threshold at 2 percent with auto-pause on. Bounce rate is the single highest
leverage lever in a cold campaign, worth more than any copy change.

Two that were wrong and cheap to fix: verify-before-send was off, and send-only-to-verified was off.
With bounce rate carrying that much weight, running verification off is the most consequential
misconfiguration in the account.

One that was silently expensive: reply-to and signature were empty on all 152 senders. A campaign
that sends into an unmonitored reply destination generates replies nobody reads, and a prospect who
replies once and hears nothing does not reply twice.

## What transfers

- Verify warmup from the provider's own account state, never from a plan document or a review site.
- Check the authentication method between sending tool and mailbox provider before buying either.
- Measure recipients before capacity. Throughput is the easy number and usually not the binding one.
- Check what your enrichment source is structurally capable of returning, not just what it returned.
- Sending domain age is the asset. Protect it first: auto-renew on, one persona per reputation blast
  radius, and a real website behind the redirect.
