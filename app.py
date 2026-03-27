import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import io
import os
from dotenv import load_dotenv

load_dotenv()

# ── LOGIN ──
def check_password():
    def password_entered():
        try:
            correct_user = st.secrets["USERNAME"]
            correct_pass = st.secrets["PASSWORD"]
        except Exception:
            correct_user = "admin"
            correct_pass = "scoutiq2024"
        if (st.session_state.get("login_user") == correct_user and
                st.session_state.get("login_pass") == correct_pass):
            st.session_state["authenticated"] = True
        else:
            st.session_state["auth_error"] = True

    if st.session_state.get("authenticated"):
        return True

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');
    * { font-family: 'DM Sans', sans-serif !important; }
    html, body, [class*="css"] { background: linear-gradient(160deg, #060d24 0%, #0f1f5c 50%, #1a3a8a 100%) !important; }
    #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
    .stApp { background: linear-gradient(160deg, #060d24 0%, #0f1f5c 50%, #1a3a8a 100%) !important; min-height: 100vh; }
    .block-container { padding-top: 0px !important; padding-bottom: 0px !important; }
    /* Brand */
    .login-brand { text-align: center; padding-top: 48px; padding-bottom: 36px; }
    .login-brand-name { font-family: 'DM Serif Display', serif !important; font-size: 52px; color: #ffffff; letter-spacing: -1px; line-height: 1; margin-bottom: 12px; font-weight: 400; }
    .login-brand-name .fc { color: #f5c842; }
    .login-brand-value { font-size: 11px; color: rgba(255,255,255,0.85); letter-spacing: 5px; text-transform: uppercase; font-weight: 500; }
    /* Divider */
    .login-divider { border: none; border-top: 1px solid rgba(255,255,255,0.12); max-width: 400px; margin: 0 auto 28px auto; }
    /* Fields */
    .stTextInput { max-width: 400px; margin: 0 auto; }
    .stTextInput > div > div { background: rgba(255,255,255,0.95) !important; border: 1px solid rgba(255,255,255,0.3) !important; border-radius: 12px !important; }
    .stTextInput > div > div:focus-within { border-color: #f5c842 !important; box-shadow: 0 0 0 3px rgba(245,200,66,0.2) !important; }
    .stTextInput input { color: #0f1623 !important; font-size: 15px !important; padding: 14px 16px !important; }
    .stTextInput input::placeholder { color: #94a3b8 !important; }
    .stTextInput label { font-size: 10px !important; font-weight: 700 !important; color: rgba(255,255,255,0.6) !important; letter-spacing: 2px !important; text-transform: uppercase !important; }
    /* Sign in button - centered */
    .stButton { max-width: 300px; margin: 0 auto; display: flex; justify-content: center; }
    .stButton > button { background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important; color: #ffffff !important; border: none !important; border-radius: 12px !important; font-weight: 700 !important; font-size: 15px !important; letter-spacing: 0.5px !important; padding: 14px 0 !important; width: 100% !important; margin-top: 16px !important; box-shadow: 0 6px 24px rgba(22,163,74,0.45) !important; }
    .stButton > button:hover { background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important; box-shadow: 0 8px 28px rgba(22,163,74,0.55) !important; transform: translateY(-1px) !important; }
    /* Error */
    .error-msg { max-width: 400px; margin: 0 auto 12px auto; background: rgba(220,38,38,0.15); border: 1px solid rgba(220,38,38,0.3); border-radius: 8px; padding: 10px 16px; font-size: 12px; color: #fca5a5; text-align: center; }
    .register-note { text-align: center; margin-top: 20px; font-size: 12px; color: rgba(255,255,255,0.45); }
    .register-note a { color: rgba(245,200,66,0.8); text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)

    # Center column
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        # Brand — right at top
        st.markdown("""
        <div class="login-brand">
            <div class="login-brand-name">Scout IQ·<span class="fc">FC</span></div>
            <div class="login-brand-value">Where Talent Is Unearthed</div>
        </div>
        <hr class="login-divider">
        """, unsafe_allow_html=True)

        if st.session_state.get("auth_error"):
            st.markdown('<div class="error-msg">Incorrect username or password</div>', unsafe_allow_html=True)

        st.text_input("Username", key="login_user", placeholder="Username")
        st.text_input("Password", type="password", key="login_pass", placeholder="Password")

        # Center the button
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2:
            st.button("Sign In", on_click=password_entered)

        st.markdown("""
        <div class="register-note">
            New to Scout IQ·FC? &nbsp;
            <a href="mailto:admin@scoutiqfc.com">Request Access</a>
        </div>
        """, unsafe_allow_html=True)

    return False
if not check_password():
    st.stop()

# ── DATABASE ──
conn = sqlite3.connect("scout_agent.db", check_same_thread=False)
cursor = conn.cursor()

# Seed demo data on first launch
try:
    from demo_data import seed_demo_data
    seed_demo_data(conn)
except Exception:
    pass

cursor.executescript("""
CREATE TABLE IF NOT EXISTS report_edits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER, edited_report TEXT, coach_notes TEXT,
    edited_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS epl_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, team TEXT, position TEXT, nationality TEXT, age INTEGER
);
CREATE TABLE IF NOT EXISTS epl_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER, gameweek INTEGER, opponent TEXT, venue TEXT,
    minutes_played INTEGER DEFAULT 0, goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0, shots INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0, xg REAL DEFAULT 0, xa REAL DEFAULT 0,
    passes_completed INTEGER DEFAULT 0, passes_attempted INTEGER DEFAULT 0,
    key_passes INTEGER DEFAULT 0, progressive_passes INTEGER DEFAULT 0,
    dribbles_completed INTEGER DEFAULT 0, dribbles_attempted INTEGER DEFAULT 0,
    touches INTEGER DEFAULT 0, ball_recoveries INTEGER DEFAULT 0,
    tackles_won INTEGER DEFAULT 0, interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0, yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0, rating REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS epl_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER, report_text TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

st.set_page_config(
    page_title="Scout IQ·FC", page_icon="⚽",
    layout="wide", initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');
* { font-family: 'DM Sans', sans-serif !important; }
html, body, [class*="css"] { background-color: #F5F6FA; color: #0f1623; }
#MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
.stApp { background: #F5F6FA; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebar"] {
    transform: none !important; display: flex !important; visibility: visible !important;
    min-width: 260px !important; max-width: 260px !important;
    background: linear-gradient(175deg, #0f1f5c 0%, #1a3a8a 60%, #1e4db7 100%) !important;
    box-shadow: 4px 0 24px rgba(15,31,92,0.2) !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* SIDEBAR LOGO AREA */
.sidebar-logo-area { padding: 14px 20px 12px 20px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); }

/* SIDEBAR INPUTS */
[data-testid="stSidebar"] .stTextInput { padding: 8px 14px 4px 14px; }
[data-testid="stSidebar"] .stTextInput > div > div { background: rgba(255,255,255,0.95) !important; border: 1px solid rgba(255,255,255,0.3) !important; border-radius: 6px !important; }
[data-testid="stSidebar"] .stTextInput input { color: #0f1623 !important; font-size: 12px !important; padding: 6px 10px !important; }
[data-testid="stSidebar"] .stTextInput input::placeholder { color: #8492b4 !important; }
[data-testid="stSidebar"] label { display: none !important; }

/* SIDEBAR SECTIONS */
.sidebar-section { padding: 6px 18px 3px 18px; font-size: 9px; color: rgba(255,255,255,0.3); letter-spacing: 3px; text-transform: uppercase; font-weight: 700; }
.beta-badge { display: inline-block; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.55); font-size: 8px; font-weight: 700; letter-spacing: 1.5px; padding: 1px 5px; border-radius: 3px; margin-left: 5px; }
.pro-badge { display: inline-block; background: rgba(255,200,0,0.12); border: 1px solid rgba(255,200,0,0.35); color: rgba(255,200,0,0.85); font-size: 8px; font-weight: 700; letter-spacing: 1.5px; padding: 1px 5px; border-radius: 3px; margin-left: 5px; }

/* SIDEBAR BUTTONS */
[data-testid="stSidebar"] .stButton { margin: 0 !important; padding: 0 !important; }
[data-testid="stSidebar"] .stButton > button { background: transparent !important; color: rgba(255,255,255,0.6) !important; border: none !important; outline: none !important; box-shadow: none !important; font-size: 12px !important; padding: 7px 18px !important; border-radius: 0 !important; width: 100% !important; text-align: left !important; border-left: 3px solid transparent !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; }
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.07) !important; color: #ffffff !important; border-left: 3px solid rgba(255,255,255,0.35) !important; }
[data-testid="stSidebar"] .stButton > button:focus, [data-testid="stSidebar"] .stButton > button:active { background: rgba(255,255,255,0.05) !important; box-shadow: none !important; outline: none !important; }
.club-row .stButton > button { font-size: 11px !important; font-weight: 700 !important; color: rgba(255,255,255,0.82) !important; text-transform: uppercase !important; padding: 8px 18px !important; letter-spacing: 0.3px !important; }
.player-row .stButton > button { font-style: italic !important; color: rgba(255,255,255,0.48) !important; padding: 5px 18px 5px 32px !important; font-size: 12px !important; }
.player-active .stButton > button { color: #ffffff !important; font-style: normal !important; font-weight: 600 !important; border-left: 3px solid rgba(255,255,255,0.75) !important; background: rgba(255,255,255,0.1) !important; }
.add-player-row .stButton > button { color: rgba(255,255,255,0.55) !important; font-size: 10px !important; padding: 5px 18px 8px 18px !important; letter-spacing: 0.3px !important; border-top: 1px solid rgba(255,255,255,0.05) !important; margin-top: 1px !important; }
.add-player-row .stButton > button:hover { color: rgba(255,255,255,0.85) !important; background: rgba(255,255,255,0.05) !important; }
.new-academy-row .stButton > button { color: rgba(255,255,255,0.5) !important; font-size: 11px !important; padding: 8px 18px !important; border: 1px dashed rgba(255,255,255,0.2) !important; border-radius: 6px !important; margin: 4px 14px !important; width: calc(100% - 28px) !important; text-align: center !important; }
.new-academy-row .stButton > button:hover { color: rgba(255,255,255,0.85) !important; border-color: rgba(255,255,255,0.4) !important; background: rgba(255,255,255,0.06) !important; }
.signout-row .stButton > button { background: rgba(255,255,255,0.06) !important; color: rgba(255,255,255,0.4) !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 6px !important; font-size: 10px !important; letter-spacing: 1px !important; text-transform: uppercase !important; margin: 6px 14px !important; width: calc(100% - 28px) !important; padding: 7px 12px !important; text-align: center !important; }
.signout-row .stButton > button:hover { background: rgba(220,38,38,0.15) !important; color: #ff8080 !important; border-color: rgba(220,38,38,0.3) !important; }
.system-info { padding: 4px 18px 10px 18px; font-size: 10px; color: rgba(255,255,255,0.22); line-height: 1.9; }
hr { border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 6px 0; }

/* MAIN CONTENT */
.main-header { padding: 32px 0 20px 0; border-bottom: 2px solid #dde2f0; margin-bottom: 24px; }
.player-name-large { font-family: 'DM Serif Display', serif !important; font-size: 46px; color: #0a0f2c; line-height: 1.1; margin: 0; }
.player-meta { font-size: 10px; color: #1a3a8a; letter-spacing: 3px; text-transform: uppercase; margin-top: 10px; font-weight: 700; }
.metric-card { background: #ffffff; border: 1.5px solid #dde2f0; border-top: 4px solid #1a3a8a; padding: 16px; border-radius: 10px; box-shadow: 0 2px 10px rgba(15,31,92,0.07); }
.metric-card-label { font-size: 9px; color: #8492b4; text-transform: uppercase; letter-spacing: 2px; font-weight: 700; margin-bottom: 6px; }
.metric-card-value { font-size: 20px; font-weight: 700; color: #0a0f2c; }
.section-title { font-family: 'DM Serif Display', serif !important; font-size: 20px; color: #0a0f2c; margin: 32px 0 12px 0; padding-bottom: 10px; border-bottom: 2px solid #1a3a8a; }
.report-block { background: #ffffff; border: 1.5px solid #dde2f0; border-radius: 12px; padding: 36px 42px; box-shadow: 0 2px 12px rgba(15,31,92,0.07); }
.report-section-title { font-size: 10px; font-weight: 700; color: #1a3a8a; letter-spacing: 3px; text-transform: uppercase; margin: 24px 0 10px 0; padding-bottom: 8px; border-bottom: 1.5px solid #e8ecf8; }
.report-body { font-size: 14px; color: #2d3452; line-height: 1.9; margin-bottom: 3px; }
.coach-notes-box { background: #fffbeb; border: 1.5px solid #f59e0b; border-radius: 10px; padding: 24px 28px; margin-top: 16px; }
.coach-notes-label { font-size: 10px; font-weight: 700; color: #b45309; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 12px; }
.stDataFrame { border: 1.5px solid #dde2f0 !important; border-radius: 10px !important; background: #ffffff !important; }
.stTextArea textarea { font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; color: #2d3452 !important; border: 1.5px solid #dde2f0 !important; border-radius: 8px !important; }
.export-btn .stButton > button { background: #0f1f5c !important; color: #ffffff !important; border: none !important; font-weight: 600 !important; font-size: 9px !important; letter-spacing: 1px !important; text-transform: uppercase !important; padding: 6px 12px !important; border-radius: 4px !important; box-shadow: none !important; white-space: nowrap !important; width: auto !important; }
.save-btn .stButton > button { background: #059669 !important; color: #ffffff !important; border: none !important; font-weight: 600 !important; font-size: 9px !important; letter-spacing: 1px !important; text-transform: uppercase !important; padding: 6px 12px !important; border-radius: 4px !important; box-shadow: none !important; width: auto !important; }
.edit-btn .stButton > button { background: #7c3aed !important; color: #ffffff !important; border: none !important; font-weight: 600 !important; font-size: 9px !important; letter-spacing: 1px !important; text-transform: uppercase !important; padding: 6px 12px !important; border-radius: 4px !important; box-shadow: none !important; width: auto !important; }
.gen-btn .stButton > button { background: linear-gradient(135deg, #059669, #047857) !important; color: #ffffff !important; border: none !important; font-weight: 700 !important; font-size: 11px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; padding: 12px 28px !important; border-radius: 8px !important; box-shadow: 0 4px 14px rgba(5,150,105,0.3) !important; width: auto !important; }
/* Small add session button */
[data-testid="stSidebar"] ~ div [key="add_sess"] .stButton > button,
div[style*="text-align:right"] .stButton > button { background: rgba(26,58,138,0.08) !important; color: #1a3a8a !important; border: 1.5px solid #dde2f0 !important; font-size: 9px !important; font-weight: 600 !important; letter-spacing: 1px !important; text-transform: uppercase !important; padding: 5px 10px !important; border-radius: 5px !important; box-shadow: none !important; width: auto !important; white-space: nowrap !important; }
.stDownloadButton > button { background: #c0392b !important; color: #ffffff !important; font-size: 9px !important; letter-spacing: 1px !important; text-transform: uppercase !important; padding: 6px 12px !important; border-radius: 4px !important; border: none !important; font-weight: 600 !important; white-space: nowrap !important; width: auto !important; min-width: 0 !important; max-width: 140px !important; }
::-webkit-scrollbar { width: 3px; } ::-webkit-scrollbar-track { background: #F5F6FA; } ::-webkit-scrollbar-thumb { background: #dde2f0; border-radius: 2px; }
div[role="radiogroup"] { display: none; }
.no-select { padding: 80px 24px; text-align: center; color: #8492b4; font-size: 14px; }
.welcome-card { background: #ffffff; border: 1.5px solid #dde2f0; border-radius: 14px; padding: 32px 28px; text-align: center; box-shadow: 0 2px 12px rgba(15,31,92,0.06); transition: all 0.2s; }
.welcome-card:hover { box-shadow: 0 4px 20px rgba(15,31,92,0.12); transform: translateY(-2px); }
.upload-banner { background: linear-gradient(135deg, #eef2ff, #f0f7ff); border: 1.5px solid #c7d2fe; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER
    import anthropic
except ImportError as e:
    st.error(f"Missing library: {e}")
    st.stop()


def get_api_key():
    try:
        return st.secrets["ANTHROPIC_KEY"]
    except Exception:
        return os.getenv("ANTHROPIC_KEY")


def ai_report(prompt):
    claude = anthropic.Anthropic(api_key=get_api_key())
    r = claude.messages.create(model="claude-opus-4-5", max_tokens=4000,
        messages=[{"role": "user", "content": prompt}])
    return r.content[0].text


def to_pdf(name, meta, text, is_pro=False):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm, topMargin=20*mm, bottomMargin=20*mm)
    navy=HexColor('#0f1f5c'); blue=HexColor('#1a3a8a'); dark=HexColor('#0a0f2c')
    bc=HexColor('#2d3452'); lc=HexColor('#8492b4'); dc=HexColor('#dde2f0')
    s = {
        'logo': ParagraphStyle('l', fontName='Helvetica-Bold', fontSize=22, textColor=navy, spaceAfter=0, leading=26),
        'tag':  ParagraphStyle('t', fontName='Helvetica', fontSize=7, textColor=lc, spaceAfter=6, leading=10),
        'name': ParagraphStyle('n', fontName='Helvetica-Bold', fontSize=17, textColor=dark, spaceAfter=3, leading=20),
        'meta': ParagraphStyle('m', fontName='Helvetica', fontSize=8, textColor=lc, spaceAfter=10, leading=12),
        'head': ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=9, textColor=blue, spaceAfter=4, spaceBefore=12, leading=13),
        'body': ParagraphStyle('b', fontName='Helvetica', fontSize=9, textColor=bc, spaceAfter=3, leading=15),
        'foot': ParagraphStyle('f', fontName='Helvetica', fontSize=7, textColor=lc, alignment=TA_CENTER),
    }
    tag = "PRO ANALYSIS — ENGLISH PREMIER LEAGUE" if is_pro else "TALENT INTELLIGENCE PLATFORM"
    story = [Paragraph("SCOUT IQ·FC", s['logo']), Spacer(1,2*mm), Paragraph(tag, s['tag']),
             HRFlowable(width="100%", thickness=0.8, color=blue, spaceAfter=6*mm),
             Paragraph(name.upper(), s['name']), Paragraph(meta, s['meta']),
             HRFlowable(width="100%", thickness=0.3, color=dc, spaceAfter=8*mm)]
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1,3*mm))
        elif line[0].isdigit() and '.' in line[:3]:
            story.append(HRFlowable(width="100%", thickness=0.2, color=dc, spaceBefore=4*mm, spaceAfter=3*mm))
            story.append(Paragraph(line.upper(), s['head']))
        else:
            clean = line.replace('**','').replace('--','').replace('- ','').replace('#','')
            if clean:
                story.append(Paragraph(clean, s['body']))
    story += [Spacer(1,10*mm), HRFlowable(width="100%",thickness=0.2,color=dc),
              Spacer(1,3*mm), Paragraph(f"Scout IQ·FC  |  {name}  |  Confidential", s['foot'])]
    doc.build(story)
    buf.seek(0)
    return buf


def to_word(name, meta, text, is_pro=False):
    doc = Document()
    doc.styles['Normal'].font.name = 'Arial Narrow'
    doc.styles['Normal'].font.size = Pt(10)
    t = doc.add_heading('SCOUT IQ·FC', 0)
    t.runs[0].font.color.rgb = RGBColor(15,31,92); t.runs[0].font.size = Pt(22); t.runs[0].font.name = 'Arial Narrow'
    tag = "PRO ANALYSIS — ENGLISH PREMIER LEAGUE" if is_pro else "TALENT INTELLIGENCE PLATFORM"
    sub = doc.add_paragraph(tag)
    sub.runs[0].font.size = Pt(8); sub.runs[0].font.color.rgb = RGBColor(132,146,180)
    doc.add_paragraph()
    n = doc.add_heading(name.upper(), 1)
    n.runs[0].font.color.rgb = RGBColor(10,15,44); n.runs[0].font.size = Pt(17); n.runs[0].font.name = 'Arial Narrow'
    m = doc.add_paragraph(meta)
    m.runs[0].font.size = Pt(9); m.runs[0].font.color.rgb = RGBColor(132,146,180)
    doc.add_paragraph()
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            doc.add_paragraph()
        elif line[0].isdigit() and '.' in line[:3]:
            h = doc.add_heading(line, 2)
            if h.runs:
                h.runs[0].font.color.rgb = RGBColor(26,58,138); h.runs[0].font.size = Pt(10)
                h.runs[0].font.name = 'Arial Narrow'; h.runs[0].bold = True
        else:
            clean = line.replace('**','').replace('--','').replace('- ','').replace('#','')
            if clean:
                p = doc.add_paragraph(clean)
                if p.runs:
                    p.runs[0].font.size = Pt(10); p.runs[0].font.name = 'Arial Narrow'
                    p.runs[0].font.color.rgb = RGBColor(45,52,82)
    fp = doc.sections[0].footer.paragraphs[0]
    fp.text = f"Scout IQ·FC   |   {name}   |   Confidential"
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    buf = io.BytesIO()
    doc.save(buf); buf.seek(0)
    return buf


def show_report(text, pid, pname, meta, is_pro=False):
    cursor.execute("SELECT edited_report, coach_notes FROM report_edits WHERE player_id=? ORDER BY edited_at DESC LIMIT 1", (pid,))
    row = cursor.fetchone()
    active = row[0] if row else text
    notes = row[1] if row and row[1] else ""
    ekey = f"edit_{pid}_{is_pro}"
    if ekey not in st.session_state:
        st.session_state[ekey] = False

    c1,c2,c3,_,_ = st.columns([1,1,1,1,5])
    with c1:
        st.markdown('<div class="edit-btn">', unsafe_allow_html=True)
        if st.button("Edit", key=f"eb_{pid}_{is_pro}"):
            st.session_state[ekey] = not st.session_state[ekey]; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="export-btn">', unsafe_allow_html=True)
        if st.button("PDF", key=f"pb_{pid}_{is_pro}"):
            st.session_state[f"sp_{pid}_{is_pro}"] = True
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="export-btn">', unsafe_allow_html=True)
        if st.button("Word", key=f"wb_{pid}_{is_pro}"):
            st.session_state[f"sw_{pid}_{is_pro}"] = True
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get(f"sp_{pid}_{is_pro}"):
        buf = to_pdf(pname, meta, active, is_pro)
        st.download_button("Download PDF", buf, f"ScoutIQFC_{pname.replace(' ','_')}.pdf", "application/pdf", key=f"dp_{pid}_{is_pro}")
    if st.session_state.get(f"sw_{pid}_{is_pro}"):
        buf = to_word(pname, meta, active, is_pro)
        st.download_button("Download Word", buf, f"ScoutIQFC_{pname.replace(' ','_')}.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document", key=f"dw_{pid}_{is_pro}")

    if st.session_state[ekey]:
        st.markdown('<div class="section-title">Edit Report</div>', unsafe_allow_html=True)
        edited = st.text_area("Report", value=active, height=500, key=f"ea_{pid}_{is_pro}", label_visibility="collapsed")
        st.markdown('<div class="coach-notes-box"><div class="coach-notes-label">Coach Annotations</div>', unsafe_allow_html=True)
        new_notes = st.text_area("Notes", value=notes, height=150, key=f"na_{pid}_{is_pro}", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        if st.button("Save", key=f"sv_{pid}_{is_pro}"):
            cursor.execute("INSERT INTO report_edits (player_id,edited_report,coach_notes) VALUES (?,?,?)", (pid, edited, new_notes))
            conn.commit(); st.session_state[ekey] = False; st.success("Saved"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        html = '<div class="report-block">'
        for line in active.split('\n'):
            line = line.strip()
            if not line:
                html += '<div style="height:8px"></div>'
            elif line[0].isdigit() and '.' in line[:3]:
                html += f'<div class="report-section-title">{line}</div>'
            else:
                clean = line.replace('**','').replace('--','').replace('- ','').replace('#','')
                html += f'<div class="report-body">{clean}</div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
        if notes:
            st.markdown(f'<div class="coach-notes-box"><div class="coach-notes-label">Coach Annotations</div><div style="font-size:13px;color:#92400e;line-height:1.8;">{notes}</div></div>', unsafe_allow_html=True)


def sg(row, idx, default=0):
    try:
        v = row[idx]
        return v if v is not None else default
    except IndexError:
        return default


def build_youth_prompt(player, sessions):
    sessions_text = "\n".join([
        f"- {s[2]} ({s[3]}): {s[4]} mins, {s[5]}km, {s[6]} sprints, top speed {s[7]}km/h, passes {s[8]}/{s[9]}, dribbles {s[10]}, defensive actions {s[11]}, goals {s[12]}, assists {s[13]}, chances {s[14]}, tackles {s[15]}. Coachability {s[16]}/10, attitude {s[17]}/10, consistency {s[18]}/10. Notes: {s[19]}"
        for s in sessions
    ])
    return f"""You are a senior youth football scout and player development specialist with 20 years of experience at academy level across Europe and South America. You write development reports that serve as a player professional CV read by academy directors, technical coaches and talent ID managers.

Your reports are concise, direct and written in the language coaches use every day. No academic language. No AI phrases. No bullet points or dashes. Full sentences throughout. Maximum 4 pages when printed.

PLAYER PROFILE:
Name: {player[1]}
Position: {player[4]}
Date of birth: {player[2]}
Age group: {player[3]}
Club: {player[6]}
Nationality: {player[7] or 'Unknown'}
Dominant foot: {player[5]}

SESSION DATA ({len(sessions)} sessions):
{sessions_text}

Write a youth development scouting report with these sections. Every section complete. No bullet points. No dashes. Confident and direct.

EXECUTIVE SUMMARY
4 sentences. Standout quality with one number. Biggest limitation with one number. Development trajectory. Recommendation.

1. PERFORMANCE RATING
Score out of 10 with two data points. Category for age and position.

2. TECHNICAL PROFILE
Pass completion rate, dribble rate, defensive actions per 90, goal and assist involvement per 90. Two sentences on quality relative to age and position. Position-appropriate assessment.

3. PHYSICAL PROFILE
Average distance, average sprints, peak speed. Two sentences on whether output is elite, adequate or concerning. Flag any session with output drop over 15 percent.

4. MENTAL AND ATTITUDE PROFILE
Coachability, attitude and consistency averages and trend. Two sentences on development potential. One specific behavioural recommendation.

5. BEST POSITION NOW AND FUTURE
Current best position from data. One alternative position to trial with justification. If struggling in current role state this directly.

6. SHORT TERM RECOMMENDATIONS (Next 4 to 8 weeks)
Three specific training recommendations. For each: current metric, target metric, training intervention.

7. MEDIUM TERM DEVELOPMENT PLAN (This season)
Three measurable development targets. Include one out-of-the-box recommendation.

8. LONG TERM CEILING AND PATHWAY
Realistic ceiling with three data points. One paragraph at age 21 without intervention. One paragraph with recommendations followed.

9. INJURY AND LOAD WATCH
Short term, medium term and long term assessment.

10. MAN MANAGEMENT GUIDE
Short term feedback approach. This season management. Long term psychological readiness.

11. TRAINING SESSION IDEAS
Two specific session formats. Name, setup, metric targeted, why it suits this player.

12. SCOUTING VERDICT
Recommendation with three data justifications. One memorable final sentence.

No bullet points. No dashes. No markdown. Direct, clear and actionable."""


# ── DATA ──
cursor.execute("SELECT id,name,position,club,age_group,nationality,dominant_foot FROM players")
players = cursor.fetchall()
clubs = {}
for p in players:
    club = p[3] or "Unassigned"
    if club not in clubs:
        clubs[club] = []
    clubs[club].append(p)

cursor.execute("SELECT DISTINCT team FROM epl_players ORDER BY team")
epl_teams = [r[0] for r in cursor.fetchall()]

for k,v in {
    "selected_player_id": players[0][0] if players else None,
    "expanded_clubs": [],
    "expanded_epl_teams": [],
    "selected_epl_player_id": None,
    "mode": "youth",
    "show_add_player": False,
    "show_add_academy": False,
    "add_player_club": None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo-area">
        <div style="font-family:'DM Serif Display',serif;font-size:21px;color:#ffffff;letter-spacing:0.3px;line-height:1;">
            Scout IQ·<span style="color:#f5c842;">FC</span>
        </div>
        <div style="font-size:8px;color:rgba(255,255,255,0.65);letter-spacing:3px;text-transform:uppercase;margin-top:5px;">
            Where Talent Is Unearthed
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mode toggle
    st.markdown('<div class="sidebar-section" style="padding-top:6px;padding-bottom:3px;">Mode</div>', unsafe_allow_html=True)
    m1,m2 = st.columns(2)
    with m1:
        if st.button("Youth", key="ny", use_container_width=True):
            st.session_state.mode="youth"; st.rerun()
    with m2:
        if st.button("Pro Data", key="np", use_container_width=True):
            st.session_state.mode="pro"; st.rerun()
    st.markdown('<div style="margin:1px 0;"></div>', unsafe_allow_html=True)

    if st.session_state.mode == "youth":
        srch = st.text_input("s", placeholder="Search player...", label_visibility="collapsed")
        st.markdown('<div class="sidebar-section">Academies <span class="beta-badge">Beta</span></div>', unsafe_allow_html=True)

        # New academy button
        st.markdown('<div class="new-academy-row">', unsafe_allow_html=True)
        if st.button("＋  New Academy", key="new_acad", use_container_width=True):
            st.session_state.show_add_academy = True
            st.session_state.show_add_player = False
            st.session_state.selected_player_id = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        for club, cplayers in clubs.items():
            filt = [p for p in cplayers if srch.lower() in p[1].lower()] if srch else cplayers
            if not filt:
                continue
            exp = club in st.session_state.expanded_clubs or bool(srch)
            st.markdown('<div class="club-row">', unsafe_allow_html=True)
            if st.button(f"{'▾' if exp else '▸'}  {club}", key=f"cl_{club}", use_container_width=True):
                if exp and not srch:
                    st.session_state.expanded_clubs.remove(club)
                elif not exp:
                    st.session_state.expanded_clubs.append(club)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            if exp:
                for p in filt:
                    active = st.session_state.selected_player_id == p[0]
                    st.markdown(f'<div class="{"player-active" if active else "player-row"}">', unsafe_allow_html=True)
                    if st.button(f"{'▸  ' if active else '  '}{p[1]}", key=f"yp_{p[0]}", use_container_width=True):
                        st.session_state.selected_player_id = p[0]
                        st.session_state.show_add_player = False
                        st.session_state.show_add_academy = False
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                # Add Player — clean button under each academy
                st.markdown('<div class="add-player-row">', unsafe_allow_html=True)
                if st.button("  ＋  Add Player", key=f"addp_{club}", use_container_width=True):
                    st.session_state.show_add_player = True
                    st.session_state.show_add_academy = False
                    st.session_state.add_player_club = club
                    st.session_state.selected_player_id = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        srch_e = st.text_input("se", placeholder="Search player...", label_visibility="collapsed")
        st.markdown('<div class="sidebar-section">Pro Teams <span class="pro-badge">EPL</span></div>', unsafe_allow_html=True)
        if epl_teams:
            for team in epl_teams:
                cursor.execute("SELECT id,name,position FROM epl_players WHERE team=?", (team,))
                tps = cursor.fetchall()
                filt_e = [p for p in tps if srch_e.lower() in p[1].lower()] if srch_e else tps
                if not filt_e:
                    continue
                exp_e = team in st.session_state.expanded_epl_teams or bool(srch_e)
                st.markdown('<div class="club-row">', unsafe_allow_html=True)
                if st.button(f"{'▾' if exp_e else '▸'}  {team}", key=f"et_{team}", use_container_width=True):
                    if exp_e and not srch_e:
                        st.session_state.expanded_epl_teams.remove(team)
                    elif not exp_e:
                        st.session_state.expanded_epl_teams.append(team)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                if exp_e:
                    for p in filt_e:
                        active = st.session_state.selected_epl_player_id == p[0]
                        st.markdown(f'<div class="{"player-active" if active else "player-row"}">', unsafe_allow_html=True)
                        if st.button(f"{'▸  ' if active else '  '}{p[1]}", key=f"ep_{p[0]}", use_container_width=True):
                            st.session_state.selected_epl_player_id = p[0]; st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="padding:10px 18px;font-size:11px;color:rgba(255,255,255,0.38);">Upload data in Pro Data tab</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown(f'<div class="system-info">Scout IQ·FC v1.0<br>{len(players)} Youth Players &nbsp;·&nbsp; {len(epl_teams)} Pro Teams</div>', unsafe_allow_html=True)
    st.markdown('<div class="signout-row">', unsafe_allow_html=True)
    if st.button("⎋  Sign Out", key="signout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["auth_error"] = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════
# YOUTH MODE
# ══════════════════════════════════════
if st.session_state.mode == "youth":

    # CREATE ACADEMY
    if st.session_state.get("show_add_academy"):
        st.markdown('<div class="main-header"><div class="player-name-large">New Academy</div><div class="player-meta">Create a new squad or club</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Academy Details</div>', unsafe_allow_html=True)

        academy_name = st.text_input("Academy or Club Name", placeholder="e.g. Riverside FC Academy", key="acad_name_input")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Create Academy", key="create_acad_btn"):
                if academy_name and academy_name.strip():
                    # Create a placeholder player to register the club in the system
                    # Actually just store it in session and show confirmation
                    st.session_state.pending_academy = academy_name.strip()
                    st.session_state.show_add_academy = False
                    st.session_state.show_add_player = True
                    st.session_state.add_player_club = academy_name.strip()
                    st.success(f"Academy '{academy_name}' created. Now add your first player.")
                    st.rerun()
                else:
                    st.error("Please enter an academy name.")
        with col2:
            if st.button("Cancel", key="cancel_acad"):
                st.session_state.show_add_academy = False; st.rerun()
        st.stop()

    # ADD PLAYER
    if st.session_state.get("show_add_player"):
        club_name = st.session_state.get("add_player_club", "Unknown Club")
        st.markdown(f'<div class="main-header"><div class="player-name-large">Add Player</div><div class="player-meta">{club_name}</div></div>', unsafe_allow_html=True)

        tab_manual, tab_upload = st.tabs(["Manual Entry", "Upload from Excel"])

        with tab_manual:
            st.markdown('<div class="section-title">Player Details</div>', unsafe_allow_html=True)
            with st.form("add_player_form"):
                c1,c2,c3 = st.columns(3)
                with c1:
                    p_name = st.text_input("Full Name *")
                    p_pos = st.selectbox("Position", ["Striker","Right Winger","Left Winger","Attacking Midfielder","Central Midfielder","Defensive Midfielder","Right Back","Left Back","Centre Back","Goalkeeper"])
                    p_dob = st.text_input("Date of Birth", placeholder="YYYY-MM-DD")
                with c2:
                    p_age = st.selectbox("Age Group", ["U13","U14","U15","U16","U17","U18"])
                    p_foot = st.selectbox("Dominant Foot", ["Right","Left"])
                    p_nat = st.text_input("Nationality")
                with c3:
                    s_date = st.text_input("Session Date", placeholder="YYYY-MM-DD")
                    s_type = st.selectbox("Session Type", ["match","training"])
                    s_mins = st.number_input("Minutes Played", 0, 120, 90)

                st.markdown("**Session Metrics**")
                sc1,sc2,sc3,sc4 = st.columns(4)
                with sc1:
                    s_dist = st.number_input("Distance (km)", 0.0, 15.0, 8.0, 0.1)
                    s_spr = st.number_input("Sprints", 0, 60, 12)
                    s_spd = st.number_input("Top Speed km/h", 0.0, 40.0, 28.0, 0.1)
                with sc2:
                    s_pcomp = st.number_input("Passes Completed", 0, 120, 30)
                    s_patt = st.number_input("Passes Attempted", 0, 120, 38)
                    s_drib = st.number_input("Dribbles Completed", 0, 30, 4)
                with sc3:
                    s_def = st.number_input("Defensive Actions", 0, 40, 6)
                    s_goals = st.number_input("Goals", 0, 10, 0)
                    s_ast = st.number_input("Assists", 0, 10, 0)
                with sc4:
                    s_chances = st.number_input("Chances Created", 0, 15, 1)
                    s_tack = st.number_input("Tackles Won", 0, 25, 3)
                    s_coach = st.slider("Coachability", 1, 10, 7)
                    s_att_s = st.slider("Attitude", 1, 10, 7)
                    s_cons = st.slider("Consistency", 1, 10, 7)

                s_notes = st.text_area("Coach Notes", placeholder="Observations from this session...")
                submitted = st.form_submit_button("Add Player")

                if submitted:
                    if not p_name or not p_name.strip():
                        st.error("Player name is required.")
                    else:
                        cursor.execute("SELECT id FROM players WHERE name=?", (p_name.strip(),))
                        ex = cursor.fetchone()
                        if ex:
                            new_pid = ex[0]
                        else:
                            cursor.execute("INSERT INTO players (name,date_of_birth,position,club,dominant_foot,age_group,nationality) VALUES (?,?,?,?,?,?,?)",
                                (p_name.strip(), p_dob, p_pos, club_name, p_foot, p_age, p_nat))
                            conn.commit()
                            new_pid = cursor.lastrowid
                        cursor.execute("""INSERT INTO sessions (player_id,session_date,session_type,minutes_played,distance_covered_km,sprint_count,top_speed_kmh,passes_completed,passes_attempted,dribbles_completed,defensive_actions,goals,assists,chances_created,tackles_won,coachability_rating,attitude_score,consistency_rating,coach_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (new_pid,s_date,s_type,s_mins,s_dist,s_spr,s_spd,s_pcomp,s_patt,s_drib,s_def,s_goals,s_ast,s_chances,s_tack,s_coach,s_att_s,s_cons,s_notes))
                        conn.commit()
                        st.session_state.selected_player_id = new_pid
                        st.session_state.show_add_player = False
                        st.success(f"{p_name} added successfully.")
                        st.rerun()

        with tab_upload:
            st.markdown('<div class="upload-banner"><p style="font-size:13px;font-weight:600;color:#1a3a8a;margin-bottom:6px;">Upload Excel to add players to this academy</p><p style="font-size:12px;color:#4a5880;margin:0;">Use the same column format as Players.xlsx. Each row is one session. Multiple rows with the same player name will be added as separate sessions.</p></div>', unsafe_allow_html=True)
            up_file = st.file_uploader("Upload Excel", type=["xlsx"], key="player_upload", label_visibility="collapsed")
            if up_file:
                try:
                    df_up = pd.read_excel(up_file)
                    st.success(f"{len(df_up)} rows detected")
                    st.dataframe(df_up.head(3), use_container_width=True)
                    if st.button("Import All", key="import_manual"):
                        imported = 0
                        for _, row in df_up.iterrows():
                            try:
                                pname = str(row.get("name","")).strip()
                                if not pname or pname=="nan": continue
                                cursor.execute("SELECT id FROM players WHERE name=?", (pname,))
                                ex = cursor.fetchone()
                                if ex:
                                    new_pid = ex[0]
                                else:
                                    cursor.execute("INSERT INTO players (name,date_of_birth,position,club,dominant_foot,age_group,nationality) VALUES (?,?,?,?,?,?,?)",
                                        (pname, str(row.get("date_of_birth",""))[:10], str(row.get("position","")),
                                         club_name, str(row.get("dominant_foot","Right")),
                                         str(row.get("age_group","U16")), str(row.get("nationality",""))))
                                    conn.commit(); new_pid = cursor.lastrowid

                                def gv(col, default=0, fl=False):
                                    try:
                                        v=row.get(col,default)
                                        if pd.isna(v): return default
                                        return float(v) if fl else int(float(v))
                                    except: return default

                                cursor.execute("""INSERT INTO sessions (player_id,session_date,session_type,minutes_played,distance_covered_km,sprint_count,top_speed_kmh,passes_completed,passes_attempted,dribbles_completed,defensive_actions,goals,assists,chances_created,tackles_won,coachability_rating,attitude_score,consistency_rating,coach_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                    (new_pid,str(row.get("session_date",""))[:10],str(row.get("session_type","match")),gv("minutes_played"),gv("distance_covered_km",0,True),gv("sprint_count"),gv("top_speed_kmh",0,True),gv("passes_completed"),gv("passes_attempted"),gv("dribbles_completed"),gv("defensive_actions"),gv("goals"),gv("assists"),gv("chances_created"),gv("tackles_won"),gv("coachability_rating"),gv("attitude_score"),gv("consistency_rating"),str(row.get("coach_notes",""))))
                                conn.commit(); imported += 1
                            except Exception:
                                continue
                        st.success(f"Imported {imported} records to {club_name}")
                        st.session_state.show_add_player = False; st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.button("Cancel", key="cancel_add"):
            st.session_state.show_add_player = False; st.rerun()
        st.stop()

    # WELCOME SCREEN
    if not st.session_state.selected_player_id:
        st.markdown('<div class="main-header"><div class="player-name-large">Scout IQ·FC</div><div class="player-meta">Youth Talent Intelligence &nbsp;&nbsp; Where Talent Is Unearthed</div></div>', unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown('<div class="welcome-card"><p style="font-size:36px;margin-bottom:12px">🏟️</p><p style="font-size:15px;font-weight:700;color:#1a3a8a;margin-bottom:8px;">Create an Academy</p><p style="font-size:12px;color:#8492b4;">Click New Academy in the sidebar to create your first squad</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="welcome-card"><p style="font-size:36px;margin-bottom:12px">👤</p><p style="font-size:15px;font-weight:700;color:#1a3a8a;margin-bottom:8px;">Add Players</p><p style="font-size:12px;color:#8492b4;">Expand any academy and click Add Player to build your roster</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="welcome-card"><p style="font-size:36px;margin-bottom:12px">📋</p><p style="font-size:15px;font-weight:700;color:#1a3a8a;margin-bottom:8px;">Generate Reports</p><p style="font-size:12px;color:#8492b4;">Select a player to view their dashboard and generate AI reports</p></div>', unsafe_allow_html=True)
        st.stop()

    # PLAYER DASHBOARD
    pid = st.session_state.selected_player_id
    cursor.execute("SELECT * FROM players WHERE id=?", (pid,))
    pl = cursor.fetchone()
    if not pl:
        st.session_state.selected_player_id = None; st.rerun()

    cursor.execute("SELECT * FROM sessions WHERE player_id=? ORDER BY session_date", (pid,))
    sess = cursor.fetchall()
    cursor.execute("SELECT * FROM reports WHERE player_id=? ORDER BY created_at DESC LIMIT 1", (pid,))
    rep = cursor.fetchone()

    st.markdown(f'<div class="main-header"><div class="player-name-large">{pl[1]}</div><div class="player-meta">{pl[4]} &nbsp;&nbsp; {pl[6]} &nbsp;&nbsp; {pl[3]} &nbsp;&nbsp; {pl[7] or ""}</div></div>', unsafe_allow_html=True)

    sc = len(sess)
    avg_d = round(sum(s[5] for s in sess)/sc,1) if sc else 0
    avg_sp = round(sum(s[6] for s in sess)/sc,1) if sc else 0
    tg = sum(s[12] for s in sess); ta = sum(s[13] for s in sess)
    tpc = sum(s[8] for s in sess); tpa = sum(s[9] for s in sess)
    pp = round(tpc/tpa*100) if tpa>0 else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col,lbl,val in [(c1,"Sessions",sc),(c2,"Avg Distance",f"{avg_d} km"),(c3,"Avg Sprints",avg_sp),(c4,"Pass Rate",f"{pp}%"),(c5,"Goals",tg),(c6,"Assists",ta)]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-card-label">{lbl}</div><div class="metric-card-value">{val}</div></div>', unsafe_allow_html=True)

    # ADD MORE DATA button
    st.markdown('<div class="section-title">Session History</div>', unsafe_allow_html=True)
    add_data_key = f"show_add_data_{pid}"
    if add_data_key not in st.session_state:
        st.session_state[add_data_key] = False

    col_title, col_btn = st.columns([6, 1])
    with col_btn:
        st.markdown("""
        <style>
        div[data-testid="column"]:last-child .stButton > button {
            background: #eef2ff !important; color: #1a3a8a !important;
            border: 1.5px solid #c7d2fe !important; border-radius: 6px !important;
            font-size: 10px !important; font-weight: 700 !important;
            letter-spacing: 0.5px !important; padding: 4px 10px !important;
            box-shadow: none !important; white-space: nowrap !important;
            width: auto !important; margin-top: 36px !important;
        }
        div[data-testid="column"]:last-child .stButton > button:hover {
            background: #e0e7ff !important; border-color: #818cf8 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("＋ Session", key=f"add_sess_{pid}"):
            st.session_state[add_data_key] = not st.session_state[add_data_key]
            st.rerun()

    if st.session_state[add_data_key]:
        with st.expander("New Session", expanded=True):
            with st.form(f"add_session_form_{pid}"):
                st.markdown("**New Session**")
                fc1,fc2,fc3 = st.columns(3)
                with fc1:
                    ns_date = st.text_input("Session Date", placeholder="YYYY-MM-DD", key=f"ns_date_{pid}")
                    ns_type = st.selectbox("Type", ["match","training"], key=f"ns_type_{pid}")
                    ns_mins = st.number_input("Minutes", 0, 120, 90, key=f"ns_mins_{pid}")
                with fc2:
                    ns_dist = st.number_input("Distance km", 0.0, 15.0, 8.0, 0.1, key=f"ns_dist_{pid}")
                    ns_spr = st.number_input("Sprints", 0, 60, 12, key=f"ns_spr_{pid}")
                    ns_spd = st.number_input("Top Speed", 0.0, 40.0, 28.0, 0.1, key=f"ns_spd_{pid}")
                    ns_pcomp = st.number_input("Passes Completed", 0, 120, 30, key=f"ns_pc_{pid}")
                    ns_patt = st.number_input("Passes Attempted", 0, 120, 38, key=f"ns_pa_{pid}")
                with fc3:
                    ns_goals = st.number_input("Goals", 0, 10, 0, key=f"ns_g_{pid}")
                    ns_ast = st.number_input("Assists", 0, 10, 0, key=f"ns_a_{pid}")
                    ns_def = st.number_input("Defensive Actions", 0, 40, 6, key=f"ns_def_{pid}")
                    ns_tack = st.number_input("Tackles Won", 0, 25, 3, key=f"ns_tack_{pid}")
                    ns_coach = st.slider("Coachability", 1, 10, 7, key=f"ns_coach_{pid}")
                    ns_att = st.slider("Attitude", 1, 10, 7, key=f"ns_att_{pid}")
                    ns_cons = st.slider("Consistency", 1, 10, 7, key=f"ns_cons_{pid}")
                ns_notes = st.text_area("Coach Notes", key=f"ns_notes_{pid}")

                # Excel upload option inside the form
                st.markdown("**Or upload Excel with multiple sessions**")
                ns_excel = st.file_uploader("Upload sessions Excel", type=["xlsx"], key=f"ns_excel_{pid}", label_visibility="collapsed")

                add_submitted = st.form_submit_button("Save Session")
                if add_submitted:
                    if ns_excel is not None:
                        try:
                            df_ns = pd.read_excel(ns_excel)
                            added = 0
                            for _, row in df_ns.iterrows():
                                def gv2(col, default=0, fl=False):
                                    try:
                                        v=row.get(col,default)
                                        if pd.isna(v): return default
                                        return float(v) if fl else int(float(v))
                                    except: return default
                                cursor.execute("""INSERT INTO sessions (player_id,session_date,session_type,minutes_played,distance_covered_km,sprint_count,top_speed_kmh,passes_completed,passes_attempted,dribbles_completed,defensive_actions,goals,assists,chances_created,tackles_won,coachability_rating,attitude_score,consistency_rating,coach_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                    (pid,str(row.get("session_date",""))[:10],str(row.get("session_type","match")),gv2("minutes_played"),gv2("distance_covered_km",0,True),gv2("sprint_count"),gv2("top_speed_kmh",0,True),gv2("passes_completed"),gv2("passes_attempted"),gv2("dribbles_completed"),gv2("defensive_actions"),gv2("goals"),gv2("assists"),gv2("chances_created"),gv2("tackles_won"),gv2("coachability_rating"),gv2("attitude_score"),gv2("consistency_rating"),str(row.get("coach_notes",""))))
                                conn.commit(); added += 1
                            st.session_state[add_data_key] = False
                            st.success(f"Added {added} sessions from Excel. Dashboard updated.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error reading Excel: {e}")
                    elif ns_date:
                        cursor.execute("""INSERT INTO sessions (player_id,session_date,session_type,minutes_played,distance_covered_km,sprint_count,top_speed_kmh,passes_completed,passes_attempted,dribbles_completed,defensive_actions,goals,assists,chances_created,tackles_won,coachability_rating,attitude_score,consistency_rating,coach_notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (pid,ns_date,ns_type,ns_mins,ns_dist,ns_spr,ns_spd,ns_pcomp,ns_patt,0,ns_def,ns_goals,ns_ast,0,ns_tack,ns_coach,ns_att,ns_cons,ns_notes))
                        conn.commit()
                        st.session_state[add_data_key] = False
                        st.success("Session added. Dashboard updated.")
                        st.rerun()
                    else:
                        st.error("Enter a session date or upload an Excel file.")

    if sess:
        rows = [{"Date":str(s[2])[:10],"Type":s[3].title(),"Mins":s[4],"Distance":f"{s[5]} km","Sprints":s[6],"Top Speed":f"{s[7]} km/h","Pass %":f"{round(s[8]/s[9]*100) if s[9]>0 else 0}%","Goals":s[12],"Assists":s[13],"Chances":s[14],"Tackles":s[15],"Coachability":f"{s[16]}/10","Attitude":f"{s[17]}/10"} for s in sess]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">Performance Charts</div>', unsafe_allow_html=True)
        dates = [str(s[2])[:10] for s in sess]
        c1,c2 = st.columns(2)
        with c1:
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=dates,y=[s[5] for s in sess],mode='lines+markers',line=dict(color='#1a3a8a',width=2.5),marker=dict(size=7),fill='tozeroy',fillcolor='rgba(26,58,138,0.08)'))
            fig.update_layout(title=dict(text='Distance per Session',font=dict(size=13,color='#0a0f2c'),x=0),paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=20,r=20,t=40,b=20),xaxis=dict(showgrid=False,type='category'),yaxis=dict(gridcolor='#f0f2f8',title='km'),height=260,showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig=go.Figure()
            fig.add_trace(go.Bar(x=dates,y=[s[6] for s in sess],marker_color='#1e4db7',opacity=0.85))
            fig.update_layout(title=dict(text='Sprint Count',font=dict(size=13,color='#0a0f2c'),x=0),paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=20,r=20,t=40,b=20),xaxis=dict(showgrid=False,type='category'),yaxis=dict(gridcolor='#f0f2f8'),height=260,showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        c3,c4 = st.columns(2)
        with c3:
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=dates,y=[round(s[8]/s[9]*100) if s[9]>0 else 0 for s in sess],mode='lines+markers',line=dict(color='#2952a3',width=2.5),marker=dict(size=7),fill='tozeroy',fillcolor='rgba(41,82,163,0.07)'))
            fig.update_layout(title=dict(text='Pass Accuracy %',font=dict(size=13,color='#0a0f2c'),x=0),paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=20,r=20,t=40,b=20),xaxis=dict(showgrid=False,type='category'),yaxis=dict(gridcolor='#f0f2f8',title='%',range=[0,100]),height=260,showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c4:
            cats=['Distance','Sprints','Passing','Attacking','Defending','Attitude']
            maxv=[12,25,100,10,20,10]
            avgv=[avg_d,avg_sp,pp,round((tg+ta+sum(s[14] for s in sess))/sc,1),round(sum(s[15] for s in sess)/sc,1),round(sum(s[17] for s in sess)/sc,1)]
            norm=[min(round((v/m)*10,1),10) for v,m in zip(avgv,maxv)]
            fig=go.Figure()
            fig.add_trace(go.Scatterpolar(r=norm+[norm[0]],theta=cats+[cats[0]],fill='toself',fillcolor='rgba(26,58,138,0.15)',line=dict(color='#1a3a8a',width=2),marker=dict(size=6)))
            fig.update_layout(title=dict(text='Performance Profile',font=dict(size=13,color='#0a0f2c'),x=0),polar=dict(radialaxis=dict(visible=True,range=[0,10],gridcolor='#e8ecf8'),angularaxis=dict(gridcolor='#e8ecf8'),bgcolor='white'),paper_bgcolor='white',margin=dict(l=20,r=20,t=40,b=20),height=260,showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Development Indicators</div>', unsafe_allow_html=True)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=dates,y=[s[16] for s in sess],name='Coachability',line=dict(color='#1a3a8a',width=2),mode='lines+markers',marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=dates,y=[s[17] for s in sess],name='Attitude',line=dict(color='#1e4db7',width=2,dash='dash'),mode='lines+markers',marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=dates,y=[s[18] for s in sess],name='Consistency',line=dict(color='#6b86c8',width=2,dash='dot'),mode='lines+markers',marker=dict(size=6)))
        fig.update_layout(title=dict(text='Attitude and Development Scores',font=dict(size=13,color='#0a0f2c'),x=0),paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=20,r=20,t=40,b=20),xaxis=dict(showgrid=False,type='category'),yaxis=dict(gridcolor='#f0f2f8',range=[0,10],title='Score /10'),legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1),height=260)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Player Media</div>', unsafe_allow_html=True)
    pc,vc = st.columns(2)
    with pc:
        st.markdown('<p style="font-size:10px;font-weight:700;color:#8492b4;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Player Photo</p>', unsafe_allow_html=True)
        photo=st.file_uploader("photo",type=["jpg","jpeg","png"],key=f"ph_{pid}",label_visibility="collapsed")
        if photo: st.image(photo, width=200)
        else: st.markdown('<div style="background:#fff;border:1.5px dashed #dde2f0;border-radius:8px;padding:24px;text-align:center;color:#8492b4;font-size:12px;">Upload player photo</div>', unsafe_allow_html=True)
    with vc:
        st.markdown('<p style="font-size:10px;font-weight:700;color:#8492b4;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Match Footage</p>', unsafe_allow_html=True)
        video=st.file_uploader("video",type=["mp4","mov","avi"],key=f"vi_{pid}",label_visibility="collapsed")
        if video: st.video(video)
        else: st.markdown('<div style="background:#fff;border:1.5px dashed #dde2f0;border-radius:8px;padding:24px;text-align:center;color:#8492b4;font-size:12px;">Upload match footage</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Scouting Report</div>', unsafe_allow_html=True)
    if rep:
        show_report(rep[2], pid, pl[1], f"{pl[4]}  |  {pl[6]}  |  {pl[3]}", is_pro=False)
    else:
        st.info("No report generated yet. Add session data then generate below.")
        st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
        if st.button("Generate AI Scouting Report", key=f"gen_youth_{pid}"):
            if not sess:
                st.warning("Add at least one session before generating a report.")
            else:
                cursor.execute("SELECT * FROM sessions WHERE player_id=? ORDER BY session_date", (pid,))
                fresh_sess = cursor.fetchall()
                with st.spinner("Generating report — this takes about 30 seconds..."):
                    rtext = ai_report(build_youth_prompt(pl, fresh_sess))
                    cursor.execute("INSERT INTO reports (player_id,report_text) VALUES (?,?)", (pid, rtext))
                    conn.commit(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════
# PRO DATA MODE
# ══════════════════════════════════════
else:
    st.markdown('<div class="main-header"><div class="player-name-large">Pro Data</div><div class="player-meta">Professional Match Analysis &nbsp;&nbsp; Real Performance Data</div></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Upload Data", "Player Report", "Team Analysis"])

    with tab1:
        st.markdown('<div class="section-title">Upload Professional Data</div>', unsafe_allow_html=True)
        st.markdown("""<div class="upload-banner">
        <p style="font-size:13px;font-weight:600;color:#1a3a8a;margin-bottom:6px;">How to get EPL data:</p>
        <p style="font-size:12px;color:#4a5880;line-height:1.9;margin:0;">
        Option 1 — Use the ScoutIQ_EPL_ManUtd_Arsenal.xlsx file already provided<br>
        Option 2 — Go to fbref.com, find a team, Share and Export, Get table as CSV, save as .xlsx<br>
        Option 3 — Export from Sofascore, WhoScored or any stats platform
        </p></div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload file", type=["xlsx","csv"], label_visibility="collapsed")
        if uploaded:
            try:
                df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
                st.success(f"{len(df)} rows loaded")
                st.dataframe(df.head(3), use_container_width=True)
                team_name = st.text_input("Team name", placeholder="e.g. Manchester United")
                cols = ["(skip)"] + list(df.columns)
                with st.expander("Map your columns"):
                    cc1,cc2,cc3 = st.columns(3)
                    with cc1:
                        nc=st.selectbox("Player name",cols,key="nc"); poc=st.selectbox("Position",cols,key="poc")
                        agc=st.selectbox("Age",cols,key="agc"); natc=st.selectbox("Nationality",cols,key="natc")
                    with cc2:
                        mc=st.selectbox("Minutes",cols,key="mc"); gc=st.selectbox("Goals",cols,key="gc")
                        ac=st.selectbox("Assists",cols,key="ac"); shc=st.selectbox("Shots",cols,key="shc")
                        sotc=st.selectbox("Shots on target",cols,key="sotc")
                    with cc3:
                        xgc=st.selectbox("xG",cols,key="xgc"); xac=st.selectbox("xA",cols,key="xac")
                        pcc=st.selectbox("Passes completed",cols,key="pcc"); tc=st.selectbox("Tackles",cols,key="tc")
                        gwc=st.selectbox("Gameweek",cols,key="gwc"); oppc=st.selectbox("Opponent",cols,key="oppc")
                        ratc=st.selectbox("Rating",cols,key="ratc")

                if st.button("Import Data", key="imp"):
                    if not team_name: st.error("Enter a team name")
                    elif nc=="(skip)": st.error("Map the player name column")
                    else:
                        def sv(row, col, default=0, fl=False):
                            if col=="(skip)": return default
                            try:
                                v=row.get(col,default)
                                if pd.isna(v): return default
                                return float(v) if fl else int(float(v))
                            except: return default
                        imported=0
                        for _,row in df.iterrows():
                            pname=str(row.get(nc,"")).strip()
                            if not pname or pname=="nan": continue
                            cursor.execute("SELECT id FROM epl_players WHERE name=? AND team=?",(pname,team_name))
                            ex=cursor.fetchone()
                            if ex: epid=ex[0]
                            else:
                                cursor.execute("INSERT INTO epl_players (name,team,position,nationality,age) VALUES (?,?,?,?,?)",
                                    (pname,team_name,str(row.get(poc,"")) if poc!="(skip)" else "",str(row.get(natc,"")) if natc!="(skip)" else "",sv(row,agc)))
                                conn.commit(); epid=cursor.lastrowid
                            cursor.execute("INSERT INTO epl_sessions (player_id,gameweek,opponent,minutes_played,goals,assists,shots,shots_on_target,xg,xa,passes_completed,tackles_won,rating) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                (epid,sv(row,gwc),str(row.get(oppc,"")) if oppc!="(skip)" else "",sv(row,mc),sv(row,gc),sv(row,ac),sv(row,shc),sv(row,sotc),sv(row,xgc,0,True),sv(row,xac,0,True),sv(row,pcc),sv(row,tc),sv(row,ratc,0,True)))
                            conn.commit(); imported+=1
                        st.success(f"Imported {imported} records for {team_name}"); st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        if not st.session_state.selected_epl_player_id:
            st.markdown('<div class="no-select"><p style="font-size:38px;margin-bottom:14px">⚽</p><p>Select a player from the sidebar or upload data first</p></div>', unsafe_allow_html=True)
        else:
            epid=st.session_state.selected_epl_player_id
            cursor.execute("SELECT * FROM epl_players WHERE id=?",(epid,)); ep=cursor.fetchone()
            cursor.execute("SELECT * FROM epl_sessions WHERE player_id=? ORDER BY gameweek",(epid,)); eps=cursor.fetchall()
            cursor.execute("SELECT * FROM epl_reports WHERE player_id=? ORDER BY created_at DESC LIMIT 1",(epid,)); epr=cursor.fetchone()

            st.markdown(f'<div class="main-header"><div class="player-name-large">{ep[1]}</div><div class="player-meta">{ep[3] or ""} &nbsp;&nbsp; {ep[2]} &nbsp;&nbsp; Age {ep[5] or "?"}</div></div>', unsafe_allow_html=True)

            if eps:
                tm=sum(sg(s,6) for s in eps); tg=sum(sg(s,7) for s in eps); ta=sum(sg(s,8) for s in eps)
                txg=round(sum(float(sg(s,11,0)) for s in eps),2); tsh=sum(sg(s,9) for s in eps); tp=sum(sg(s,13) for s in eps)
                c1,c2,c3,c4,c5,c6=st.columns(6)
                for col,lbl,val in [(c1,"Minutes",tm),(c2,"Goals",tg),(c3,"Assists",ta),(c4,"xG",txg),(c5,"Shots",tsh),(c6,"Passes",tp)]:
                    with col: st.markdown(f'<div class="metric-card"><div class="metric-card-label">{lbl}</div><div class="metric-card-value">{val}</div></div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">Match Data</div>', unsafe_allow_html=True)
                mrows=[{"GW":sg(s,2),"Opponent":sg(s,3,""),"Mins":sg(s,6),"Goals":sg(s,7),"Assists":sg(s,8),"Shots":sg(s,9),"xG":round(float(sg(s,11,0)),2),"Passes":sg(s,13),"Tackles":sg(s,21),"Rating":sg(s,26)} for s in eps]
                st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

                st.markdown('<div class="section-title">Performance Charts</div>', unsafe_allow_html=True)
                gws=[f"GW{sg(s,2)}" for s in eps]
                cc1,cc2=st.columns(2)
                with cc1:
                    fig=go.Figure()
                    fig.add_trace(go.Bar(x=gws,y=[sg(s,7) for s in eps],name='Goals',marker_color='#1a3a8a',opacity=0.85))
                    fig.add_trace(go.Bar(x=gws,y=[sg(s,8) for s in eps],name='Assists',marker_color='#6b86c8',opacity=0.85))
                    fig.update_layout(title=dict(text='Goals and Assists',font=dict(size=13,color='#0a0f2c'),x=0),barmode='group',paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=20,r=20,t=40,b=20),xaxis=dict(showgrid=False,type='category'),yaxis=dict(gridcolor='#f0f2f8'),legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1),height=260)
                    st.plotly_chart(fig, use_container_width=True)
                with cc2:
                    fig=go.Figure()
                    fig.add_trace(go.Scatter(x=gws,y=[round(float(sg(s,11,0)),2) for s in eps],name='xG',line=dict(color='#1a3a8a',width=2.5),mode='lines+markers',marker=dict(size=7)))
                    fig.add_trace(go.Scatter(x=gws,y=[sg(s,7) for s in eps],name='Goals',line=dict(color='#c0392b',width=2,dash='dash'),mode='lines+markers',marker=dict(size=7)))
                    fig.update_layout(title=dict(text='xG vs Actual Goals',font=dict(size=13,color='#0a0f2c'),x=0),paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=20,r=20,t=40,b=20),xaxis=dict(showgrid=False,type='category'),yaxis=dict(gridcolor='#f0f2f8'),legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1),height=260)
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-title">Performance Audit Report</div>', unsafe_allow_html=True)
            if epr:
                show_report(epr[2], epid, ep[1], f"{ep[3] or ''}  |  {ep[2]}", is_pro=True)
            else:
                st.info("No report yet for this player.")
                st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
                if st.button("Generate Performance Audit", key="gen_epl"):
                    if not eps:
                        st.warning("No match data found.")
                    else:
                        stext="\n".join([f"GW{sg(s,2)} vs {sg(s,3,'Unknown')}: {sg(s,6)} mins, {sg(s,7)} goals, {sg(s,8)} assists, {sg(s,9)} shots, xG {round(float(sg(s,11,0)),2)}, {sg(s,13)} passes, {sg(s,21)} tackles, rating {sg(s,26)}" for s in eps])
                        prompt=f"""You are the chief scout at a Premier League club writing a professional performance audit for the sporting director and head coach. Full sentences only. No bullet points. No dashes. Every observation backed by a specific number. Maximum 4 pages.

PLAYER: {ep[1]}
TEAM: {ep[2]}
POSITION: {ep[3] or 'Unknown'}
AGE: {ep[5] or 'Unknown'}

MATCH DATA ({len(eps)} gameweeks):
{stext}

Write a structured performance audit:

EXECUTIVE SUMMARY — 4 sentences: standout quality with data, biggest limitation with data, season trajectory, transfer verdict.

1. SEASON PERFORMANCE RATING — Score out of 10 with two data point justification.
2. GENERAL PERFORMANCE AUDIT — All metrics across all gameweeks. Per 90 rates. Consistency assessment. At, above or below standard verdict.
3. TECHNICAL AND CREATIVE QUALITY — Passing contribution, best technical gameweek, decision making conclusions.
4. DEFENSIVE CONTRIBUTION — Tackles and pressing. Strength, neutral or liability verdict.
5. CONSISTENCY AND AVAILABILITY — Minutes and performance variance. Reliability verdict.
6. BEST POSITION AND TACTICAL FIT — Best position from data. One alternative role suggestion.
7. THREE STANDOUT PERFORMANCES — Three gameweeks showing peak ability with context.
8. SEASON TRAJECTORY — Improving, plateauing or declining with evidence. Season end prediction.
9. INJURY AND FITNESS ASSESSMENT — Availability concerns. Short term risk and projection.
10. LEADERSHIP ASSESSMENT — Consistency under pressure. Captaincy suitability verdict.
11. TRANSFER INTELLIGENCE — Realistic fee range with three metric justifications. Best fit club. One negotiation observation.
12. CHIEF SCOUT VERDICT — What this player is now. What signing them gives. What the risk is. Final recommendation.

No bullet points. No dashes. No markdown. Authoritative, direct and precise."""
                        with st.spinner("Generating performance audit..."):
                            rtext=ai_report(prompt)
                            cursor.execute("INSERT INTO epl_reports (player_id,report_text) VALUES (?,?)",(epid,rtext))
                            conn.commit(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-title">Team Analysis</div>', unsafe_allow_html=True)
        if not epl_teams:
            st.markdown('<div class="no-select"><p style="font-size:38px;margin-bottom:14px">⚽</p><p>Upload data in the Upload Data tab first</p></div>', unsafe_allow_html=True)
        else:
            sel_team=st.selectbox("Select team",epl_teams,key="st")
            if sel_team:
                cursor.execute("""SELECT p.name,p.position,p.age,SUM(s.minutes_played),SUM(s.goals),SUM(s.assists),ROUND(SUM(s.xg),2),SUM(s.shots),SUM(s.passes_completed),SUM(s.tackles_won),COUNT(s.id) FROM epl_players p LEFT JOIN epl_sessions s ON p.id=s.player_id WHERE p.team=? GROUP BY p.id ORDER BY SUM(s.goals) DESC""",(sel_team,))
                ts=cursor.fetchall()
                if ts:
                    cols=["Player","Position","Age","Minutes","Goals","Assists","xG","Shots","Passes","Tackles","Games"]
                    df_t=pd.DataFrame(ts,columns=cols)
                    st.dataframe(df_t,use_container_width=True,hide_index=True)
                    cc1,cc2=st.columns(2)
                    top8=df_t.nlargest(8,'Goals')
                    with cc1:
                        fig=go.Figure()
                        fig.add_trace(go.Bar(x=top8['Player'],y=top8['Goals'],marker_color='#1a3a8a',opacity=0.85))
                        fig.update_layout(title=dict(text='Goals by Player',font=dict(size=13,color='#0a0f2c'),x=0),paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=20,r=20,t=40,b=80),xaxis=dict(showgrid=False,tickangle=45),yaxis=dict(gridcolor='#f0f2f8'),height=320,showlegend=False)
                        st.plotly_chart(fig,use_container_width=True)
                    with cc2:
                        fig=go.Figure()
                        fig.add_trace(go.Bar(x=top8['Player'],y=top8['xG'],name='xG',marker_color='#2952a3',opacity=0.85))
                        fig.add_trace(go.Bar(x=top8['Player'],y=top8['Goals'],name='Goals',marker_color='#1a3a8a',opacity=0.6))
                        fig.update_layout(title=dict(text='xG vs Goals',font=dict(size=13,color='#0a0f2c'),x=0),barmode='group',paper_bgcolor='white',plot_bgcolor='white',margin=dict(l=20,r=20,t=40,b=80),xaxis=dict(showgrid=False,tickangle=45),yaxis=dict(gridcolor='#f0f2f8'),height=320,legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1))
                        st.plotly_chart(fig,use_container_width=True)
                    st.markdown('<div class="section-title">Generate Team Report</div>', unsafe_allow_html=True)
                    if st.button("Generate Team Analysis",key="gta"):
                        summary=df_t.to_string(index=False)
                        prompt=f"""You are a Premier League performance analyst writing a team report for a sporting director.
TEAM: {sel_team}
SQUAD STATS:
{summary}
Write: 1. TEAM OVERVIEW, 2. GENERAL PERFORMANCE AUDIT, 3. SQUAD DEPTH, 4. KEY PLAYERS (top 3 with data), 5. UNDERPERFORMERS, 6. TACTICAL OBSERVATIONS, 7. TRANSFER RECOMMENDATIONS, 8. OVERALL ASSESSMENT.
No bullet points. Full sentences. Specific players and numbers throughout."""
                        with st.spinner("Generating..."):
                            rtext=ai_report(prompt)
                            html='<div class="report-block">'
                            for line in rtext.split('\n'):
                                line=line.strip()
                                if not line: html+='<div style="height:8px"></div>'
                                elif line[0].isdigit() and '.' in line[:3]: html+=f'<div class="report-section-title">{line}</div>'
                                else:
                                    clean=line.replace('**','').replace('--','').replace('- ','').replace('#','')
                                    html+=f'<div class="report-body">{clean}</div>'
                            html+='</div>'
                            st.markdown(html,unsafe_allow_html=True)
