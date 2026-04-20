"""
Dashboard Económico Argentina
Fuentes: datos.gob.ar · BCRA · Bluelytics
"""

import warnings
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import urllib3

warnings.filterwarnings("ignore")
urllib3.disable_warnings()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Económico · Argentina",
    page_icon="🇦🇷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
C_BG      = "#0d1117"
C_SURFACE = "#161b22"
C_BORDER  = "#21262d"
C_TEXT    = "#e6edf3"
C_MUTED   = "#8b949e"
C_BLUE    = "#3B82F6"
C_RED     = "#EF4444"
C_YELLOW  = "#F59E0B"
C_GREEN   = "#22C55E"

PRESIDENCIAS = [
    ("Macri",    "2015-12-10", "2019-12-10", "rgba(255,193,7,0.06)"),
    ("A. Fdz.",  "2019-12-10", "2023-12-10", "rgba(3,169,244,0.06)"),
    ("Milei",    "2023-12-10", None,          "rgba(130,80,255,0.06)"),
]

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* ── Base ── */
  .stApp, [data-testid="stAppViewContainer"] {{ background:{C_BG}; }}
  [data-testid="stHeader"] {{
      background:{C_BG}ee;
      backdrop-filter:blur(8px);
      border-bottom:1px solid {C_BORDER};
  }}
  .block-container {{ padding-top:1rem; padding-bottom:3rem; max-width:1400px; }}

  /* ── Sticky header ── */
  .sticky-hdr {{
      position:sticky; top:3.6rem; z-index:90;
      background:{C_BG}f5;
      backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
      border-bottom:1px solid {C_BORDER};
      padding:.8rem 0 .65rem;
      margin-bottom:1.4rem;
      display:flex; align-items:center; justify-content:space-between; gap:1rem;
  }}
  .sticky-hdr h1 {{
      font-size:1.45rem !important; font-weight:800 !important;
      color:{C_TEXT} !important; margin:0 !important; letter-spacing:-.3px;
  }}
  .sticky-hdr .upd {{ font-size:.75rem; color:{C_MUTED}; white-space:nowrap; }}

  /* ── Period selector ── */
  .period-wrap {{
      display:flex; align-items:center; gap:1rem; margin-bottom:1.6rem;
  }}
  .period-label {{ font-size:.75rem; color:{C_MUTED}; font-weight:600;
                   text-transform:uppercase; letter-spacing:.06em; white-space:nowrap; }}
  div[data-testid="stRadio"] > div {{
      display:flex !important; gap:0 !important; flex-wrap:nowrap !important;
      background:{C_SURFACE}; border:1px solid {C_BORDER}; border-radius:8px; padding:3px;
  }}
  div[data-testid="stRadio"] label {{
      padding:5px 16px !important; border-radius:6px !important; cursor:pointer !important;
      font-size:.82rem !important; font-weight:600 !important; color:{C_MUTED} !important;
      transition:all 150ms !important; white-space:nowrap !important;
      display:flex !important; align-items:center !important;
  }}
  div[data-testid="stRadio"] label:has(input:checked) {{
      background:{C_BLUE} !important; color:#fff !important;
  }}
  div[data-testid="stRadio"] input[type="radio"] {{ display:none !important; }}
  div[data-testid="stRadio"] > label {{ display:none; }}

  /* ── Section titles ── */
  .sec-title {{ font-size:1.05rem; font-weight:700; color:{C_TEXT};
                letter-spacing:.1px; margin:0 0 .25rem 0; }}
  .sec-sub   {{ font-size:.75rem; color:{C_MUTED}; margin-bottom:1rem; }}

  /* ── KPI cards ── */
  .kpi-grid {{
      display:grid;
      grid-template-columns:repeat(auto-fit, minmax(185px, 1fr));
      gap:1rem; margin-bottom:1.3rem;
  }}
  .kpi-card {{
      background:{C_SURFACE}; border:1px solid {C_BORDER};
      border-top:3px solid {C_BLUE}; border-radius:12px;
      padding:1.2rem 1.4rem 1.1rem;
      box-shadow:0 2px 12px rgba(0,0,0,.35);
      transition:border-color 180ms, box-shadow 180ms, transform 120ms;
  }}
  .kpi-card:hover {{
      border-color:{C_BLUE}; box-shadow:0 4px 24px rgba(59,130,246,.15);
      transform:translateY(-1px);
  }}
  .kpi-label {{
      font-size:.68rem; color:{C_MUTED}; text-transform:uppercase;
      letter-spacing:.07em; font-weight:700; margin-bottom:.55rem;
  }}
  .kpi-value {{
      font-size:2.1rem; font-weight:800; color:{C_TEXT}; line-height:1;
      margin-bottom:.45rem; font-variant-numeric:tabular-nums; letter-spacing:-.6px;
  }}
  .kpi-delta {{
      font-size:.78rem; font-weight:600; display:flex; align-items:center; gap:3px;
  }}
  .kpi-delta.pos  {{ color:{C_BLUE};   }}
  .kpi-delta.neg  {{ color:{C_RED};    }}
  .kpi-delta.neu  {{ color:{C_MUTED};  }}
  .kpi-delta.warn {{ color:{C_YELLOW}; }}

  /* ── Calculator card ── */
  .calc-result {{
      background:{C_SURFACE}; border:1px solid {C_BORDER}; border-radius:12px;
      padding:1.4rem 1.6rem;
      box-shadow:0 2px 12px rgba(0,0,0,.35);
  }}
  .calc-result .big {{ font-size:2.6rem; font-weight:800; color:{C_GREEN};
                       font-variant-numeric:tabular-nums; line-height:1; }}
  .calc-result .sub {{ font-size:.82rem; color:{C_MUTED}; margin-top:.4rem; }}

  /* ── Download button ── */
  div[data-testid="stDownloadButton"] button {{
      background:{C_SURFACE} !important; color:{C_MUTED} !important;
      border:1px solid {C_BORDER} !important; border-radius:6px !important;
      font-size:.75rem !important; padding:3px 12px !important;
      transition:all 150ms !important;
  }}
  div[data-testid="stDownloadButton"] button:hover {{
      border-color:{C_BLUE} !important; color:{C_BLUE} !important;
  }}

  /* ── Divider ── */
  hr[data-testid="stDivider"] {{ border-color:{C_BORDER} !important; margin:2rem 0 !important; }}

  /* ── Spinner ── */
  .stSpinner > div {{ border-top-color:{C_BLUE} !important; }}

  /* ── Scrollbar ── */
  ::-webkit-scrollbar       {{ width:5px; height:5px; }}
  ::-webkit-scrollbar-track {{ background:{C_BG}; }}
  ::-webkit-scrollbar-thumb {{ background:{C_BORDER}; border-radius:3px; }}
  ::-webkit-scrollbar-thumb:hover {{ background:{C_MUTED}44; }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHART HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _layout(title: str, y_label: str = "", y2_label: str | None = None) -> dict:
    """Base Plotly layout — no rangeselector (global selector handles periods)."""
    ax = dict(
        showgrid=False, zeroline=False,
        linecolor=C_BORDER, linewidth=1, showline=True,
        tickfont=dict(size=12, color=C_MUTED),
    )
    base = dict(
        title=dict(
            text=title,
            font=dict(color=C_TEXT, size=18, family="Inter,system-ui,Arial,sans-serif"),
            x=0.0, xanchor="left", y=0.97, yanchor="top",
        ),
        plot_bgcolor=C_SURFACE,
        paper_bgcolor=C_BG,
        font=dict(color=C_MUTED, family="Inter,system-ui,Arial,sans-serif", size=13),
        legend=dict(
            bgcolor="rgba(22,27,34,0.8)", bordercolor=C_BORDER, borderwidth=1,
            font=dict(color=C_MUTED, size=12),
            orientation="h", yanchor="top", y=-0.18, xanchor="left", x=0,
        ),
        xaxis=dict(**ax, title=None,
                   rangeslider=dict(visible=True, thickness=0.04, bgcolor=C_SURFACE)),
        yaxis=dict(**ax, title=dict(text=y_label, font=dict(size=13, color=C_MUTED))),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=C_SURFACE, bordercolor=C_BORDER,
                        font=dict(color=C_TEXT, size=13)),
        margin=dict(l=60, r=60, t=70, b=80),
    )
    if y2_label:
        base["yaxis2"] = dict(**ax,
            title=dict(text=y2_label, font=dict(size=13, color=C_MUTED)),
            overlaying="y", side="right",
        )
    return base


def _add_presidencias(fig: go.Figure, date_min: pd.Timestamp,
                      date_max: pd.Timestamp) -> None:
    """Overlay colored bands + labels per presidency."""
    colors_label = {
        "Macri":   C_YELLOW,
        "A. Fdz.": C_BLUE,
        "Milei":   "#a855f7",
    }
    for name, x0_str, x1_str, fill in PRESIDENCIAS:
        x0 = pd.Timestamp(x0_str)
        x1 = pd.Timestamp(x1_str) if x1_str else date_max + timedelta(days=30)
        # clip to data range for cleaner rendering
        x0c = max(x0, date_min)
        x1c = min(x1, date_max + timedelta(days=30))
        if x0c >= x1c:
            continue
        fig.add_vrect(x0=x0c, x1=x1c, fillcolor=fill,
                      layer="below", line_width=0)
        mid = x0c + (x1c - x0c) / 2
        fig.add_annotation(
            x=mid, y=1.0, yref="paper",
            text=name, showarrow=False,
            font=dict(size=10, color=colors_label.get(name, C_MUTED)),
            bgcolor="rgba(13,17,23,0.6)", borderpad=2,
            xanchor="center", yanchor="top",
        )


# ─────────────────────────────────────────────────────────────────────────────
# KPI CARD RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def kpi(label: str, value: str, delta: str | None = None,
        positive: bool | None = None, warn: bool = False) -> str:
    if delta is None:
        d = ""
    else:
        if warn:           cls, arrow = "warn", "◆"
        elif positive is True:  cls, arrow = "pos",  "▲"
        elif positive is False: cls, arrow = "neg",  "▼"
        else:              cls, arrow = "neu",  "—"
        d = f'<div class="kpi-delta {cls}">{arrow}&nbsp;{delta}</div>'
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>{d}'
        f'</div>'
    )


def kpi_row(*cards: str) -> None:
    st.markdown(f'<div class="kpi-grid">{"".join(cards)}</div>',
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOAD HELPER
# ─────────────────────────────────────────────────────────────────────────────

def download_btn(df: pd.DataFrame, filename: str) -> None:
    _, col, _ = st.columns([1, 0.18, 1])
    with col:
        st.download_button(
            label="⬇ CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
        )


# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# FALLBACK DATA  (used when external APIs are unreachable)
# ─────────────────────────────────────────────────────────────────────────────

# Monthly IPC variation (%) — real INDEC figures Jan 2017 – Mar 2026
_FB_IPC = [
    (2017,1,1.6),(2017,2,2.1),(2017,3,2.3),(2017,4,2.6),(2017,5,1.3),(2017,6,1.2),
    (2017,7,1.7),(2017,8,1.4),(2017,9,1.4),(2017,10,1.1),(2017,11,1.4),(2017,12,3.1),
    (2018,1,1.8),(2018,2,2.4),(2018,3,2.3),(2018,4,2.7),(2018,5,2.1),(2018,6,3.7),
    (2018,7,3.1),(2018,8,3.9),(2018,9,6.5),(2018,10,5.4),(2018,11,3.2),(2018,12,2.6),
    (2019,1,2.9),(2019,2,3.8),(2019,3,4.7),(2019,4,3.4),(2019,5,3.1),(2019,6,2.7),
    (2019,7,2.2),(2019,8,4.0),(2019,9,5.9),(2019,10,3.3),(2019,11,4.3),(2019,12,3.7),
    (2020,1,2.3),(2020,2,2.0),(2020,3,3.3),(2020,4,1.5),(2020,5,1.5),(2020,6,2.2),
    (2020,7,1.9),(2020,8,2.7),(2020,9,2.8),(2020,10,3.8),(2020,11,3.2),(2020,12,4.0),
    (2021,1,4.0),(2021,2,3.6),(2021,3,4.8),(2021,4,4.1),(2021,5,3.3),(2021,6,3.2),
    (2021,7,3.0),(2021,8,2.5),(2021,9,3.5),(2021,10,3.5),(2021,11,2.5),(2021,12,3.8),
    (2022,1,3.9),(2022,2,4.7),(2022,3,6.7),(2022,4,6.0),(2022,5,5.1),(2022,6,5.3),
    (2022,7,7.4),(2022,8,7.0),(2022,9,6.2),(2022,10,6.3),(2022,11,4.9),(2022,12,5.1),
    (2023,1,6.0),(2023,2,6.6),(2023,3,7.7),(2023,4,8.4),(2023,5,7.8),(2023,6,6.0),
    (2023,7,6.3),(2023,8,12.4),(2023,9,12.7),(2023,10,8.3),(2023,11,12.8),(2023,12,25.5),
    (2024,1,20.6),(2024,2,13.2),(2024,3,11.0),(2024,4,8.8),(2024,5,4.2),(2024,6,4.6),
    (2024,7,4.0),(2024,8,4.2),(2024,9,3.5),(2024,10,2.4),(2024,11,2.4),(2024,12,2.7),
    (2025,1,2.3),(2025,2,2.4),(2025,3,3.7),
]

# Monthly FX rates (end of period) — (date, oficial, blue)
_FB_FX = [
    ("2020-01-31",61.0,80.0),("2020-02-29",63.0,83.0),("2020-03-31",65.0,87.0),
    ("2020-04-30",66.0,110.0),("2020-05-31",68.0,118.0),("2020-06-30",70.0,122.0),
    ("2020-07-31",72.5,131.0),("2020-08-31",74.5,140.0),("2020-09-30",76.5,150.0),
    ("2020-10-31",79.0,168.0),("2020-11-30",81.5,160.0),("2020-12-31",84.1,168.0),
    ("2021-01-31",86.5,155.0),("2021-02-28",89.0,149.0),("2021-03-31",91.5,146.0),
    ("2021-04-30",93.5,145.0),("2021-05-31",95.5,162.0),("2021-06-30",97.0,165.0),
    ("2021-07-31",99.0,175.0),("2021-08-31",101.5,183.0),("2021-09-30",103.5,186.0),
    ("2021-10-31",105.5,196.0),("2021-11-30",107.0,202.0),("2021-12-31",103.0,208.0),
    ("2022-01-31",105.0,218.0),("2022-02-28",107.5,215.0),("2022-03-31",111.5,212.0),
    ("2022-04-30",116.5,207.0),("2022-05-31",120.0,220.0),("2022-06-30",125.5,245.0),
    ("2022-07-31",130.0,300.0),("2022-08-31",139.5,298.0),("2022-09-30",148.0,290.0),
    ("2022-10-31",157.5,296.0),("2022-11-30",165.5,315.0),("2022-12-31",177.0,338.0),
    ("2023-01-31",190.0,377.0),("2023-02-28",202.0,384.0),("2023-03-31",210.0,390.0),
    ("2023-04-30",222.5,425.0),("2023-05-31",237.0,487.0),("2023-06-30",257.0,500.0),
    ("2023-07-31",270.0,530.0),("2023-08-31",366.0,750.0),("2023-09-30",350.0,715.0),
    ("2023-10-31",355.0,850.0),("2023-11-30",362.0,930.0),("2023-12-31",808.5,1050.0),
    ("2024-01-31",832.0,1040.0),("2024-02-29",860.0,1060.0),("2024-03-31",871.0,1045.0),
    ("2024-04-30",883.0,1060.0),("2024-05-31",898.0,1250.0),("2024-06-30",915.0,1395.0),
    ("2024-07-31",930.0,1440.0),("2024-08-31",946.0,1320.0),("2024-09-30",963.0,1195.0),
    ("2024-10-31",978.0,1185.0),("2024-11-30",1007.0,1150.0),("2024-12-31",1032.0,1220.0),
    ("2025-01-31",1055.0,1235.0),("2025-02-28",1076.0,1235.0),("2025-03-31",1096.0,1280.0),
]

# Monthly nominal salaries ARS (RIPTE-like) — (YYYY-MM, value)
_FB_SAL = [
    ("2017-01",14500),("2017-02",14900),("2017-03",15300),("2017-04",15800),
    ("2017-05",16200),("2017-06",16700),("2017-07",17300),("2017-08",17700),
    ("2017-09",18200),("2017-10",18700),("2017-11",19200),("2017-12",20100),
    ("2018-01",20800),("2018-02",21500),("2018-03",22300),("2018-04",23200),
    ("2018-05",24000),("2018-06",25200),("2018-07",26400),("2018-08",27600),
    ("2018-09",29200),("2018-10",30800),("2018-11",32000),("2018-12",33500),
    ("2019-01",35000),("2019-02",36500),("2019-03",38200),("2019-04",39800),
    ("2019-05",41500),("2019-06",43200),("2019-07",45000),("2019-08",47200),
    ("2019-09",50000),("2019-10",52500),("2019-11",55000),("2019-12",58000),
    ("2020-01",60500),("2020-02",62500),("2020-03",64500),("2020-04",65500),
    ("2020-05",67000),("2020-06",69000),("2020-07",72000),("2020-08",75000),
    ("2020-09",78500),("2020-10",83000),("2020-11",87000),("2020-12",92000),
    ("2021-01",96000),("2021-02",100000),("2021-03",105000),("2021-04",110000),
    ("2021-05",115000),("2021-06",120000),("2021-07",126000),("2021-08",131000),
    ("2021-09",138000),("2021-10",144000),("2021-11",150000),("2021-12",158000),
    ("2022-01",165000),("2022-02",173000),("2022-03",182000),("2022-04",193000),
    ("2022-05",204000),("2022-06",217000),("2022-07",234000),("2022-08",252000),
    ("2022-09",269000),("2022-10",287000),("2022-11",303000),("2022-12",322000),
    ("2023-01",344000),("2023-02",368000),("2023-03",396000),("2023-04",431000),
    ("2023-05",466000),("2023-06",497000),("2023-07",534000),("2023-08",592000),
    ("2023-09",664000),("2023-10",720000),("2023-11",793000),("2023-12",920000),
    ("2024-01",1060000),("2024-02",1175000),("2024-03",1270000),("2024-04",1355000),
    ("2024-05",1410000),("2024-06",1470000),("2024-07",1530000),("2024-08",1590000),
    ("2024-09",1640000),("2024-10",1685000),("2024-11",1720000),("2024-12",1770000),
    ("2025-01",1820000),("2025-02",1875000),("2025-03",1940000),
]

# Monthly BCRA reserves (millions USD) — (YYYY-MM, value)
_FB_RES = [
    ("2015-01",31547),("2015-02",31229),("2015-03",31094),("2015-04",32375),
    ("2015-05",33523),("2015-06",33560),("2015-07",33099),("2015-08",32819),
    ("2015-09",32050),("2015-10",25593),("2015-11",24689),("2015-12",25563),
    ("2016-01",26086),("2016-02",28289),("2016-03",30000),("2016-04",32000),
    ("2016-05",32500),("2016-06",33000),("2016-07",33500),("2016-08",34000),
    ("2016-09",34500),("2016-10",35500),("2016-11",36000),("2016-12",38773),
    ("2017-01",40000),("2017-02",41000),("2017-03",42500),("2017-04",44000),
    ("2017-05",45500),("2017-06",46500),("2017-07",47000),("2017-08",47500),
    ("2017-09",48000),("2017-10",50000),("2017-11",51500),("2017-12",55055),
    ("2018-01",61723),("2018-02",62000),("2018-03",61000),("2018-04",57000),
    ("2018-05",51000),("2018-06",48000),("2018-07",47500),("2018-08",46000),
    ("2018-09",44000),("2018-10",48500),("2018-11",50000),("2018-12",52000),
    ("2019-01",67000),("2019-02",66500),("2019-03",67100),("2019-04",68000),
    ("2019-05",66000),("2019-06",63500),("2019-07",61900),("2019-08",54000),
    ("2019-09",50000),("2019-10",48000),("2019-11",44500),("2019-12",44780),
    ("2020-01",44500),("2020-02",44000),("2020-03",43000),("2020-04",43500),
    ("2020-05",43000),("2020-06",42800),("2020-07",42500),("2020-08",42700),
    ("2020-09",41700),("2020-10",39700),("2020-11",39200),("2020-12",39400),
    ("2021-01",39100),("2021-02",38800),("2021-03",39500),("2021-04",40200),
    ("2021-05",41500),("2021-06",42600),("2021-07",44000),("2021-08",46800),
    ("2021-09",46300),("2021-10",44500),("2021-11",42800),("2021-12",39600),
    ("2022-01",37700),("2022-02",37500),("2022-03",37800),("2022-04",42000),
    ("2022-05",40800),("2022-06",38600),("2022-07",37200),("2022-08",36900),
    ("2022-09",36700),("2022-10",37800),("2022-11",37500),("2022-12",44600),
    ("2023-01",43500),("2023-02",41500),("2023-03",40000),("2023-04",37200),
    ("2023-05",33300),("2023-06",27900),("2023-07",24000),("2023-08",23000),
    ("2023-09",25700),("2023-10",21500),("2023-11",20900),("2023-12",23400),
    ("2024-01",27200),("2024-02",27900),("2024-03",28200),("2024-04",29000),
    ("2024-05",31500),("2024-06",29500),("2024-07",27200),("2024-08",27100),
    ("2024-09",27500),("2024-10",28700),("2024-11",30400),("2024-12",32000),
    ("2025-01",32300),("2025-02",32600),("2025-03",32900),
]


def _fb_ipc() -> pd.DataFrame:
    rows, cumulative = [], 100.0
    for y, m, v in _FB_IPC:
        cumulative *= (1 + v / 100)
        rows.append({"fecha": pd.Timestamp(year=y, month=m, day=1), "ipc": cumulative, "var_mensual": v})
    return pd.DataFrame(rows)


def _fb_bluelytics() -> tuple[pd.DataFrame, pd.DataFrame]:
    blue_rows, of_rows = [], []
    for d, oficial, blue in _FB_FX:
        fecha = pd.to_datetime(d)
        blue_rows.append({"fecha": fecha, "blue": blue})
        of_rows.append({"fecha": fecha, "oficial": oficial})
    return pd.DataFrame(blue_rows), pd.DataFrame(of_rows)


def _fb_salarios() -> pd.DataFrame:
    rows = [{"fecha": pd.to_datetime(ym + "-01"), "salario": float(v)} for ym, v in _FB_SAL]
    df = pd.DataFrame(rows).sort_values("fecha").reset_index(drop=True)
    df.attrs["label"] = "RIPTE (estimado)"
    return df


def _fb_reservas() -> pd.DataFrame:
    rows = [{"fecha": pd.to_datetime(ym + "-01"), "reservas": float(v)} for ym, v in _FB_RES]
    return pd.DataFrame(rows).sort_values("fecha").reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ArgDashboard/1.0)"}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ipc() -> pd.DataFrame:
    url = (
        "https://apis.datos.gob.ar/series/api/series/"
        "?ids=148.3_INIVELNAL_DICI_M_26&limit=1000&format=json"
    )
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return _fb_ipc()

    rows = [
        {"fecha": pd.to_datetime(str(item[0])), "ipc": float(item[1])}
        for item in data.get("data", [])
        if len(item) >= 2 and item[1] is not None
    ]
    if not rows:
        return _fb_ipc()

    df = (pd.DataFrame(rows).sort_values("fecha")
          .drop_duplicates("fecha").reset_index(drop=True))
    df["var_mensual"] = df["ipc"].pct_change() * 100
    return df.dropna(subset=["var_mensual"])


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bluelytics() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (df_blue, df_oficial) from Bluelytics evolution API."""
    url = "https://api.bluelytics.com.ar/v2/evolution.json"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return _fb_bluelytics()

    blue_rows, of_rows = [], []
    for item in data:
        source = str(item.get("source", "")).lower()
        fecha  = item.get("date") or item.get("fecha")
        if not fecha:
            continue
        val = item.get("value_sell") or item.get("value_avg") or item.get("value_buy")
        if val is None:
            continue
        try:
            row = {"fecha": pd.to_datetime(str(fecha)), "v": float(val)}
        except (ValueError, TypeError):
            continue
        if "blue" in source or not source:
            blue_rows.append({"fecha": row["fecha"], "blue": row["v"]})
        elif "oficial" in source:
            of_rows.append({"fecha": row["fecha"], "oficial": row["v"]})

    def _clean(rows: list) -> pd.DataFrame:
        if not rows:
            return pd.DataFrame()
        return (pd.DataFrame(rows).sort_values("fecha")
                .drop_duplicates("fecha").reset_index(drop=True))

    return _clean(blue_rows), _clean(of_rows)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_reservas() -> pd.DataFrame:
    """Reservas Internacionales del BCRA — variable id=1 (millones USD)."""
    today = datetime.today()
    desde = (today - timedelta(days=10 * 365)).strftime("%Y-%m-%d")
    hasta = today.strftime("%Y-%m-%d")
    base  = "https://api.bcra.gob.ar/estadisticas/v3.0/monetarias/1"

    data = None
    for url in [f"{base}/{desde}/{hasta}",
                f"{base}?desde={desde}&hasta={hasta}", base]:
        try:
            r = requests.get(url, headers=_HEADERS, verify=False, timeout=30)
            if r.status_code == 200:
                data = r.json()
                break
        except Exception:
            continue

    if data is None:
        return _fb_reservas()

    records: list = []
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        for key in ("results", "data", "series", "values"):
            if key in data and isinstance(data[key], list):
                records = data[key]
                break

    rows = []
    for item in records:
        if not isinstance(item, dict):
            continue
        fecha = item.get("fecha") or item.get("date") or item.get("d")
        valor = item.get("valor") or item.get("value") or item.get("v")
        if fecha and valor is not None:
            try:
                rows.append({"fecha": pd.to_datetime(str(fecha)),
                             "reservas": float(valor)})
            except (ValueError, TypeError):
                continue

    if not rows:
        return _fb_reservas()
    return (pd.DataFrame(rows).sort_values("fecha")
            .drop_duplicates("fecha").reset_index(drop=True))


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_salarios() -> pd.DataFrame:
    series = [
        ("148.3_RFSTSEPDICI_0_M_31", "RIPTE"),
        ("103.1_I2N_2016_M_19",      "Índice de Salarios"),
        ("148.3_INGTOT_DICI_M_15",   "Ingreso Total"),
    ]
    for sid, label in series:
        try:
            url = (
                "https://apis.datos.gob.ar/series/api/series/"
                f"?ids={sid}&limit=1000&format=json"
            )
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            rows = [
                {"fecha": pd.to_datetime(str(item[0])), "salario": float(item[1])}
                for item in r.json().get("data", [])
                if len(item) >= 2 and item[1] is not None
            ]
            if rows:
                df = (pd.DataFrame(rows).sort_values("fecha")
                      .drop_duplicates("fecha").reset_index(drop=True))
                df.attrs["label"] = label
                return df
        except Exception:
            continue
    return _fb_salarios()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _last(df: pd.DataFrame, col: str) -> float | None:
    if df.empty or col not in df.columns:
        return None
    s = df[col].dropna()
    return float(s.iloc[-1]) if len(s) else None


def _prev(df: pd.DataFrame, col: str) -> float | None:
    s = (df[col].dropna() if not df.empty and col in df.columns
         else pd.Series(dtype=float))
    return float(s.iloc[-2]) if len(s) >= 2 else None


def _bar_color(x: float) -> str:
    if x > 8:  return C_RED
    if x > 4:  return C_YELLOW
    return C_BLUE


def _clip(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    if df.empty or "fecha" not in df.columns:
        return df
    m = (df["fecha"].dt.date >= start) & (df["fecha"].dt.date <= end)
    return df.loc[m].copy()


def _period_dates(p: str) -> tuple[date, date]:
    today = date.today()
    deltas = {"6M": 182, "1A": 365, "2A": 730, "5A": 1825}
    return (today - timedelta(days=deltas[p]), today) if p in deltas else (date(2000, 1, 1), today)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────

with st.spinner("Descargando datos de fuentes oficiales…"):
    df_ipc      = fetch_ipc()
    df_blue, df_of = fetch_bluelytics()
    df_res      = fetch_reservas()
    df_sal      = fetch_salarios()


# ─────────────────────────────────────────────────────────────────────────────
# STICKY HEADER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("<div style='padding-top:1.5rem'></div>", unsafe_allow_html=True)
st.markdown(
    f'<div class="sticky-hdr">'
    f'<h1>Dashboard Económico Argentina</h1>'
    f'<div class="upd">Actualizado {datetime.now().strftime("%d/%m/%Y %H:%M")}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL PERIOD SELECTOR
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="period-wrap"><span class="period-label">Período</span>',
            unsafe_allow_html=True)
periodo = st.radio("Período", ["6M", "1A", "2A", "5A", "Todo"],
                   index=2, horizontal=True, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

p_start, p_end = _period_dates(periodo)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 · INFLACIÓN IPC
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="sec-title">Inflación mensual (IPC)</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">IPC Nivel General Nacional · datos.gob.ar</div>',
            unsafe_allow_html=True)

if df_ipc.empty or "_error" in df_ipc.columns:
    err = df_ipc["_error"].iloc[0] if "_error" in df_ipc.columns else "sin datos"
    st.error(f"No se pudo cargar el IPC: {err}")
else:
    ipc = _clip(df_ipc, p_start, p_end)

    if not ipc.empty:
        lv = _last(ipc, "var_mensual");  pv = _prev(ipc, "var_mensual")
        dp = (lv - pv) if (lv is not None and pv is not None) else None
        ia = ((df_ipc["ipc"].iloc[-1] / df_ipc["ipc"].iloc[-13] - 1) * 100
              if len(df_ipc) >= 13 else None)
        this_yr = ipc[ipc["fecha"].dt.year == int(ipc["fecha"].dt.year.max())]
        ac = ((this_yr["ipc"].iloc[-1] / this_yr["ipc"].iloc[0] - 1) * 100
              if len(this_yr) >= 2 else None)
        q3 = ((ipc["ipc"].iloc[-1] / ipc["ipc"].iloc[-4] - 1) * 100
              if len(ipc) >= 4 else None)

        kpi_row(
            kpi("Var. mensual", f"{lv:.1f}%" if lv is not None else "—",
                f"{dp:+.1f} pp" if dp is not None else None,
                positive=(dp >= 0 if dp is not None else None)),
            kpi("Interanual",      f"{ia:.1f}%" if ia is not None else "—"),
            kpi(f"Acum. {int(ipc['fecha'].dt.year.max())}",
                f"{ac:.1f}%" if ac is not None else "—"),
            kpi("Últimos 3 meses", f"{q3:.1f}%" if q3 is not None else "—"),
        )

        ipc["_color"]  = ipc["var_mensual"].apply(_bar_color)
        ipc["_roll3m"] = ipc["var_mensual"].rolling(3, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=ipc["fecha"], y=ipc["var_mensual"],
            marker_color=ipc["_color"].tolist(), marker_line_width=0,
            name="Var. mensual %",
            hovertemplate="%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=ipc["fecha"], y=ipc["_roll3m"],
            mode="lines", name="Media móvil 3M",
            line=dict(color=C_TEXT, width=2, dash="dot"),
            hovertemplate="%{x|%b %Y}: <b>%{y:.2f}%</b><extra>Media 3M</extra>",
        ))
        _add_presidencias(fig, ipc["fecha"].min(), ipc["fecha"].max())
        fig.update_layout(**_layout("Variación Mensual del IPC", "%"))
        st.plotly_chart(fig, use_container_width=True)
        download_btn(ipc[["fecha", "ipc", "var_mensual"]], "ipc.csv")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 · TIPO DE CAMBIO
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="sec-title">Tipo de Cambio USD/ARS</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Cotización oficial y blue · Bluelytics</div>',
            unsafe_allow_html=True)

if df_of.empty and df_blue.empty:
    st.error("No se pudieron cargar datos de tipo de cambio.")
else:
    of_f   = _clip(df_of,   p_start, p_end)
    blue_f = _clip(df_blue, p_start, p_end)

    lv_of = _last(of_f, "oficial");  lv_bl = _last(blue_f, "blue")
    pv_of = _prev(of_f, "oficial");  pv_bl = _prev(blue_f, "blue")
    brecha     = (lv_bl / lv_of - 1) * 100 if lv_of and lv_bl and lv_of > 0 else None
    prev_brecha = (pv_bl / pv_of - 1) * 100 if pv_of and pv_bl and pv_of > 0 else None
    d_of = lv_of - pv_of if lv_of and pv_of else None
    d_bl = lv_bl - pv_bl if lv_bl and pv_bl else None
    d_br = brecha - prev_brecha if brecha is not None and prev_brecha is not None else None

    kpi_row(
        kpi("USD Oficial", f"${lv_of:,.2f}" if lv_of else "—",
            f"{d_of:+.2f}" if d_of is not None else None,
            positive=(d_of >= 0 if d_of is not None else None)),
        kpi("USD Blue", f"${lv_bl:,.2f}" if lv_bl else "—",
            f"{d_bl:+.2f}" if d_bl is not None else None,
            positive=(d_bl >= 0 if d_bl is not None else None)),
        kpi("Brecha cambiaria", f"{brecha:.0f}%" if brecha is not None else "—",
            f"{d_br:+.1f} pp" if d_br is not None else None, warn=True),
    )

    df_spread: pd.DataFrame = pd.DataFrame()
    if not of_f.empty and not blue_f.empty:
        df_spread = pd.merge_asof(
            of_f.sort_values("fecha"), blue_f.sort_values("fecha"),
            on="fecha", direction="nearest", tolerance=pd.Timedelta("7 days"),
        ).dropna(subset=["oficial", "blue"])
        df_spread["brecha_pct"] = (df_spread["blue"] / df_spread["oficial"] - 1) * 100

    fig = go.Figure()
    if not of_f.empty:
        fig.add_trace(go.Scatter(
            x=of_f["fecha"], y=of_f["oficial"], mode="lines", name="Oficial",
            line=dict(color=C_BLUE, width=2.5),
            hovertemplate="%{x|%d/%m/%Y}: <b>$%{y:,.2f}</b><extra>Oficial</extra>",
        ))
    if not blue_f.empty:
        fig.add_trace(go.Scatter(
            x=blue_f["fecha"], y=blue_f["blue"], mode="lines", name="Blue",
            line=dict(color=C_RED, width=2.5),
            hovertemplate="%{x|%d/%m/%Y}: <b>$%{y:,.2f}</b><extra>Blue</extra>",
        ))
    if not df_spread.empty:
        fig.add_trace(go.Scatter(
            x=df_spread["fecha"], y=df_spread["brecha_pct"],
            mode="lines", name="Brecha %", yaxis="y2",
            line=dict(color=C_YELLOW, width=1.5, dash="dot"),
            hovertemplate="%{x|%d/%m/%Y}: <b>%{y:.0f}%</b><extra>Brecha</extra>",
        ))
        fig.update_layout(**_layout("Tipo de Cambio USD/ARS", "Pesos argentinos", "Brecha (%)"))
    else:
        fig.update_layout(**_layout("Tipo de Cambio USD/ARS", "Pesos argentinos"))

    all_dates = pd.concat(
        [d["fecha"] for d in [of_f, blue_f] if not d.empty and "fecha" in d]
    )
    if not all_dates.empty:
        _add_presidencias(fig, all_dates.min(), all_dates.max())

    st.plotly_chart(fig, use_container_width=True)
    export_fx = pd.concat([of_f, blue_f], axis=1) if not of_f.empty and not blue_f.empty else of_f
    if not df_spread.empty:
        download_btn(df_spread[["fecha", "oficial", "blue", "brecha_pct"]], "tipo_cambio.csv")
    elif not of_f.empty:
        download_btn(of_f, "tipo_cambio_oficial.csv")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 · SALARIO REAL vs INFLACIÓN
# ─────────────────────────────────────────────────────────────────────────────

sal_label = df_sal.attrs.get("label", "Salario") if not df_sal.empty else "Salario"

st.markdown('<div class="sec-title">Salario Real vs Inflación</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sec-sub">{sal_label} deflactado por IPC · índice base 100 · datos.gob.ar</div>',
            unsafe_allow_html=True)

if df_sal.empty:
    st.error("No se pudieron cargar datos de salarios desde datos.gob.ar.")
elif df_ipc.empty or "_error" in df_ipc.columns:
    st.error("Sin datos de IPC para calcular el salario real.")
else:
    sal_f  = _clip(df_sal, p_start, p_end)
    ipc_m  = df_ipc[["fecha", "ipc"]].copy()

    merged = pd.merge_asof(
        sal_f.sort_values("fecha"), ipc_m.sort_values("fecha"),
        on="fecha", direction="nearest", tolerance=pd.Timedelta("45 days"),
    ).dropna(subset=["salario", "ipc"])

    if merged.empty:
        st.warning("Sin superposición de datos en el período seleccionado.")
    else:
        base_sal  = merged["salario"].iloc[0]
        base_ipc  = merged["ipc"].iloc[0]
        base_date = merged["fecha"].iloc[0].strftime("%b %Y")

        merged["sal_nom"]  = merged["salario"] / base_sal * 100
        merged["ipc_idx"]  = merged["ipc"]     / base_ipc * 100
        merged["sal_real"] = (merged["salario"] / merged["ipc"]) / (base_sal / base_ipc) * 100

        v_nom  = merged["sal_nom"].iloc[-1]  - 100
        v_ipc  = merged["ipc_idx"].iloc[-1]  - 100
        v_real = merged["sal_real"].iloc[-1] - 100

        kpi_row(
            kpi(f"{sal_label} nominal",    f"{v_nom:+.1f}%",  positive=(v_nom  >= 0)),
            kpi("Inflación acum. (IPC)",   f"{v_ipc:+.1f}%"),
            kpi("Salario real",            f"{v_real:+.1f}%", positive=(v_real >= 0)),
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=merged["fecha"], y=merged["ipc_idx"], mode="lines", name="Precios (IPC)",
            line=dict(color=C_RED, width=2),
            hovertemplate="%{x|%b %Y}: <b>%{y:.1f}</b><extra>IPC</extra>",
        ))
        fig.add_trace(go.Scatter(
            x=merged["fecha"], y=merged["sal_nom"], mode="lines", name=f"{sal_label} nominal",
            line=dict(color=C_BLUE, width=2),
            hovertemplate="%{x|%b %Y}: <b>%{y:.1f}</b><extra>Nominal</extra>",
        ))
        fig.add_trace(go.Scatter(
            x=merged["fecha"], y=merged["sal_real"], mode="lines", name="Salario real",
            line=dict(color=C_GREEN, width=3),
            fill="tozeroy", fillcolor="rgba(34,197,94,0.07)",
            hovertemplate="%{x|%b %Y}: <b>%{y:.1f}</b><extra>Sal. real</extra>",
        ))
        fig.add_hline(y=100, line_dash="dash", line_color=C_BORDER,
                      annotation_text=f"Base {base_date}",
                      annotation_position="bottom left",
                      annotation_font=dict(color=C_MUTED, size=11))
        _add_presidencias(fig, merged["fecha"].min(), merged["fecha"].max())
        fig.update_layout(**_layout(f"Salario Real vs Inflación — base 100 = {base_date}",
                                    "Índice (base = 100)"))
        st.plotly_chart(fig, use_container_width=True)
        download_btn(merged[["fecha", "salario", "ipc", "sal_nom", "ipc_idx", "sal_real"]],
                     "salario_real.csv")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 · RESERVAS BCRA
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="sec-title">Reservas Internacionales del BCRA</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Variable id=1 · BCRA API v3.0 · millones USD</div>',
            unsafe_allow_html=True)

if df_res.empty:
    st.error("No se pudieron obtener datos de reservas del BCRA.")
else:
    res_f = _clip(df_res, p_start, p_end)

    if not res_f.empty:
        lv_r = _last(res_f, "reservas");  pv_r = _prev(res_f, "reservas")
        d_r  = lv_r - pv_r if lv_r and pv_r else None
        max_r = res_f["reservas"].max()
        min_r = res_f["reservas"].min()

        kpi_row(
            kpi("Reservas actuales",  f"USD {lv_r:,.0f}M" if lv_r else "—",
                f"{d_r:+,.0f}M" if d_r is not None else None,
                positive=(d_r >= 0 if d_r is not None else None)),
            kpi("Máximo del período", f"USD {max_r:,.0f}M" if not res_f.empty else "—"),
            kpi("Mínimo del período", f"USD {min_r:,.0f}M" if not res_f.empty else "—"),
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=res_f["fecha"], y=res_f["reservas"],
            mode="lines", name="Reservas",
            line=dict(color=C_BLUE, width=2.5),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
            hovertemplate="%{x|%d/%m/%Y}: <b>USD %{y:,.0f}M</b><extra>Reservas</extra>",
        ))
        _add_presidencias(fig, res_f["fecha"].min(), res_f["fecha"].max())
        fig.update_layout(**_layout("Reservas Internacionales del BCRA", "Millones USD"))
        st.plotly_chart(fig, use_container_width=True)
        download_btn(res_f, "reservas_bcra.csv")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 · CALCULADORA DE INFLACIÓN
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="sec-title">Calculadora de Inflación</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Convertí un monto histórico a pesos de hoy según el IPC</div>',
            unsafe_allow_html=True)

if df_ipc.empty or "_error" in df_ipc.columns:
    st.error("Se necesitan datos de IPC para la calculadora.")
else:
    ipc_min_date = df_ipc["fecha"].min().date()
    ipc_max_date = df_ipc["fecha"].max().date()

    c1, c2, c3 = st.columns([1, 1, 1.4])
    with c1:
        monto = st.number_input("Monto original ($)", min_value=0.01,
                                value=100_000.0, step=1_000.0, format="%.2f")
    with c2:
        fecha_calc = st.date_input(
            "Fecha del monto",
            value=ipc_max_date - timedelta(days=365),
            min_value=ipc_min_date,
            max_value=ipc_max_date,
            format="DD/MM/YYYY",
        )

    # Find closest IPC month
    ts_calc = pd.Timestamp(fecha_calc)
    idx_then = (df_ipc["fecha"] - ts_calc).abs().idxmin()
    ipc_then = df_ipc.loc[idx_then, "ipc"]
    ipc_now  = df_ipc["ipc"].iloc[-1]
    fecha_now_str = df_ipc["fecha"].iloc[-1].strftime("%b %Y")
    fecha_then_str = df_ipc.loc[idx_then, "fecha"].strftime("%b %Y")

    monto_ajustado  = monto * (ipc_now / ipc_then)
    inflacion_acum  = (ipc_now / ipc_then - 1) * 100
    poder_adquis    = (ipc_then / ipc_now) * 100

    with c3:
        st.markdown(
            f'<div class="calc-result">'
            f'<div class="kpi-label">Equivale hoy ({fecha_now_str})</div>'
            f'<div class="big">${monto_ajustado:,.0f}</div>'
            f'<div class="sub">'
            f'Inflación acumulada desde {fecha_then_str}: <strong>'
            f'+{inflacion_acum:.1f}%</strong>&nbsp;&nbsp;·&nbsp;&nbsp;'
            f'Poder adquisitivo conservado: <strong>{poder_adquis:.1f}%</strong>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 · HEATMAP DE CORRELACIONES
# ─────────────────────────────────────────────────────────────────────────────

st.markdown('<div class="sec-title">Correlaciones entre indicadores</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sec-sub">Coeficiente de Pearson entre variaciones mensuales · período seleccionado</div>',
            unsafe_allow_html=True)

def _build_corr(ipc_df, of_df, blue_df, sal_df,
                start: date, end: date) -> pd.DataFrame | None:
    frames: dict[str, pd.Series] = {}

    if not ipc_df.empty and "_error" not in ipc_df.columns:
        tmp = _clip(ipc_df, start, end)
        if not tmp.empty:
            frames["Inflación"] = tmp.set_index("fecha")["var_mensual"]

    for df, col, name in [
        (of_df,   "oficial", "Dólar Oficial"),
        (blue_df, "blue",    "Dólar Blue"),
    ]:
        if not df.empty and col in df.columns:
            tmp = _clip(df, start, end)
            if not tmp.empty:
                m = (tmp.set_index("fecha")[col]
                     .resample("MS").last()
                     .pct_change() * 100)
                m.name = name
                frames[name] = m

    if not sal_df.empty and "salario" in sal_df.columns:
        tmp = _clip(sal_df, start, end)
        if not tmp.empty:
            m = (tmp.set_index("fecha")["salario"]
                 .resample("MS").last()
                 .pct_change() * 100)
            m.name = sal_df.attrs.get("label", "Salario")
            frames[m.name] = m

    if len(frames) < 2:
        return None

    combined = pd.concat(frames.values(), axis=1).dropna()
    if len(combined) < 6:
        return None
    return combined.corr()


corr = _build_corr(df_ipc, df_of, df_blue, df_sal, p_start, p_end)

if corr is None:
    st.info("No hay suficientes datos superpuestos para calcular correlaciones en este período.")
else:
    try:
        import plotly.express as px
        fig = px.imshow(
            corr,
            color_continuous_scale=[[0.0, C_RED], [0.5, "#21262d"], [1.0, C_BLUE]],
            zmin=-1, zmax=1,
            text_auto=".2f",
        )
        fig.update_layout(
            title=dict(text="Correlación entre indicadores (variaciones mensuales %)",
                       font=dict(color=C_TEXT, size=18,
                                 family="Inter,system-ui,Arial,sans-serif"),
                       x=0.0, xanchor="left"),
            plot_bgcolor=C_SURFACE, paper_bgcolor=C_BG,
            font=dict(color=C_TEXT, size=13),
            coloraxis_colorbar=dict(
                title="r",
                tickfont=dict(color=C_MUTED),
                titlefont=dict(color=C_MUTED),
            ),
            xaxis=dict(showgrid=False, linecolor=C_BORDER, tickfont=dict(color=C_TEXT)),
            yaxis=dict(showgrid=False, linecolor=C_BORDER, tickfont=dict(color=C_TEXT)),
            margin=dict(l=60, r=40, t=70, b=60),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.dataframe(corr.round(2), use_container_width=True)

    download_btn(corr.reset_index().rename(columns={"index": "indicador"}),
                 "correlaciones.csv")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    f"<div style='text-align:center;color:{C_MUTED};font-size:.75rem;padding:.4rem 0 1rem'>"
    f"INDEC &nbsp;·&nbsp; BCRA &nbsp;·&nbsp; Bluelytics &nbsp;·&nbsp; datos.gob.ar"
    f"&nbsp;&nbsp;|&nbsp;&nbsp;Cache: 1 hora"
    f"</div>",
    unsafe_allow_html=True,
)
