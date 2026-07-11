#!/usr/bin/env python3
"""
Website Conversion Audit — deterministic scoring engine.

Takes a structured set of observations about a B2B page and returns findings
ranked by revenue impact (P0 > P1 > P2). No dependencies, no API keys.

Observation schema (all optional; omitted keys are treated as "unknown", not a finding):
{
  "hero_states_what_and_for_whom": bool,   # can a buyer tell what this is + who it's for in 5s
  "primary_cta_count": int,                 # number of DISTINCT primary CTAs on first screen
  "primary_cta_works": bool,                # does the main CTA actually work / not broken
  "self_serve_asset_on_homepage": bool,     # is the strongest low-friction asset (free trial/demo) surfaced
  "form_field_count": int,                  # number of required fields
  "form_has_company_field": bool,           # can marketing route/score the lead
  "proof_above_the_fold": bool,             # logos / numbers / security visible before the ask
  "mobile_ok": bool,                        # does it hold up on mobile
  "broken_links": int                       # count of dead/broken primary paths
}
"""
import json, sys

def audit(o):
    f = []  # findings

    # --- FLOW (broken things leak conversions immediately) ---
    if o.get("primary_cta_works") is False:
        f.append(("Flow","P0","The primary CTA does not work",
                  "A broken main action means every click intending to convert is lost. This is pipeline leaking in real time.",
                  "Fix the CTA target/handler so it routes to the intended booking or sign-up flow.",
                  "Track clicks vs completions on the CTA; target near-zero drop between click and next step."))
    if o.get("broken_links",0) > 0:
        f.append(("Flow","P0",f"{o['broken_links']} broken primary path(s) found",
                  "Dead links on conversion paths silently kill intent.",
                  "Repair or remove the broken paths; add uptime monitoring on conversion routes.",
                  "Zero broken links on any path that leads to the primary CTA."))

    # --- CLARITY ---
    if o.get("hero_states_what_and_for_whom") is False:
        f.append(("Clarity","P1","Hero does not say what this is or who it is for",
                  "If a buyer cannot place the product in 5 seconds, they leave before reaching the CTA.",
                  "Rewrite the hero as an outcome for a named buyer, e.g. 'Ramp reps in 15 days, not 90 — for enterprise sales teams.'",
                  "5-second test with 5 target-persona users; 4/5 should describe the product correctly."))

    # --- CTA ---
    n = o.get("primary_cta_count")
    if n is not None and n > 1:
        f.append(("CTA","P1",f"{n} competing primary CTAs on the first screen",
                  "More than one primary action splits attention and lowers the rate on all of them.",
                  "Pick one primary action; demote the rest to secondary styling.",
                  "A/B test single vs multiple primary CTA; measure primary-action click rate."))
    if o.get("self_serve_asset_on_homepage") is False:
        f.append(("CTA","P0","The strongest low-friction asset is hidden from the homepage",
                  "A free trial / instant demo converts far better than a 'contact us' form, but only if visitors can find it.",
                  "Surface the self-serve asset as a primary homepage CTA alongside the sales CTA.",
                  "Track % of conversions coming through the self-serve path; target 30%+."))

    # --- FORM ---
    fc = o.get("form_field_count")
    if fc is not None and fc > 4:
        f.append(("Form","P1",f"The form asks for {fc} fields",
                  "Every extra required field measurably lowers completion.",
                  "Cut to name, work email, and one qualifier. Enrich the rest automatically after submit.",
                  "Measure completion rate before/after; expect an 8-15% lift from trimming alone."))
    if o.get("form_has_company_field") is False:
        f.append(("Form","P0","The form cannot be routed or scored (no company field)",
                  "Without company/role, marketing cannot score or route the lead and sales walks in blind.",
                  "Add a company field (and enrich role/size via Clay/Apollo on submit).",
                  "% of new leads with a resolvable company; target 95%+."))

    # --- TRUST ---
    if o.get("proof_above_the_fold") is False:
        f.append(("Trust","P1","Proof is not visible before the ask",
                  "Buyers need a reason to believe before they act; proof buried below the fold arrives too late.",
                  "Move customer logos, a hard ROI number, and a security badge above the fold.",
                  "Scroll-depth to proof vs conversion; proof should sit in the first viewport."))

    # --- FLOW: mobile ---
    if o.get("mobile_ok") is False:
        f.append(("Flow","P1","The page breaks or degrades on mobile",
                  "A large share of B2B first-touches are mobile; a broken mobile view loses them silently.",
                  "Fix responsive layout on the hero, CTA, and form specifically.",
                  "Mobile vs desktop conversion rate; close the gap."))

    order = {"P0":0,"P1":1,"P2":2}
    f.sort(key=lambda x: order[x[1]])
    findings = [{"pillar":p,"severity":s,"what":w,"why":why,"fix":fix,"measure":m}
                for (p,s,w,why,fix,m) in f]

    p0 = sum(1 for x in findings if x["severity"]=="P0")
    verdict = (f"{len(findings)} findings, {p0} are P0 (fix this week). "
               "Performance is not the constraint; the funnel is." if findings
               else "No conversion leaks detected in the observed elements.")
    pillars = {}
    for x in findings:
        pillars[x["pillar"]] = pillars.get(x["pillar"],0)+1
    return {"verdict":verdict,"pillar_findings":pillars,"findings":findings}

SAMPLE = {
    "url": "https://example-saas.com",
    "hero_states_what_and_for_whom": False,
    "primary_cta_count": 2,
    "primary_cta_works": False,
    "self_serve_asset_on_homepage": False,
    "form_field_count": 5,
    "form_has_company_field": False,
    "proof_above_the_fold": True,
    "mobile_ok": True,
    "broken_links": 0
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        obs = json.load(open(sys.argv[1], encoding="utf-8"))
        url = obs.get("url","(provided file)")
    else:
        obs, url = SAMPLE, SAMPLE["url"]
    result = audit(obs)
    result = {"url": url, **result}
    print(json.dumps(result, indent=2))
