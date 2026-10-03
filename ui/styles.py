"""
Design tokens and global CSS for the dashboard.

Operate-mode product UI: one sans family, tight type scale, hairline
separators instead of nested cards, colour reserved for sentiment data
and state. Light and dark themes share the same tokens.
"""

FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Geist:wght@400;500;600&display=swap');"
)

CSS = FONT_IMPORT + """
:root {
  --font: 'Geist', ui-sans-serif, -apple-system, 'SF Pro Text', 'Segoe UI',
          system-ui, sans-serif;

  --bg: #F5F5F2;
  --surface: #FFFFFF;
  --ink: #121417;
  --ink-2: #4A5058;
  --ink-3: #656C75;
  --line: #E2E2DC;
  --line-soft: #ECECE7;

  --pos: #0B7A5E;  --pos-tint: #E1F2EC;
  --neg: #C23B22;  --neg-tint: #FBE8E3;
  --neu: #8A9099;  --neu-tint: #ECECE8;

  --radius: 10px;
  --shadow: 0 1px 2px rgba(18,20,23,.04), 0 8px 24px -12px rgba(18,20,23,.10);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0E0F11;
    --surface: #16181B;
    --ink: #F2F3F4;
    --ink-2: #B4BAC1;
    --ink-3: #8D949C;
    --line: #2A2D32;
    --line-soft: #1F2226;

    --pos: #3DD6A6;  --pos-tint: rgba(61,214,166,.14);
    --neg: #FF7A5F;  --neg-tint: rgba(255,122,95,.14);
    --neu: #7C838C;  --neu-tint: rgba(138,144,153,.16);
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 8px 24px -12px rgba(0,0,0,.6);
  }
}

/* ---------- Streamlit shell ---------- */
html, body, .stApp { background: var(--bg) !important; color: var(--ink); }
.stApp, .stApp *:not([data-testid="stIconMaterial"]) {
  font-family: var(--font) !important;
  font-feature-settings: 'tnum' 1, 'cv11' 1;
  -webkit-font-smoothing: antialiased;
}
[data-testid="stHeader"] { background: transparent !important; height: 0; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
footer, #MainMenu { display: none !important; }
.block-container {
  max-width: 1180px !important;
  padding: 2rem 2rem 5rem !important;
}
@media (max-width: 640px) {
  .block-container { padding: 1.25rem 1rem 4rem !important; }
}
::selection { background: var(--ink); color: var(--bg); }
* { caret-color: var(--ink); scrollbar-width: thin;
    scrollbar-color: var(--line) transparent; }
:focus-visible { outline: 2px solid var(--ink) !important; outline-offset: 2px; }

/* ---------- Native widgets ---------- */
.stApp label, .stApp [data-testid="stWidgetLabel"] p {
  font-size: 12.5px !important; font-weight: 500 !important;
  color: var(--ink-3) !important; letter-spacing: .01em;
}
.stApp [data-baseweb="input"], .stApp [data-baseweb="base-input"],
.stApp [data-testid="stDateInputField"] {
  background: var(--surface) !important;
  border-radius: 8px !important;
}
.stApp [data-baseweb="input"] { border: 1px solid var(--line) !important; }
.stApp input { font-size: 14px !important; }
.stApp button[kind="primary"], .stApp button[kind="secondary"] {
  border-radius: 999px; font-size: 14px; font-weight: 500;
  padding: .45rem 1.1rem; min-height: 0;
  transition: background .15s ease, border-color .15s ease, transform .15s ease;
}
.stApp button[kind="primary"] {
  background: var(--ink); color: var(--bg); border: 1px solid var(--ink);
}
.stApp button[kind="primary"] * { color: var(--bg) !important; }
.stApp button[kind="primary"]:hover { opacity: .88; }
.stApp button[kind="secondary"] {
  background: transparent; color: var(--ink); border: 1px solid var(--line);
}
.stApp button[kind="secondary"]:hover { border-color: var(--ink-3); }
.stApp button[kind="primary"]:active,
.stApp button[kind="secondary"]:active { transform: translateY(1px); }
.stApp button[kind="primary"]:disabled,
.stApp button[kind="secondary"]:disabled { opacity: .45; }
[data-testid="stExpander"] {
  border: 1px solid var(--line) !important; border-radius: var(--radius);
  background: transparent !important;
}
[data-testid="stExpander"] summary { font-size: 14px; font-weight: 500; }

/* ---------- Layout primitives ---------- */
.bh-header { display: flex; align-items: baseline; gap: 14px;
  flex-wrap: wrap; padding-bottom: 20px; }
.bh-brand { font-size: 22px; font-weight: 600; letter-spacing: -.02em; }
.bh-sub { font-size: 14px; color: var(--ink-3); }
.bh-meta { font-size: 13px; color: var(--ink-3); }

.bh-section { padding-top: 40px; }
.bh-section h2 { font-size: 18px; font-weight: 600; letter-spacing: -.015em;
  margin: 0 0 4px; color: var(--ink); }
.bh-section .bh-lede { font-size: 14px; color: var(--ink-2);
  margin: 0 0 18px; max-width: 68ch; line-height: 1.5; }

.bh-headline { font-size: clamp(24px, 3.2vw, 34px); line-height: 1.18;
  font-weight: 600; letter-spacing: -.025em; margin: 6px 0 22px;
  max-width: 30ch; text-wrap: balance; }
.bh-headline .muted { color: var(--ink-3); font-weight: 500; }

/* Stat strip: hairline-separated, no cards */
.bh-stats { display: grid; grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.bh-stat { padding: 16px 20px 16px 0; }
.bh-stat + .bh-stat { padding-left: 20px; border-left: 1px solid var(--line); }
.bh-stat dt { font-size: 13px; color: var(--ink-3); margin: 0 0 6px; }
.bh-stat dd { margin: 0; font-size: 30px; font-weight: 600;
  letter-spacing: -.03em; line-height: 1.05; }
.bh-stat dd small { font-size: 15px; font-weight: 500; color: var(--ink-3);
  letter-spacing: 0; margin-left: 2px; }
.bh-stat .foot { font-size: 12.5px; color: var(--ink-3); margin-top: 6px; }
.bh-stat .up { color: var(--pos); } .bh-stat .down { color: var(--neg); }
@media (max-width: 720px) {
  .bh-stats { grid-template-columns: 1fr 1fr; }
  .bh-stat:nth-child(3) { padding-left: 0; border-left: 0; }
  .bh-stat:nth-child(n+3) { border-top: 1px solid var(--line); }
}

/* Mix bar */
.bh-mix { display: flex; gap: 3px; height: 14px; margin: 22px 0 10px;
  border-radius: 4px; overflow: hidden; }
.bh-mix > i { display: block; min-width: 3px; }
.bh-legend { display: flex; flex-wrap: wrap; gap: 6px 22px;
  font-size: 13.5px; color: var(--ink-2); }
.bh-legend b { color: var(--ink); font-weight: 600; }
.dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%;
  margin-right: 7px; }
.c-pos { background: var(--pos); } .c-neg { background: var(--neg); }
.c-neu { background: var(--neu); }

/* ---------- Trend chart ---------- */
.bh-chart { position: relative; display: grid;
  grid-template-columns: 38px 1fr; column-gap: 8px; }
.bh-yaxis { position: relative; font-size: 11.5px; color: var(--ink-3);
  text-align: right; }
.bh-yaxis span { position: absolute; right: 0; transform: translateY(-50%); }
.bh-plot { position: relative; }
.bh-plot > div[role="img"] { display: block; width: 100%; }
.bh-bars { display: flex; align-items: flex-end; gap: 3px; height: 56px;
  margin-top: 14px; }
.bh-bars i { flex: 1; background: var(--neu-tint); border-radius: 2px 2px 0 0;
  min-height: 1px; transition: background .15s ease; }
.bh-hits { position: absolute; inset: 0; display: flex; }
.bh-hit { position: relative; flex: 1; outline-offset: -2px; }
.bh-hit::before { content: ''; position: absolute; top: 0; bottom: 0;
  left: 50%; width: 1px; background: var(--ink-3); opacity: 0;
  transition: opacity .12s ease; }
.bh-hit:hover::before, .bh-hit:focus::before { opacity: .5; }
.bh-hit .pt { position: absolute; width: 9px; height: 9px; border-radius: 50%;
  background: var(--ink); border: 2px solid var(--bg); left: 50%;
  transform: translate(-50%, -50%); opacity: 0;
  transition: opacity .12s ease; }
.bh-hit:hover .pt, .bh-hit:focus .pt { opacity: 1; }
.bh-hit .tip { position: absolute; top: -6px; left: 50%;
  transform: translate(-50%, -100%); z-index: 5; pointer-events: none;
  min-width: 168px; padding: 10px 12px; border-radius: 10px;
  background: var(--surface); color: var(--ink); border: 1px solid var(--line);
  box-shadow: var(--shadow); font-size: 12.5px; line-height: 1.5;
  opacity: 0; visibility: hidden; transition: opacity .12s ease; }
.bh-hit.edge-l .tip { left: 0; transform: translate(0, -100%); }
.bh-hit.edge-r .tip { left: auto; right: 0; transform: translate(0, -100%); }
.bh-hit:hover .tip, .bh-hit:focus .tip { opacity: 1; visibility: visible; }
.tip b { font-weight: 600; } .tip .row { display: flex;
  justify-content: space-between; gap: 18px; color: var(--ink-2); }
.tip .row span:last-child { color: var(--ink); font-weight: 500; }
.bh-xaxis { grid-column: 2; display: flex; justify-content: space-between;
  font-size: 11.5px; color: var(--ink-3); margin-top: 8px; }
.bh-xaxis span { white-space: nowrap; }
.bh-key { display: flex; gap: 18px; flex-wrap: wrap; font-size: 12.5px;
  color: var(--ink-3); margin-top: 14px; }
.bh-key .sw { display: inline-block; width: 18px; height: 0; margin-right: 8px;
  vertical-align: middle; border-top: 2px solid var(--ink); }
.bh-key .sw.dash { border-top: 1.5px dotted var(--ink-3); }
.bh-key .sw.bar { height: 8px; border: 0; background: var(--neu-tint);
  border-radius: 2px; }

/* ---------- Rating cross-check + terms ---------- */
.bh-two { display: grid; grid-template-columns: 1fr 1fr; gap: 56px; }
@media (max-width: 860px) { .bh-two { grid-template-columns: 1fr; gap: 8px; } }
.bh-rate { display: grid; grid-template-columns: 54px 1fr 56px;
  align-items: center; gap: 12px; padding: 7px 0; font-size: 13.5px; }
.bh-rate .lbl { color: var(--ink-2); }
.bh-rate .n { color: var(--ink-3); text-align: right; font-size: 12.5px; }
.bh-bar { display: flex; height: 12px; gap: 2px; border-radius: 3px;
  overflow: hidden; background: var(--line-soft); }
.bh-bar i { display: block; }
.bh-note { margin-top: 14px; padding: 12px 14px; border-radius: var(--radius);
  background: var(--neu-tint); color: var(--ink-2); font-size: 13.5px;
  line-height: 1.5; }
.bh-note b { color: var(--ink); font-weight: 600; }

.bh-term { display: grid; grid-template-columns: 110px 1fr 44px;
  align-items: center; gap: 12px; padding: 6px 0; font-size: 14px; }
.bh-term .w { color: var(--ink); overflow: hidden; text-overflow: ellipsis; }
.bh-term .t { height: 6px; border-radius: 3px; background: var(--line-soft); }
.bh-term .t i { display: block; height: 100%; border-radius: 3px;
  background: var(--ink-3); }
.bh-term .n { color: var(--ink-3); text-align: right; font-size: 12.5px; }
.bh-sub-h { font-size: 13px; font-weight: 600; color: var(--ink-2);
  margin: 0 0 8px; }

/* ---------- Review list ---------- */
.bh-reviews { border-top: 1px solid var(--line); }
.bh-review { display: grid; grid-template-columns: 78px 96px 1fr;
  gap: 8px 18px; padding: 14px 0; border-bottom: 1px solid var(--line-soft);
  align-items: start; }
.bh-review .d { font-size: 12.5px; color: var(--ink-3); padding-top: 3px; }
.bh-review .tx { font-size: 14.5px; line-height: 1.5; color: var(--ink);
  overflow-wrap: anywhere; display: -webkit-box; -webkit-line-clamp: 4;
  -webkit-box-orient: vertical; overflow: hidden; }
.bh-review .stars { font-size: 12.5px; color: var(--ink-3); margin-top: 6px; }
.pill { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px;
  font-weight: 500; padding: 3px 10px 3px 8px; border-radius: 999px; }
.pill .dot { width: 7px; height: 7px; margin: 0; }
.pill.pos { background: var(--pos-tint); color: var(--pos); }
.pill.neg { background: var(--neg-tint); color: var(--neg); }
.pill.neu { background: var(--neu-tint); color: var(--ink-2); }
@media (max-width: 640px) {
  .bh-review { grid-template-columns: 1fr; gap: 6px; }
  .bh-review .d { order: 3; padding: 0; }
}

/* ---------- States ---------- */
.bh-empty { padding: 64px 0; max-width: 52ch; }
.bh-empty h2 { font-size: 22px; letter-spacing: -.02em; margin: 0 0 8px; }
.bh-empty p { color: var(--ink-2); font-size: 15px; line-height: 1.55; margin: 0; }
.bh-method { margin-top: 40px; font-size: 13.5px; color: var(--ink-2); }
.bh-method summary { cursor: pointer; font-weight: 600; color: var(--ink);
  font-size: 14px; padding: 6px 0; }
.bh-method ul { margin: 10px 0 0; padding-left: 18px; line-height: 1.65;
  max-width: 78ch; }
.bh-method code { background: var(--neu-tint); padding: 1px 6px;
  border-radius: 5px; font-size: 12.5px; }
"""
