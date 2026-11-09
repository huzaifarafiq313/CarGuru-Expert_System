"""
INFERENCE ENGINE - Car Fault Diagnosis Expert System
-----------------------------------------------------
Pure logic (no GUI code), so it can be tested and explained separately.

Features implemented here:
  infer()                    -> forward chaining with weighted confidence
  why_not()                  -> "why was this fault rejected?" explanation
  rule_breakdown()           -> "show your work" for one rule
  ordered_symptoms()         -> severity-based question ordering
  detect_multiple_faults()   -> multi-fault detection (explaining-away)
"""
from functools import lru_cache

from knowledge_base import (CATEGORIES, MULTI_THRESHOLD, RULES, SEVERITY_RANK,
                            SYMPTOMS, THRESHOLD)

RULE_BY_NAME = {r["name"]: r for r in RULES}
SEVERITY_NAME = {v: k for k, v in SEVERITY_RANK.items()}


# ---------------------------------------------------------------
# 1. FORWARD CHAINING
# ---------------------------------------------------------------
def infer(facts, threshold=THRESHOLD, min_matched=1):
    """Test EVERY rule against the reported facts.
    confidence = sum(weights of matched symptoms) x 100
    Returns the rules that reach the threshold, best first."""
    results = []
    for rule in RULES:
        matched = [s for s in rule["symptoms"] if s in facts]
        if len(matched) < min_matched:
            continue
        confidence = round(sum(rule["symptoms"][s] for s in matched) * 100, 1)
        if confidence >= threshold:
            missing = [s for s in rule["symptoms"] if s not in facts]
            results.append({"rule": rule, "confidence": confidence,
                            "matched": matched, "missing": missing})
    # best confidence first; if tie, the more severe fault first
    results.sort(key=lambda r: (r["confidence"], SEVERITY_RANK[r["rule"]["severity"]]),
                 reverse=True)
    return results


# ---------------------------------------------------------------
# 2. SELF-EXPLAINING "WHY NOT?"
# ---------------------------------------------------------------
def why_not(rule_name, facts):
    """Explain why a given fault was (or was not) accepted."""
    rule = RULE_BY_NAME[rule_name]
    weights = rule["symptoms"]
    matched = [(s, w) for s, w in weights.items() if s in facts]
    missing = sorted([(s, w) for s, w in weights.items() if s not in facts],
                     key=lambda x: -x[1])
    confidence = round(sum(w for _, w in matched) * 100, 1)
    fired = confidence >= THRESHOLD

    # which missing symptoms would have been enough to reach the threshold?
    needed, running = [], confidence
    for s, w in missing:
        if running >= THRESHOLD:
            break
        needed.append(s)
        running += w * 100
    return {"rule": rule, "confidence": confidence, "fired": fired,
            "matched": matched, "missing": missing,
            "shortfall": round(max(0.0, THRESHOLD - confidence), 1),
            "needed": needed if not fired else [],
            "confidence_if_needed": round(min(running, 100.0), 1)}


# ---------------------------------------------------------------
# 3. RULE JUSTIFICATION ("show your work")
# ---------------------------------------------------------------
def rule_breakdown(rule_name, facts):
    """Row-by-row weight table + formula text for one rule."""
    rule = RULE_BY_NAME[rule_name]
    rows, total = [], 0.0
    for s, w in rule["symptoms"].items():
        hit = s in facts
        total += w if hit else 0.0
        rows.append({"symptom": s, "label": SYMPTOMS[s][1], "weight": w,
                     "reported": hit, "contribution": w if hit else 0.0})
    hits = [f"{r['weight']:.2f}" for r in rows if r["reported"]]
    formula = (" + ".join(hits) if hits else "0") + f" = {total:.2f}  ->  {total * 100:.0f}%"
    return {"rule": rule, "rows": rows, "total": round(total * 100, 1), "formula": formula}


# ---------------------------------------------------------------
# 4. SEVERITY-BASED QUESTION ORDERING
# ---------------------------------------------------------------
@lru_cache(maxsize=None)
def _priority():
    """For every symptom: (highest severity rank among rules using it, its biggest weight there)."""
    best = {}
    for r in RULES:
        rank = SEVERITY_RANK[r["severity"]]
        for s, w in r["symptoms"].items():
            best[s] = max(best.get(s, (0, 0.0)), (rank, w))
    return best


def symptom_top_severity(symptom):
    return SEVERITY_NAME[_priority()[symptom][0]]


def symptoms_for_categories(categories):
    """All symptoms used by the rules of the chosen categories."""
    if not categories or set(categories) >= set(CATEGORIES):
        return list(SYMPTOMS)
    chosen = set()
    for r in RULES:
        if r["category"] in categories:
            chosen.update(r["symptoms"])
    return list(chosen)


def ordered_symptoms(categories=None):
    """Ask Critical-linked symptoms first, then High, Medium, Low."""
    pri = _priority()
    return sorted(symptoms_for_categories(categories),
                  key=lambda s: (-pri[s][0], -pri[s][1], SYMPTOMS[s][1]))


# ---------------------------------------------------------------
# 5. MULTI-FAULT DETECTION  ("explaining away")
# ---------------------------------------------------------------
def detect_multiple_faults(facts, max_faults=4):
    """1) take the best fault
       2) remove the symptoms it explains
       3) re-run the rules on the leftover symptoms
       4) repeat - a second fault must still be strong using ONLY unexplained symptoms.
    Competing explanations of the same symptoms disappear after step 2;
    genuinely independent faults survive."""
    remaining = set(facts)
    found = []
    first = infer(remaining)
    if not first:
        return found
    top = first[0]
    found.append(top)
    remaining -= set(top["matched"])
    while len(found) < max_faults:
        nxt = infer(remaining, threshold=MULTI_THRESHOLD, min_matched=2)
        if not nxt:
            break
        top = nxt[0]
        found.append(top)
        remaining -= set(top["matched"])
    return found
