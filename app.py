"""
AutoDoc - Car Fault Diagnosis Expert System (Streamlit GUI)
Run with:   streamlit run app.py
"""
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

import engine as eng
from knowledge_base import (CATEGORIES, CRITICAL_ALERT, DEMO_SCENARIOS, MULTI_THRESHOLD,
                            RULES, SEVERITY_RANK, SYMPTOMS, THRESHOLD)

st.set_page_config(page_title="AutoDoc Expert System", page_icon="🚗", layout="wide")

SEV_COLORS = {"Low": "#2e9e5b", "Medium": "#d9a000", "High": "#e0661a", "Critical": "#d62839"}
SEV_ICONS = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
LOG_FILE = Path(__file__).with_name("accuracy_log.json")


# STYLE
st.markdown("""
<style>
.hero {background: linear-gradient(120deg,#0f2027,#203a43,#2c5364); padding:1.3rem 1.8rem;
       border-radius:16px; color:white; margin-bottom:1rem;}
.hero h1 {margin:0; font-size:2rem; color:white; padding:0;}
.hero p {margin:.3rem 0 0 0; opacity:.85;}
.badge {display:inline-block; padding:2px 10px; border-radius:999px; font-size:.75rem;
        font-weight:700; color:white; letter-spacing:.03em;}
.chip {display:inline-block; padding:3px 10px; margin:2px 4px 2px 0; border-radius:999px;
       font-size:.82rem; background:rgba(120,120,120,.18);}
.chip.ok {background:rgba(46,158,91,.25);}
.chip.miss {background:rgba(214,40,57,.15);}
.alert-crit {background:rgba(214,40,57,.14); border-left:6px solid #d62839;
             padding:.9rem 1.1rem; border-radius:10px; margin:.6rem 0;}
.card {border:1px solid rgba(120,120,120,.3); border-radius:14px; padding:.9rem 1.2rem; margin:.5rem 0;}
.bigq {font-size:1.6rem; font-weight:600; margin:.5rem 0 .3rem 0; line-height:1.3;}
.formula {font-family:monospace; font-size:1.05rem; padding:.6rem .9rem; border-radius:8px;
          background:rgba(120,120,120,.15); margin:.4rem 0;}
</style>
""", unsafe_allow_html=True)


def badge(sev):
    return f'<span class="badge" style="background:{SEV_COLORS[sev]}">{sev.upper()}</span>'


def chips(keys, cls=""):
    return "".join(f'<span class="chip {cls}">{SYMPTOMS[k][1]}</span>' for k in keys)



# ACCURACY LOG  

def load_log():
    try:
        return json.loads(LOG_FILE.read_text())
    except Exception:
        return []

def save_log(entries):
    LOG_FILE.write_text(json.dumps(entries, indent=2))


def accuracy_stats():
    log = load_log()
    n = len(log)
    correct = sum(1 for e in log if e["correct"])
    return log, n, correct



# SESSION STATE
def init_state():
    defaults = {"stage": "setup", "facts": set(), "queue": [], "qi": 0, "history": [],
                "alerted": None, "feedback": None, "wrong": False, "mode": "guided"}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_session():
    for k in list(st.session_state.keys()):
        if k.startswith("chk_") or k.startswith("insp_"):
            del st.session_state[k]
    st.session_state.update(stage="setup", facts=set(), queue=[], qi=0, history=[],
                            alerted=None, feedback=None, wrong=False)


def load_demo(name):
    reset_session()
    st.session_state.facts = set(DEMO_SCENARIOS[name])
    st.session_state.stage = "results"


# ---------- guided interview callbacks ----------
def check_alert():
    s = st.session_state
    if s.alerted is None:
        for r in eng.infer(s.facts):
            if r["rule"]["severity"] == "Critical" and r["confidence"] >= CRITICAL_ALERT:
                s.alerted = r["rule"]["name"]
                break


def go_results():
    st.session_state.stage = "results"
    st.session_state.feedback = None
    st.session_state.wrong = False


def answer(yes):
    s = st.session_state
    sym = s.queue[s.qi]
    s.history.append((sym, yes))
    if yes:
        s.facts.add(sym)
    s.qi += 1
    check_alert()
    if s.qi >= len(s.queue):
        go_results()


def undo():
    s = st.session_state
    if not s.history:
        return
    sym, yes = s.history.pop()
    if yes:
        s.facts.discard(sym)
    s.qi -= 1
    s.alerted = None
    check_alert()


def start_clicked():
    s = st.session_state
    mode = "guided" if s.mode_choice.startswith("🧭") else "checklist"
    cats = s.cat_choice or CATEGORIES
    s.mode = mode
    s.queue = eng.ordered_symptoms(cats)
    s.qi, s.history, s.facts, s.alerted = 0, [], set(), None
    s.stage = "asking" if mode == "guided" else "checklist"


def finish_checklist():
    s = st.session_state
    s.facts = {k for k in s.queue if s.get(f"chk_{k}")}
    go_results()


# ---------- feedback callbacks ----------
def log_feedback(correct, predicted, confidence, actual=None):
    log = load_log()
    log.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "predicted": predicted, "confidence": confidence,
                "correct": correct, "actual": actual,
                "symptoms": sorted(st.session_state.facts)})
    save_log(log)
    st.session_state.feedback = "correct" if correct else "wrong"


def mark_wrong():
    st.session_state.wrong = True


def submit_wrong(predicted, confidence):
    actual = st.session_state.get("actual_choice")
    log_feedback(False, predicted, confidence, actual)


def clear_log():
    save_log([])



# SIDEBAR
def render_sidebar():
    init_state()
    with st.sidebar:
        st.markdown("## 🚗 CarGurU")
        st.caption("Rule-based expert system for car fault diagnosis")
        _, n, correct = accuracy_stats()
        if n:
            st.metric("🎯 Self-measured accuracy", f"{correct / n * 100:.0f}%", f"{correct}/{n} sessions correct")
        else:
            st.metric("🎯 Self-measured accuracy", "—", "no feedback yet")
        st.divider()
        st.markdown("**⚡ Demo scenarios**")
        for name in DEMO_SCENARIOS:
            st.button(name, key=f"demo_{name}", on_click=load_demo, args=(name,), width="stretch")
        st.divider()
        st.button("🔄 New diagnosis", on_click=reset_session, width="stretch")
        st.caption(f"{len(RULES)} rules · {len(SYMPTOMS)} symptoms · {len(CATEGORIES)} systems")



# TAB 1 - DIAGNOSE

def render_setup():
    st.markdown("### Tell me what's wrong with your car")
    st.radio("How do you want to describe the problem?",
             ["🧭 Guided interview — most dangerous faults are asked FIRST",
              "☑️ Quick checklist — tick everything you notice"],
             key="mode_choice")
    st.multiselect("Which areas are affected? (leave empty to check everything)",
                   CATEGORIES, key="cat_choice")
    st.button("🚀 Start diagnosis", type="primary", on_click=start_clicked)
    st.info("💡 In guided mode the system asks about symptoms linked to **Critical** faults first, "
            "and raises an alarm the moment a dangerous fault becomes likely.")


def render_asking():
    s = st.session_state
    q, i = s.queue, s.qi
    if s.alerted:
        st.markdown(f'<div class="alert-crit">🚨 <b>Critical fault likely: {s.alerted}</b><br>'
                    f'Do not keep driving the car. You can continue the interview or stop now.</div>',
                    unsafe_allow_html=True)
    st.progress(i / len(q), text=f"Question {i + 1} of {len(q)}")
    left, right = st.columns([3, 2])
    with left:
        sym = q[i]
        sev = eng.symptom_top_severity(sym)
        st.markdown(f'{badge(sev)} &nbsp; linked to a **{sev.lower()}**-severity fault · '
                    f'<span style="opacity:.7">{SYMPTOMS[sym][0]}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="bigq">“{SYMPTOMS[sym][1]}”</div>', unsafe_allow_html=True)
        st.write("Please confirm whether your vehicle has this issue: ")
        c1, c2 = st.columns(2)
        c1.button("✅ Yes", on_click=answer, args=(True,), width="stretch", type="primary")
        c2.button("❌ No / not sure", on_click=answer, args=(False,), width="stretch")
        c3, c4 = st.columns(2)
        c3.button("↩️ Undo last answer", on_click=undo, disabled=not s.history, width="stretch")
        c4.button("⏭️ Diagnose now", on_click=go_results, width="stretch")
    with right:
        st.markdown("**🧠 Live hypotheses**")
        live = eng.infer(s.facts, threshold=20)[:4]
        if not live:
            st.caption("Answer a few questions and the engine's current best guesses appear here.")
        for r in live:
            st.progress(min(r["confidence"] / 100, 1.0),
                        text=f'{SEV_ICONS[r["rule"]["severity"]]} {r["rule"]["name"]} — {r["confidence"]:.0f}%')
        st.caption(f"Symptoms reported so far: {len(s.facts)}")


def render_checklist():
    s = st.session_state
    st.markdown("### ☑️ Tick everything you notice")
    st.caption("Grouped by the severity of the faults they point to — Critical first.")
    tiers = {sev: [] for sev in ["Critical", "High", "Medium", "Low"]}
    for sym in s.queue:
        tiers[eng.symptom_top_severity(sym)].append(sym)
    for sev, syms in tiers.items():
        if not syms:
            continue
        with st.expander(f"{SEV_ICONS[sev]} {sev}-linked symptoms ({len(syms)})", expanded=(sev == "Critical")):
            cols = st.columns(2)
            for idx, sym in enumerate(syms):
                cols[idx % 2].checkbox(SYMPTOMS[sym][1], key=f"chk_{sym}")
    st.button("🔍 Diagnose", type="primary", on_click=finish_checklist)


def build_report(facts, results, multi):
    lines = ["CAR DIAGNOSIS REPORT", "=" * 40,
             f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             "Symptoms: " + ", ".join(SYMPTOMS[f][1] for f in sorted(facts)), ""]
    if len(multi) >= 2:
        lines.append(f"MULTIPLE INDEPENDENT FAULTS DETECTED ({len(multi)})")
    for i, r in enumerate(results[:8], 1):
        ru = r["rule"]
        lines += [f"#{i} {ru['name']}  [{ru['severity']}]  {r['confidence']:.0f}%",
                  "   Matched : " + ", ".join(SYMPTOMS[s][1] for s in r["matched"]),
                  f"   Fix     : {ru['fix']}", ""]
    return "\n".join(lines)


def render_why_not(facts, key_prefix):
    st.markdown("#### 🤔 Could it be something else? — “why not?” explainer")
    cat = st.selectbox("Area", ["All areas"] + CATEGORIES, key=f"{key_prefix}_cat")
    names = [r["name"] for r in RULES if cat == "All areas" or r["category"] == cat]
    name = st.selectbox("Fault you suspect", names, key=f"{key_prefix}_{cat}")
    wn = eng.why_not(name, facts)
    ru = wn["rule"]
    if wn["fired"]:
        st.success(f"✅ **{name}** WAS accepted — confidence {wn['confidence']:.0f}% "
                   f"(threshold {THRESHOLD}%).")
    else:
        st.error(f"❌ **{name}** was REJECTED — confidence {wn['confidence']:.0f}% is "
                 f"{wn['shortfall']:.0f} points below the {THRESHOLD}% threshold.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Symptoms you reported that support it**")
        if wn["matched"]:
            for s, w in wn["matched"]:
                st.markdown(f"✔️ {SYMPTOMS[s][1]} &nbsp; `+{w:.2f}`", unsafe_allow_html=True)
        else:
            st.caption("None.")
    with c2:
        st.markdown("**Required symptoms that were missing**")
        if wn["missing"]:
            for s, w in wn["missing"]:
                st.markdown(f"✖️ {SYMPTOMS[s][1]} &nbsp; `{w:.2f}`", unsafe_allow_html=True)
        else:
            st.caption("Nothing missing.")
    if not wn["fired"] and wn["needed"]:
        extra = ", ".join(f"“{SYMPTOMS[s][1]}”" for s in wn["needed"])
        st.info(f"To accept this fault the system would also need: {extra} "
                f"(confidence would rise to ~{wn['confidence_if_needed']:.0f}%).")
    return wn


def render_results():
    s = st.session_state
    facts = s.facts
    if not facts:
        st.warning("No symptoms were reported — nothing to diagnose.")
        st.button("🔄 Start again", on_click=reset_session)
        return

    results = eng.infer(facts)
    multi = eng.detect_multiple_faults(facts)

    st.markdown("### 🧾 Reported symptoms")
    st.markdown(chips(sorted(facts)), unsafe_allow_html=True)

    if not results:
        st.info(f"No fault reached the {THRESHOLD}% confidence threshold. Try adding more symptoms, "
                "or use the “why not?” explainer below to see how close each fault was.")
    else:
        crit = [r for r in results if r["rule"]["severity"] == "Critical" and r["confidence"] >= CRITICAL_ALERT]
        if crit:
            st.markdown(f'<div class="alert-crit">🚨 <b>SAFETY WARNING — {crit[0]["rule"]["name"]}</b> is likely '
                        f'({crit[0]["confidence"]:.0f}%).<br><b>Do NOT drive the car.</b> '
                        f'{crit[0]["rule"]["fix"]}</div>', unsafe_allow_html=True)

        top = results[0]
        st.markdown("### 🏁 Primary diagnosis")
        a, b, c = st.columns([3, 1, 1])
        a.markdown(f"## {top['rule']['name']}")
        b.metric("Confidence", f"{top['confidence']:.0f}%")
        c.markdown(f"**Severity**<br>{badge(top['rule']['severity'])}", unsafe_allow_html=True)
        st.success(f"🔧 **Recommended fix:** {top['rule']['fix']}")

        # ---- multi-fault detection (feature 5) ----
        st.markdown("### 🔀 Multi-fault detection")
        if len(multi) >= 2:
            st.warning(f"**{len(multi)} independent faults detected.** Each one is explained by a "
                       f"*separate* group of symptoms, so your car likely has more than one problem.")
            cols = st.columns(len(multi))
            for col, r in zip(cols, multi):
                with col:
                    st.markdown(f'<div class="card"><b>{r["rule"]["name"]}</b><br>{badge(r["rule"]["severity"])} '
                                f'&nbsp; {r["confidence"]:.0f}%<br><br>{chips(r["matched"], "ok")}<br><br>'
                                f'🔧 {r["rule"]["fix"]}</div>', unsafe_allow_html=True)
            st.caption(f"How it works: after picking the best fault, its symptoms are removed and the rules "
                       f"are run again; a further fault must still reach {MULTI_THRESHOLD}% using only the "
                       f"leftover symptoms.")
        else:
            st.caption("Only one independent fault pattern found — the other candidates below are "
                       "competing explanations of the same symptoms.")

        # ---- ranked candidates ----
        st.markdown("### 📋 All candidate faults (ranked)")
        for i, r in enumerate(results[:8]):
            ru = r["rule"]
            with st.expander(f"#{i + 1}  {ru['name']} — {r['confidence']:.0f}%  ·  {SEV_ICONS[ru['severity']]} {ru['severity']}",
                             expanded=(i < 2)):
                st.progress(min(r["confidence"] / 100, 1.0))
                st.markdown(f"**Why:** " + chips(r["matched"], "ok"), unsafe_allow_html=True)
                if r["missing"]:
                    st.markdown("**Also check:** " + chips(r["missing"], "miss"), unsafe_allow_html=True)
                st.markdown(f"🔧 **Fix:** {ru['fix']}  \n📂 *{ru['category']}*")
        if len(results) > 8:
            st.caption(f"Showing the top 8 of {len(results)} candidate faults.")
        df = pd.DataFrame({"Fault": [r["rule"]["name"] for r in results[:8]],
                           "Confidence %": [r["confidence"] for r in results[:8]]}).set_index("Fault")
        st.bar_chart(df)

    st.divider()
    render_why_not(facts, "wn_res")

    # ---- accuracy feedback (feature 2) ----
    if results:
        st.divider()
        top = results[0]
        st.markdown("### 🎯 Was the primary diagnosis correct?")
        st.caption("Your answer is logged so the system can measure its own accuracy over time.")
        if s.feedback is None:
            if not s.wrong:
                c1, c2 = st.columns(2)
                c1.button("✅ Yes, correct", width="stretch",
                          on_click=log_feedback, args=(True, top["rule"]["name"], top["confidence"]))
                c2.button("❌ No, incorrect", width="stretch", on_click=mark_wrong)
            else:
                st.selectbox("What was the actual fault?",
                             ["Not sure / not in the system"] + [r["name"] for r in RULES], key="actual_choice")
                st.button("Submit feedback", type="primary", on_click=submit_wrong,
                          args=(top["rule"]["name"], top["confidence"]))
        else:
            _, n, correct = accuracy_stats()
            st.success(f"Thanks! Logged. Running accuracy: **correct in {correct}/{n} sessions "
                       f"({correct / n * 100:.0f}%)**.")

    st.divider()
    d1, d2 = st.columns(2)
    d1.download_button("📄 Download report", build_report(facts, results, multi),
                       file_name="car_diagnosis_report.txt", width="stretch")
    d2.button("🔄 Start a new diagnosis", on_click=reset_session, width="stretch")


def tab_diagnose():
    stage = st.session_state.stage
    if stage == "setup":
        render_setup()
    elif stage == "asking":
        render_asking()
    elif stage == "checklist":
        render_checklist()
    else:
        render_results()


# ===================================================================
# TAB 2 - RULE INSPECTOR  (feature 3)
# ===================================================================
def tab_inspector():
    st.markdown("### 🔬 Rule Inspector — “show your work”")
    st.caption("Type a rule name to see its full symptom-weight breakdown. Tick symptoms to "
               "watch the confidence calculation update live (pre-ticked from your current diagnosis).")
    typed = st.text_input("Type a rule name (or part of it)", placeholder="e.g. brake pads, battery, coolant…")
    matches = [r for r in RULES if typed.lower() in r["name"].lower()] if typed else RULES
    if not matches:
        st.warning("No rule matches that text.")
        return
    name = st.selectbox(f"Matching rules ({len(matches)})", [r["name"] for r in matches])
    rule = eng.RULE_BY_NAME[name]
    idx = RULES.index(rule)

    st.markdown(f"## {name}")
    st.markdown(f"{badge(rule['severity'])} &nbsp; 📂 {rule['category']} &nbsp; · &nbsp; 🔧 {rule['fix']}",
                unsafe_allow_html=True)
    parts = [f"{SYMPTOMS[s][1]} ({w:.2f})" for s, w in rule["symptoms"].items()]
    st.markdown("**IF** " + " **AND** ".join(parts) + f" **THEN** *{name}* "
                f"(confidence = sum of matched weights)")

    st.markdown("**Tick the symptoms to test this rule:**")
    chosen = set()
    cols = st.columns(2)
    for i, (sym, w) in enumerate(rule["symptoms"].items()):
        default = sym in st.session_state.facts
        if cols[i % 2].checkbox(f"{SYMPTOMS[sym][1]}  —  weight {w:.2f}", value=default,
                                key=f"insp_{idx}_{sym}"):
            chosen.add(sym)

    bd = eng.rule_breakdown(name, chosen)
    st.markdown(f'<div class="formula">Confidence = {bd["formula"]}</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    m1.metric("Confidence", f"{bd['total']:.0f}%")
    if bd["total"] >= THRESHOLD:
        m2.success(f"≥ {THRESHOLD}% threshold → rule FIRES")
    else:
        m2.error(f"< {THRESHOLD}% threshold → rule does NOT fire")
    table = pd.DataFrame([{"Symptom": r["label"], "Weight": r["weight"],
                           "Reported": "✔" if r["reported"] else "—",
                           "Contribution": r["contribution"]} for r in bd["rows"]])
    st.dataframe(table, hide_index=True, width="stretch")
    st.bar_chart(pd.DataFrame({"Weight": [r["weight"] for r in bd["rows"]]},
                              index=[r["label"] for r in bd["rows"]]))


# ===================================================================
# TAB 3 - KNOWLEDGE BASE
# ===================================================================
def tab_kb():
    st.markdown("### 📚 Knowledge Base")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rules", len(RULES))
    m2.metric("Symptoms", len(SYMPTOMS))
    m3.metric("Systems covered", len(CATEGORIES))
    m4.metric("Critical rules", sum(1 for r in RULES if r["severity"] == "Critical"))
    f1, f2 = st.columns(2)
    cat = f1.selectbox("Filter by area", ["All areas"] + CATEGORIES, key="kb_cat")
    sev = f2.selectbox("Filter by severity", ["All"] + list(SEVERITY_RANK), key="kb_sev")
    rows = [{"Fault": r["name"], "Area": r["category"], "Severity": r["severity"],
             "# Symptoms": len(r["symptoms"]), "Fix": r["fix"]}
            for r in RULES
            if (cat == "All areas" or r["category"] == cat) and (sev == "All" or r["severity"] == sev)]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    counts = pd.Series([r["category"] for r in RULES]).value_counts()
    st.markdown("**Rules per system**")
    st.bar_chart(counts)


# ===================================================================
# TAB 4 - ACCURACY TRACKER  (feature 2)
# ===================================================================
def tab_accuracy():
    st.markdown("### 📊 Accuracy Tracker")
    log, n, correct = accuracy_stats()
    if not n:
        st.info("No feedback logged yet. After a diagnosis, press ✅ / ❌ under “Was the primary "
                "diagnosis correct?” and the results will appear here.")
        return
    a, b, c = st.columns(3)
    a.metric("Sessions logged", n)
    b.metric("Correct", correct)
    c.metric("Accuracy", f"{correct / n * 100:.0f}%")
    st.progress(correct / n, text=f"Correct in {correct}/{n} sessions")
    running, ok = [], 0
    for i, e in enumerate(log, 1):
        ok += 1 if e["correct"] else 0
        running.append(ok / i * 100)
    st.markdown("**Running accuracy over time (%)**")
    st.line_chart(pd.DataFrame({"Running accuracy %": running}, index=range(1, n + 1)))
    hist = pd.DataFrame([{"Time": e["time"], "Predicted fault": e["predicted"],
                          "Confidence %": e["confidence"], "Correct?": "✅" if e["correct"] else "❌",
                          "Actual fault (if wrong)": e.get("actual") or ""} for e in log])
    st.dataframe(hist.iloc[::-1], hide_index=True, width="stretch")
    st.button("🗑️ Clear log", on_click=clear_log)


# ===================================================================
# TAB 5 - ABOUT
# ===================================================================
def tab_about():
    st.markdown("""
### ℹ️ How the system works
| Expert-system component | Where it lives |
|---|---|
| **Knowledge base** | `knowledge_base.py` — 67 weighted IF-THEN rules over 109 symptoms |
| **Inference engine** | `engine.py` — forward chaining, weighted confidence |
| **User interface** | `app.py` — Streamlit GUI |
| **Explanation facility** | “Why”, “Also check”, “why not?”, Rule Inspector |

**Confidence formula:** each rule's weights add up to 1.0, so `confidence = Σ weights of reported symptoms × 100`.
A fault is shown when confidence ≥ 40 %.

**Special features**
1. **Why-not answers** — pick any rejected fault and see exactly which symptoms were missing.
2. **Accuracy tracker** — every diagnosis can be marked correct/incorrect; accuracy is logged to `accuracy_log.json`.
3. **Rule inspector** — full weight breakdown of any rule, with a live calculator.
4. **Severity-based ordering** — guided interview asks Critical-linked symptoms first and raises an alarm early.
5. **Multi-fault detection** — “explaining-away” algorithm finds independent faults that explain separate symptoms.
""")


# ===================================================================
# MAIN
# ===================================================================
render_sidebar()
st.markdown('<div class="hero"><h1>🚗 AutoDoc — Car Fault Diagnosis Expert System</h1>'
            '<p>67 expert rules · forward-chaining inference · self-explaining · self-evaluating</p></div>',
            unsafe_allow_html=True)
tabs = st.tabs(["🩺 Diagnose", "🔬 Rule Inspector", "📚 Knowledge Base", "📊 Accuracy Tracker", "ℹ️ About"])
with tabs[0]:
    tab_diagnose()
with tabs[1]:
    tab_inspector()
with tabs[2]:
    tab_kb()
with tabs[3]:
    tab_accuracy()
with tabs[4]:
    tab_about()
