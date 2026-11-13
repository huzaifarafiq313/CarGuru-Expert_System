"""
CarGuru - Car Fault Diagnosis Expert System (Streamlit GUI)
Run with:   streamlit run app.py

Logic lives in engine.py / knowledge_base.py (unchanged).
Presentation helpers (icons, CSS, components) live in ui.py / icons.py.
"""
import json
from datetime import datetime
from html import escape as esc
from pathlib import Path

import pandas as pd
import streamlit as st

import engine as eng
import ui
from knowledge_base import (CATEGORIES, CRITICAL_ALERT, DEMO_SCENARIOS, MULTI_THRESHOLD,
                            RULES, SEVERITY_RANK, SYMPTOMS, THRESHOLD)

st.set_page_config(page_title="CarGuru | Car Fault Diagnosis Expert System",
                   page_icon=":material/directions_car:", layout="wide",
                   initial_sidebar_state="auto")

LOG_FILE = Path(__file__).with_name("accuracy_log.json")
PAGES = [("dashboard", "Dashboard"), ("diagnose", "Diagnosis"), ("inspector", "Rule Inspector"),
         ("kb", "Knowledge Base"), ("accuracy", "Accuracy Tracker"), ("about", "About")]
MODES = ["Guided interview", "Symptom checklist"]
ADVICE_KIND = {"Critical": "critical", "High": "warning", "Medium": "warning", "Low": "success"}
CONF_NOTE = ("Confidence is a heuristic rule-weight score (the sum of the weights of the reported "
             "symptoms). It is not a statistical probability or a guarantee.")


# ===================================================================
# ACCURACY LOG
# ===================================================================
def load_log():
    try:
        return json.loads(LOG_FILE.read_text())
    except Exception:
        return []


def save_log(entries):
    try:
        LOG_FILE.write_text(json.dumps(entries, indent=2))
    except OSError:
        pass  # read-only file systems: keep running, just do not persist


def accuracy_stats():
    log = load_log()
    return log, len(log), sum(1 for e in log if e["correct"])


# SESSION STATE + CALLBACKS
def init_state():
    defaults = {"page": "dashboard", "stage": "setup", "facts": set(), "selected": set(), "queue": [],
                "qi": 0, "history": [], "alerted": None, "feedback": None, "wrong": False, "mode": "guided",
                "areas": [], "trail": []}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if "theme" not in st.session_state:        # remembered across browser reloads via ?theme=dark
        saved = str(st.query_params.get("theme", "")).lower()
        st.session_state.theme = {"light": "Light", "dark": "Dark"}.get(saved, "System")


def reset_session():
    for k in list(st.session_state.keys()):
        if k.startswith(("chk_", "insp_", "area_", "sym_search", "wn_")):
            del st.session_state[k]
    st.session_state.update(stage="setup", facts=set(), selected=set(), queue=[], qi=0, history=[],
                            alerted=None, feedback=None, wrong=False, areas=[])

# Back button
def push_trail():
    s = st.session_state
    snap = {"page": s.page, "stage": s.stage, "qi": s.qi}
    if not s.trail or s.trail[-1] != snap:
        s.trail.append(snap)
        del s.trail[:-40]

def back():
    """Return to the previous page / diagnosis step, like a browser back button."""
    s = st.session_state
    if not s.trail:
        return
    snap = s.trail.pop()
    s.page, s.stage, s.qi = snap["page"], snap["stage"], snap["qi"]
    if s.stage in ("asking", "checklist") and not s.queue:
        s.stage = "setup"
    if s.stage == "results" and not s.facts:
        s.stage = "setup"
    if s.stage == "asking":
        if s.qi >= len(s.queue) and s.history:     # came back after the last question: reopen it
            undo()
        s.qi = max(0, min(s.qi, len(s.queue) - 1))
        s.alerted = None
        check_alert()

def go(page):
    if st.session_state.page != page:
        push_trail()
        st.session_state.page = page

def new_diagnosis():
    push_trail()
    reset_session()
    st.session_state.page = "diagnose"

def load_demo(name):
    push_trail()
    reset_session()
    st.session_state.facts = set(DEMO_SCENARIOS[name])
    st.session_state.stage = "results"
    st.session_state.page = "diagnose"


def set_theme(theme):
    st.session_state.theme = theme
    st.query_params["theme"] = theme.lower()


def restart_app():
    """Full restart: forget everything (except the chosen theme) and return to the dashboard."""
    theme = st.session_state.get("theme", "System")
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state["theme"] = theme


def check_alert():
    s = st.session_state
    if s.alerted is None:
        for r in eng.infer(s.facts):
            if r["rule"]["severity"] == "Critical" and r["confidence"] >= CRITICAL_ALERT:
                s.alerted = r["rule"]["name"]
                break

def go_results():
    push_trail()
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
    mode = "checklist" if s.get("mode_choice") == MODES[1] else "guided"
    cats = [c for i, c in enumerate(CATEGORIES) if s.get(f"area_{i}")] or CATEGORIES
    push_trail()
    s.mode = mode
    s.areas = [c for c in cats if c in CATEGORIES] if cats != CATEGORIES else []
    s.queue = eng.ordered_symptoms(cats)          # severity-based ordering
    s.qi, s.history, s.facts, s.selected, s.alerted = 0, [], set(), set(), None
    s.stage = "asking" if mode == "guided" else "checklist"


def toggle_sym(sym):
    s = st.session_state
    (s.selected.add if s.get(f"chk_{sym}") else s.selected.discard)(sym)

def clear_selection():
    for k in [k for k in st.session_state.keys() if k.startswith("chk_")]:
        del st.session_state[k]
    st.session_state.selected = set()


def finish_checklist():
    s = st.session_state
    s.facts = set(s.selected)
    go_results()


def log_feedback(correct, predicted, confidence, actual=None):
    log = load_log()
    log.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "predicted": predicted,
                "confidence": confidence, "correct": correct, "actual": actual,
                "symptoms": sorted(st.session_state.facts)})
    save_log(log)
    st.session_state.feedback = "correct" if correct else "wrong"

def mark_wrong():
    st.session_state.wrong = True


def submit_wrong(predicted, confidence):
    log_feedback(False, predicted, confidence, st.session_state.get("actual_choice"))


def clear_log():
    save_log([])


# SMALL RENDER HELPERS

def md(html_str):
    st.markdown(html_str, unsafe_allow_html=True)


def chips(keys, kind=""):
    return "".join(ui.chip(SYMPTOMS[k][1], kind) for k in keys)

def sys_label(category):
    return f'<span class="sys">{ui.icon(ui.CAT_ICON[category], 16)}{category}</span>'

def demo_buttons(place):
    cols = st.columns(3)
    for i, name in enumerate(DEMO_SCENARIOS):
        cols[i % 3].button(name, key=f"demo_{place}_{i}", on_click=load_demo, args=(name,), width="stretch")


def build_report(facts, results, multi):
    lines = ["CARGURU - DIAGNOSTIC REPORT", "=" * 44,
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
             "Symptoms reported: " + ", ".join(SYMPTOMS[f][1] for f in sorted(facts)), ""]
    if len(multi) >= 2:
        lines.append(f"Multiple independent faults detected: {len(multi)}")
        lines.append("")
    for i, r in enumerate(results[:8], 1):
        ru = r["rule"]
        lines += [f"{i}. {ru['name']}  [{ru['severity']}]  confidence score {r['confidence']:.0f}%",
                  "   System   : " + ru["category"],
                  "   Matched  : " + ", ".join(SYMPTOMS[s][1] for s in r["matched"]),
                  "   Action   : " + ru["fix"], ""]
    lines.append("Note: " + CONF_NOTE)
    return "\n".join(lines)


# SIDEBAR

def render_sidebar():
    with st.sidebar:
        md(ui.brand())
        md('<div class="cg-navlabel">Navigation</div>')
        for pid, label in PAGES:
            st.button(label, key=f"nav_{pid}", on_click=go, args=(pid,), width="stretch")
        _, n, correct = accuracy_stats()
        acc = f"{correct / n * 100:.0f}%" if n else "n/a"
        md(ui.html(f"""
        <div class="cg-sidestat">
          <div class="ttl">{ui.icon("shield-check", 16)} Knowledge base</div>
          <div class="row"><span>Diagnostic rules</span><b>{len(RULES)}</b></div>
          <div class="row"><span>Symptoms</span><b>{len(SYMPTOMS)}</b></div>
          <div class="row"><span>Vehicle systems</span><b>{len(CATEGORIES)}</b></div>
          <div class="row"><span>Logged accuracy</span><b>{acc}</b></div>
        </div>"""))


def render_topbar():
    """Back / restart on the bar; theme choice lives in the three-dot menu."""
    s = st.session_state
    with st.container(horizontal=True, horizontal_alignment="distribute", vertical_alignment="center", key="topbar"):
        st.button("Back", key="btn_back", on_click=back, disabled=not s.trail, help="Go back to the previous page or step")
        with st.container(horizontal=True, vertical_alignment="center", gap="small"):
            st.button("Restart", key="btn_restart", on_click=restart_app, help="Reset CarGuru and start again")
            with st.popover("", key="menu_pop", help="Menu"):
                md('<div class="cg-menuhead">Appearance</div>')
                for label, name in [("Light", "light"), ("Dark", "dark"), ("System", "system")]:
                    st.button(label, key=f"btn_theme_{name}", on_click=set_theme, args=(label,), width="stretch",
                              help=f"{label} theme" if name != "system" else "Follow your device setting")


def render_mobile_nav():
    """Compact page switcher shown only on small screens (the sidebar is collapsed there)."""
    labels = dict(PAGES)
    inverse = {label: pid for pid, label in PAGES}
    st.session_state["mnav"] = labels[st.session_state.page]
    with st.container(key="mobilenav"):
        st.selectbox("Navigate to", [label for _, label in PAGES], key="mnav", label_visibility="collapsed",
                     on_change=lambda: go(inverse[st.session_state.mnav]))



# PAGE: DASHBOARD

def page_dashboard():
    log, n, correct = accuracy_stats()
    systems = [(cat, ui.CAT_ICON[cat], sum(1 for r in RULES if r["category"] == cat)) for cat in CATEGORIES]
    md(ui.hero_carousel(len(RULES), len(SYMPTOMS), systems))

    crit = sum(1 for r in RULES if r["severity"] == "Critical")
    md(ui.grid([
        ui.kpi("clipboard-list", "Rules", len(RULES), "Weighted IF-THEN", "blue"),
        ui.kpi("list-checks", "Symptoms", len(SYMPTOMS), "Observable signs", "teal"),
        ui.kpi("layers", "Systems", len(CATEGORIES), "Vehicle areas", "navy"),
        ui.kpi("octagon-alert", "Critical", crit, "Safety rules", "red"),
        ui.kpi("target", "Accuracy", f"{correct / n * 100:.0f}%" if n else "n/a",
               f"{correct} of {n} rated" if n else "No ratings yet", "amber"),
    ], 150))

    md(ui.section("play", "Quick access"))
    c1, c2, c3 = st.columns(3)
    with c1.container(key="card_qa_1"):
        md(ui.html(f'<b>New diagnosis</b><div class="cg-note" style="margin:.2rem 0 .8rem">Report symptoms through a guided '
                   f'interview or a searchable checklist.</div>'))
        st.button("Start diagnosis", key="btn_go_diag", type="primary", on_click=new_diagnosis, width="stretch")
    with c2.container(key="card_qa_2"):
        md(ui.html('<b>Knowledge base</b><div class="cg-note" style="margin:.2rem 0 .8rem">Browse all fault rules, '
                   'severities and the symptom catalogue.</div>'))
        st.button("Open knowledge base", key="btn_go_kb", on_click=go, args=("kb",), width="stretch")
    with c3.container(key="card_qa_3"):
        md(ui.html('<b>Rule inspector</b><div class="cg-note" style="margin:.2rem 0 .8rem">See the full symptom-weight '
                   'breakdown of any rule.</div>'))
        st.button("Open rule inspector", key="btn_go_inspector", on_click=go, args=("inspector",), width="stretch")

    left, right = st.columns([3, 2], gap="large")
    with left:
        md(ui.section("layers", "Vehicle systems covered"))
        tiles = []
        for cat in CATEGORIES:
            cnt = sum(1 for r in RULES if r["category"] == cat)
            tiles.append(f'<div class="cg-sys"><div class="cg-sys-ico">{ui.icon(ui.CAT_ICON[cat], 20)}</div>'
                         f'<div><b>{cat}</b><span>{cnt} diagnostic rules</span></div></div>')
        md(ui.grid(tiles, 220))
    with right:
        md(ui.section("history", "Recent diagnoses", "rated by you"))
        if not log:
            md(ui.empty_state("clipboard-list", "No rated diagnoses yet",
                              "Rate a diagnosis as correct or incorrect and it will appear here."))
        else:
            rows = "".join(f'<tr><td>{e["predicted"]}<div class="cg-note" style="margin:0">{e["time"]}</div></td>'
                           f'<td>{e["confidence"]:.0f}%</td><td>{ui.pill(e["correct"])}</td></tr>'
                           for e in log[-5:][::-1])
            md(ui.html(f'<div class="cg-card" style="padding:.4rem .9rem"><table class="cg-table"><tr><th>Fault</th>'
                       f'<th>Score</th><th>Outcome</th></tr>{rows}</table></div>'))

    md(ui.section("play", "Sample cases", "load a ready-made scenario"))
    demo_buttons("dash")



# PAGE: DIAGNOSIS

def render_setup():
    s = st.session_state
    with st.container(key="card_setup"):
        md(ui.section("sliders-horizontal", "1. Choose a diagnosis method", tight=True))
        st.segmented_control("Diagnosis method", MODES, default=MODES[1] if s.mode == "checklist" else MODES[0],
                             key="mode_choice", label_visibility="collapsed")
        if s.get("mode_choice") == MODES[1]:
            st.caption("Search and tick every symptom you notice. Best when you already know what is wrong.")
        else:
            st.caption("The system asks one question at a time, starting with symptoms linked to the most "
                       "dangerous faults, and alerts you as soon as a critical fault becomes likely.")
        md(ui.section("layers", "2. Select affected systems", "optional - leave empty to check every system"))
        cols = st.columns(3)
        for i, cat in enumerate(CATEGORIES):
            if f"area_{i}" not in s:
                s[f"area_{i}"] = cat in s.areas         # restore choices after pressing Back
            cols[i % 3].checkbox(cat, key=f"area_{i}")
        st.write("")
        st.button("Start diagnosis", key="btn_start", type="primary", on_click=start_clicked)
    md(ui.section("play", "Or load a sample case"))
    demo_buttons("diag")


def render_asking():
    s = st.session_state
    q, i = s.queue, s.qi
    if s.alerted:
        md(ui.callout("critical", f"Critical fault likely: {s.alerted}",
                      "Do not keep driving the vehicle. You can continue the interview or stop and view the report now."))
    md(ui.progress(i, len(q), f"Question {i + 1} of {len(q)}"))
    left, right = st.columns([3, 2], gap="large")
    with left:
        sym = q[i]
        sev = eng.symptom_top_severity(sym)
        cat = SYMPTOMS[sym][0]
        with st.container(key="card_question"):
            md(ui.html(f'<div class="cg-qhead"><span class="cg-qico">{ui.icon(ui.CAT_ICON[cat], 20)}</span>'
                       f'<span>{cat}</span>{ui.badge(sev)}<span>linked to a {sev.lower()}-severity fault</span></div>'))
            md(f'<div class="cg-bigq">{SYMPTOMS[sym][1]}</div>')
            st.caption("Is this happening with your vehicle?")
            c1, c2 = st.columns(2)
            c1.button("Yes", key="btn_yes", type="primary", on_click=answer, args=(True,), width="stretch")
            c2.button("No / not sure", key="btn_no", on_click=answer, args=(False,), width="stretch")
        st.write("")
        c3, c4 = st.columns(2)
        c3.button("Undo last answer", key="btn_undo", on_click=undo, disabled=not s.history, width="stretch")
        c4.button("Diagnose now", key="btn_diag_now", on_click=go_results, width="stretch")
    with right:
        with st.container(key="card_live"):
            md(ui.section("brain-circuit", "Current assessment", tight=True))
            live = eng.infer(s.facts, threshold=20)[:4]
            if not live:
                st.caption("Answer a few questions and the engine's current best hypotheses appear here.")
            for r in live:
                col = ui.SEV[r["rule"]["severity"]]["bar"]
                md(ui.html(f'<div class="cg-hyp"><div class="top"><span>{r["rule"]["name"]}</span>'
                           f'<b>{r["confidence"]:.0f}%</b></div>{ui.bar(r["confidence"], col, 7)}</div>'))
            st.caption(f"Symptoms reported so far: {len(s.facts)}")


def render_checklist():
    s = st.session_state
    st.text_input("Search symptoms", key="sym_search", label_visibility="collapsed",
                  placeholder="Search symptoms, e.g. squeal, overheating, smoke, vibration")
    q = (s.get("sym_search") or "").strip().lower()

    groups = {}
    for sym in s.queue:
        if q and q not in SYMPTOMS[sym][1].lower():
            continue
        groups.setdefault(SYMPTOMS[sym][0], []).append(sym)

    with st.container(key="card_selected"):
        md(ui.section("list-checks", "Selected symptoms", f"{len(s.selected)} selected", tight=True))
        if s.selected:
            md(chips(sorted(s.selected), "ok"))
        else:
            st.caption("Nothing selected yet. Tick the symptoms below.")

    first = next((c for c in CATEGORIES if c in groups), None)
    if not groups:
        md(ui.empty_state("search", "No matching symptoms", "Try a different keyword or clear the search box."))
    for cat in CATEGORIES:
        syms = groups.get(cat)
        if not syms:
            continue
        n_sel = sum(1 for x in syms if x in s.selected)
        with st.expander(f"{cat}  -  {n_sel} selected of {len(syms)}", expanded=bool(q) or n_sel > 0 or cat == first):
            cols = st.columns(2)
            for idx, sym in enumerate(syms):
                k = f"chk_{sym}"
                if k not in s:
                    s[k] = sym in s.selected          # keep selection when a symptom is filtered out and back
                cols[idx % 2].checkbox(SYMPTOMS[sym][1], key=k, on_change=toggle_sym, args=(sym,))
    st.write("")
    b1, b2, _ = st.columns([2, 2, 3])
    b1.button("Run diagnosis", key="btn_checklist_go", type="primary", on_click=finish_checklist,
              disabled=not s.selected, width="stretch")
    b2.button("Clear selection", key="btn_clear_sel__dang", on_click=clear_selection,
              disabled=not s.selected, width="stretch")


def render_why_not(facts):
    with st.container(key="card_whynot"):
        md(ui.section("circle-help", "Could it be something else?", "why-not explainer", tight=True))
        st.caption("Pick any fault to see why it was accepted or rejected, and which symptoms were missing.")
        c1, c2 = st.columns(2)
        cat = c1.selectbox("System", ["All systems"] + CATEGORIES, key="wn_cat")
        names = [r["name"] for r in RULES if cat == "All systems" or r["category"] == cat]
        name = c2.selectbox("Suspected fault", names, key=f"wn_{cat}")
        wn = eng.why_not(name, facts)
        if wn["fired"]:
            md(ui.callout("success", f"{name} was accepted",
                          f"Confidence score {wn['confidence']:.0f}% meets the {THRESHOLD}% threshold."))
        else:
            md(ui.callout("critical", f"{name} was rejected",
                          f"Confidence score {wn['confidence']:.0f}% is {wn['shortfall']:.0f} points below the "
                          f"{THRESHOLD}% threshold."))
        a, b = st.columns(2)
        with a:
            st.markdown("**Reported symptoms that support it**")
            if wn["matched"]:
                md(ui.symptom_list([(SYMPTOMS[x][1], w) for x, w in wn["matched"]], "match"))
            else:
                st.caption("None of this fault's indicators were reported.")
        with b:
            st.markdown("**Indicators that were missing**")
            if wn["missing"]:
                md(ui.symptom_list([(SYMPTOMS[x][1], w) for x, w in wn["missing"]], "missing"))
            else:
                st.caption("Nothing missing.")
        if not wn["fired"] and wn["needed"]:
            extra = ", ".join(SYMPTOMS[x][1] for x in wn["needed"])
            md(ui.callout("info", "What would change the outcome",
                          f"If these were also reported the score would reach about {wn['confidence_if_needed']:.0f}%: {extra}."))


def render_results():
    s = st.session_state
    facts = s.facts
    if not facts:
        md(ui.callout("warning", "No symptoms were reported", "There is nothing to diagnose yet."))
        st.button("Start again", key="btn_start_again", type="primary", on_click=new_diagnosis)
        return

    results = eng.infer(facts)
    multi = eng.detect_multiple_faults(facts)
    now = datetime.now()
    md(ui.html(f"""
    <div class="cg-reporthead">
      <div class="t">{ui.icon("file-text", 22)} Diagnostic Report</div>
      <div class="m">Reference CG-{now:%Y%m%d-%H%M}<br>{now:%d %b %Y, %H:%M} &nbsp;|&nbsp; {len(facts)} symptoms reported</div>
    </div>"""))
    md(chips(sorted(facts)))

    if not results:
        md(ui.callout("info", f"No fault reached the {THRESHOLD}% threshold",
                      "Report more symptoms, or use the why-not explainer below to see how close each fault came."))
    else:
        crit = [r for r in results if r["rule"]["severity"] == "Critical" and r["confidence"] >= CRITICAL_ALERT]
        if crit:
            md(ui.callout("critical", f"Safety warning: {crit[0]['rule']['name']} is likely",
                          f"Confidence score {crit[0]['confidence']:.0f}%. Do not drive the vehicle. {crit[0]['rule']['fix']}"))
        top = results[0]
        ru, sev = top["rule"], top["rule"]["severity"]
        sc = ui.SEV[sev]

# primary finding 
        md(ui.section("stethoscope", "Primary finding"))
        left, right = st.columns([5, 3], gap="medium")
        with left:
            md(ui.html(f"""
            <div class="cg-card"><div class="cg-diag">
              {ui.gauge(top["confidence"])}
              <div style="flex:1;min-width:220px">
                <div class="cg-eyebrow">Most probable fault</div>
                <div class="cg-fault-name">{ru["name"]}</div>
                <div class="cg-meta">{sys_label(ru["category"])}{ui.badge(sev)}
                  <span>{sc["label"]}</span></div>
              </div></div>
              <div style="margin-top:1rem"><div class="cg-meta" style="justify-content:space-between">
                <span>Confidence score</span><b>{top["confidence"]:.0f}%</b></div>
                {ui.bar(top["confidence"], ui.BLUE, 10)}</div>
              <div class="cg-note">{CONF_NOTE}</div>
            </div>"""))
            md(ui.callout(ADVICE_KIND[sev], ui.DRIVE_ADVICE[sev], f"Severity level: {sev}."))
        with right:
            md(ui.html(f"""
            <div class="cg-card"><div class="cg-eyebrow" style="margin-bottom:.5rem">Report summary</div>
            <table class="cg-table">
              <tr><td>Symptoms reported</td><td><b>{len(facts)}</b></td></tr>
              <tr><td>Rules evaluated</td><td><b>{len(RULES)}</b></td></tr>
              <tr><td>Candidate faults</td><td><b>{len(results)}</b></td></tr>
              <tr><td>Independent faults</td><td><b>{len(multi)}</b></td></tr>
              <tr><td>Reporting threshold</td><td><b>{THRESHOLD}%</b></td></tr>
            </table></div>"""))

        # explanation 
        md(ui.section("lightbulb", "Why this diagnosis"))
        total = len(ru["symptoms"])
        runner = (f" No other candidate scored higher; the next closest is {results[1]['rule']['name']} at "
                  f"{results[1]['confidence']:.0f}%." if len(results) > 1 else "")
        w_list = [f"{ru['symptoms'][x]:.2f}" for x in top["matched"]]
        miss = [(SYMPTOMS[x][1], ru["symptoms"][x]) for x in top["missing"]]
        miss_body = ui.symptom_list(miss, "missing") if miss else '<div class="cg-note">Every indicator was reported.</div>'
        card_a = ui.html(f"""
            <div class="cg-card"><div class="cg-eyebrow">Matched symptoms</div>
              {ui.symptom_list([(SYMPTOMS[x][1], ru["symptoms"][x]) for x in top["matched"]], "match")}
              <div class="cg-formula">{" + ".join(w_list)} = {top["confidence"] / 100:.2f}</div>
              <div class="cg-note" style="margin-top:.3rem">{len(top["matched"])} of {total} indicators defined for this
              fault were reported. Their combined weight is {top["confidence"]:.0f}% of the rule, which meets the
              {THRESHOLD}% reporting threshold.{runner}</div></div>""")
        card_b = ui.html(f"""
            <div class="cg-card"><div class="cg-eyebrow">Indicators not reported</div>{miss_body}
              <div class="cg-note">Checking these would help confirm or rule out the diagnosis.</div></div>""")
        md(ui.grid([card_a, card_b], 360))

    # -next steps 
        md(ui.section("clipboard-check", "Recommended next steps"))
        steps = [f"<b>Repair action:</b> {ru['fix']}"]
        if top["missing"]:
            steps.append("<b>Confirm the diagnosis</b> by checking: " +
                         ", ".join(SYMPTOMS[x][1][0].lower() + SYMPTOMS[x][1][1:] for x in top["missing"]) + ".")
        steps.append(f"<b>Driving advice:</b> {ui.DRIVE_ADVICE[sev]}.")
        steps.append("<b>Verify with a qualified technician</b> before carrying out major repairs.")
        md(f'<div class="cg-card"><ol class="cg-ol">{"".join(f"<li>{x}</li>" for x in steps)}</ol></div>')

        # multi-fault 
        md(ui.section("split", "Multi-fault detection"))
        if len(multi) >= 2:
            md(ui.callout("warning", f"{len(multi)} independent faults detected",
                          "Each fault below is explained by a separate group of symptoms, so the vehicle probably has "
                          "more than one problem."))
            cards = []
            for r in multi:
                c = ui.SEV[r["rule"]["severity"]]["bar"]
                cards.append(ui.html(f"""
                <div class="cg-card"><b>{r["rule"]["name"]}</b>
                  <div class="cg-meta" style="margin:.35rem 0">{ui.badge(r["rule"]["severity"])}<span>{r["confidence"]:.0f}%</span></div>
                  {ui.bar(r["confidence"], c, 7)}
                  <div style="margin-top:.6rem">{chips(r["matched"], "ok")}</div>
                  <div class="cg-note"><b>Action:</b> {r["rule"]["fix"]}</div></div>"""))
            md(ui.grid(cards, 300))
            st.caption(f"Method: after the best fault is chosen its symptoms are removed and the rules are run again; "
                       f"another fault must still reach {MULTI_THRESHOLD}% using only the leftover symptoms.")
        else:
            md(ui.callout("info", "One fault pattern found",
                          "The other candidates below are competing explanations of the same symptoms, not separate faults."))

        #  ranked candidates 
        md(ui.section("list-filter", "All candidate faults", "ranked by confidence score"))
        for i, r in enumerate(results[:8]):
            ru2 = r["rule"]
            with st.expander(f"{i + 1}.  {ru2['name']}   |   {r['confidence']:.0f}%   |   {ru2['severity']}",
                             expanded=(i < 2)):
                md(ui.bar(r["confidence"], ui.SEV[ru2["severity"]]["bar"], 8))
                md(ui.html(f'<div class="cg-meta" style="margin:.6rem 0">{sys_label(ru2["category"])}{ui.badge(ru2["severity"])}</div>'))
                md("<b>Matched:</b> " + chips(r["matched"], "ok"))
                if r["missing"]:
                    md("<b>Also check:</b> " + chips(r["missing"], "miss"))
                md(f'<div class="cg-note"><b>Action:</b> {ru2["fix"]}</div>')
        if len(results) > 8:
            st.caption(f"Showing the top 8 of {len(results)} candidate faults.")

    render_why_not(facts)

    # accuracy feedback 
    if results:
        top = results[0]
        with st.container(key="card_feedback"):
            md(ui.section("target", "Was the primary diagnosis correct?", "helps CarGuru measure its own accuracy", tight=True))
            if s.feedback is None:
                if not s.wrong:
                    c1, c2, _ = st.columns([2, 2, 3])
                    c1.button("Yes, correct", key="btn_correct__succ", on_click=log_feedback,
                              args=(True, top["rule"]["name"], top["confidence"]), width="stretch")
                    c2.button("No, incorrect", key="btn_wrong", on_click=mark_wrong, width="stretch")
                else:
                    st.selectbox("What was the actual fault?",
                                 ["Not sure / not in the system"] + [r["name"] for r in RULES], key="actual_choice")
                    st.button("Submit feedback", key="btn_submit", type="primary", on_click=submit_wrong,
                              args=(top["rule"]["name"], top["confidence"]))
            else:
                _, n, correct = accuracy_stats()
                md(ui.callout("success", "Feedback recorded",
                              f"Running accuracy: correct in {correct} of {n} sessions ({correct / n * 100:.0f}%)."))

    st.write("")
    d1, d2, _ = st.columns([2, 2, 3])
    d1.download_button("Download report", build_report(facts, results, multi), key="btn_download__succ",
                       file_name="carguru_diagnostic_report.txt", mime="text/plain", width="stretch")
    d2.button("New diagnosis", key="btn_new", on_click=new_diagnosis, width="stretch")


def page_diagnose():
    stage = st.session_state.stage
    md(ui.page_header("stethoscope", "Vehicle Diagnosis",
                      "Report the symptoms you observe and CarGuru will identify the most probable faults."))
    md(ui.stepper({"setup": 1, "asking": 2, "checklist": 2}.get(stage, 3)))
    {"setup": render_setup, "asking": render_asking, "checklist": render_checklist}.get(stage, render_results)()



# PAGE: RULE INSPECTOR

def page_inspector():
    md(ui.page_header("microscope", "Rule Inspector",
                      "Show the full symptom-weight breakdown of any rule and test it interactively."))
    c1, c2 = st.columns([2, 3])
    typed = c1.text_input("Search rules", placeholder="Type a rule name, e.g. brake pads, battery, coolant")
    matches = [r for r in RULES if typed.lower() in r["name"].lower()] if typed else RULES
    if not matches:
        md(ui.callout("warning", "No rule matches that text", "Try a shorter or different keyword."))
        return
    name = c2.selectbox(f"Matching rules ({len(matches)})", [r["name"] for r in matches])
    rule = eng.RULE_BY_NAME[name]
    idx = RULES.index(rule)
    sev = rule["severity"]

    conds = f' <span class="kw">AND</span> '.join(
        ui.chip(f'{SYMPTOMS[s][1]} <b>{w:.2f}</b>') for s, w in rule["symptoms"].items())
    md(ui.html(f"""
    <div class="cg-card">
      <div class="cg-diag" style="gap:1rem">
        <div style="flex:1;min-width:240px">
          <div class="cg-eyebrow">Rule</div>
          <div class="cg-fault-name" style="font-size:1.5rem">{rule["name"]}</div>
          <div class="cg-meta">{sys_label(rule["category"])}{ui.badge(sev)}</div>
        </div>
      </div>
      <div class="cg-cond" style="margin-top:.9rem"><span class="kw">IF</span>{conds}<span class="kw">THEN</span>
        <b>{rule["name"]}</b></div>
      <div class="cg-note"><b>Recommended action:</b> {rule["fix"]}</div>
    </div>"""))

    md(ui.section("sliders-horizontal", "Test the rule", "tick symptoms to see the score change - pre-filled from your current diagnosis"))
    chosen = set()
    cols = st.columns(2)
    for i, (sym, w) in enumerate(rule["symptoms"].items()):
        if cols[i % 2].checkbox(f"{SYMPTOMS[sym][1]}  (weight {w:.2f})", value=sym in st.session_state.facts,
                                key=f"insp_{idx}_{sym}"):
            chosen.add(sym)

    bd = eng.rule_breakdown(name, chosen)
    fires = bd["total"] >= THRESHOLD
    a, b = st.columns([3, 2], gap="medium")
    with a:
        md(ui.html(f"""
        <div class="cg-card"><div class="cg-eyebrow">Calculation</div>
          <div class="cg-formula">Confidence = {bd["formula"]}</div>
          <div class="cg-meta" style="justify-content:space-between;margin-top:.5rem"><span>Confidence score</span><b>{bd["total"]:.0f}%</b></div>
          {ui.bar(bd["total"], ui.BLUE if fires else "#94A3B8", 10)}
          <div class="cg-note">Threshold: {THRESHOLD}%. {CONF_NOTE}</div></div>"""))
    with b:
        if fires:
            md(ui.callout("success", "Rule fires", f"{bd['total']:.0f}% meets the {THRESHOLD}% threshold."))
        else:
            md(ui.callout("critical", "Rule does not fire", f"{bd['total']:.0f}% is below the {THRESHOLD}% threshold."))
    trs = []
    for r in bd["rows"]:
        status = ui.chip("Reported", "ok") if r["reported"] else ui.chip("Not reported", "miss")
        wcell = (f'<div style="display:flex;align-items:center;gap:.7rem"><div style="flex:1;min-width:90px">'
                 f'{ui.bar(r["weight"] * 100, ui.BLUE, 8)}</div><b>{r["weight"]:.2f}</b></div>')
        trs.append([esc(r["label"]), wcell, status, f'{r["contribution"]:.2f}'])
    md(ui.table(["Indicator", "Weight", "Status", "Contribution"], trs))


# PAGE: KNOWLEDGE BASE

def page_kb():
    md(ui.page_header("library", "Knowledge Base", "All diagnostic rules, symptoms and system coverage."))
    crit = sum(1 for r in RULES if r["severity"] == "Critical")
    md(ui.grid([ui.kpi("clipboard-list", "Rules", len(RULES), tone="blue"),
                ui.kpi("list-checks", "Symptoms", len(SYMPTOMS), tone="teal"),
                ui.kpi("layers", "Systems", len(CATEGORIES), tone="navy"),
                ui.kpi("octagon-alert", "Critical rules", crit, tone="red")], 180))
    t1, t2, t3 = st.tabs(["Fault rules", "Symptom catalogue", "Coverage"])
    with t1:
        f1, f2, f3 = st.columns([2, 2, 1])
        text = f1.text_input("Search faults", placeholder="Search by fault name", key="kb_text")
        cat = f2.selectbox("System", ["All systems"] + CATEGORIES, key="kb_cat")
        sev = f3.selectbox("Severity", ["All"] + list(SEVERITY_RANK), key="kb_sev")
        rows = [r for r in RULES
                if (cat == "All systems" or r["category"] == cat) and (sev == "All" or r["severity"] == sev)
                and text.lower() in r["name"].lower()]
        st.caption(f"{len(rows)} of {len(RULES)} rules")
        md(ui.table(["Fault", "System", "Severity", "Indicators", "Recommended action"],
                    [[f"<b>{esc(r['name'])}</b>", esc(r["category"]), ui.badge(r["severity"]), len(r["symptoms"]),
                      esc(r["fix"])] for r in rows], max_height=480))
    with t2:
        stext = st.text_input("Search symptoms", placeholder="Search by symptom", key="kb_sym")
        use = {s: sum(1 for r in RULES if s in r["symptoms"]) for s in SYMPTOMS}
        rows = [(k, c, lbl) for k, (c, lbl) in SYMPTOMS.items() if stext.lower() in lbl.lower()]
        st.caption(f"{len(rows)} of {len(SYMPTOMS)} symptoms")
        md(ui.table(["Symptom", "System", "Highest linked severity", "Used by rules"],
                    [[esc(lbl), esc(c), ui.badge(eng.symptom_top_severity(k)), use[k]] for k, c, lbl in rows],
                    max_height=480))
    with t3:
        mx = max(sum(1 for r in RULES if r["category"] == c) for c in CATEGORIES)
        parts = []
        for c in CATEGORIES:
            n = sum(1 for r in RULES if r["category"] == c)
            parts.append(ui.html(f'<div class="cg-card"><div class="cg-meta" style="justify-content:space-between;margin-bottom:.4rem">'
                                 f'{sys_label(c)}<b>{n} rules</b></div>{ui.bar(n / mx * 100, ui.BLUE, 8)}</div>'))
        md(ui.grid(parts, 300))


# PAGE: ACCURACY TRACKER

def page_accuracy():
    md(ui.page_header("target", "Accuracy Tracker", "How often the primary diagnosis matched what you found in reality."))
    log, n, correct = accuracy_stats()
    if not n:
        md(ui.empty_state("clipboard-list", "No feedback logged yet",
                          "After a diagnosis, answer 'Was the primary diagnosis correct?' and the results appear here."))
        return
    md(ui.grid([ui.kpi("clipboard-list", "Sessions rated", n, tone="blue"),
                ui.kpi("circle-check", "Correct", correct, tone="teal"),
                ui.kpi("circle-x", "Incorrect", n - correct, tone="red"),
                ui.kpi("target", "Accuracy", f"{correct / n * 100:.0f}%", f"correct in {correct}/{n} sessions", "amber")], 180))
    md(ui.html(f'<div class="cg-card" style="margin-top:.8rem"><div class="cg-meta" style="justify-content:space-between">'
               f'<span>Correct in {correct} of {n} sessions</span><b>{correct / n * 100:.0f}%</b></div>'
               f'{ui.bar(correct / n * 100, ui.TEAL, 10)}</div>'))
    running, ok = [], 0
    for i, e in enumerate(log, 1):
        ok += 1 if e["correct"] else 0
        running.append(ok / i * 100)
    md(ui.section("chart-line", "Running accuracy", "percent correct after each rated session"))
    md(ui.line_chart(running))
    md(ui.section("history", "History"))
    md(ui.table(["Time", "Predicted fault", "Confidence", "Outcome", "Actual fault (if wrong)"],
                [[esc(e["time"]), f"<b>{esc(e['predicted'])}</b>", f"{e['confidence']:.0f}%", ui.pill(e["correct"]),
                  esc(e.get("actual") or "-")] for e in log[::-1]], max_height=420))
    st.button("Clear log", key="btn_clear_log__dang", on_click=clear_log)



# PAGE: ABOUT

def page_about():
    md(ui.page_header("info", "About CarGuru", "A rule-based expert system for vehicle fault diagnosis."))
    md(ui.section("layers", "Expert system architecture"))
    parts = [("library", "Knowledge base", "knowledge_base.py",
              f"{len(RULES)} weighted IF-THEN rules over {len(SYMPTOMS)} symptoms in {len(CATEGORIES)} vehicle systems."),
             ("cpu", "Inference engine", "engine.py",
              "Forward chaining: every rule is tested against the reported facts and scored."),
             ("layout-dashboard", "User interface", "app.py, ui.py",
              "Streamlit dashboard with guided interview, searchable checklist and diagnostic report."),
             ("lightbulb", "Explanation facility", "engine.py, app.py",
              "Matched symptoms, missing indicators, why-not answers and the rule inspector.")]
    md(ui.grid([ui.html(f'<div class="cg-kpi" style="align-items:flex-start"><div class="cg-kpi-ico tone-blue">'
                        f'{ui.icon(i, 22)}</div><div><div class="cg-kpi-label">{f}</div><div style="font-weight:700;font-size:1.05rem">{t}</div>'
                        f'<div class="cg-kpi-note" style="font-size:.88rem;margin-top:.25rem">{d}</div></div></div>')
                for i, t, f, d in parts], 340))

    md(ui.section("gauge", "How the confidence score works"))
    md(ui.html(f"""
    <div class="cg-card">
      <div class="cg-formula">confidence = (sum of the weights of the reported symptoms) x 100</div>
      <div class="cg-note" style="font-size:.9rem">The weights of each rule add up to 1.0. A fault is shown when its score reaches
      {THRESHOLD}%. {CONF_NOTE}</div>
    </div>"""))

    md(ui.section("badge-check", "Special features"))
    feats = [("circle-help", "Why-not answers", "Pick any rejected fault to see exactly which symptoms were missing."),
             ("target", "Accuracy tracker", "Every diagnosis can be rated; accuracy is logged and charted."),
             ("microscope", "Rule inspector", "Full weight breakdown of any rule with a live calculator."),
             ("list-filter", "Severity-based ordering", "Questions linked to critical faults are asked first, with an early alert."),
             ("split", "Multi-fault detection", "An explaining-away step finds independent faults in the same report.")]
    md(ui.grid([ui.html(f'<div class="cg-sys" style="align-items:flex-start"><div class="cg-sys-ico">{ui.icon(i, 20)}</div>'
                        f'<div><b>{t}</b><span>{d}</span></div></div>') for i, t, d in feats], 300))
    st.caption("Icons by Lucide (lucide.dev), ISC license. Built with Python and Streamlit.")


# MAIN

init_state()
md(ui.global_css(st.session_state.page, st.session_state.theme))
render_sidebar()
render_topbar()
render_mobile_nav()
{"dashboard": page_dashboard, "diagnose": page_diagnose, "inspector": page_inspector,
 "kb": page_kb, "accuracy": page_accuracy, "about": page_about}[st.session_state.page]()
