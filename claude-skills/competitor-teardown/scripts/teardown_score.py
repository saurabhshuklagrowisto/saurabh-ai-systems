#!/usr/bin/env python3
"""
Competitor Teardown — scored positioning matrix and wedge finder.

Takes your brand + competitors scored 0-5 across weighted buyer-decision
dimensions and returns where you win, where you lose, the category whitespace,
and the single sharpest wedge to position on. No dependencies, no API keys.

Input schema:
{
  "brand": "YourBrand",
  "competitors": ["Rival A", "Rival B"],
  "dimensions": [
    {"name": "Time to value", "weight": 3, "scores": {"YourBrand": 5, "Rival A": 2, "Rival B": 3}}
  ]
}
weight: 1-3 (how much the dimension moves a buyer). scores: 0-5 per player.
"""
import json, sys

def teardown(d):
    brand = d["brand"]
    players = [brand] + d["competitors"]
    dims = d["dimensions"]

    # weighted totals
    totals = {p: 0 for p in players}
    maxw = sum(dim.get("weight", 1) * 5 for dim in dims)
    for dim in dims:
        w = dim.get("weight", 1)
        for p in players:
            totals[p] += dim["scores"].get(p, 0) * w
    ranking = sorted(
        ({"player": p, "score": totals[p], "pct": round(totals[p] / maxw * 100)} for p in players),
        key=lambda x: -x["score"]
    )

    wins, losses, whitespace = [], [], []
    best_wedge = None
    for dim in dims:
        s = dim["scores"]
        w = dim.get("weight", 1)
        mine = s.get(brand, 0)
        rivals = {c: s.get(c, 0) for c in d["competitors"]}
        best_rival = max(rivals.values()) if rivals else 0
        field_max = max([mine] + list(rivals.values()))

        if mine > best_rival:
            wins.append({"dimension": dim["name"], "you": mine, "best_rival": best_rival, "weight": w})
        elif best_rival > mine:
            leader = max(rivals, key=rivals.get)
            losses.append({"dimension": dim["name"], "you": mine, "leader": leader,
                           "leader_score": best_rival, "weight": w})

        # whitespace: nobody in the category is strong here
        if field_max <= 2:
            whitespace.append({"dimension": dim["name"], "field_max": field_max, "weight": w})

        # wedge candidate: you are strong AND the field is weak, weighted by importance
        wedge_gap = (mine - best_rival) * w
        if mine >= 4 and best_rival <= 3:
            if best_wedge is None or wedge_gap > best_wedge["gap"]:
                best_wedge = {"dimension": dim["name"], "you": mine, "best_rival": best_rival,
                              "weight": w, "gap": wedge_gap}

    if best_wedge:
        wedge = {
            "dimension": best_wedge["dimension"],
            "why": (f"You score {best_wedge['you']}/5 here while the strongest competitor manages "
                    f"{best_wedge['best_rival']}/5, and this dimension carries weight {best_wedge['weight']}. "
                    "Lead your positioning here — it is defensible and the field cannot easily counter it."),
        }
    else:
        wedge = {"dimension": None,
                 "why": "No clean wedge: you do not lead any high-weight dimension by a clear margin. "
                        "Either raise your score on a high-weight dimension or find a new dimension buyers care about."}

    return {
        "brand": brand,
        "ranking": ranking,
        "wins": sorted(wins, key=lambda x: -x["weight"]),
        "losses": sorted(losses, key=lambda x: -x["weight"]),
        "whitespace": whitespace,
        "wedge": wedge,
    }

def _sample():
    return {
        "brand": "YourBrand",
        "competitors": ["Rival A", "Rival B"],
        "dimensions": [
            {"name": "Time to value",      "weight": 3, "scores": {"YourBrand": 5, "Rival A": 2, "Rival B": 3}},
            {"name": "Price transparency",  "weight": 2, "scores": {"YourBrand": 4, "Rival A": 2, "Rival B": 2}},
            {"name": "Enterprise security", "weight": 3, "scores": {"YourBrand": 3, "Rival A": 5, "Rival B": 4}},
            {"name": "Ease of onboarding",  "weight": 2, "scores": {"YourBrand": 5, "Rival A": 3, "Rival B": 2}},
            {"name": "Integrations depth",  "weight": 2, "scores": {"YourBrand": 2, "Rival A": 4, "Rival B": 3}},
            {"name": "AI-native workflow",   "weight": 3, "scores": {"YourBrand": 4, "Rival A": 2, "Rival B": 1}},
            {"name": "Community / content",  "weight": 1, "scores": {"YourBrand": 1, "Rival A": 2, "Rival B": 1}},
        ],
    }

if __name__ == "__main__":
    d = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else _sample()
    print(json.dumps(teardown(d), indent=2))
