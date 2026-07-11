"""Scout stage 2 — ICP scoring against the red-flag/green-flag rubric.

Deterministic keyword pass implementing memory/icp-and-scoring/icp.md.
In production a Claude call refines ambiguous middle scores; the rubric,
weights, and output schema are identical, so demo output == real output shape.
Input: newest data/jobs_raw_*.csv  ->  Output: data/scored_<date>.csv
"""
import csv
import re
import sys
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

HARD_DISQUALIFIERS = {
    "clinical duties": r"take vitals|room(ing)? patients|phlebotomy|draw blood|administer injection|\bEKG\b|specimen collection|assist (the )?provider with exams|back office clinical",
    "clinical certification": r"\bCNA\b|BLS/?CPR (certified|required)|\bscrubs\b|clinical MA certification",
    "in-person legal": r"fingerprint(ing)? in person",
}

RED_FLAGS = {  # pattern: penalty
    r"on-?site|in-?office\b|in person\b|must report to our office|local candidates only": 30,
    r"must (live|reside|be located) in [A-Z][a-z]+|no remote": 25,
    r"reliable transportation|valid driver'?s license|travel between (locations|offices)": 20,
    r"must be authorized to work in the (US|United States)|W-?2 only|no (contractors|1099)": 25,
}

HOSPITAL_PAT = re.compile(
    r"hospital|health system|health services\b|medical center\b|\bVA\b|Kaiser|HCA|Ascension|CommonSpirit|Providence|Banner Health|Cleveland Clinic|Mayo Clinic|UPMC|Mount Sinai|Cedars|Mass General|Brigham"
    r"|University of|Mercy(health| Health)?\b|Premier Health|Baxter Health|Fairview|SimonMed|Intermountain|Sutter|Geisinger|Sanford Health|Corewell|Northwell|AdventHealth|Baylor Scott|Trinity Health|Bon Secours|Scripps|Sharp Health|Legacy Health"
    r"|National General|Allstate|GEICO|State Farm|Progressive Insurance|Liberty Mutual"
    r"|Elevate Patient Financial|OneOncology|BenchMark Physical|Upstream Rehab",
    re.I,
)

# Known large orgs that pattern-match poorly (production: Claude judges size).
BIG_ORGS = re.compile(
    r"VillageMD|US Acute Care|AssistRx|Shields Health|Optum|Athenahealth|R1 RCM|Ensemble Health|Conifer|Change Healthcare|Envision|TeamHealth|senior living|assisted living|UnitedHealth|Pfizer|Sharecare|\bCVS\b|Walgreens|Humana|Aetna|Cigna|Centene|Elevance|McKesson|Cardinal Health|Quest Diagnostics|Labcorp|Merck|Novartis|AstraZeneca|Johnson & Johnson",
    re.I,
)

# Clinical or licensed roles — a body in the room / a provider, not a VA seat.
CLINICAL_TITLE = re.compile(
    r"physical therapist|\bPTA\b|occupational therapist|\bnurse\b|\bRN\b|\bLPN\b|\bCNA\b|pharmacist|pharmacy technician|physician|provider\b|psychologist|psychiatrist|therapist|counselor|hygienist|paramedic|\bEMT\b|phlebotomist|dietitian|social worker",
    re.I,
)

# Leadership / non-admin seats — a buyer signal, not a fillable VA seat.
NON_ADMIN_TITLE = re.compile(
    r"director|manager\b|supervisor|\bVP\b|president|sales|marketing|business development|account executive|engineer|developer|designer|recruiter|copywriter|media buyer|paid media|\bSEO\b|analyst|scientist|pharmaceutical",
    re.I,
)

MEDICAL_CONTEXT = re.compile(
    r"medical|dental|patient|health|clinic|billing|claims|insurance|revenue cycle|referral|\bDME\b|\bEHR\b|\bEMR\b|prior auth",
    re.I,
)

GREEN_FLAGS = {  # pattern: bonus
    r"\bremote\b|work from home|\bwfh\b|telecommute|\bvirtual\b|\banywhere\b": 20,
    r"answer(ing)? phones|schedul(e|ing) appointments|appointment (confirmation|reminder)|verify(ing)? insurance|eligibility|prior authorization|data entry|medical records|billing|claims|AR follow-?up|collections|referrals|patient intake": 15,
    r"Athena(health)?|eClinicalWorks|\beCW\b|Kareo|Tebra|DrChrono|NextGen|\bEpic\b|Cerner|AdvancedMD|Practice Fusion|Dentrix|Eaglesoft|Open Dental|EHR|EMR": 15,
    r"high call volume|growing practice|multiple (providers|locations)|need to scale|backlog|busy (practice|office)": 10,
    r"private practice|family (practice|medicine)|small (practice|office)|billing (company|service)|\bMSO\b|group practice|dental (office|practice)|clinic\b": 10,
}


def score_job(title: str, company: str, desc: str) -> dict:
    text = f"{title} {desc}"
    reasons = []

    for name, pat in HARD_DISQUALIFIERS.items():
        if re.search(pat, text, re.I):
            return {"score": 0, "verdict": "disqualified", "reasons": [f"hard: {name}"],
                    "practice_size_guess": "n/a", "remote_signal": "n/a"}
    if CLINICAL_TITLE.search(title):
        return {"score": 0, "verdict": "disqualified", "reasons": ["hard: clinical/licensed role"],
                "practice_size_guess": "n/a", "remote_signal": "n/a"}
    if HOSPITAL_PAT.search(company or "") or BIG_ORGS.search(company or ""):
        return {"score": 0, "verdict": "disqualified", "reasons": ["hard: hospital / large org — not small/mid practice ICP"],
                "practice_size_guess": "large", "remote_signal": "n/a"}

    score = 50
    for pat, pen in RED_FLAGS.items():
        if re.search(pat, text, re.I):
            score -= pen
            reasons.append(f"-{pen} {re.search(pat, text, re.I).group(0)[:40].strip().lower()}")
    if HOSPITAL_PAT.search(desc[:500]):
        score -= 20
        reasons.append("-20 health-system language in description")

    for pat, bonus in GREEN_FLAGS.items():
        m = re.search(pat, text, re.I)
        if m:
            score += bonus
            reasons.append(f"+{bonus} {m.group(0)[:40].strip().lower()}")

    remote = bool(re.search(r"\bremote\b|work from home|wfh|telecommute|virtual|anywhere", text, re.I))
    onsite = bool(re.search(r"on-?site|in-?office\b|in person\b", text, re.I))
    remote_signal = "explicit-remote" if remote and not onsite else ("on-site" if onsite else "ambiguous")

    if re.search(r"billing (company|service)|revenue cycle management|\bRCM\b", text, re.I):
        size = "billing-company"
    elif re.search(r"multiple (providers|locations)|group practice|\bMSO\b", text, re.I):
        size = "mid-size"
    elif re.search(r"private practice|solo|small (practice|office)|family (practice|medicine)|dental (office|practice)", text, re.I):
        size = "solo-small"
    else:
        size = "unknown"

    if NON_ADMIN_TITLE.search(title):
        score = min(score, 60)
        reasons.append("cap 60: leadership/non-admin seat — buyer signal, not a VA-fillable role")
    if not MEDICAL_CONTEXT.search(title) and not MEDICAL_CONTEXT.search(company or ""):
        score = min(score, 55)
        reasons.append("cap 55: weak medical context in title/company")

    score = max(0, min(100, score))
    if remote_signal == "ambiguous":
        score = min(score, 69)                       # cap per rubric
    verdict = "qualified" if score >= 70 else ("deprioritized" if score >= 40 else "disqualified")
    return {"score": score, "verdict": verdict, "reasons": reasons,
            "practice_size_guess": size, "remote_signal": remote_signal}


def main() -> None:
    raws = sorted(DATA_DIR.glob("jobs_raw_*.csv"))
    if not raws:
        sys.exit("no jobs_raw_*.csv found — run scrape.py first")
    src = raws[-1]

    rows = []
    with open(src, encoding="utf-8") as f:
        for job in csv.DictReader(f):
            res = score_job(job["title"], job["company"], job["description"])
            job.update(res)
            job["reasons"] = "; ".join(res["reasons"])
            job["description"] = job["description"][:600]
            rows.append(job)

    rows.sort(key=lambda r: r["score"], reverse=True)
    out = DATA_DIR / f"scored_{date.today().isoformat()}.csv"
    fields = ["id", "score", "verdict", "practice_size_guess", "remote_signal", "title",
              "company", "location", "source", "date_posted", "url", "reasons", "description"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    q = sum(1 for r in rows if r["verdict"] == "qualified")
    d = sum(1 for r in rows if r["verdict"] == "deprioritized")
    print(f"scored {len(rows)} jobs -> {out}")
    print(f"qualified: {q} | deprioritized: {d} | disqualified: {len(rows) - q - d}")


if __name__ == "__main__":
    main()
