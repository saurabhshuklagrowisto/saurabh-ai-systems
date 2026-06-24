"""
cliq-bot-parsing.py

Sanitised example of the parsing logic in the Workflow 3 Cliq Bot.
Real production version is internal to Growisto; this file shows the
exact parsing patterns and the title priority ladder.

When an SDR drops a message in the #abm-leads channel, the bot needs to
figure out what kind of input it is (LinkedIn profile URL, LinkedIn
company URL, raw domain, or plain company name) and route to the right
Apollo endpoint accordingly.

The four parsing patterns and the title priority ladder are the
production rules. The Apollo API call is stubbed with comments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

# -----------------------------------------------------------------------------
# Parsing patterns
# -----------------------------------------------------------------------------

LINKEDIN_PROFILE_RE = re.compile(
    r"linkedin\.com/in/([a-zA-Z0-9-]+)/?",
    re.IGNORECASE,
)

LINKEDIN_COMPANY_RE = re.compile(
    r"linkedin\.com/company/([a-zA-Z0-9-]+)/?",
    re.IGNORECASE,
)

# Generic domain pattern. We then check against a skip list.
DOMAIN_RE = re.compile(
    r"\b([a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?\b"
)

# Domains we explicitly skip — these are tools/platforms, not target accounts.
SKIP_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "github.com",
    "youtube.com", "instagram.com", "facebook.com",
    "drive.google.com", "docs.google.com", "sheets.google.com",
    "zoho.com", "zoho.in", "growisto.com",
    "apollo.io", "hubspot.com", "salesforce.com",
    "gmail.com", "yahoo.com", "outlook.com",
}

# -----------------------------------------------------------------------------
# Title priority ladder (lower = better match for marketing buyer)
# -----------------------------------------------------------------------------

TITLE_PRIORITY: dict[str, int] = {
    # Tier 1 · ideal buyer
    "cmo": 1,
    "chief marketing officer": 1,
    "vp marketing": 2,
    "vp growth": 3,
    "vp ecommerce": 3,
    "head of marketing": 4,
    "head of growth": 5,
    "head of ecommerce": 5,
    "head of digital": 5,
    "marketing director": 6,
    "director of marketing": 6,
    "director of ecommerce": 7,
    "director of growth": 7,
    # Tier 2 · operator or sponsor
    "general manager": 8,
    # Tier 3 · fallback when no marketing role found
    "ceo": 9,
    "founder": 9,
    "co-founder": 9,
    "coo": 10,
    "president": 10,
    "cto": 11,
}


# -----------------------------------------------------------------------------
# Input classification
# -----------------------------------------------------------------------------


@dataclass
class CliqInput:
    """A parsed message from the #abm-leads Cliq channel."""

    raw_message: str
    input_type: Literal[
        "linkedin_profile", "linkedin_company", "domain",
        "company_name", "unparseable",
    ]
    value: str   # the slug, the domain, or the company name


def classify_cliq_message(text: str) -> CliqInput:
    """Decide how to route this message to Apollo.

    Order of detection matters: LinkedIn URLs are more specific than
    raw domains, so we check them first.
    """

    # 1. LinkedIn profile URL
    if m := LINKEDIN_PROFILE_RE.search(text):
        return CliqInput(
            raw_message=text,
            input_type="linkedin_profile",
            value=m.group(1),
        )

    # 2. LinkedIn company URL
    if m := LINKEDIN_COMPANY_RE.search(text):
        return CliqInput(
            raw_message=text,
            input_type="linkedin_company",
            value=m.group(1),
        )

    # 3. Domain (after filtering out tools/platforms)
    for m in DOMAIN_RE.finditer(text):
        candidate = m.group(1).lower()
        # Strip leading "www." if any matched
        candidate = candidate.removeprefix("www.")
        # Skip tool/platform domains
        if candidate in SKIP_DOMAINS:
            continue
        # Skip if it's part of an email address (caught after @ sign)
        if f"@{candidate}" in text.lower():
            continue
        return CliqInput(
            raw_message=text,
            input_type="domain",
            value=candidate,
        )

    # 4. Fallback — treat the whole message as a plain company name.
    # Strip common politeness words and pull the longest noun-phrase-looking chunk.
    cleaned = text.strip().rstrip(".?!,")
    if 2 <= len(cleaned) <= 80 and not cleaned.startswith(("hi ", "hey ", "ok ", "thanks")):
        return CliqInput(
            raw_message=text,
            input_type="company_name",
            value=cleaned,
        )

    return CliqInput(
        raw_message=text,
        input_type="unparseable",
        value="",
    )


# -----------------------------------------------------------------------------
# Apollo routing (stubbed)
# -----------------------------------------------------------------------------


def route_to_apollo(parsed: CliqInput) -> dict:
    """Dispatch to the right Apollo endpoint based on input type.

    The real implementation calls the Apollo API. This stub describes
    what each branch would do.
    """

    if parsed.input_type == "linkedin_profile":
        # apollo.people_match(linkedin_url=...)
        # Returns: phone, verified email, current job title
        return {
            "endpoint": "apollo_people_match",
            "input": {"linkedin_url": f"https://linkedin.com/in/{parsed.value}"},
            "expect": "single person record with contact data",
        }

    if parsed.input_type == "linkedin_company":
        # apollo.organizations_enrich(linkedin_url=...)
        # Then apollo.mixed_people_api_search() against the resolved domain
        return {
            "endpoint": "apollo_organizations_enrich + mixed_people_api_search",
            "input": {"linkedin_url": f"https://linkedin.com/company/{parsed.value}"},
            "expect": "company record + ranked list of marketing buyers",
        }

    if parsed.input_type == "domain":
        # apollo.organizations_enrich(domain=...)
        # Then apollo.mixed_people_api_search(organization_domains=[domain])
        return {
            "endpoint": "apollo_organizations_enrich + mixed_people_api_search",
            "input": {"domain": parsed.value},
            "expect": "company record + ranked list of marketing buyers",
        }

    if parsed.input_type == "company_name":
        # apollo.mixed_companies_search(q=...)
        # Disambiguation step if multiple candidates returned
        return {
            "endpoint": "apollo_mixed_companies_search",
            "input": {"query": parsed.value},
            "expect": "candidate company list, disambiguate then enrich",
        }

    return {
        "endpoint": None,
        "input": None,
        "expect": "send back a 'sorry, could not parse' message to the channel",
    }


# -----------------------------------------------------------------------------
# Rank Apollo people results by title
# -----------------------------------------------------------------------------


def rank_by_title(people: list[dict]) -> list[dict]:
    """Sort a list of Apollo people records by title priority.

    Each person is a dict with at least: name, title, email, phone, linkedin_url.
    Lower priority number = more senior marketing role = sorted first.
    Unmatched titles get a fallback priority of 99.
    """

    def priority_for(title: str) -> int:
        t = (title or "").lower().strip()
        # Exact match first
        if t in TITLE_PRIORITY:
            return TITLE_PRIORITY[t]
        # Contains-match for compound titles like "VP Marketing & Growth"
        for key, score in TITLE_PRIORITY.items():
            if key in t:
                return score
        return 99

    return sorted(people, key=lambda p: priority_for(p.get("title", "")))


# -----------------------------------------------------------------------------
# Quick test
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    test_messages = [
        "Hey can we get POCs for https://linkedin.com/in/jane-doe-cmo?",
        "Please enrich linkedin.com/company/acme-corp/",
        "We're targeting acmewidgets.com — need the marketing decision maker",
        "Need POC at SkyHigh Fashions, mid-market India D2C",
        "thanks!",
    ]

    print(f"{'Type':<22} {'Value':<40} Route")
    print("-" * 90)
    for msg in test_messages:
        parsed = classify_cliq_message(msg)
        route = route_to_apollo(parsed)
        print(f"{parsed.input_type:<22} {parsed.value:<40} {route['endpoint']}")

    # Output:
    # linkedin_profile       jane-doe-cmo                             apollo_people_match
    # linkedin_company       acme-corp                                apollo_organizations_enrich + ...
    # domain                 acmewidgets.com                          apollo_organizations_enrich + ...
    # company_name           Need POC at SkyHigh Fashions, mid-market ... apollo_mixed_companies_search
    # unparseable                                                     None
