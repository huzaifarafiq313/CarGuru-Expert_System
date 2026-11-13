"""
CarGuru UI toolkit
------------------
Design tokens (light + dark), Lucide icon helpers, global CSS and small HTML components.
Pure presentation - no diagnosis logic lives here.

Theming: every colour is a CSS variable. global_css(page, theme) emits the Light palette,
the Dark palette, or "System" (light + a prefers-color-scheme: dark override).
"""
import base64
from html import escape as esc

from icons import ICONS
from knowledge_base import CATEGORIES

THEMES = ["Light", "Dark", "System"]

# ------------------------------------------------------------------ design tokens
NAVY = "#14243A"
BLUE = "#2563EB"
TEAL = "#0D9488"

# severity -> bar colour / icon / label (badge colours come from CSS variables)
SEV = {
    "Low":      {"bar": "#16A34A", "icon": "circle-check",   "label": "Low concern"},
    "Medium":   {"bar": "#D97706", "icon": "triangle-alert", "label": "Warning"},
    "High":     {"bar": "#EA580C", "icon": "triangle-alert", "label": "High priority"},
    "Critical": {"bar": "#DC2626", "icon": "octagon-alert",  "label": "Critical"},
}
DRIVE_ADVICE = {
    "Critical": "Do not drive the vehicle",
    "High": "Drive only to a workshop",
    "Medium": "Have it inspected soon",
    "Low": "Safe to drive - schedule a repair",
}
CAT_ICON = {
    "Engine & Fuel": "engine",
    "Cooling": "thermometer-snowflake",
    "Brakes": "disc-3",
    "Steering, Suspension & Tires": "ship-wheel",
    "Transmission & Clutch": "cog",
    "Electrical & Battery": "battery-charging",
    "Exhaust & Emissions": "wind",
    "Climate Control": "snowflake",
    "Hybrid & Electric Drivetrain": "plug-zap",
}
CALLOUT_ICON = {"info": "info", "success": "circle-check", "warning": "triangle-alert", "critical": "octagon-alert"}

LIGHT = {
    "bg": "#F4F7FB", "surface": "#FFFFFF", "surface-2": "#F1F5F9", "border": "#E3E9F2", "border-strong": "#CBD5E1",
    "text": "#14243A", "text-2": "#334155", "text-muted": "#64748B", "primary": "#2563EB", "primary-soft": "#EFF6FF",
    "track": "#E5EAF2", "shadow": "0 1px 3px rgba(20,36,58,.06), 0 1px 2px rgba(20,36,58,.04)",
    "sidebar-bg": "#14243A", "pagehead-bg": "#14243A", "icon-bg": "#E8EEF6", "formula-bg": "#F1F5F9",
    "chip-bg": "#EEF2F7", "chip-fg": "#334155", "chip-ok-bg": "#DCFCE7", "chip-ok-fg": "#166534",
    "sev-low-bg": "#DCFCE7", "sev-low-fg": "#166534", "sev-medium-bg": "#FEF3C7", "sev-medium-fg": "#92400E",
    "sev-high-bg": "#FFEDD5", "sev-high-fg": "#C2410C", "sev-critical-bg": "#FEE2E2", "sev-critical-fg": "#B91C1C",
    "co-info-bg": "#EFF6FF", "co-info-bd": "#BFDBFE", "co-info-fg": "#1E3A8A",
    "co-success-bg": "#F0FDF4", "co-success-bd": "#BBF7D0", "co-success-fg": "#166534",
    "co-warning-bg": "#FFFBEB", "co-warning-bd": "#FDE68A", "co-warning-fg": "#92400E",
    "co-critical-bg": "#FEF2F2", "co-critical-bd": "#FECACA", "co-critical-fg": "#991B1B",
    "tone-blue-bg": "#EFF6FF", "tone-blue-fg": "#2563EB", "tone-teal-bg": "#F0FDFA", "tone-teal-fg": "#0D9488",
    "tone-amber-bg": "#FFFBEB", "tone-amber-fg": "#D97706", "tone-red-bg": "#FEF2F2", "tone-red-fg": "#DC2626",
    "tone-slate-bg": "#F1F5F9", "tone-slate-fg": "#475569", "tone-navy-bg": "#E8EEF6", "tone-navy-fg": "#14243A",
}
DARK = {
    "bg": "#0B1322", "surface": "#121E32", "surface-2": "#18273F", "border": "#243650", "border-strong": "#33496B",
    "text": "#E6EDF7", "text-2": "#C3CFE0", "text-muted": "#9AABC4", "primary": "#3B82F6", "primary-soft": "#15294A",
    "track": "#22334F", "shadow": "0 1px 3px rgba(0,0,0,.35)",
    "sidebar-bg": "#0A1220", "pagehead-bg": "#1E3A5F", "icon-bg": "#1B2C47", "formula-bg": "#0E192B",
    "chip-bg": "#1B2C47", "chip-fg": "#C7D2E3", "chip-ok-bg": "rgba(34,197,94,.16)", "chip-ok-fg": "#86EFAC",
    "sev-low-bg": "rgba(34,197,94,.16)", "sev-low-fg": "#4ADE80", "sev-medium-bg": "rgba(245,158,11,.16)",
    "sev-medium-fg": "#FBBF24", "sev-high-bg": "rgba(249,115,22,.17)", "sev-high-fg": "#FB923C",
    "sev-critical-bg": "rgba(239,68,68,.18)", "sev-critical-fg": "#F87171",
    "co-info-bg": "rgba(59,130,246,.12)", "co-info-bd": "rgba(59,130,246,.38)", "co-info-fg": "#93C5FD",
    "co-success-bg": "rgba(34,197,94,.10)", "co-success-bd": "rgba(34,197,94,.32)", "co-success-fg": "#86EFAC",
    "co-warning-bg": "rgba(245,158,11,.10)", "co-warning-bd": "rgba(245,158,11,.34)", "co-warning-fg": "#FCD34D",
    "co-critical-bg": "rgba(239,68,68,.12)", "co-critical-bd": "rgba(239,68,68,.38)", "co-critical-fg": "#FCA5A5",
    "tone-blue-bg": "rgba(59,130,246,.16)", "tone-blue-fg": "#60A5FA", "tone-teal-bg": "rgba(20,184,166,.16)",
    "tone-teal-fg": "#2DD4BF", "tone-amber-bg": "rgba(245,158,11,.16)", "tone-amber-fg": "#FBBF24",
    "tone-red-bg": "rgba(239,68,68,.16)", "tone-red-fg": "#F87171", "tone-slate-bg": "rgba(148,163,184,.14)",
    "tone-slate-fg": "#CBD5E1", "tone-navy-bg": "rgba(148,163,184,.16)", "tone-navy-fg": "#E2E8F0",
}

# Streamlit widget key -- Lucide icon drawn inside the real button.
BUTTON_ICONS = {
    "nav_dashboard": "layout-dashboard", "nav_diagnose": "stethoscope", "nav_inspector": "microscope",
    "nav_kb": "library", "nav_accuracy": "target", "nav_about": "info",
    "btn_go_diag": "stethoscope", "btn_go_kb": "library", "btn_go_inspector": "microscope",
    "btn_start": "play", "btn_yes": "check", "btn_no": "x", "btn_undo": "undo-2",
    "btn_diag_now": "fast-forward", "btn_checklist_go": "stethoscope", "btn_clear_sel__dang": "x",
    "btn_correct__succ": "circle-check", "btn_wrong": "circle-x", "btn_submit": "check",
    "btn_download__succ": "download", "btn_new": "rotate-ccw", "btn_clear_log__dang": "trash-2",
    "btn_start_again": "rotate-ccw",
    "btn_back": "arrow-left", "btn_restart": "refresh-cw",
    "btn_theme_light": "sun", "btn_theme_dark": "moon", "btn_theme_system": "monitor",
}


#  helpers
def html(s):
    """Collapse indented HTML so Markdown never mistakes it for a code block."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def icon(name, size=18, stroke=2, color="currentColor", style=""):
    """Inline Lucide SVG."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" '
            f'stroke-linejoin="round" style="flex-shrink:0;{style}" aria-hidden="true">{ICONS[name]}</svg>')


def _mask_uri(name, stroke=2):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" '
           f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>')
    return 'url("data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '")'


#  components
def badge(sev, with_icon=True):
    ic = icon(SEV[sev]["icon"], 13, 2.2) if with_icon else ""
    return f'<span class="cg-badge sev-{sev.lower()}">{ic}{sev}</span>'


def pill(ok):
    """Correct / Incorrect outcome pill."""
    if ok:
        return f'<span class="cg-badge sev-low">{icon("circle-check", 13, 2.2)}Correct</span>'
    return f'<span class="cg-badge sev-critical">{icon("circle-x", 13, 2.2)}Incorrect</span>'


def chip(text, kind=""):
    return f'<span class="cg-chip {kind}">{text}</span>'


def bar(pct, color=BLUE, height=8):
    pct = max(0, min(100, pct))
    return f'<div class="cg-bar" style="height:{height}px"><div style="width:{pct:.0f}%;background:{color}"></div></div>'


def progress(done, total, label):
    pct = done / total * 100 if total else 0
    return html(f'<div class="cg-progress"><div class="cg-progress-top"><span>{label}</span>'
                f'<b>{pct:.0f}%</b></div>{bar(pct, BLUE, 8)}</div>')


def page_header(icon_name, title, subtitle=""):
    return html(f"""
    <div class="cg-pagehead">
      <div class="cg-pagehead-ico">{icon(icon_name, 24)}</div>
      <div><h1>{title}</h1><p>{subtitle}</p></div>
    </div>""")


def section(icon_name, title, subtitle="", tight=False):
    sub = f'<span class="cg-section-sub">{subtitle}</span>' if subtitle else ""
    top = ' style="margin-top:0"' if tight else ""
    return html(f"""
    <div class="cg-section"{top}>
      <span class="cg-section-ico">{icon(icon_name, 17)}</span>
      <span class="cg-section-title">{title}</span>{sub}
    </div>""")


def kpi(icon_name, label, value, note="", tone="blue"):
    note_html = f'<div class="cg-kpi-note">{note}</div>' if note else ""
    return html(f"""
    <div class="cg-kpi">
      <div class="cg-kpi-ico tone-{tone}">{icon(icon_name, 22)}</div>
      <div>
        <div class="cg-kpi-label">{label}</div>
        <div class="cg-kpi-value">{value}</div>{note_html}
      </div>
    </div>""")


def grid(items, min_width=210):
    return f'<div class="cg-grid" style="--min:{min_width}px">{"".join(items)}</div>'


def callout(kind, title, body=""):
    body_html = f'<div class="cg-callout-body">{body}</div>' if body else ""
    return html(f"""
    <div class="cg-callout co-{kind}">
      {icon(CALLOUT_ICON[kind], 20)}
      <div><div class="cg-callout-title">{title}</div>{body_html}</div>
    </div>""")


def empty_state(icon_name, title, body):
    return html(f"""
    <div class="cg-card cg-empty">
      <div class="cg-empty-ico">{icon(icon_name, 30)}</div>
      <div class="cg-empty-title">{title}</div><div>{body}</div>
    </div>""")


def symptom_list(items, kind="match"):
    """items: list of (label, weight|None). kind = match | missing"""
    ic = icon("check", 15, 2.6) if kind == "match" else icon("circle-dot", 15, 2)
    rows = []
    for label, w in items:
        wt = f'<span class="cg-li-w">{w:.2f}</span>' if w is not None else ""
        rows.append(f'<li class="{kind}"><span class="cg-li-ico">{ic}</span><span>{esc(label)}</span>{wt}</li>')
    return f'<ul class="cg-list">{"".join(rows)}</ul>'


def stepper(active):
    steps = [("Select system", "clipboard-list"), ("Report symptoms", "list-checks"), ("Diagnostic report", "file-text")]
    out = []
    for i, (label, ic) in enumerate(steps, 1):
        state = "active" if i == active else ("done" if i < active else "")
        dot = icon("check", 16, 3) if i < active else icon(ic, 16)
        out.append(f'<div class="cg-step {state}"><span class="cg-step-dot">{dot}</span>'
                   f'<span class="cg-step-label">{label}</span></div>')
        if i < len(steps):
            out.append(f'<div class="cg-step-line {"done" if i < active else ""}"></div>')
    return f'<div class="cg-stepper">{"".join(out)}</div>'


def gauge(pct, color=BLUE, size=132):
    r = 46
    c = 2 * 3.14159265 * r
    dash = c * max(0, min(100, pct)) / 100
    return html(f"""
    <svg width="{size}" height="{size}" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" role="img"
         aria-label="Confidence {pct:.0f} percent">
      <circle cx="60" cy="60" r="{r}" fill="none" style="stroke:var(--track)" stroke-width="10"/>
      <circle cx="60" cy="60" r="{r}" fill="none" stroke="{color}" stroke-width="10" stroke-linecap="round"
              stroke-dasharray="{dash:.1f} {c:.1f}" transform="rotate(-90 60 60)"/>
      <text x="60" y="64" text-anchor="middle" font-size="26" font-weight="700" style="fill:var(--text)"
            font-family="Inter,Segoe UI,Arial,sans-serif">{pct:.0f}%</text>
      <text x="60" y="82" text-anchor="middle" font-size="9" style="fill:var(--text-muted)" letter-spacing=".6"
            font-family="Inter,Segoe UI,Arial,sans-serif">CONFIDENCE</text>
    </svg>""")


def table(headers, rows, max_height=None):
    """Theme-aware HTML table. Cells are trusted HTML (escape plain text with esc() first)."""
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    style = f' style="max-height:{max_height}px"' if max_height else ""
    return f'<div class="cg-tablewrap"{style}><table class="cg-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def line_chart(values, y_max=100):
    """Small responsive SVG line chart of percentages."""
    w, h, pl, pr, pt, pb = 640, 230, 40, 16, 14, 30
    n = len(values)
    xs = [pl + (w - pl - pr) * (i / (n - 1) if n > 1 else 0.5) for i in range(n)]
    ys = [pt + (h - pt - pb) * (1 - v / y_max) for v in values]
    parts = []
    for g in (0, 25, 50, 75, 100):
        y = pt + (h - pt - pb) * (1 - g / y_max)
        parts.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{w - pr}" y2="{y:.1f}" style="stroke:var(--border)" stroke-width="1"/>')
        parts.append(f'<text x="{pl - 8}" y="{y + 4:.1f}" text-anchor="end" font-size="11" style="fill:var(--text-muted)">{g}%</text>')
    step = max(1, n // 8)
    for i in range(0, n, step):
        parts.append(f'<text x="{xs[i]:.1f}" y="{h - 8}" text-anchor="middle" font-size="11" style="fill:var(--text-muted)">{i + 1}</text>')
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    if n > 1:
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    for x, y in zip(xs, ys):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{BLUE}" style="stroke:var(--surface)" stroke-width="2"/>')
    return (f'<div class="cg-card"><svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Running accuracy chart" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="Inter,Segoe UI,Arial,sans-serif">{"".join(parts)}</svg></div>')


def hero_carousel(n_rules, n_symptoms, systems):
    """4-slide hero: brand slide + details. Pure CSS (radio inputs); autoplays until a dot / arrow is used.
    systems = [(name, icon_name, rule_count)]"""
    steps = [("list-checks", "Report symptoms", "Answer a guided interview or tick a searchable checklist."),
             ("cpu", "Rules are scored", "Every weighted rule is evaluated by forward chaining."),
             ("list-filter", "Faults are ranked", "See probable faults with severity and a confidence score."),
             ("shield-check", "Act safely", "Get the repair action and clear driving advice.")]
    feats = [("circle-help", "Why-not answers", "Ask why a fault was rejected and see the missing symptoms."),
             ("list-filter", "Severity-first questions", "Dangerous faults are checked first, with an early alert."),
             ("split", "Multi-fault detection", "Finds independent faults hidden in the same report."),
             ("target", "Self-measured accuracy", "Rate each diagnosis and watch the accuracy tracker.")]

    def arrows(k):
        prev_id, next_id = (k - 2) % 4 + 1, k % 4 + 1
        return (f'<label class="cg-arrow l" for="cgs{prev_id}" aria-label="Previous slide">{icon("chevron-left", 20)}</label>'
                f'<label class="cg-arrow r" for="cgs{next_id}" aria-label="Next slide">{icon("chevron-right", 20)}</label>')

    s1 = (f'<div class="cg-slide s1" style="--n:1"><div class="cg-s1">'
          f'<div class="cg-eyebrow-w">{icon("shield-check", 15)} Automotive diagnostic expert system</div>'
          f'<div class="cg-wordmark"><div class="cg-wordmark-mark">{icon("gauge", 34, 1.8)}</div>'
          f'<div class="cg-wordmark-text"><span class="car">Car</span><span class="guru">Guru</span></div></div>'
          f'<div class="cg-s1-tag">Describe the symptoms. CarGuru reasons like a workshop expert and tells you what is wrong, '
          f'how serious it is and what to do next.</div>'
          f'<div class="cg-s1-stats"><span><b>{n_rules}</b>expert rules</span><span><b>{n_symptoms}</b>symptoms</span>'
          f'<span><b>{len(systems)}</b>vehicle systems</span></div>'
          f'<div class="cg-s1-art">{icon("car", 230, 1.2)}</div></div>{arrows(1)}</div>')
    cards = "".join(f'<div class="cg-s-card cg-s-step"><span class="num">{i}</span><div class="cg-s-ico">{icon(ic, 19)}</div>'
                    f'<div><b>{t}</b><span>{d}</span></div></div>' for i, (ic, t, d) in enumerate(steps, 1))
    s2 = (f'<div class="cg-slide s2" style="--n:2"><div class="cg-eyebrow-w">{icon("cpu", 15)} How it works</div>'
          f'<div class="cg-s-title">From symptoms to a verified diagnosis</div><div class="cg-s-grid">{cards}</div>{arrows(2)}</div>')
    chips_ = "".join(
        f'<div class="cg-s-card"><div class="cg-s-ico">{icon(ic, 19)}</div><div><b>{name}'
        f'{"<i class=new>NEW</i>" if name.startswith("Hybrid") else ""}</b><span>{cnt} expert rules</span></div></div>'
        for name, ic, cnt in systems)
    s3 = (f'<div class="cg-slide s3" style="--n:3"><div class="cg-eyebrow-w">{icon("layers", 15)} Coverage</div>'
          f'<div class="cg-s-title">{len(systems)} vehicle systems, from everyday faults to hybrid and electric drivetrains</div>'
          f'<div class="cg-s-grid" style="grid-template-columns:repeat(auto-fit,minmax(250px,1fr))">{chips_}</div>{arrows(3)}</div>')
    fcards = "".join(f'<div class="cg-s-card"><div class="cg-s-ico">{icon(ic, 19)}</div><div><b>{t}</b><span>{d}</span></div></div>'
                     for ic, t, d in feats)
    s4 = (f'<div class="cg-slide s4" style="--n:4"><div class="cg-eyebrow-w">{icon("lightbulb", 15)} Built to explain itself</div>'
          f'<div class="cg-s-title">Transparent reasoning you can check</div><div class="cg-s-grid">{fcards}</div>{arrows(4)}</div>')
    radios = "".join(f'<input type="radio" name="cgsl" id="cgs{k}">' for k in range(1, 5))
    dots = "".join(f'<label class="d{k}" for="cgs{k}" style="--n:{k}" aria-label="Go to slide {k}"></label>' for k in range(1, 5))
    return (f'<div class="cg-carousel">{radios}<div class="cg-slides">{s1}{s2}{s3}{s4}</div>'
            f'<div class="cg-dots">{dots}</div></div>')


def brand():
    return html(f"""
    <div class="cg-brand">
      <div class="cg-brand-logo">{icon("car", 24, 2)}</div>
      <div><div class="cg-brand-name">CarGuru</div>
      <div class="cg-brand-sub">Diagnostic Expert System</div></div>
    </div>""")


# ------------------------------------------------------------------ global CSS
_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.stApp {font-family:'Inter','Segoe UI',system-ui,-apple-system,Roboto,sans-serif; background:var(--bg); color:var(--text);}
[data-testid="stAppViewContainer"] {background:var(--bg);}
header[data-testid="stHeader"] {background:transparent; pointer-events:none;}
header[data-testid="stHeader"] button, [data-testid="stExpandSidebarButton"], [data-testid="stExpandSidebarButton"] * {pointer-events:auto;}
/* keep the sidebar reopen button, hide Streamlit's own menu/deploy actions (CarGuru has its own controls) */
[data-testid="stToolbarActions"], [data-testid="stMainMenu"], [data-testid="stAppDeployButton"], .stAppDeployButton,
[data-testid="stDecoration"], #MainMenu, footer {display:none !important;}
[data-testid="stExpandSidebarButton"] {background:var(--primary); color:#fff; border-radius:10px; padding:.25rem .45rem;
    box-shadow:0 2px 8px rgba(37,99,235,.35);}
[data-testid="stExpandSidebarButton"] * {color:#fff !important;}
[data-testid="stHeaderActionElements"] {display:none !important;}
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style) {display:none;}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] p {opacity:1 !important; color:var(--text-muted) !important;}
.block-container {padding:3.6rem 2.4rem 4rem; max-width:1240px;}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {color:var(--text); letter-spacing:-.01em; font-weight:700;}
.stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stMarkdownContainer"] p, .stApp li {color:var(--text);}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {color:var(--text-muted) !important;}
.stApp [data-testid="stWidgetLabel"] p {font-weight:600; font-size:.88rem; color:var(--text-2);}
hr {border-color:var(--border);}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {background:var(--sidebar-bg) !important; border-right:1px solid rgba(255,255,255,.06);}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {padding-top:.5rem;}
.cg-brand {display:flex; align-items:center; gap:.75rem; padding:.9rem .4rem 1.1rem;}
.cg-brand-logo {width:42px; height:42px; border-radius:12px; background:#2563EB; color:#fff; display:flex;
                align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(37,99,235,.35);}
.cg-brand-name {color:#fff; font-size:1.25rem; font-weight:700; letter-spacing:-.01em; line-height:1.1;}
.cg-brand-sub {color:#8FA3BF; font-size:.76rem; margin-top:2px;}
.cg-navlabel {color:#6F86A6; font-size:.7rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase;
              padding:.4rem .9rem .5rem;}
.cg-sidestat {margin:1.2rem .2rem 0; padding:.9rem 1rem; border-radius:12px; background:rgba(255,255,255,.05);
              border:1px solid rgba(255,255,255,.08); color:#C7D2E3; font-size:.82rem; line-height:1.7;}
.cg-sidestat b {color:#fff; font-weight:600;}
.cg-sidestat .row {display:flex; justify-content:space-between;}
.cg-sidestat .ttl {display:flex; align-items:center; gap:.45rem; color:#fff; font-weight:600; margin-bottom:.3rem;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] {margin-bottom:-.35rem;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
    background:transparent; border:none; box-shadow:none; color:#C7D2E3; justify-content:flex-start;
    width:100%; min-height:2.7rem; border-radius:10px; padding:.55rem .9rem; font-weight:500;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {background:rgba(255,255,255,.07); color:#fff;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div, section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div > span {width:100%; display:flex; justify-content:flex-start;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button [data-testid="stMarkdownContainer"] {width:100%; text-align:left;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button p {color:#C7D2E3 !important; text-align:left; font-size:.95rem; justify-content:flex-start;}
section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover p {color:#FFFFFF !important;}

/* ---------- buttons ---------- */
.stApp button[data-testid^="stBaseButton"] {
    border-radius:10px; font-weight:600; min-height:2.6rem; padding:.45rem 1.1rem;
    transition:background .15s, border-color .15s, box-shadow .15s, transform .05s;}
.stApp button[data-testid="stBaseButton-primary"] {background:#2563EB; border:1px solid #2563EB; color:#fff;
    box-shadow:0 1px 2px rgba(37,99,235,.25);}
.stApp button[data-testid="stBaseButton-primary"] p {color:#fff;}
.stApp button[data-testid="stBaseButton-primary"]:hover {background:#1D4ED8; border-color:#1D4ED8;
    box-shadow:0 4px 10px rgba(37,99,235,.28);}
.stApp button[data-testid="stBaseButton-primary"]:active {background:#1E40AF; transform:translateY(1px);}
.stApp button[data-testid="stBaseButton-secondary"] {background:var(--surface); border:1px solid var(--border-strong); color:var(--text);}
.stApp button[data-testid="stBaseButton-secondary"] p {color:var(--text);}
.stApp button[data-testid="stBaseButton-secondary"]:hover {background:var(--surface-2); border-color:var(--text-muted);}
.stApp button[data-testid="stBaseButton-secondary"]:active {transform:translateY(1px);}
.stApp [class*="__succ"] button {background:#0D9488 !important; border:1px solid #0D9488 !important;}
.stApp [class*="__succ"] button p {color:#fff !important;}
.stApp [class*="__succ"] button:hover {background:#0F766E !important; border-color:#0F766E !important;}
.stApp [class*="__dang"] button {background:#DC2626 !important; border:1px solid #DC2626 !important;}
.stApp [class*="__dang"] button p {color:#fff !important;}
.stApp [class*="__dang"] button:hover {background:#B91C1C !important; border-color:#B91C1C !important;}
.stApp button:disabled {opacity:.45;}
.stApp button:focus-visible {outline:2px solid #93C5FD; outline-offset:2px;}
[class*="st-key-btn_"] button p, [class*="st-key-nav_"] button p, [class*="st-key-demo_"] button p,
[class*="st-key-area_"] label [data-testid="stMarkdownContainer"] p {
    display:inline-flex; align-items:center; gap:.55rem; margin:0;}
[class*="st-key-btn_"] button p::before, [class*="st-key-nav_"] button p::before,
[class*="st-key-demo_"] button p::before, [class*="st-key-area_"] label [data-testid="stMarkdownContainer"] p::before {
    content:""; width:1.1rem; height:1.1rem; flex:0 0 1.1rem; background-color:currentColor;
    -webkit-mask:var(--ico) center/contain no-repeat; mask:var(--ico) center/contain no-repeat;}
/* segmented control (diagnosis method) */
.stApp [data-testid="stButtonGroup"] button {background:var(--surface); border:1px solid var(--border-strong); color:var(--text);}
.stApp [data-testid="stButtonGroup"] button p {color:inherit;}
.stApp [data-testid="stButtonGroup"] button[data-testid*="Active"], .stApp [data-testid="stButtonGroup"] button[aria-checked="true"] {
    background:var(--primary-soft); border-color:var(--primary); color:var(--primary);}
/* top bar */
.st-key-topbar {margin:-.4rem 0 1.1rem;}
.st-key-topbar button[data-testid^="stBaseButton"] {min-height:2.3rem; padding:.3rem .85rem; font-size:.88rem;}
.stApp .st-key-btn_theme_active_marker {display:none;}

/* ---------- inputs ---------- */
.stApp div[data-baseweb="input"], .stApp div[data-baseweb="base-input"] {border-radius:10px; background:var(--surface) !important;}
.stApp div[data-baseweb="input"] {border:1px solid var(--border-strong);}
.stApp div[data-baseweb="input"]:focus-within {border-color:#2563EB; box-shadow:0 0 0 3px rgba(37,99,235,.18);}
.stApp input, .stApp textarea {color:var(--text) !important; -webkit-text-fill-color:var(--text) !important; background:transparent !important;}
.stApp input::placeholder {color:var(--text-muted) !important; -webkit-text-fill-color:var(--text-muted) !important; opacity:1;}
.stApp div[data-baseweb="select"] > div {background:var(--surface); border:1px solid var(--border-strong); border-radius:10px; color:var(--text);}
.stApp div[data-baseweb="select"] > div:hover {border-color:var(--text-muted);}
.stApp div[data-baseweb="select"] div, .stApp div[data-baseweb="select"] span, .stApp div[data-baseweb="select"] svg {color:var(--text); fill:var(--text);}
[data-baseweb="popover"] > div, [data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul {background:var(--surface) !important; color:var(--text);}
[data-baseweb="popover"] > div {border:1px solid var(--border); border-radius:10px;}
[data-baseweb="popover"] li, [data-baseweb="popover"] li * {color:var(--text) !important; background:transparent;}
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] {background:var(--surface-2) !important;}
[data-testid="stCheckbox"] label p {font-weight:500; color:var(--text);}
[data-testid="stCheckbox"] label > span:first-child {border-color:var(--border-strong);}
[data-testid="stProgressBarTrack"] {background:var(--track) !important;}
button[data-baseweb="tab"] {font-weight:600; color:var(--text-muted);}
button[data-baseweb="tab"] p {color:inherit;}
button[data-baseweb="tab"][aria-selected="true"] {color:#2563EB;}
div[data-baseweb="tab-highlight"] {background:#2563EB;}
div[data-baseweb="tab-border"] {background:var(--border);}
[data-testid="stExpander"] details {background:var(--surface); border:1px solid var(--border); border-radius:12px;}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {font-weight:600; color:var(--text);}
[data-testid="stExpander"] summary:hover {background:var(--surface-2); border-radius:12px;}

/* native widget surfaces (text input, select, expander, checkbox) */
.stApp [data-testid="stTextInputRootElement"], .stApp [data-testid="stSelectbox"] div[role="group"], .stApp [data-testid="stNumberInputContainer"] {
    background:var(--surface) !important; border:1px solid var(--border-strong) !important; border-radius:10px !important;}
.stApp [data-testid="stTextInputRootElement"]:focus-within, .stApp [data-testid="stSelectbox"] div[role="group"]:focus-within {
    border-color:#2563EB !important; box-shadow:0 0 0 3px rgba(37,99,235,.18);}
.stApp [data-testid="stSelectbox"] svg, .stApp [data-testid="stSelectbox"] button {color:var(--text-muted) !important; fill:var(--text-muted) !important;}
[data-testid="stExpander"] summary {background:var(--surface) !important; border-radius:12px;}
[data-testid="stExpander"] details[open] summary {border-bottom-left-radius:0; border-bottom-right-radius:0;}
[data-testid="stCheckbox"] label:not(:has(input:checked)) > div:not([data-testid="stWidgetLabel"]) {
    background:var(--surface-2) !important; border:1px solid var(--border-strong) !important;}
.st-key-topbar {justify-content:space-between !important;}
.st-key-topbar > [data-testid="stLayoutWrapper"] {margin-left:auto; width:auto !important; flex:0 0 auto !important;}
[data-testid="stSelectboxVirtualDropdown"], ul[role="listbox"] {background:var(--surface) !important; border:1px solid var(--border); border-radius:10px;}
[data-testid="stSelectboxVirtualDropdown"] [role="option"], [data-testid="stSelectboxVirtualDropdown"] [role="option"] * {color:var(--text) !important;}
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover, [data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"] {background:var(--surface-2) !important;}

/* ---------- cards ---------- */
.cg-card, [class*="st-key-card_"] {background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:1.15rem 1.3rem;
    box-shadow:var(--shadow); color:var(--text);}
[class*="st-key-area_"], [class*="st-key-area_"] [data-testid="stCheckbox"] {width:100%;}
[class*="st-key-area_"] label {display:flex; box-sizing:border-box; border:1px solid var(--border-strong); background:var(--surface);
    border-radius:12px; padding:.8rem .9rem; width:100%; cursor:pointer; transition:border-color .15s, background .15s;}
[class*="st-key-area_"] label:hover {border-color:#60A5FA; background:var(--surface-2);}
[class*="st-key-area_"] label:has(input:checked) {border-color:#2563EB; background:var(--primary-soft); box-shadow:0 0 0 1px #2563EB inset;}
[class*="st-key-area_"] label p {font-weight:600; font-size:.92rem;}

/* ---------- hero / headers ---------- */
.cg-hero {display:flex; align-items:center; justify-content:space-between; gap:1.5rem; flex-wrap:wrap;
    background:#14243A; border:1px solid var(--border); border-radius:18px; padding:1.8rem 2.1rem; color:#fff; margin-bottom:1.2rem;}
.stApp .cg-hero h1 {color:#fff; margin:0 0 .4rem; font-size:1.85rem; padding:0;}
.stApp .cg-hero p {color:#B6C4D8; margin:0; max-width:620px; line-height:1.6; font-size:1rem;}
.cg-hero-art {width:104px; height:104px; border-radius:26px; background:rgba(13,148,136,.18);
    border:1px solid rgba(94,234,212,.3); display:flex; align-items:center; justify-content:center; color:#5EEAD4;}
.cg-hero-tags {margin-top:1rem; display:flex; gap:.5rem; flex-wrap:wrap;}
.cg-hero-tags span {display:inline-flex; align-items:center; gap:.4rem; background:rgba(255,255,255,.08);
    border:1px solid rgba(255,255,255,.12); color:#DCE5F2; padding:.3rem .8rem; border-radius:999px; font-size:.8rem;}
.cg-pagehead {display:flex; align-items:center; gap:1rem; margin:0 0 1.2rem;}
.cg-pagehead-ico {width:48px; height:48px; border-radius:13px; background:var(--pagehead-bg); color:#fff;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;}
.stApp .cg-pagehead h1 {margin:0; padding:0; font-size:1.55rem; line-height:1.2; color:var(--text);}
.stApp .cg-pagehead p {margin:.15rem 0 0; color:var(--text-muted); font-size:.95rem;}
.cg-section {display:flex; align-items:center; gap:.6rem; margin:1.6rem 0 .8rem;}
.cg-section-ico {width:30px; height:30px; border-radius:9px; background:var(--icon-bg); color:var(--text);
    display:flex; align-items:center; justify-content:center;}
.cg-section-title {font-size:1.1rem; font-weight:700; color:var(--text);}
.cg-section-sub {color:var(--text-muted); font-size:.88rem; margin-left:.3rem;}

/* ---------- kpi / grid ---------- */
.cg-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(var(--min,210px),1fr)); gap:.9rem; margin-bottom:.4rem;}
.cg-kpi {display:flex; align-items:center; gap:.9rem; background:var(--surface); border:1px solid var(--border); border-radius:14px;
    padding:.95rem 1rem; box-shadow:var(--shadow);}
.cg-kpi-ico {width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0;}
.cg-kpi-label {font-size:.74rem; text-transform:uppercase; letter-spacing:.07em; color:var(--text-muted); font-weight:600;}
.cg-kpi-value {font-size:1.7rem; font-weight:700; color:var(--text); line-height:1.15;}
.cg-kpi-note {font-size:.78rem; color:var(--text-muted); margin-top:1px;}
.cg-sys {display:flex; align-items:center; gap:.8rem; background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:.75rem .95rem;}
.cg-sys-ico {width:38px; height:38px; border-radius:10px; background:var(--primary-soft); color:var(--primary);
    display:flex; align-items:center; justify-content:center; flex-shrink:0;}
.cg-sys b {display:block; font-size:.9rem; color:var(--text);}
.cg-sys span {font-size:.78rem; color:var(--text-muted);}
.tone-blue {background:var(--tone-blue-bg); color:var(--tone-blue-fg);} .tone-teal {background:var(--tone-teal-bg); color:var(--tone-teal-fg);}
.tone-amber {background:var(--tone-amber-bg); color:var(--tone-amber-fg);} .tone-red {background:var(--tone-red-bg); color:var(--tone-red-fg);}
.tone-slate {background:var(--tone-slate-bg); color:var(--tone-slate-fg);} .tone-navy {background:var(--tone-navy-bg); color:var(--tone-navy-fg);}

/* ---------- small parts ---------- */
.cg-badge {display:inline-flex; align-items:center; gap:.3rem; padding:3px 11px 3px 8px; border-radius:999px;
    font-size:.76rem; font-weight:700; letter-spacing:.02em;}
.sev-low {background:var(--sev-low-bg); color:var(--sev-low-fg);} .sev-medium {background:var(--sev-medium-bg); color:var(--sev-medium-fg);}
.sev-high {background:var(--sev-high-bg); color:var(--sev-high-fg);} .sev-critical {background:var(--sev-critical-bg); color:var(--sev-critical-fg);}
.cg-chip {display:inline-block; padding:3px 11px; margin:2px 4px 2px 0; border-radius:999px; font-size:.82rem;
    background:var(--chip-bg); color:var(--chip-fg);}
.cg-chip.ok {background:var(--chip-ok-bg); color:var(--chip-ok-fg);}
.cg-chip.miss {background:transparent; color:var(--text-muted); border:1px dashed var(--border-strong);}
.cg-bar {width:100%; background:var(--track); border-radius:999px; overflow:hidden;}
.cg-bar > div {height:100%; border-radius:999px;}
.cg-progress {margin:.2rem 0 1rem;}
.cg-progress-top {display:flex; justify-content:space-between; font-size:.86rem; color:var(--text-2); margin-bottom:.35rem;}
.cg-callout {display:flex; gap:.8rem; align-items:flex-start; border:1px solid; border-radius:12px;
    padding:.85rem 1.05rem; margin:.5rem 0; line-height:1.5;}
.cg-callout svg {margin-top:2px;}
.cg-callout-title {font-weight:700;}
.cg-callout-body {font-size:.92rem; margin-top:2px;}
.co-info {background:var(--co-info-bg); border-color:var(--co-info-bd); color:var(--co-info-fg);}
.co-success {background:var(--co-success-bg); border-color:var(--co-success-bd); color:var(--co-success-fg);}
.co-warning {background:var(--co-warning-bg); border-color:var(--co-warning-bd); color:var(--co-warning-fg);}
.co-critical {background:var(--co-critical-bg); border-color:var(--co-critical-bd); color:var(--co-critical-fg);}
.cg-empty {text-align:center; color:var(--text-muted); padding:2.2rem 1rem;}
.cg-empty-ico {width:60px; height:60px; border-radius:16px; background:var(--primary-soft); color:var(--primary); margin:0 auto .8rem;
    display:flex; align-items:center; justify-content:center;}
.cg-empty-title {font-size:1.05rem; font-weight:700; color:var(--text); margin-bottom:.2rem;}
.cg-list {list-style:none; padding:0; margin:.2rem 0;}
.stApp .cg-list li {display:flex; align-items:center; gap:.6rem; padding:.45rem 0; border-bottom:1px solid var(--border); font-size:.93rem; color:var(--text);}
.cg-list li:last-child {border-bottom:none;}
.cg-list li.match .cg-li-ico {color:#16A34A;}
.stApp .cg-list li.missing {color:var(--text-muted);}
.cg-list li.missing .cg-li-ico {color:var(--text-muted);}
.cg-li-ico {display:flex;}
.cg-li-w {margin-left:auto; font-size:.8rem; color:var(--text-muted); font-variant-numeric:tabular-nums;}
.cg-eyebrow {font-size:.74rem; text-transform:uppercase; letter-spacing:.09em; color:var(--text-muted); font-weight:600;}
.cg-fault-name {font-size:1.75rem; font-weight:700; color:var(--text); line-height:1.2; margin:.15rem 0 .5rem;}
.cg-meta {display:flex; align-items:center; gap:.9rem; flex-wrap:wrap; color:var(--text-2); font-size:.9rem;}
.cg-meta .sys {display:inline-flex; align-items:center; gap:.4rem;}
.cg-diag {display:flex; align-items:center; gap:1.6rem; flex-wrap:wrap;}
.cg-note {font-size:.8rem; color:var(--text-muted); margin-top:.5rem; line-height:1.45;}
.cg-reporthead {display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;
    background:#14243A; border:1px solid var(--border); color:#fff; border-radius:14px; padding:1rem 1.3rem; margin-bottom:.9rem;}
.cg-reporthead .t {display:flex; align-items:center; gap:.7rem; font-weight:700; font-size:1.1rem; color:#fff;}
.cg-reporthead .m {color:#B6C4D8; font-size:.84rem; text-align:right; line-height:1.5;}
.cg-qhead {display:flex; align-items:center; gap:.65rem; flex-wrap:wrap; margin-bottom:.4rem; color:var(--text-2); font-size:.88rem;}
.cg-qico {width:38px; height:38px; border-radius:10px; background:var(--primary-soft); color:var(--primary); display:flex; align-items:center; justify-content:center;}
.cg-bigq {font-size:1.45rem; font-weight:600; line-height:1.35; color:var(--text); margin:.5rem 0 .35rem;}
.cg-hyp {margin-bottom:.8rem;}
.cg-hyp .top {display:flex; justify-content:space-between; gap:.6rem; font-size:.88rem; margin-bottom:.3rem; color:var(--text); font-weight:500;}
.cg-hyp .top b {font-variant-numeric:tabular-nums;}
.cg-formula {font-family:ui-monospace,Consolas,monospace; background:var(--formula-bg); color:var(--text); padding:.65rem .9rem;
    border-radius:10px; font-size:.98rem; margin:.5rem 0;}
.cg-cond {display:flex; flex-wrap:wrap; align-items:center; gap:.4rem; line-height:2;}
.cg-cond .kw {font-weight:700; color:var(--primary); font-size:.8rem; letter-spacing:.06em;}
.cg-tablewrap {background:var(--surface); border:1px solid var(--border); border-radius:12px; overflow:auto; box-shadow:var(--shadow);}
.cg-table {width:100%; border-collapse:collapse; font-size:.9rem;}
.cg-table th {text-align:left; color:var(--text-muted); font-size:.72rem; text-transform:uppercase; letter-spacing:.07em;
    padding:.6rem .8rem; border-bottom:1px solid var(--border); background:var(--surface); position:sticky; top:0; z-index:1; white-space:nowrap;}
.cg-table td {padding:.62rem .8rem; border-bottom:1px solid var(--border); color:var(--text); vertical-align:middle;}
.cg-table tr:last-child td {border-bottom:none;}
.cg-table tbody tr:hover td {background:var(--surface-2);}
.cg-ol {padding-left:1.25rem; margin:.2rem 0;}
.stApp .cg-ol li {padding:.35rem 0; color:var(--text); line-height:1.55;}

/* ---------- stepper ---------- */
.cg-stepper {display:flex; align-items:center; margin:0 0 1.4rem; background:var(--surface); border:1px solid var(--border);
    border-radius:14px; padding:.9rem 1.2rem; box-shadow:var(--shadow);}
.cg-step {display:flex; align-items:center; gap:.6rem; color:var(--text-muted); font-weight:600; font-size:.9rem;}
.cg-step-dot {width:34px; height:34px; border-radius:50%; background:var(--surface-2); color:var(--text-muted); display:flex;
    align-items:center; justify-content:center; flex-shrink:0; border:1px solid var(--border);}
.cg-step.active {color:var(--text);}
.cg-step.active .cg-step-dot {background:#2563EB; color:#fff; border-color:#2563EB; box-shadow:0 0 0 4px rgba(37,99,235,.2);}
.cg-step.done {color:#0D9488;}
.cg-step.done .cg-step-dot {background:#0D9488; color:#fff; border-color:#0D9488;}
.cg-step-line {flex:1; height:2px; background:var(--border); margin:0 .9rem; min-width:20px;}
.cg-step-line.done {background:#0D9488;}


/* -- three-dot menu (popover) --*/
.st-key-menu_pop button[data-testid="stPopoverButton"] {width:2.35rem; min-width:2.35rem; padding:0 !important; justify-content:center;
    background:var(--surface); border:1px solid var(--border-strong); border-radius:9px; color:var(--text);}
.st-key-menu_pop button[data-testid="stPopoverButton"] > div {display:none;}
.st-key-menu_pop button[data-testid="stPopoverButton"]::before {content:""; display:block; width:1.2rem; height:1.2rem;
    background-color:currentColor; -webkit-mask:var(--ico) center/contain no-repeat; mask:var(--ico) center/contain no-repeat;}
.st-key-menu_pop button[data-testid="stPopoverButton"]:hover {background:var(--surface-2); border-color:var(--text-muted);}
[data-testid="stPopoverBody"] {background:var(--surface) !important; border:1px solid var(--border) !important; border-radius:14px !important;
    box-shadow:0 14px 34px rgba(8,15,30,.28) !important; min-width:210px;}
.cg-menuhead {font-size:.7rem; text-transform:uppercase; letter-spacing:.12em; color:var(--text-muted); font-weight:700; margin:.1rem 0 .5rem;}
[data-testid="stPopoverBody"] button[data-testid^="stBaseButton"] {width:100%; justify-content:flex-start; min-height:2.4rem; padding:.4rem .9rem;
    background:var(--surface); border:1px solid var(--border-strong); color:var(--text); border-radius:10px; font-weight:600;}
[data-testid="stPopoverBody"] button p {color:var(--text); text-align:left; margin:0;}
[data-testid="stPopoverBody"] button:hover {background:var(--surface-2); border-color:var(--text-muted);}
[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] p {color:var(--text);}
[data-testid="stPopoverBody"] [data-testid="stButton"] button > div, [data-testid="stPopoverBody"] [data-testid="stButton"] button > div > span {width:100%; display:flex; justify-content:flex-start;}

/* - hero slider (pure CSS, no JavaScript) -- */
.cg-carousel {position:relative; background:#14243A; border:1px solid rgba(255,255,255,.08); border-radius:20px; color:#fff;
    overflow:hidden; margin-bottom:1.2rem; box-shadow:var(--shadow);}
.cg-carousel input[type=radio] {display:none;}
.cg-slides {display:grid;}
.cg-slide {grid-area:1/1; display:flex; flex-direction:column; justify-content:center; opacity:0; visibility:hidden; padding:2.1rem 4.2rem 3.4rem; position:static;
    animation:cgfade 32s infinite; animation-delay:calc((var(--n) - 1) * 8s);}
.cg-slide .cg-arrow {position:absolute; top:50%; margin-top:-20px; width:40px; height:40px; border-radius:50%; cursor:pointer;
    background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.16); color:#DCE5F2; display:flex; align-items:center;
    justify-content:center; transition:background .15s;}
.cg-slide .cg-arrow:hover {background:rgba(255,255,255,.18);}
.cg-slide .cg-arrow.l {left:.9rem;}
.cg-slide .cg-arrow.r {right:.9rem;}
.cg-dots {position:absolute; left:0; right:0; bottom:1.05rem; display:flex; justify-content:center; gap:.5rem; z-index:2;}
.cg-dots label {display:block; width:9px; height:9px; border-radius:999px; background:rgba(255,255,255,.3); cursor:pointer;
    transition:width .25s, background .25s; animation:cgdot 32s infinite; animation-delay:calc((var(--n) - 1) * 8s);}
.cg-carousel:hover .cg-slide, .cg-carousel:hover .cg-dots label {animation-play-state:paused;}
@keyframes cgfade {0%{opacity:0; visibility:hidden;} 1.6%{opacity:1; visibility:visible;} 23.4%{opacity:1; visibility:visible;}
                   25%{opacity:0; visibility:hidden;} 100%{opacity:0; visibility:hidden;}}
@keyframes cgdot {0%{background:rgba(255,255,255,.3); width:9px;} 1.6%{background:#5EEAD4; width:24px;} 23.4%{background:#5EEAD4; width:24px;}
                  25%{background:rgba(255,255,255,.3); width:9px;} 100%{background:rgba(255,255,255,.3); width:9px;}}
.cg-carousel input:checked ~ .cg-slides .cg-slide, .cg-carousel input:checked ~ .cg-dots label {animation:none !important;}
.cg-carousel input:checked ~ .cg-slides .cg-slide {opacity:0; visibility:hidden;}
#cgs1:checked ~ .cg-slides .s1, #cgs2:checked ~ .cg-slides .s2, #cgs3:checked ~ .cg-slides .s3, #cgs4:checked ~ .cg-slides .s4 {opacity:1; visibility:visible;}
#cgs1:checked ~ .cg-dots .d1, #cgs2:checked ~ .cg-dots .d2, #cgs3:checked ~ .cg-dots .d3, #cgs4:checked ~ .cg-dots .d4 {background:#5EEAD4; width:24px;}
@media (prefers-reduced-motion: reduce) {
  .cg-slide, .cg-dots label {animation:none;}
  .cg-slide.s1 {opacity:1; visibility:visible;}
  .cg-dots .d1 {background:#5EEAD4; width:24px;}
}
.cg-eyebrow-w {display:inline-flex; align-items:center; gap:.5rem; font-size:.74rem; text-transform:uppercase; letter-spacing:.14em; color:#5EEAD4; font-weight:600;}
.cg-s1 {position:relative; min-height:250px; display:flex; flex-direction:column; justify-content:center;}
.cg-wordmark {display:flex; align-items:center; gap:1rem; margin:.7rem 0 .5rem;}
.cg-wordmark-mark {width:64px; height:64px; border-radius:18px; background:rgba(13,148,136,.22); border:1px solid rgba(94,234,212,.4);
    color:#5EEAD4; display:flex; align-items:center; justify-content:center; flex-shrink:0;}
.cg-wordmark-text {font-size:4rem; line-height:1; letter-spacing:-.03em; color:#fff;}
.cg-wordmark-text .car {font-weight:300;}
.cg-wordmark-text .guru {font-weight:800; color:#5EEAD4; position:relative; display:inline-block;}
.cg-wordmark-text .guru::after {content:""; position:absolute; left:2px; right:2px; bottom:-8px; height:4px; border-radius:4px; background:#0D9488;}
.cg-s1-tag {color:#B6C4D8; max-width:560px; line-height:1.6; margin:.9rem 0 1rem; font-size:1.02rem;}
.cg-s1-stats {display:flex; flex-wrap:wrap; gap:.55rem;}
.cg-s1-stats span {background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.12); color:#DCE5F2; padding:.35rem .9rem;
    border-radius:999px; font-size:.84rem;}
.cg-s1-stats b {color:#5EEAD4; font-size:1rem; margin-right:.25rem;}
.cg-s1-art {position:absolute; right:-10px; bottom:-30px; color:#fff; opacity:.06; pointer-events:none;}
.cg-s-title {font-size:1.5rem; font-weight:700; color:#fff; margin:.35rem 0 1.1rem; line-height:1.25;}
.cg-s-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:.8rem;}
.cg-s-card {display:flex; gap:.75rem; align-items:flex-start; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.1);
    border-radius:14px; padding:.85rem .95rem;}
.cg-s-ico {width:38px; height:38px; border-radius:10px; background:rgba(94,234,212,.12); color:#5EEAD4; display:flex;
    align-items:center; justify-content:center; flex-shrink:0;}
.cg-s-card b {display:block; font-size:.92rem; color:#fff; margin-bottom:2px;}
.cg-s-card span {display:block; font-size:.8rem; color:#B6C4D8; line-height:1.4;}
.cg-s-card .new {display:inline-block; background:#0D9488; color:#fff; font-size:.62rem; font-weight:700; letter-spacing:.08em;
    border-radius:999px; padding:1px 7px; margin-left:.4rem; vertical-align:middle; font-style:normal;}
.cg-s-step {position:relative;}
.cg-s-step .num {position:absolute; top:-9px; left:12px; background:#0D9488; color:#fff !important; font-size:.68rem; font-weight:700;
    padding:1px 8px; border-radius:999px;}

/* ---------- responsive ---------- */
.stApp button[data-testid^="stBaseButton"] p {white-space:normal; line-height:1.25; word-break:normal; overflow-wrap:normal;}
.st-key-mobilenav {display:none;}
@media (max-width: 1100px) {
  [data-testid="stHorizontalBlock"] {flex-wrap:wrap !important; row-gap:.8rem;}
  [data-testid="stColumn"] {flex:1 1 300px !important; min-width:min(100%, 300px) !important;}
}
@media (max-width: 900px) {
  .block-container {padding:3.6rem 1rem 4rem;}
  .cg-hero {padding:1.3rem;}
  .stApp .cg-hero h1 {font-size:1.45rem;}
  .cg-hero-art {display:none;}
  .cg-fault-name {font-size:1.4rem;}
}
@media (max-width: 768px) {
  .st-key-mobilenav {display:block; margin-bottom:.6rem;}
}
@media (max-width: 640px) {
  .cg-slide {padding:1.4rem 1.2rem 3.2rem;}
  .cg-slide .cg-arrow {display:none;}
  .cg-wordmark-text {font-size:2.7rem;}
  .cg-wordmark-mark {width:48px; height:48px;}
  .cg-s1 {min-height:0;}
  [data-testid="stColumn"] {flex:1 1 100% !important; min-width:100% !important;}
  .cg-step-label {display:none;}
  .cg-step.active .cg-step-label {display:inline;}
  .cg-diag {flex-direction:column; align-items:flex-start;}
  .cg-reporthead .m {text-align:left;}
  .cg-bigq {font-size:1.2rem;}
}
"""


def _vars(d):
    return "".join(f"--{k}:{v};" for k, v in d.items())


def global_css(active_page, theme="System"):
    """Theme variables + base stylesheet + Lucide icon rules for buttons + active nav / theme highlight."""
    if theme == "Dark":
        palette = f":root{{{_vars(DARK)}color-scheme:dark;}}"
    elif theme == "Light":
        palette = f":root{{{_vars(LIGHT)}color-scheme:light;}}"
    else:  # follow the system theme preference
        palette = (f":root{{{_vars(LIGHT)}color-scheme:light;}}"
                   f"@media (prefers-color-scheme: dark){{:root{{{_vars(DARK)}color-scheme:dark;}}}}")
    rules = [f".st-key-{key} {{--ico:{_mask_uri(name)};}}" for key, name in BUTTON_ICONS.items()]
    rules.append(f'[class*="st-key-demo_"] {{--ico:{_mask_uri("play")};}}')
    for i, cat in enumerate(CATEGORIES):
        rules.append(f".st-key-area_{i} {{--ico:{_mask_uri(CAT_ICON[cat])};}}")
    rules.append(
        f'section[data-testid="stSidebar"] .st-key-nav_{active_page} button {{'
        f'background:rgba(37,99,235,.32); color:#fff; box-shadow:inset 3px 0 0 #60A5FA;}}')
    rules.append(
        f'.st-key-btn_theme_{theme.lower()} button {{background:var(--primary-soft) !important; '
        f'border-color:#2563EB !important; color:#2563EB !important;}}'
        f'.st-key-btn_theme_{theme.lower()} button p {{color:#2563EB !important;}}')
    rules.append(f'.st-key-menu_pop {{--ico:{_mask_uri("ellipsis-vertical")};}}')
    rules.append(f'section[data-testid="stSidebar"] .st-key-nav_{active_page} button p {{color:#FFFFFF !important;}}')
    return f"<style>{palette}\n{_BASE_CSS}\n{chr(10).join(rules)}</style>"
