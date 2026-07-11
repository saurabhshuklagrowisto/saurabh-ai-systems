#!/usr/bin/env python3
"""
eCommerce (D2C) Conversion Audit — deterministic scoring engine.

Takes structured observations about a D2C store's path to purchase and returns
findings ranked by revenue impact (P0 > P1 > P2). No dependencies, no API keys.

Observation schema (all optional; omitted keys are "unknown", not a finding):
{
  "pdp_multiple_images": bool,       # product page has multiple / zoomable images
  "pdp_benefit_led_copy": bool,      # copy sells benefits, not just specs
  "price_clearly_visible": bool,     # price obvious without hunting
  "add_to_cart_above_fold": bool,    # add-to-cart visible without scrolling
  "checkout_broken": bool,           # checkout errors / fails
  "guest_checkout": bool,            # can buy without creating an account
  "checkout_steps": int,             # number of checkout steps
  "payment_options_count": int,      # card + wallet(s) etc.
  "shipping_cost_shown_early": bool, # total incl. shipping shown before final step
  "reviews_on_pdp": bool,            # ratings/reviews on the product page
  "returns_policy_visible": bool,    # returns/refund policy easy to find
  "secure_badges": bool,             # payment-security / trust badges present
  "urgency_signals": bool,           # honest stock levels / offers
  "mobile_optimized": bool           # mobile-first buying experience
}
"""
import json, sys

def audit(o):
    f = []

    # --- CHECKOUT / COST (biggest purchase leaks) ---
    if o.get("checkout_broken") is True:
        f.append(("Checkout","P0","Checkout is broken or throwing errors",
                  "A failing checkout means paying customers cannot complete. Every cart at this step is lost revenue.",
                  "Fix the checkout errors immediately; add synthetic monitoring on the purchase path.",
                  "Track add-to-cart to purchase completion; the checkout-step drop should fall to baseline."))
    if o.get("guest_checkout") is False:
        f.append(("Checkout","P0","No guest checkout — account creation is forced",
                  "Forced account creation is one of the single biggest causes of checkout abandonment.",
                  "Enable guest checkout; offer account creation optionally after purchase.",
                  "Checkout completion rate before/after enabling guest checkout."))
    if o.get("shipping_cost_shown_early") is False:
        f.append(("Cost","P0","Shipping cost is sprung at the final step",
                  "Unexpected shipping at the last step is the #1 documented reason for cart abandonment.",
                  "Show shipping (or a threshold for free shipping) on the cart/PDP, before the final step.",
                  "Cart-to-purchase rate; abandonment at the shipping step should drop sharply."))
    cs = o.get("checkout_steps")
    if cs is not None and cs > 3:
        f.append(("Checkout","P1",f"Checkout has {cs} steps",
                  "Every extra checkout step sheds buyers. Long checkouts convert worse, especially on mobile.",
                  "Collapse to a single-page or 2-3 step checkout; remove non-essential fields.",
                  "Completion rate per step; target fewer steps and higher overall completion."))
    po = o.get("payment_options_count")
    if po is not None and po < 2:
        f.append(("Checkout","P1","Only one payment option",
                  "Shoppers abandon when their preferred method (wallet, UPI, BNPL, PayPal) is missing.",
                  "Add at least one wallet / express-pay option beside card.",
                  "Share of orders by method after adding options; watch completion lift."))

    # --- PRODUCT PAGE (PDP) ---
    if o.get("price_clearly_visible") is False:
        f.append(("Product","P1","Price is not clearly visible on the product page",
                  "If a shopper has to hunt for the price, trust drops and many leave.",
                  "Show price prominently near the product title and the add-to-cart button.",
                  "PDP bounce rate and add-to-cart rate before/after."))
    if o.get("add_to_cart_above_fold") is False:
        f.append(("Cart","P1","Add-to-cart is below the fold",
                  "If the primary buying action is not immediately visible, add-to-cart rate suffers.",
                  "Move add-to-cart above the fold; keep it sticky on scroll for mobile.",
                  "Add-to-cart click rate on the PDP."))
    if o.get("pdp_multiple_images") is False:
        f.append(("Product","P2","Product page has limited imagery",
                  "Shoppers cannot touch the product; images do the selling. Thin imagery lowers confidence.",
                  "Add multiple angles, zoom, lifestyle shots, and ideally a short video.",
                  "PDP engagement and add-to-cart rate."))
    if o.get("pdp_benefit_led_copy") is False:
        f.append(("Product","P2","Product copy is spec-led, not benefit-led",
                  "Specs inform; benefits sell. Copy that only lists features underperforms.",
                  "Lead each section with the benefit, then support it with the spec.",
                  "A/B test benefit-led vs current copy on add-to-cart rate."))

    # --- TRUST ---
    if o.get("reviews_on_pdp") is False:
        f.append(("Trust","P1","No reviews or ratings on the product page",
                  "Social proof is decisive for D2C; an absent review block lowers conversion at the exact decision point.",
                  "Add ratings and reviews to the PDP; seed with real early-customer reviews.",
                  "Add-to-cart and purchase rate on PDPs with vs without reviews visible."))
    if o.get("returns_policy_visible") is False:
        f.append(("Trust","P2","Returns / refund policy is hard to find",
                  "A clear returns policy removes purchase risk; hiding it adds hesitation.",
                  "Link the returns policy near add-to-cart and in checkout.",
                  "Checkout completion; support tickets asking about returns."))
    if o.get("secure_badges") is False:
        f.append(("Trust","P2","No payment-security or trust badges at checkout",
                  "Consumers look for security cues before entering card details.",
                  "Add recognised secure-payment badges near the payment field.",
                  "Checkout completion at the payment step."))

    # --- URGENCY + MOBILE ---
    if o.get("mobile_optimized") is False:
        f.append(("Mobile","P0","The store is not mobile-first",
                  "The majority of D2C traffic is mobile; a poor mobile buying flow loses most of your visitors.",
                  "Fix mobile PDP, sticky add-to-cart, and a mobile-optimised checkout specifically.",
                  "Mobile vs desktop conversion rate; close the gap."))
    if o.get("urgency_signals") is False:
        f.append(("Urgency","P2","No honest urgency or scarcity cues",
                  "Genuine low-stock or time-bound offers nudge decisions; none means fence-sitters drift.",
                  "Add honest stock counts or limited offers — never fake ones, which erode trust.",
                  "Add-to-cart rate on pages with vs without urgency cues."))

    order = {"P0":0,"P1":1,"P2":2}
    f.sort(key=lambda x: order[x[1]])
    findings = [{"pillar":p,"severity":s,"what":w,"why":why,"fix":fix,"measure":m}
                for (p,s,w,why,fix,m) in f]
    p0 = sum(1 for x in findings if x["severity"]=="P0")
    verdict = (f"{len(findings)} findings, {p0} are P0 (fix this week). "
               "The leak is between interested and paid, not in traffic." if findings
               else "No purchase-path leaks detected in the observed elements.")
    pillars = {}
    for x in findings:
        pillars[x["pillar"]] = pillars.get(x["pillar"],0)+1
    return {"verdict":verdict,"pillar_findings":pillars,"findings":findings}

SAMPLE = {
    "url": "https://example-d2c-store.com/products/hero-item",
    "pdp_multiple_images": True,
    "pdp_benefit_led_copy": False,
    "price_clearly_visible": True,
    "add_to_cart_above_fold": True,
    "checkout_broken": False,
    "guest_checkout": False,
    "checkout_steps": 5,
    "payment_options_count": 1,
    "shipping_cost_shown_early": False,
    "reviews_on_pdp": False,
    "returns_policy_visible": True,
    "secure_badges": False,
    "urgency_signals": False,
    "mobile_optimized": True
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        obs = json.load(open(sys.argv[1], encoding="utf-8"))
        url = obs.get("url","(provided file)")
    else:
        obs, url = SAMPLE, SAMPLE["url"]
    result = {"url": url, **audit(obs)}
    print(json.dumps(result, indent=2))
