# Building pages for answer engines, not just search engines

A ten-page service section rebuilt so that an AI assistant can quote it correctly, and so that it
cannot quote the things we do not want it to say.

Architecture write-up. The pages themselves are a live client site, so they are not in this repo.

## The shift this is built around

Classic SEO optimises for a click. An answer engine never gives you the click. It reads the page,
compresses it, and repeats a version of it to someone who will never see your site. So there are two
new questions that ranking does not answer:

1. When it quotes us, does it quote the right sentence?
2. When it does not know something about us, what does it say instead?

The second one is where the damage lives. A model asked "how much does this cost" will answer. If the
page does not say, it will reach for a plausible number from a competitor or from thin air, and the
prospect arrives anchored to a price nobody quoted.

## `llms.txt`, written as a brief with boundaries

The site publishes an `llms.txt`: a plain-language brief of what the company does, the service list
with one line each, and how the process works. Standard so far.

The section that earns its place is the last one, notes for AI systems, and it is written in
negatives:

- Rates are quoted per client and are not published. **Any figure attributed to our pricing did not
  come from us.**
- Assistants work inside the client's existing tools. We do not claim prior hands-on experience in
  specific named software platforms.
- We do not currently state round-the-clock coverage.

Each line exists because it is a claim a model would otherwise invent, and each one is a claim that
would be caught on the first sales call. Stating the boundary is cheaper than correcting the
inference.

Writing the negative space is the part most `llms.txt` files skip. A brief that only lists strengths
gives a model nothing to refuse with.

## Answer-first page structure

Every page opens with a heading that matches the question, followed by a single self-contained
paragraph marked `.answer` that resolves it without needing the rest of the page.

The schema then points at that block explicitly:

```json
"speakable": {
  "@type": "SpeakableSpecification",
  "cssSelector": ["h1", ".answer"]
}
```

That pair is the whole trick. The page names the passage it wants quoted, and the passage is written
to survive being lifted out of its context. If it only makes sense with the two paragraphs above it,
it is not an answer, it is an introduction.

## One entity graph, not ten copies of a company

Each page ships a single JSON-LD `@graph` whose nodes cross-reference by `@id` rather than repeating
the company object:

| Node | Role |
|---|---|
| `WebSite` | site root, publisher points at the organization |
| `Organization` | the one canonical company entity: name, logo, email, phone, postal address, area served |
| `WebPage` | this page, `isPartOf` the site, `mainEntity` the service, plus `speakable` |
| `BreadcrumbList` | position in the section hierarchy |
| `Service` | service type, provider, audience, and a `hasOfferCatalog` of the concrete tasks |
| `FAQPage` | five questions with full-sentence answers, including the pricing question answered honestly as "quoted individually" |

Ten pages, one organization `@id`. A resolver that walks the graph sees a single entity described
from ten angles instead of ten similar companies. `hasOfferCatalog` is what turns a vague service
page into a list a model can enumerate: inbound call answering, live chat, order processing,
appointment booking.

The FAQ answers are written at full-sentence length on purpose. A three-word answer is unquotable,
so it gets paraphrased, and paraphrase is where the wrong claim enters.

## Shipping into a CMS that will not take a head tag

The live site runs on a hosted builder with no raw `<head>` access, so the build emits three
artifacts per page instead of one:

| Artifact | Goes where |
|---|---|
| `<page>.embed.html` | the page body, as a self-contained embed with inline critical CSS |
| `<page>.jsonld.json` | the structured data block, pasted into the platform's custom-code slot |
| `<page>.seo.json` | title and meta description, typed into the platform's own SEO panel |

Thirty-one files for ten pages. Unglamorous, and it is the reason the section could actually be
handed to someone else to deploy without a developer.

## The staging copy that could have cost the section

The preview deploy carries canonical URLs pointing at the production domain, which does not serve
those pages yet. Left alone, the preview is a perfect duplicate of pages that do not exist, indexable
before the real ones ship.

So the review copy ships with both belts on:

```
# robots.txt, review copy
User-agent: *
Disallow: /
```

```
# _headers
/*
  X-Robots-Tag: noindex, nofollow
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
```

`robots.txt` asks crawlers not to fetch. `X-Robots-Tag` covers the case where something fetched the
URL anyway, from a link or a share. Both, because the two failure modes are different and only one of
them is polite.

## Details that are easy to skip and worth not skipping

The palette came from the client's own brand kit, including a brand colour the live site had never
used. One shade got darkened by two percent, purely so white text on it clears 4.5:1 contrast rather
than sitting at 4.47:1. Nobody will ever notice. It is the difference between passing an audit and
explaining one.

## What transfers

- Publish an `llms.txt` and put real boundaries in it. The refusals matter more than the features.
- Mark the passage you want quoted, and write it so it survives being lifted out.
- One organization entity, referenced by `@id`, not copied per page.
- Answer the pricing question in words even when the answer is "we do not publish a number", because
  silence gets filled in by a model that has no reason to be careful with your numbers.
- Any staging copy of a page that carries a production canonical needs both `robots.txt` and an
  `X-Robots-Tag` header before it goes up.
