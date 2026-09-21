# Email Verification Gate

A hard gate between a lead pipeline and the CRM. No email address reaches Close CRM or SalesBlink without a verification verdict on it, an unproven address is held rather than pushed, and an address that already holds a verdict never costs a second credit.

This is the piece of outbound infrastructure nobody puts in a portfolio and every outbound team pays for twice: once in bounced sends against a warmed domain, and once in verification credits burned re-checking the same addresses every run.

## The rule

Three lines, enforced in code rather than in a runbook.

1. **No verdict, no push.** Every source is covered: people-search exports, registry enrichment, CSV imports, manually typed addresses. An address with no verdict is treated exactly like an address that failed.
2. **Only a clean verdict ships.** Catch-all and unknown are held, not pushed. Any status the verifier returns that the code does not recognise is held too, because an unrecognised status is not a verdict anyone can stand behind.
3. **Never buy the same verdict twice.** Verdicts are cached by lowercased address in a JSON file that survives runs, bands, re-exports and re-scrapes. A cached address is never sent to the API again.

## Why the cache is the product

The obvious reading of a verdict cache is a performance optimisation. It is not. Verification is metered, the same lead base gets re-scraped and re-exported every week, and without a durable cache a pipeline re-bills the entire base on every run.

Two consequences shaped the code:

**A corrupt cache file stops the run.** The loader refuses to fall back to an empty dict on a JSON parse error. An empty cache looks harmless and quietly bills the whole base a second time, so the failure is made loud and a human looks at the file.

**Writes are atomic.** The cache is written to a temp file and moved into place, so a crash mid-write leaves the previous cache intact rather than a truncated file that fails to parse on the next run.

There is also a read-only mode. It answers "what do we already know about these addresses" without touching a credit, which is what a pre-flight checker wants.

## The verdict table

The verifier answers with a bare status word, not JSON. Those words are grouped into three buckets plus a fourth for request failures.

| Bucket | What happens | Examples |
|---|---|---|
| **Pass** | Ships to the CRM | `ok` |
| **Fail** | Address is dead, dropped permanently | `fail`, `invalid`, `email_disabled`, `domain_disabled`, `disposable`, `spamtrap` |
| **Hold** | Unproven, kept out of the CRM | `ok_for_all` (catch-all), `accept_all`, `unknown`, `antispam_system`, `attempt_rejected`, `role` |
| **Request error** | Nothing cached, no credit counted, surfaced as an error | `key_not_valid`, `no_connect`, `timeout` |

Anything outside these lists falls through to **Hold**. That default matters more than the lists do: a verifier adds status words over time, and a fail-open default would quietly start pushing unproven addresses the first time one appeared.

## A held email does not drop the lead

The address is held, not the person. A contact whose email is held keeps their phone number and stays in the push. Only if they have no reachable channel at all do they fall through to the unreachable bucket, exactly as a contact with no details always did.

This sounds obvious and was the single most common bug in earlier versions. Dropping the whole record on a catch-all domain silently deleted usable phone-reachable contacts from the pipeline.

## Two gates, not one

The gate that runs before push is the last line of defence, not the fix.

An early run failed with twelve violations in one batch, every one a catch-all or antispam address the exporter had written into the CSV without ever asking the verifier. Blocking at the gate was correct and useless: the run was already dead, and the temptation was to hand-edit the CSV to get it through.

So the check moved to the stage that creates the row. The exporter asks for verdicts while building contacts and drops an address it cannot prove. The pre-push gate stayed in place and now almost never fires, which is what a last line of defence should look like.

## Test coverage

The rule has two halves and both are tested against the real module, not a mock of it.

The verdict cases run the actual gate over a one-row CSV: no email at all passes (the rule does not apply), an email with no verdict is blocked, `ok` passes, a dead address is blocked, catch-all is blocked, unknown is blocked, an invented status is blocked, and verdict matching is case-insensitive.

The credit rule is tested with a landmine. The API call function is replaced with one that raises, then the verifier is asked to check an address that already holds a verdict, in three spellings with different case and whitespace. If the cache is consulted correctly the landmine is never reached. If a cached address is ever re-sent, the test fails. Re-billing a verified address is treated as a defect, not as a slightly wasteful outcome.

## Key handling

The API key lives in exactly one file outside every repo, with an environment variable taking precedence when it is set. No key in the pipeline, no key in the CSV exports, nothing to commit by accident. The key file is read at call time and never logged.

## What it reports

Every run prints the same three numbers: addresses checked, cached and skipped, credits actually spent. A run that spends more than a handful of credits on a base that has been verified before is a bug, and the number makes that visible without anyone having to go look at a billing page.

## Stack

Python 3 standard library only, no dependencies · EmailListVerify API · JSON verdict cache on disk · Close CRM and SalesBlink as the downstream systems the gate protects

## Why this transfers

Any metered enrichment or verification API sitting in front of a system of record has the same three problems: unverified records leaking through, unproven records being treated as proven, and the same records being re-billed on every run. Swap the verifier, keep the shape: a normalised cache key, a durable cache that fails loudly, an explicit verdict table with a fail-closed default, the check at the stage that creates the record, and a credit-spend test that fails the build.
