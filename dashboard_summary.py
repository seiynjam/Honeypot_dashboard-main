import streamlit as st
import pandas as pd
import re
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import xlsxwriter
import time

# Page Configuration
st.set_page_config(
    page_title="🤖 Bot Performance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    /* Import Google Fonts - Sarabun สำหรับภาษาไทย + Sora สำหรับหัวข้อ */
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Sora:wght@600;700;800&display=swap');

    /* ── CSS Variables ─────────────────────────── */
    :root {
        --brand-purple:  #667eea;
        --brand-violet:  #764ba2;
        --brand-pink:    #f093fb;
        --brand-red:     #f5576c;
        --brand-cyan:    #4facfe;
        --brand-teal:    #11998e;
        --surface:       #ffffff;
        --surface-soft:  #f4f6ff;
        --border:        #dde3ff;
        --text-primary:  #1a1d3a;
        --text-secondary:#4a4f72;
        --text-muted:    #8890b5;
        --shadow-sm:     0 2px 8px rgba(102,126,234,0.10);
        --shadow-md:     0 6px 20px rgba(102,126,234,0.15);
        --shadow-lg:     0 12px 36px rgba(102,126,234,0.20);
        --radius-sm:     10px;
        --radius-md:     16px;
        --radius-lg:     22px;
    }

    /* ── Global ────────────────────────────────── */
    html, body, .stApp {
        font-family: 'Sarabun', sans-serif;
        font-size: 15px;
        color: var(--text-primary);
        background: linear-gradient(145deg, #eef0ff 0%, #f8f5ff 50%, #f0f7ff 100%);
    }

    /* ── Main Container ────────────────────────── */
    .main .block-container {
        padding: 2rem 2.5rem 3rem;
        background: var(--surface);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-lg);
        margin: 1rem auto;
        max-width: 1400px;
    }

    /* ── Page Title ────────────────────────────── */
    .main-title {
        font-family: 'Sora', sans-serif;
        background: linear-gradient(135deg, var(--brand-purple) 0%, var(--brand-violet) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.6rem;
        font-weight: 800;
        text-align: center;
        margin: 0.5rem 0 2rem;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }

    /* ── Section Headers ───────────────────────── */
    .section-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        background: linear-gradient(90deg, var(--brand-purple), var(--brand-violet));
        color: #ffffff;
        padding: 0.85rem 1.8rem;
        border-radius: var(--radius-md);
        font-family: 'Sora', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 0.2px;
        margin: 2.2rem 0 1rem;
        box-shadow: var(--shadow-md);
    }

    /* ── Metric Cards ──────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, #7b5ea7 0%, #5e43c3 100%);
        padding: 1.4rem 1.6rem;
        border-radius: var(--radius-md);
        color: #ffffff;
        text-align: center;
        box-shadow: var(--shadow-md);
        margin: 0.75rem 0;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        border: 1px solid rgba(255,255,255,0.15);
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }

    .metric-card h3 {
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        opacity: 0.85;
        margin-bottom: 0.4rem;
    }

    .metric-card h2 {
        font-family: 'Sora', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        margin: 0.2rem 0;
        line-height: 1.1;
    }

    .metric-card p {
        font-size: 0.8rem;
        opacity: 0.75;
        margin: 0;
    }

    .performance-card {
        background: linear-gradient(135deg, #3a7bd5 0%, #2563c7 100%);
        padding: 1.2rem 1.4rem;
        border-radius: var(--radius-md);
        color: #ffffff;
        text-align: center;
        box-shadow: var(--shadow-md);
        margin: 0.75rem 0;
        border: 1px solid rgba(255,255,255,0.15);
    }

    .performance-card h4 {
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        opacity: 0.8;
        margin-bottom: 0.3rem;
    }

    .performance-card p {
        font-family: 'Sora', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0;
    }

    /* ── Buttons ───────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, var(--brand-purple) 0%, var(--brand-violet) 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.6rem 1.6rem !important;
        font-family: 'Sarabun', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.2px !important;
        transition: all 0.25s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
        opacity: 0.92 !important;
    }

    /* ── Alerts ────────────────────────────────── */
    .stAlert > div {
        border-radius: var(--radius-sm) !important;
        border-left: 4px solid var(--brand-purple) !important;
        font-family: 'Sarabun', sans-serif !important;
        font-size: 0.95rem !important;
    }

    /* ── Data Tables ───────────────────────────── */
    .stDataFrame {
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
        border: 1px solid var(--border) !important;
    }

    .stDataFrame thead tr th {
        background: var(--surface-soft) !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.3px !important;
        border-bottom: 2px solid var(--border) !important;
        padding: 0.75rem 1rem !important;
    }

    .stDataFrame tbody tr td {
        font-size: 0.9rem !important;
        color: var(--text-primary) !important;
        padding: 0.6rem 1rem !important;
        border-bottom: 1px solid #f0f2ff !important;
    }

    .stDataFrame tbody tr:hover td {
        background: #f7f8ff !important;
    }

    /* ── Sidebar ───────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9ff 0%, #f0f2ff 100%) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: var(--text-primary) !important;
        font-family: 'Sarabun', sans-serif !important;
        font-size: 0.93rem !important;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: var(--text-primary) !important;
        font-family: 'Sora', sans-serif !important;
    }

    /* ── Number / Text Inputs ──────────────────── */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        border-radius: var(--radius-sm) !important;
        border: 1.5px solid var(--border) !important;
        padding: 0.55rem 0.9rem !important;
        font-family: 'Sarabun', sans-serif !important;
        font-size: 0.95rem !important;
        color: var(--text-primary) !important;
        background: var(--surface) !important;
        transition: border-color 0.2s !important;
    }

    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: var(--brand-purple) !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.15) !important;
    }

    /* ── Checkbox ──────────────────────────────── */
    .stCheckbox label span {
        font-size: 0.93rem !important;
        color: var(--text-primary) !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* ── Chart Container ───────────────────────── */
    .chart-container {
        background: var(--surface);
        border-radius: var(--radius-md);
        padding: 1.25rem 1.5rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
        margin: 1rem 0;
    }

    /* ── Gauge Container ───────────────────────── */
    .gauge-container {
        background: linear-gradient(135deg, #ede9ff 0%, #ddd5f9 100%);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid rgba(118,75,162,0.15);
        margin: 0.75rem 0;
    }

    /* ── Spinner / Write Text ──────────────────── */
    .stSpinner > div {
        border-top-color: var(--brand-purple) !important;
    }

    p, .stMarkdown p {
        color: var(--text-secondary);
        font-size: 0.93rem;
        line-height: 1.65;
    }

    /* ── Status Indicators ─────────────────────── */
    .status-good    { color: #059669; font-weight: 700; font-size: 0.95rem; }
    .status-warning { color: #d97706; font-weight: 700; font-size: 0.95rem; }
    .status-error   { color: #dc2626; font-weight: 700; font-size: 0.95rem; }

    /* ── Subtle fade-in for charts ─────────────── */
    .stPlotlyChart {
        animation: fadeUp 0.45s ease both;
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── st.write / description text ──────────── */
    .stMarkdown > div > p {
        color: var(--text-secondary);
        font-size: 0.93rem;
        margin-bottom: 0.8rem;
    }

    /* ── Download button override ──────────────── */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, var(--brand-teal) 0%, #38ef7d 100%) !important;
        color: #fff !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.7rem 2rem !important;
        box-shadow: 0 6px 18px rgba(17,153,142,0.3) !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 24px rgba(17,153,142,0.4) !important;
    }

    /* ── Sidebar Header Card ───────────────────── */
    .sidebar-header {
        background: linear-gradient(135deg, var(--brand-purple) 0%, var(--brand-violet) 100%);
        padding: 1.4rem 1.2rem 1.2rem;
        border-radius: var(--radius-md);
        text-align: center;
        margin-bottom: 1.4rem;
        box-shadow: var(--shadow-md);
    }

    .sidebar-header h2 {
        font-family: 'Sora', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: 0.3px;
    }

    /* ── Sidebar Section Label ─────────────────── */
    .sidebar-label {
        font-family: 'Sora', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: var(--text-muted);
        padding: 0.3rem 0 0.5rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 0.8rem;
    }

    /* ── Section Divider ───────────────────────── */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 0.5rem 0 1.5rem;
    }

    /* ── Description text under section header ─── */
    .section-desc {
        color: var(--text-muted);
        font-size: 0.88rem;
        text-align: center;
        margin: -0.5rem 0 1.2rem;
    }

    /* ── Bot Config panel ──────────────────────── */
    .config-panel {
        background: var(--surface-soft);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
    }

    /* ── Export panel ──────────────────────────── */
    .export-panel {
        background: linear-gradient(135deg, #f0f4ff 0%, #f7f0ff 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.6rem 2rem;
        margin: 1rem 0;
        text-align: center;
    }

    .export-panel h4 {
        font-family: 'Sora', sans-serif;
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin-bottom: 1rem;
        font-weight: 600;
    }

    /* ── Coming-soon buttons (secondary actions) ── */
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]) {
        background: var(--surface) !important;
        color: var(--brand-purple) !important;
        border: 1.5px solid var(--brand-purple) !important;
        border-radius: 50px !important;
        padding: 0.55rem 1.4rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:not([kind="primary"]):hover {
        background: #f0f2ff !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── Empty / Ready state ───────────────────── */
    .empty-state {
        text-align: center;
        padding: 3.5rem 2rem;
        background: linear-gradient(135deg, #f0f2ff 0%, #f5f0ff 100%);
        border: 1.5px dashed var(--border);
        border-radius: var(--radius-lg);
        margin: 1.5rem 0;
    }

    .empty-state .empty-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 1rem;
    }

    .empty-state h3 {
        font-family: 'Sora', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--brand-violet);
        margin-bottom: 0.5rem;
    }

    .empty-state p {
        color: var(--text-muted);
        font-size: 0.93rem;
        margin: 0.2rem 0;
    }

    /* ── Footer ────────────────────────────────── */
    .dashboard-footer {
        margin-top: 4rem;
        padding: 2rem 2.5rem;
        background: linear-gradient(135deg, var(--brand-purple) 0%, var(--brand-violet) 100%);
        border-radius: var(--radius-lg);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .dashboard-footer::before {
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 160px; height: 160px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }

    .dashboard-footer::after {
        content: '';
        position: absolute;
        bottom: -30px; left: -30px;
        width: 120px; height: 120px;
        background: rgba(255,255,255,0.04);
        border-radius: 50%;
    }

    .footer-title {
        font-family: 'Sora', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .footer-tagline {
        color: rgba(255,255,255,0.75);
        font-size: 0.88rem;
        margin-bottom: 1rem;
        letter-spacing: 0.3px;
    }

    .footer-divider {
        height: 1px;
        background: rgba(255,255,255,0.2);
        margin: 0.9rem auto;
        width: 60%;
    }

    .footer-team {
        color: rgba(255,255,255,0.85);
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.2rem 0;
    }

    .footer-meta {
        color: rgba(255,255,255,0.45);
        font-size: 0.78rem;
        margin-top: 0.8rem;
        letter-spacing: 0.3px;
    }
</style>
""", unsafe_allow_html=True)

# Constants
LOG_PATH = "log_denfender/logs/honeypot_log.txt"
PERF_LOG = "log_denfender/logs/performance_log.txt"
SAVE_PATH = "bot_summary.json"
TCP_LOG_PATH = "log_denfender/logs/tcp.txt"

def parse_tcp_raw(bot_number=None):
    """อ่านและสกัดข้อมูลจาก tcpdump log โดย filter ตาม divider ถ้าระบุ bot_number"""
    if not os.path.exists(TCP_LOG_PATH):
        return pd.DataFrame()

    with open(TCP_LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        all_lines = f.readlines()

    # หา divider indices ใน tcp.txt
    divider_indices = {}
    for idx, line in enumerate(all_lines):
        if line.startswith("#divider:"):
            try:
                divider_indices[int(line.split(":")[1].strip())] = idx
            except Exception:
                continue

    # กำหนดช่วง lines ที่จะอ่าน
    if bot_number is not None and bot_number in divider_indices:
        start_idx = divider_indices[bot_number] + 1
        sorted_divs = sorted(divider_indices.items())
        end_idx = len(all_lines)
        for i, (bnum, idx) in enumerate(sorted_divs):
            if bnum == bot_number and i + 1 < len(sorted_divs):
                end_idx = sorted_divs[i + 1][1]
                break
        lines_to_parse = all_lines[start_idx:end_idx]
    else:
        # Show All: อ่านทั้งไฟล์ (ข้าม divider lines)
        lines_to_parse = [ln for ln in all_lines if not ln.startswith("#divider:")]

    tcp_pattern = re.compile(r"^(\d{2}:\d{2}:\d{2}\.\d+)\s+IP\s+([\d\.]+)\.\d+\s+>\s+([\d\.]+)\.\d+:\s+Flags\s+\[(.*?)\]")
    recs = []
    for line in lines_to_parse:
        m = tcp_pattern.search(line)
        if m:
            flags = m.group(4)
            flag_name = "SYN" if "S" in flags else "ACK" if "." in flags else "OTHER"
            recs.append({
                "src_ip": m.group(2),
                "flags": flag_name,
                "count": 1
            })
    return pd.DataFrame(recs)

# Utility Functions
def read_log_and_get_section(log_path=LOG_PATH):
    """อ่านไฟล์ log และดึงตำแหน่ง divider ของแต่ละจำนวนบอท (#divider:<num>)"""
    if not os.path.exists(log_path):
        return [], {}
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    divider_indices = {}
    for idx, line in enumerate(lines):
        if line.startswith("#divider:"):
            try:
                divider_indices[int(line.split(":")[1])] = idx
            except Exception:
                continue
    return lines, divider_indices

def migrate_state_rows(rows):
    """ปรับข้อมูลเก่าให้เหลือฟิลด์รวมและชนิดข้อมูลถูกต้อง"""
    fixed = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        out = {
            "Number of bot": r.get("Number of bot"),
            "Mean Delay (ms)": r.get("Mean Delay (ms)"),
            "Packet Loss (%)": r.get("Packet Loss (%)"),
        }
        try:
            out["Number of bot"] = int(out["Number of bot"]) if out["Number of bot"] is not None else None
        except:
            out["Number of bot"] = None
        for k in ["Mean Delay (ms)", "Packet Loss (%)"]:
            try:
                out[k] = float(out[k]) if out[k] is not None else None
            except:
                out[k] = None
        fixed.append(out)
    return fixed

def safe_sort(df, cols):
    ok_cols = [c for c in cols if c in df.columns]
    return df.sort_values(ok_cols) if ok_cols else df

def format_bytes(bytes_value):
    """Format bytes to human readable format"""
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024**2:
        return f"{bytes_value/1024:.1f} KB"
    elif bytes_value < 1024**3:
        return f"{bytes_value/(1024**2):.1f} MB"
    else:
        return f"{bytes_value/(1024**3):.1f} GB"

def get_status_color(value, thresholds):
    """Get status color based on value and thresholds"""
    if value <= thresholds['good']:
        return "status-good"
    elif value <= thresholds['warning']:
        return "status-warning"
    else:
        return "status-error"

# Regex Patterns
pat_delay_loss = re.compile(
    r"\[(.*?)\]\s+([\d\.]+).*?\|\s*loss=([\d\.]+)%\s*\|\s*delay=([\d\.\-]+)ms",
    re.IGNORECASE
)
pat_net = re.compile(
    r"\[(.*?)\]\s+([\d\.]+).*?\|\s*tx=(\d+)\s*B?\s*\|\s*rx=(\d+)\s*B?\s*\|\s*tx_rate=(\d+)\s*(?:bps|kbps)\s*\|\s*rx_rate=(\d+)\s*(?:bps|kbps)",
    re.IGNORECASE
)

# Parse Performance Log
def parse_perf_log(bot_number=None):
    """Read performance_log and calculate average CPU/RAM for bot_number or entire file"""
    if not os.path.exists(PERF_LOG):
        return None, None
    with open(PERF_LOG, "r", encoding="utf-8") as f:
        lines = f.readlines()

    divider_indices = {}
    for idx, line in enumerate(lines):
        if line.startswith("#divider:"):
            try:
                divider_indices[int(line.split(":")[1])] = idx
            except:
                continue

    start_idx = 0
    end_idx = len(lines)
    if bot_number is not None and bot_number in divider_indices:
        start_idx = divider_indices[bot_number] + 1
        sorted_divs = sorted(divider_indices.items())
        for i, (bnum, idx) in enumerate(sorted_divs):
            if bnum == bot_number and i + 1 < len(sorted_divs):
                end_idx = sorted_divs[i + 1][1]
                break

    cpu_vals, ram_vals = [], []
    for ln in lines[start_idx:end_idx]:
        if "CPU=" in ln and "RAM=" in ln:
            try:
                cpu_val = float(ln.split("CPU=")[1].split("%")[0])
                ram_val = float(ln.split("RAM=")[1].split("%")[0])
                cpu_vals.append(cpu_val)
                ram_vals.append(ram_val)
            except:
                continue

    if not cpu_vals or not ram_vals:
        return None, None

    avg_cpu = sum(cpu_vals) / len(cpu_vals)
    avg_ram = sum(ram_vals) / len(ram_vals)
    return avg_cpu, avg_ram

def get_all_perf():
    """Return DataFrame with average CPU and RAM for each bot number"""
    if not os.path.exists(PERF_LOG):
        return pd.DataFrame(columns=["Number of bot", "Avg CPU (%)", "Avg RAM (%)"])
    with open(PERF_LOG, "r", encoding="utf-8") as f:
        lines = f.readlines()

    divider_indices = {}
    for idx, line in enumerate(lines):
        if line.startswith("#divider:"):
            try:
                divider_indices[int(line.split(":")[1])] = idx
            except:
                continue

    sorted_divs = sorted(divider_indices.items())
    perf_results = []
    for bot, start_idx in sorted_divs:
        end_idx = len(lines)
        for i, (b2, idx2) in enumerate(sorted_divs):
            if b2 == bot and i + 1 < len(sorted_divs):
                end_idx = sorted_divs[i + 1][1]
                break

        cpu_vals, ram_vals = [], []
        for ln in lines[start_idx + 1:end_idx]:
            if "CPU=" in ln and "RAM=" in ln:
                try:
                    cpu_val = float(ln.split("CPU=")[1].split("%")[0])
                    ram_val = float(ln.split("RAM=")[1].split("%")[0])
                    cpu_vals.append(cpu_val)
                    ram_vals.append(ram_val)
                except:
                    continue

        if cpu_vals and ram_vals:
            perf_results.append({
                "Number of bot": int(bot),
                "Avg CPU (%)": round(sum(cpu_vals) / len(cpu_vals), 2),
                "Avg RAM (%)": round(sum(ram_vals) / len(ram_vals), 2)
            })

    df = pd.DataFrame(perf_results)
    if not df.empty:
        df = safe_sort(df, ["Number of bot"])
    return df

# Parse Raw Rows
def parse_raw_rows():
    """Return DataFrame from log file, using dividers to separate bots"""
    all_lines, divider_indices = read_log_and_get_section()
    if not all_lines:
        return pd.DataFrame(columns=["Number of bot", "IP", "loss", "delay"])

    sorted_divs = sorted(divider_indices.items())
    recs = []
    for bot, start_idx in sorted_divs:
        end_idx = len(all_lines)
        for j, (b2, idx2) in enumerate(sorted_divs):
            if b2 == bot and j + 1 < len(sorted_divs):
                end_idx = sorted_divs[j + 1][1]
                break
        seg = all_lines[start_idx + 1:end_idx]
        for ln in seg:
            m = pat_delay_loss.search(ln)
            if not m:
                continue
            try:
                ip = m.group(2)
                loss = float(m.group(3))
                delay = float(m.group(4))
                if delay < 0:
                    delay = None
                recs.append({
                    "Number of bot": int(bot),
                    "IP": ip,
                    "loss": loss,
                    "delay": delay
                })
            except:
                continue
    df = pd.DataFrame(recs)
    if not df.empty:
        df["Number of bot"] = df["Number of bot"].astype(int)
    return df

# Main Application
def main():
    # Title with gradient effect
    st.markdown('<h1 class="main-title">🤖 Bot Performance Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>🎛️ Control Panel</h2>
        </div>
        <div class="sidebar-label">📊 Chart Visibility</div>
        """, unsafe_allow_html=True)
        show_delay_chart = st.checkbox("Show Mean Delay Chart", value=True)
        show_loss_chart = st.checkbox("Show Packet Loss Chart", value=True)
        show_perf_chart = st.checkbox("Show CPU/RAM Performance Chart", value=True)
        st.markdown('<div class="sidebar-label">📡 Divider Selection</div>', unsafe_allow_html=True)
        # ดึง divider list จาก log
        _all_lines_div, _divider_indices_div = read_log_and_get_section()
        _divider_options = sorted(_divider_indices_div.keys())
        if _divider_options:
            _select_choices = ["Show All"] + [f"Divider {d}" for d in _divider_options]
            _divider_selection = st.selectbox(
                "Select Divider for Detail",
                options=_select_choices,
                index=0,
                help="เลือก divider เพื่อดู IP details หรือเลือก Show All เพื่อดูทุก divider"
            )
            if _divider_selection == "Show All":
                bot_number_ip = None
            else:
                bot_number_ip = int(_divider_selection.replace("Divider ", ""))
        else:
            st.caption("ยังไม่มี divider ในระบบ")
            bot_number_ip = None

        # Quick Stats
        all_lines, divider_indices = read_log_and_get_section()
        total_bots = len(divider_indices)
        st.markdown('<div class="sidebar-label">📈 Overview</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Quick Stats</h3>
            <h2>{total_bots}</h2>
            <p>Total Bots Configured</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Last Update Time
        if os.path.exists(LOG_PATH):
            mod_time = datetime.fromtimestamp(os.path.getmtime(LOG_PATH))
            st.markdown(f"""
            <div class="performance-card">
                <h4>🕒 Last Update</h4>
                <p>{mod_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            """, unsafe_allow_html=True)

    # Session State Initialization
    if "bot_results" not in st.session_state:
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
            except Exception:
                loaded = []
        else:
            loaded = []
        st.session_state.bot_results = migrate_state_rows(loaded)

    # Bot Configuration Section
    st.markdown('<div class="section-header">🛠️ Bot Configuration & Data Collection</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">กำหนดค่าและเพิ่มข้อมูล performance ของแต่ละ bot</p>', unsafe_allow_html=True)

    st.markdown('<div class="config-panel">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        bot_number = st.number_input("🤖 Bot Number", min_value=1, step=1, 
                                   help="Enter the bot number you want to configure or analyze")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        add_data = st.button("➕ Add Bot Data", help="Process and add performance data for this bot", type="primary")

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        clear_data = st.button("🗑️ Clear All Data", help="Remove all stored bot data from dashboard", type="secondary")
    st.markdown('</div>', unsafe_allow_html=True)

    # Process clear data
    if clear_data:
        st.session_state.bot_results = []
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)
        st.success("🧹 All data cleared from dashboard successfully.")
        st.rerun()

    # Process bot data
    if add_data:
        with st.spinner('🔄 Processing bot data...'):
            all_lines, divider_indices = read_log_and_get_section()
            
            if bot_number not in divider_indices:
                os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
                with open(LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(f"#divider:{bot_number}\n")
                with open(PERF_LOG, "a", encoding="utf-8") as f:
                    f.write(f"#divider:{bot_number}\n")
                    # 👇 ส่วนที่เพิ่มเข้ามาใหม่สำหรับ tcp.txt
                with open(TCP_LOG_PATH, "a", encoding="utf-8") as f:
                    f.write(f"#divider:{bot_number}\n")
                
                st.success(f"✅ Created divider for Bot #{bot_number}. Please wait for new log data.")
                st.rerun()

            start_idx = divider_indices[bot_number]
            sorted_divs = sorted(divider_indices.items())
            end_idx = len(all_lines)
            for i, (b2, idx2) in enumerate(sorted_divs):
                if b2 == bot_number and i + 1 < len(sorted_divs):
                    end_idx = sorted_divs[i + 1][1]
                    break
            seg = all_lines[start_idx + 1:end_idx]

            rows = []
            for ln in seg:
                m = pat_delay_loss.search(ln)
                if not m:
                    continue
                try:
                    loss = float(m.group(3))
                    delay = float(m.group(4))
                    if delay < 0:
                        delay = None
                    rows.append({"loss": loss, "delay": delay})
                except:
                    continue

            if not rows:
                st.warning("⚠️ No log data found after this divider. Please ensure the bot is active.")
                st.stop()

            df = pd.DataFrame(rows)
            mean_delay = df["delay"].dropna().mean() if df["delay"].notna().any() else None
            mean_loss  = df["loss"].dropna().mean() if df["loss"].notna().any() else None

            rec = {
                "Number of bot": int(bot_number),
                "Mean Delay (ms)": round(mean_delay, 2) if mean_delay is not None else None,
                "Packet Loss (%)": round(mean_loss, 2) if mean_loss is not None else None
            }
            
            found = next((i for i, r in enumerate(st.session_state.bot_results)
                          if r.get("Number of bot") == int(bot_number)), None)
            if found is None:
                st.session_state.bot_results.append(rec)
            else:
                st.session_state.bot_results[found] = rec

            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(st.session_state.bot_results, f, ensure_ascii=False)

            st.success(f"🎉 Successfully processed data for Bot #{int(bot_number)}")

    # Parse raw data for charts and IP details
    df_raw = parse_raw_rows()
    df_bot = pd.DataFrame(columns=["Number of bot", "Mean Delay (ms)", "Packet Loss (%)", "IP Addresses"])
    if not df_raw.empty:
        df_bot = df_raw.groupby("Number of bot", as_index=False).agg({
            "delay": "mean",
            "loss": "mean",
            "IP": lambda x: ", ".join(sorted(set(x)))
        }).rename(columns={"delay": "Mean Delay (ms)", "loss": "Packet Loss (%)", "IP": "IP Addresses"})
        # แปลงเป็นตัวเลขก่อน (ตัวไหนแปลงไม่ได้จะกลายเป็น NaN) แล้วค่อยปัดเศษ
        df_bot["Mean Delay (ms)"] = pd.to_numeric(df_bot["Mean Delay (ms)"], errors='coerce').round(2)
        df_bot["Packet Loss (%)"] = pd.to_numeric(df_bot["Packet Loss (%)"], errors='coerce').round(2)
        df_bot = safe_sort(df_bot, ["Number of bot"])

    # System Performance Section
    st.markdown('<div class="section-header">💻 System Performance Monitor</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="section-desc">ติดตาม CPU และ RAM usage สำหรับ Bot #{bot_number}</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    
    with col1:
        bot_number_perf = st.number_input("🎯 Select Bot Number for Performance Analysis", 
                                        min_value=1, step=1, value=1, 
                                        help="Choose which bot's performance you want to monitor")
    
    with col2:
        if st.button("🔄 Refresh Performance", help="Reload performance data"):
            st.rerun()

    cpu_val, ram_val = parse_perf_log(bot_number=bot_number_perf)

    if cpu_val is not None and ram_val is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
            cpu_color = "red" if cpu_val > 80 else "orange" if cpu_val > 60 else "green"
            fig_cpu = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=cpu_val,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "🔥 CPU Usage", 'font': {'size': 22, 'color': '#667eea', 'family': 'Sora'}},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': "white"},
                    'bar': {'color': cpu_color, 'thickness': 0.3},
                    'bgcolor': "rgba(255,255,255,0.1)",
                    'borderwidth': 2,
                    'bordercolor': "white",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(0,255,0,0.3)'},
                        {'range': [50, 80], 'color': 'rgba(255,255,0,0.3)'},
                        {'range': [80, 100], 'color': 'rgba(255,0,0,0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_cpu.update_layout(
                height=300, 
                margin=dict(t=50, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#1a1d3a', 'family': 'Inter', 'size': 14}
            )
            st.plotly_chart(fig_cpu, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
            ram_color = "red" if ram_val > 80 else "orange" if ram_val > 60 else "blue"
            fig_ram = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=ram_val,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "🧠 RAM Usage", 'font': {'size': 22, 'color': '#764ba2', 'family': 'Sora'}},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': "white"},
                    'bar': {'color': ram_color, 'thickness': 0.3},
                    'bgcolor': "rgba(255,255,255,0.1)",
                    'borderwidth': 2,
                    'bordercolor': "white",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(0,255,0,0.3)'},
                        {'range': [50, 80], 'color': 'rgba(255,255,0,0.3)'},
                        {'range': [80, 100], 'color': 'rgba(255,0,0,0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_ram.update_layout(
                height=300, 
                margin=dict(t=50, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#1a1d3a', 'family': 'Inter', 'size': 14}
            )
            st.plotly_chart(fig_ram, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Performance Status
        col1, col2, col3 = st.columns(3)
        with col1:
            cpu_status = get_status_color(cpu_val, {'good': 60, 'warning': 80})
            st.markdown(f'<p class="{cpu_status}">CPU: {"🟢 Excellent" if cpu_val <= 60 else "🟡 Moderate" if cpu_val <= 80 else "🔴 High"}</p>', unsafe_allow_html=True)
        
        with col2:
            ram_status = get_status_color(ram_val, {'good': 60, 'warning': 80})
            st.markdown(f'<p class="{ram_status}">RAM: {"🟢 Excellent" if ram_val <= 60 else "🟡 Moderate" if ram_val <= 80 else "🔴 High"}</p>', unsafe_allow_html=True)
        
        with col3:
            overall_status = "🟢 Optimal" if cpu_val <= 60 and ram_val <= 60 else "🟡 Moderate" if cpu_val <= 80 and ram_val <= 80 else "🔴 Critical"
            st.markdown(f'<p><strong>Overall: {overall_status}</strong></p>', unsafe_allow_html=True)

    else:
        st.warning(f"⚠️ No CPU/RAM data for Bot #{bot_number_perf}. Check performance_log.txt.")

    # Get performance data for all bots
    df_perf = get_all_perf()

    # Network Performance Analytics
    if not df_bot.empty:
        st.markdown('<div class="section-header">📊 Network Performance Analytics</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">เปรียบเทียบ Mean Delay, Packet Loss และ CPU/RAM ของแต่ละ bot</p>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if show_delay_chart:
                fig_delay = px.bar(
                    df_bot,
                    x="Number of bot",
                    y="Mean Delay (ms)",
                    text="Mean Delay (ms)",
                    title="📊 Mean Delay per Bot (All IPs Combined)",
                    color="Mean Delay (ms)",
                    color_continuous_scale="RdYlGn_r",
                    template="plotly_white",
                    hover_data=["IP Addresses"]
                )
                fig_delay.update_traces(
                    texttemplate="%{text:.2f}ms", 
                    textposition="outside",
                    textfont=dict(size=13, color="#1a1d3a", family="Inter", weight="bold"),
                )
                fig_delay.update_layout(
                    yaxis_title="Mean Delay (ms)",
                    xaxis_title="Bot Number",
                    font=dict(family="Inter", size=12),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=400,
                    showlegend=False
                )
                fig_delay.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                fig_delay.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                st.plotly_chart(fig_delay, use_container_width=True)

        with col2:
            if show_loss_chart:
                fig_loss = px.bar(
                    df_bot,
                    x="Number of bot",
                    y="Packet Loss (%)",
                    text="Packet Loss (%)",
                    title="📉 Packet Loss per Bot (All IPs Combined)",
                    color="Packet Loss (%)",
                    color_continuous_scale="RdYlGn_r",
                    template="plotly_white",
                    hover_data=["IP Addresses"]
                )
                fig_loss.update_traces(
                    texttemplate="%{text:.2f}%", 
                    textposition="outside",
                    textfont=dict(size=13, color="#1a1d3a", family="Inter", weight="bold"),
                )
                fig_loss.update_layout(
                    yaxis_title="Packet Loss (%)",
                    xaxis_title="Bot Number",
                    font=dict(family="Inter", size=12),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=400,
                    showlegend=False
                )
                fig_loss.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                fig_loss.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                st.plotly_chart(fig_loss, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
            
        # CPU/RAM Bar Chart
        if not df_perf.empty and show_perf_chart:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            df_melt = df_perf.melt(
                id_vars=["Number of bot"],
                value_vars=["Avg CPU (%)", "Avg RAM (%)"],
                var_name="Metric",
                value_name="Percentage"
            )
            df_melt = df_melt.merge(df_bot[["Number of bot", "IP Addresses"]], on="Number of bot", how="left")
            
            fig_perf = px.bar(
                df_melt,
                x="Number of bot",
                y="Percentage",
                color="Metric",
                barmode="group",
                text="Percentage",
                title="📊 CPU and RAM Usage per Bot Number",
                template="plotly_white",
                color_discrete_sequence=["#FF4B4B", "#4B4BFF"],
                hover_data=["IP Addresses"]
            )
            fig_perf.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside",
                textfont=dict(size=13, color="#1a1d3a", family="Inter", weight="bold"),
            )
            fig_perf.update_layout(
                yaxis_title="Usage (%)",
                xaxis_title="Bot Number",
                font=dict(family="Inter", size=13, color="#1a1d3a"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=13, color="#1a1d3a", family="Inter")
                ),
                showlegend=True
            )
            fig_perf.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            fig_perf.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            st.plotly_chart(fig_perf, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

        # New Section for Normal User (Specific IP)
        st.markdown('<div class="section-header">📊 Normal User Performance (IP: 192.168.39.178)</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">Mean Delay และ Packet Loss สำหรับ Normal User (Single IP)</p>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        df_normal = df_raw[df_raw['IP'] == '192.168.39.178']
        if not df_normal.empty:
            df_normal_agg = df_normal.groupby("Number of bot", as_index=False).agg({
                "delay": "mean",
                "loss": "mean"
            }).rename(columns={"delay": "Mean Delay (ms)", "loss": "Packet Loss (%)"})
            df_normal_agg["Mean Delay (ms)"] = df_normal_agg["Mean Delay (ms)"].round(2)
            df_normal_agg["Packet Loss (%)"] = df_normal_agg["Packet Loss (%)"].round(2)
            df_normal_agg = safe_sort(df_normal_agg, ["Number of bot"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if show_delay_chart:
                    fig_delay_normal = px.bar(
                        df_normal_agg,
                        x="Number of bot",
                        y="Mean Delay (ms)",
                        text="Mean Delay (ms)",
                        title="📊 Mean Delay per Bot (IP: 192.168.39.178)",
                        color="Mean Delay (ms)",
                        color_continuous_scale="RdYlGn_r",
                        template="plotly_white"
                    )
                    fig_delay_normal.update_traces(
                        texttemplate="%{text:.2f}ms", 
                        textposition="outside",
                        textfont=dict(size=13, color="#1a1d3a", family="Inter", weight="bold"),
                    )
                    fig_delay_normal.update_layout(
                        yaxis_title="Mean Delay (ms)",
                        xaxis_title="Bot Number",
                        font=dict(family="Inter", size=12),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=400,
                        showlegend=False
                    )
                    fig_delay_normal.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                    fig_delay_normal.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                    st.plotly_chart(fig_delay_normal, use_container_width=True)

            with col2:
                if show_loss_chart:
                    fig_loss_normal = px.bar(
                        df_normal_agg,
                        x="Number of bot",
                        y="Packet Loss (%)",
                        text="Packet Loss (%)",
                        title="📉 Packet Loss per Bot (IP: 192.168.39.178)",
                        color="Packet Loss (%)",
                        color_continuous_scale="RdYlGn_r",
                        template="plotly_white"
                    )
                    fig_loss_normal.update_traces(
                        texttemplate="%{text:.2f}%", 
                        textposition="outside",
                        textfont=dict(size=13, color="#1a1d3a", family="Inter", weight="bold"),
                    )
                    fig_loss_normal.update_layout(
                        yaxis_title="Packet Loss (%)",
                        xaxis_title="Bot Number",
                        font=dict(family="Inter", size=12),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=400,
                        showlegend=False
                    )
                    fig_loss_normal.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                    fig_loss_normal.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
                    st.plotly_chart(fig_loss_normal, use_container_width=True)
        else:
            st.warning("⚠️ No data available for IP 192.168.39.178.")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # IP Details Table
        st.markdown('<div class="section-header">📍 IP Details</div>', unsafe_allow_html=True)
        if bot_number_ip is None:
            st.markdown('<p class="section-desc">ข้อมูล performance แยกตาม IP — แสดงทุก Divider</p>', unsafe_allow_html=True)
            df_ip_details = df_raw[["Number of bot", "IP", "loss", "delay"]].copy()
            df_ip_details = df_ip_details.rename(columns={
                "Number of bot": "Divider",
                "loss": "Packet Loss (%)",
                "delay": "Delay (ms)"
            })
        else:
            st.markdown(f'<p class="section-desc">ข้อมูล performance แยกตาม IP สำหรับ Divider {bot_number_ip}</p>', unsafe_allow_html=True)
            df_ip_details = df_raw[df_raw["Number of bot"] == bot_number_ip][["IP", "loss", "delay"]].copy()
            df_ip_details = df_ip_details.rename(columns={"loss": "Packet Loss (%)", "delay": "Delay (ms)"})
        if not df_ip_details.empty:
            df_ip_details["Delay (ms)"] = pd.to_numeric(df_ip_details["Delay (ms)"], errors='coerce').round(2)
            df_ip_details["Packet Loss (%)"] = pd.to_numeric(df_ip_details["Packet Loss (%)"], errors='coerce').round(2)
            st.dataframe(df_ip_details, use_container_width=True)
        else:
            label = "all dividers" if bot_number_ip is None else f"Divider {bot_number_ip}"
            st.warning(f"⚠️ No IP data for {label}.")

    # Data Summary Table
    if st.session_state.bot_results:
        st.markdown('<div class="section-header">📋 Bot Performance Summary</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-desc">สรุปผล performance พร้อม IP addresses ของแต่ละ bot</p>', unsafe_allow_html=True)
        
        df_summary = pd.DataFrame(st.session_state.bot_results)
        df_summary["Number of bot"] = pd.to_numeric(df_summary["Number of bot"], errors="coerce")
        df_summary = df_summary.merge(df_bot[["Number of bot", "IP Addresses"]], on="Number of bot", how="left")
        if not df_perf.empty:
            df_summary = df_summary.merge(
                df_perf[["Number of bot", "Avg CPU (%)", "Avg RAM (%)"]],
                on="Number of bot",
                how="left"
            )
        
        df_display = df_summary.copy()
        if "Mean Delay (ms)" in df_display.columns:
            df_display["Delay Status"] = df_display["Mean Delay (ms)"].apply(
                lambda x: "🟢 Good" if pd.isna(x) or x < 50 else "🟡 Fair" if x < 100 else "🔴 Poor"
            )
        if "Packet Loss (%)" in df_display.columns:
           df_display["Loss Status"] = df_display["Packet Loss (%)"].apply(
                lambda x: "🟢 Good" if pd.isna(x) or x < 1 else "🟡 Fair" if x < 5 else "🔴 Poor"
            )
        if "Avg CPU (%)" in df_display.columns:
            df_display["CPU Status"] = df_display["Avg CPU (%)"].apply(
                lambda x: "🟢 Good" if pd.isna(x) or x <= 60 else "🟡 Moderate" if x <= 80 else "🔴 High"
            )
        if "Avg RAM (%)" in df_display.columns:
            df_display["RAM Status"] = df_display["Avg RAM (%)"].apply(
                lambda x: "🟢 Good" if pd.isna(x) or x <= 60 else "🟡 Moderate" if x <= 80 else "🔴 High"
            )
        
        st.dataframe(df_display, use_container_width=True, height=400)

    # Network Traffic Analysis
    st.markdown('<div class="section-header">📶 Network Traffic Analysis</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">ข้อมูล upload/download traffic ของแต่ละ bot</p>', unsafe_allow_html=True)
    
    all_lines, divider_indices = read_log_and_get_section()
    sorted_divs = sorted(divider_indices.items())
    bot_net_result = []

    for bot, start_idx in sorted_divs:
        end_idx = len(all_lines)
        for j, (b2, idx2) in enumerate(sorted_divs):
            if b2 == bot and j + 1 < len(sorted_divs):
                end_idx = sorted_divs[j + 1][1]
                break
        seg = all_lines[start_idx + 1:end_idx]

        recs = []
        for ln in seg:
            m = pat_net.search(ln)
            if m:
                try:
                    ip = m.group(2)
                    tx_bytes = int(m.group(3))
                    rx_bytes = int(m.group(4))
                    tx_rate_raw = float(m.group(5))
                    rx_rate_raw = float(m.group(6))
                    recs.append({
                        "IP": ip,
                        "tx": tx_bytes,
                        "rx": rx_bytes,
                        "tx_bps": tx_rate_raw,
                        "rx_bps": rx_rate_raw,
                    })
                except:
                    continue
        if not recs:
            continue

        dnet_all = pd.DataFrame(recs)
        tx_kbps = round(dnet_all["tx_bps"].mean() / 1000.0, 2) if not dnet_all.empty else 0.0
        rx_kbps = round(dnet_all["rx_bps"].mean() / 1000.0, 2) if not dnet_all.empty else 0.0
        last_by_ip = dnet_all.groupby("IP", as_index=False).last()
        total_tx_bytes = int(last_by_ip["tx"].sum())
        total_rx_bytes = int(last_by_ip["rx"].sum())

        bot_net_result.append({
            "Number of bot": int(bot),
            "Tx Bitrate (kbps)": tx_kbps,
            "Rx Bitrate (kbps)": rx_kbps,
            "Total Tx Bytes": total_tx_bytes,
            "Total Rx Bytes": total_rx_bytes,
        })

    if bot_net_result:
        df_net = pd.DataFrame(bot_net_result)
        df_net = safe_sort(df_net, ["Number of bot"])

        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_tx = df_net["Total Tx Bytes"].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3>📤 Total Upload</h3>
                <h2>{format_bytes(total_tx)}</h2>
                <p>Across All Bots</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_rx = df_net["Total Rx Bytes"].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3>📥 Total Download</h3>
                <h2>{format_bytes(total_rx)}</h2>
                <p>Across All Bots</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_tx_rate = df_net["Tx Bitrate (kbps)"].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚡ Avg TX Rate</h3>
                <h2>{avg_tx_rate:.1f} kbps</h2>
                <p>Upload Speed</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            df_bitrate = df_net.melt(
                id_vars=["Number of bot"],
                value_vars=["Tx Bitrate (kbps)", "Rx Bitrate (kbps)"],
                var_name="Direction",
                value_name="kbps",
            )
            
            fig_bitrate = px.bar(
                df_bitrate,
                x="Number of bot",
                y="kbps",
                color="Direction",
                barmode="group",
                title="📶 Tx/Rx Bitrate Comparison",
                template="plotly_white",
                color_discrete_sequence=["#667eea", "#764ba2"]
            )
            fig_bitrate.update_layout(
                height=400,
                font=dict(family="Inter", size=13, color="#1a1d3a"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(size=13, color="#1a1d3a"))
            )
            fig_bitrate.update_traces(marker_line_width=2, marker_line_color="white")
            st.plotly_chart(fig_bitrate, use_container_width=True)
        
        with col2:
            df_bytes = df_net.melt(
                id_vars=["Number of bot"],
                value_vars=["Total Tx Bytes", "Total Rx Bytes"],
                var_name="Direction",
                value_name="Bytes",
            )
            
            fig_bytes = px.bar(
                df_bytes,
                x="Number of bot",
                y="Bytes",
                color="Direction",
                barmode="group",
                title="📦 Total Data Transfer",
                template="plotly_white",
                color_discrete_sequence=["#11998e", "#38ef7d"]
            )
            fig_bytes.update_layout(
                height=400,
                font=dict(family="Inter", size=13, color="#1a1d3a"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                            font=dict(size=13, color="#1a1d3a"))
            )
            fig_bytes.update_traces(marker_line_width=2, marker_line_color="white")
            st.plotly_chart(fig_bytes, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
    # 🛑 เพิ่มใหม่: TCP Packet Analytics (Raw Traffic)
    # ==========================================
    st.markdown('<div class="section-header">🔍 TCP Packet Analysis (Deep Dive)</div>', unsafe_allow_html=True)
    _tcp_label = f"Divider {bot_number_ip}" if bot_number_ip is not None else "All Dividers"
    st.markdown(f'<p class="section-desc">ภาพรวม Raw TCP Packets ที่ได้จาก tcpdump — แสดงข้อมูล: <strong>{_tcp_label}</strong></p>', unsafe_allow_html=True)

    df_tcp = parse_tcp_raw(bot_number=bot_number_ip)
    if not df_tcp.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            # สรุปจำนวน Flags (เน้นดู SYN vs ACK)
            flag_summary = df_tcp.groupby("flags")["count"].sum().reset_index()
            fig_tcp_flags = px.pie(
                flag_summary, 
                values="count", 
                names="flags", 
                title="🚩 Overall TCP Flags (SYN vs ACK Ratio)",
                hole=0.4,
                color_discrete_sequence=["#FF4B4B", "#4facfe", "#f59e0b"]
            )
            fig_tcp_flags.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter", size=13, color="#1a1d3a"))
            st.plotly_chart(fig_tcp_flags, use_container_width=True)
            
        with col2:
            # สรุป IP โจมตีที่ระดับ Transport Layer
            top_tcp_ip = df_tcp.groupby("src_ip")["count"].sum().reset_index().sort_values(by="count", ascending=False).head(5)
            fig_top_tcp = px.bar(
                top_tcp_ip,
                x="src_ip",
                y="count",
                title="🎯 Top 5 Attackers by Raw Packet Count",
                text="count",
                template="plotly_white",
                color_discrete_sequence=["#764ba2"]
            )
            fig_top_tcp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter", size=13, color="#1a1d3a"))
            fig_top_tcp.update_traces(textfont=dict(size=13, color="#1a1d3a", family="Inter", weight="bold"), textposition="outside")
            st.plotly_chart(fig_top_tcp, use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ No TCP dump data available. Ensure tcpdump is running and logging to tcp.txt.")

    # IP Details Table for Network Traffic
    st.markdown('<div class="section-header">📍 Network Traffic IP Details</div>', unsafe_allow_html=True)

    # Export Section
    st.markdown('<div class="section-header">💾 Data Export & Reports</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Export ข้อมูลทั้งหมดเป็น Excel report</p>', unsafe_allow_html=True)
    
    try:
        df_final = pd.DataFrame(st.session_state.bot_results)
        if not df_final.empty:
            df_final["Number of bot"] = pd.to_numeric(df_final["Number of bot"], errors="coerce")
        df_final = safe_sort(df_final, ["Number of bot"])
        df_merged = df_final.merge(df_bot[["Number of bot", "IP Addresses"]], on="Number of bot", how="left")
        if not df_perf.empty:
            df_merged = df_merged.merge(df_perf[["Number of bot", "Avg CPU (%)", "Avg RAM (%)"]], on="Number of bot", how="left")
        if not df_net.empty:
            df_merged = df_merged.merge(df_net, on=["Number of bot"], how="left")
    except Exception:
        df_merged = df_bot.copy()

    # ── ดึงข้อมูล TCP ทั้งหมด (ไม่ filter bot) แล้วสรุปสำหรับ Excel ──
    df_tcp_all = parse_tcp_raw()
    df_tcp_raw_export = pd.DataFrame()
    df_tcp_summary_export = pd.DataFrame()
    if not df_tcp_all.empty:
        # ข้อมูล raw: นับ packet ต่อ src_ip + flags
        df_tcp_raw_export = (
            df_tcp_all.groupby(["src_ip", "flags"])["count"]
            .sum()
            .reset_index()
            .rename(columns={"src_ip": "Source IP", "flags": "TCP Flag", "count": "Packet Count"})
            .sort_values("Packet Count", ascending=False)
            .reset_index(drop=True)
        )
        # ข้อมูลสรุป: รวม SYN / ACK / OTHER
        df_tcp_summary_export = (
            df_tcp_all.groupby("flags")["count"]
            .sum()
            .reset_index()
            .rename(columns={"flags": "TCP Flag", "count": "Total Packets"})
        )
        total_tcp = df_tcp_summary_export["Total Packets"].sum()
        df_tcp_summary_export["Percentage (%)"] = (
            df_tcp_summary_export["Total Packets"] / total_tcp * 100
        ).round(2)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_merged.to_excel(writer, sheet_name="Bot Performance Summary", index=False)
        df_net.to_excel(writer, sheet_name="Network Analytics", index=False)
        if not df_perf.empty:
            df_perf.to_excel(writer, sheet_name="Performance Analytics", index=False)
        if not df_raw.empty:
            df_raw.to_excel(writer, sheet_name="Raw Log Data", index=False)
        if not df_bot.empty:
            df_bot.to_excel(writer, sheet_name="IP Details", index=False)
        if not df_tcp_raw_export.empty:
            df_tcp_raw_export.to_excel(writer, sheet_name="TCP Packet Detail", index=False)
        if not df_tcp_summary_export.empty:
            df_tcp_summary_export.to_excel(writer, sheet_name="TCP Flag Summary", index=False)

        summary_stats = {
            "Metric": ["Total Bots", "Avg Delay (ms)", "Avg Packet Loss (%)", "Avg CPU (%)", "Avg RAM (%)", "Total Upload (MB)", "Total Download (MB)"],
            "Value": [
                len(df_merged),
                df_merged["Mean Delay (ms)"].mean() if "Mean Delay (ms)" in df_merged.columns else 0,
                df_merged["Packet Loss (%)"].mean() if "Packet Loss (%)" in df_merged.columns else 0,
                df_merged["Avg CPU (%)"].mean() if "Avg CPU (%)" in df_merged.columns else 0,
                df_merged["Avg RAM (%)"].mean() if "Avg RAM (%)" in df_merged.columns else 0,
                df_net["Total Tx Bytes"].sum() / (1024*1024) if not df_net.empty else 0,
                df_net["Total Rx Bytes"].sum() / (1024*1024) if not df_net.empty else 0
            ]
        }
        pd.DataFrame(summary_stats).to_excel(writer, sheet_name="Executive Summary", index=False)

    # ── Helper: สร้าง table string สำหรับ TXT ────────────────────────
    def _txt_table(df_table, cols):
        if df_table.empty:
            return ["  (ไม่มีข้อมูล)"]
        rows_out = []
        header_row = "  " + " | ".join(f"{c:<22}" for c in cols)
        rows_out.append(header_row)
        rows_out.append("  " + "-" * max(len(header_row) - 2, 10))
        for _, row in df_table.iterrows():
            rows_out.append("  " + " | ".join(
                f"{str(round(row[c], 2)) if isinstance(row[c], float) else str(row[c]):<22}"
                for c in cols
            ))
        return rows_out

    # ── บล็อกสร้างเนื้อหาแต่ละประเภท ────────────────────────────────
    generated_at_txt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _txt_header(title):
        lines = []
        lines.append("=" * 60)
        lines.append(f"  BOT PERFORMANCE ANALYTICS — {title}")
        lines.append(f"  Generated: {generated_at_txt}")
        lines.append("=" * 60)
        lines.append("")
        return lines

    def _txt_footer():
        return [
            "",
            "=" * 60,
            "  Bot Performance Analytics Dashboard",
            "  NT National Telecom — นักศึกษาสหกิจศึกษา มทส.",
            "=" * 60,
        ]

    def _build_overview():
        """ภาพรวมทั้งหมด (ทุก section รวมกัน)"""
        L = _txt_header("FULL OVERVIEW REPORT")

        # Executive Summary
        L.append("[ EXECUTIVE SUMMARY ]")
        L.append(f"  Total Bots Monitored : {len(df_merged)}")
        if "Mean Delay (ms)" in df_merged.columns:
            L.append(f"  Avg Mean Delay (ms)  : {df_merged['Mean Delay (ms)'].mean():.2f}")
        if "Packet Loss (%)" in df_merged.columns:
            L.append(f"  Avg Packet Loss (%%) : {df_merged['Packet Loss (%)'].mean():.2f}%")
        if "Avg CPU (%)" in df_merged.columns:
            L.append(f"  Avg CPU Usage (%%)   : {df_merged['Avg CPU (%)'].mean():.2f}%")
        if "Avg RAM (%)" in df_merged.columns:
            L.append(f"  Avg RAM Usage (%%)   : {df_merged['Avg RAM (%)'].mean():.2f}%")
        if not df_net.empty:
            L.append(f"  Total Upload (MB)    : {df_net['Total Tx Bytes'].sum() / (1024*1024):.2f}")
            L.append(f"  Total Download (MB)  : {df_net['Total Rx Bytes'].sum() / (1024*1024):.2f}")
        L.append("")

        # Bot Performance Detail
        L.append("[ BOT PERFORMANCE DETAIL ]")
        detail_cols = [c for c in ["Number of bot", "Mean Delay (ms)", "Packet Loss (%)", "IP Addresses", "Avg CPU (%)", "Avg RAM (%)"] if c in df_merged.columns]
        L.extend(_txt_table(df_merged, detail_cols))
        L.append("")

        # Network Analytics
        if not df_net.empty:
            L.append("[ NETWORK ANALYTICS ]")
            L.extend(_txt_table(df_net, list(df_net.columns)))
            L.append("")

        # TCP Analytics
        _df_tcp_txt = parse_tcp_raw()
        if not _df_tcp_txt.empty:
            L.append("[ TCP PACKET ANALYTICS ]")
            L.append("  -- Flag Summary --")
            tcp_sum = _df_tcp_txt.groupby("flags")["count"].sum().reset_index()
            total_t = tcp_sum["count"].sum()
            for _, r in tcp_sum.iterrows():
                pct = r["count"] / total_t * 100
                L.append(f"  {r['flags']:<10} : {int(r['count']):>8} packets  ({pct:.1f}%)")
            L.append("")
            L.append("  -- Top 10 Source IPs --")
            top_ip = _df_tcp_txt.groupby("src_ip")["count"].sum().reset_index().sort_values("count", ascending=False).head(10)
            for _, r in top_ip.iterrows():
                L.append(f"  {r['src_ip']:<20} : {int(r['count']):>8} packets")
            L.append("")

        L.extend(_txt_footer())
        return "\n".join(L)

    def _build_performance():
        """ดู Performance อย่างเดียว (Delay, Packet Loss, CPU, RAM)"""
        L = _txt_header("PERFORMANCE REPORT")
        L.append("[ BOT PERFORMANCE METRICS ]")
        perf_cols = [c for c in ["Number of bot", "Mean Delay (ms)", "Packet Loss (%)", "Avg CPU (%)", "Avg RAM (%)"] if c in df_merged.columns]
        L.extend(_txt_table(df_merged, perf_cols))
        L.append("")

        # สรุปค่าเฉลี่ย/min/max
        L.append("[ STATISTICS SUMMARY ]")
        for col in ["Mean Delay (ms)", "Packet Loss (%)", "Avg CPU (%)", "Avg RAM (%)"]:
            if col in df_merged.columns:
                L.append(f"  {col:<25}  Avg: {df_merged[col].mean():.2f}  Min: {df_merged[col].min():.2f}  Max: {df_merged[col].max():.2f}")
        L.append("")
        L.extend(_txt_footer())
        return "\n".join(L)

    def _build_network():
        """ดู Network Analytics อย่างเดียว"""
        L = _txt_header("NETWORK ANALYTICS REPORT")
        if not df_net.empty:
            L.append("[ NETWORK ANALYTICS ]")
            L.extend(_txt_table(df_net, list(df_net.columns)))
            L.append("")
            L.append("[ NETWORK SUMMARY ]")
            if "Tx Bitrate (kbps)" in df_net.columns:
                L.append(f"  Avg Tx Bitrate (kbps) : {df_net['Tx Bitrate (kbps)'].mean():.2f}")
                L.append(f"  Avg Rx Bitrate (kbps) : {df_net['Rx Bitrate (kbps)'].mean():.2f}" if "Rx Bitrate (kbps)" in df_net.columns else "")
            if "Total Tx Bytes" in df_net.columns:
                L.append(f"  Total Upload (MB)     : {df_net['Total Tx Bytes'].sum() / (1024*1024):.2f}")
                L.append(f"  Total Download (MB)   : {df_net['Total Rx Bytes'].sum() / (1024*1024):.2f}" if "Total Rx Bytes" in df_net.columns else "")
            L.append("")
        else:
            L.append("  (ไม่มีข้อมูล Network)")
            L.append("")
        L.extend(_txt_footer())
        return "\n".join(L)

    def _build_tcp():
        """ดู TCP Packet Analysis อย่างเดียว"""
        L = _txt_header("TCP PACKET ANALYSIS REPORT")
        _df_tcp_txt = parse_tcp_raw()
        if not _df_tcp_txt.empty:
            tcp_sum = _df_tcp_txt.groupby("flags")["count"].sum().reset_index()
            total_t = tcp_sum["count"].sum()
            L.append("[ TCP FLAG SUMMARY ]")
            for _, r in tcp_sum.iterrows():
                pct = r["count"] / total_t * 100
                L.append(f"  {r['flags']:<10} : {int(r['count']):>8} packets  ({pct:.1f}%)")
            L.append(f"  {'TOTAL':<10} : {int(total_t):>8} packets")
            L.append("")

            L.append("[ TOP 20 SOURCE IPs BY PACKET COUNT ]")
            top_ip = (_df_tcp_txt.groupby("src_ip")["count"].sum()
                      .reset_index().sort_values("count", ascending=False).head(20))
            for i, (_, r) in enumerate(top_ip.iterrows(), 1):
                L.append(f"  #{i:<3} {r['src_ip']:<20} : {int(r['count']):>8} packets")
            L.append("")

            L.append("[ PACKET DETAIL (Source IP × Flag) ]")
            detail = (_df_tcp_txt.groupby(["src_ip", "flags"])["count"].sum()
                      .reset_index().sort_values("count", ascending=False))
            L.extend(_txt_table(detail.rename(columns={"src_ip": "Source IP", "flags": "TCP Flag", "count": "Packet Count"}),
                                ["Source IP", "TCP Flag", "Packet Count"]))
            L.append("")
        else:
            L.append("  (ไม่มีข้อมูล TCP — ตรวจสอบว่า tcpdump กำลังทำงาน)")
            L.append("")
        L.extend(_txt_footer())
        return "\n".join(L)

    # ── Dropdown เลือกประเภท TXT ─────────────────────────────────────
    TXT_REPORT_OPTIONS = {
        "🌐 ภาพรวมทั้งหมด (Full Overview)": ("overview",   "bot_analytics_overview"),
        "⚡ Performance อย่างเดียว":          ("performance","bot_analytics_performance"),
        "📡 Network Analytics อย่างเดียว":   ("network",    "bot_analytics_network"),
        "🔍 TCP Packet Analysis อย่างเดียว": ("tcp",        "bot_analytics_tcp"),
    }

    st.markdown('<div class="export-panel">', unsafe_allow_html=True)
    st.markdown('<h4>📥 เลือกรูปแบบ Export</h4>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.download_button(
            label="⬇️ Download Complete Analytics Report",
            data=output.getvalue(),
            file_name=f"bot_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download comprehensive Excel report with all analytics data",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("**📄 ดาวน์โหลดรายงาน .txt**")
        txt_report_choice = st.selectbox(
            "เลือกประเภทรายงาน TXT",
            options=list(TXT_REPORT_OPTIONS.keys()),
            index=0,
            help="เลือกว่าต้องการ export ข้อมูลส่วนไหนลงในไฟล์ .txt",
            label_visibility="collapsed",
        )
        _report_key, _report_prefix = TXT_REPORT_OPTIONS[txt_report_choice]
        if _report_key == "overview":
            _txt_content = _build_overview()
        elif _report_key == "performance":
            _txt_content = _build_performance()
        elif _report_key == "network":
            _txt_content = _build_network()
        else:
            _txt_content = _build_tcp()

        st.download_button(
            label=f"📄 Download  {txt_report_choice.split(' ', 1)[0]}  (.txt)",
            data=_txt_content.encode("utf-8"),
            file_name=f"{_report_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            help=f"ดาวน์โหลดรายงาน: {txt_report_choice}",
            use_container_width=True,
        )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Export Charts as Images", help="Save all charts as PNG files (ZIP)"):
            with st.spinner("📸 กำลัง render charts เป็นภาพ..."):
                try:
                    import zipfile
                    charts_to_export = []

                    # Build charts from available data
                    if not df_bot.empty:
                        fig_delay_exp = px.bar(
                            df_bot, x="Number of bot", y="Mean Delay (ms)",
                            text="Mean Delay (ms)",
                            title="Mean Delay per Bot (All IPs Combined)",
                            color="Mean Delay (ms)", color_continuous_scale="RdYlGn_r",
                            template="plotly_white"
                        )
                        fig_delay_exp.update_traces(texttemplate="%{text:.2f}ms", textposition="outside")
                        fig_delay_exp.update_layout(height=450, paper_bgcolor="white", plot_bgcolor="white")
                        charts_to_export.append(("01_mean_delay.png", fig_delay_exp))

                        fig_loss_exp = px.bar(
                            df_bot, x="Number of bot", y="Packet Loss (%)",
                            text="Packet Loss (%)",
                            title="Packet Loss per Bot (All IPs Combined)",
                            color="Packet Loss (%)", color_continuous_scale="RdYlGn_r",
                            template="plotly_white"
                        )
                        fig_loss_exp.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
                        fig_loss_exp.update_layout(height=450, paper_bgcolor="white", plot_bgcolor="white")
                        charts_to_export.append(("02_packet_loss.png", fig_loss_exp))

                    if not df_perf.empty:
                        df_melt_exp = df_perf.melt(
                            id_vars=["Number of bot"],
                            value_vars=["Avg CPU (%)", "Avg RAM (%)"],
                            var_name="Metric", value_name="Percentage"
                        )
                        fig_perf_exp = px.bar(
                            df_melt_exp, x="Number of bot", y="Percentage",
                            color="Metric", barmode="group", text="Percentage",
                            title="CPU and RAM Usage per Bot",
                            template="plotly_white",
                            color_discrete_sequence=["#FF4B4B", "#4B4BFF"]
                        )
                        fig_perf_exp.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
                        fig_perf_exp.update_layout(height=450, paper_bgcolor="white", plot_bgcolor="white")
                        charts_to_export.append(("03_cpu_ram.png", fig_perf_exp))

                    if not df_net.empty:
                        df_bitrate_exp = df_net.melt(
                            id_vars=["Number of bot"],
                            value_vars=["Tx Bitrate (kbps)", "Rx Bitrate (kbps)"],
                            var_name="Direction", value_name="kbps"
                        )
                        fig_bitrate_exp = px.bar(
                            df_bitrate_exp, x="Number of bot", y="kbps",
                            color="Direction", barmode="group",
                            title="Tx/Rx Bitrate Comparison",
                            template="plotly_white",
                            color_discrete_sequence=["#667eea", "#764ba2"]
                        )
                        fig_bitrate_exp.update_layout(height=450, paper_bgcolor="white", plot_bgcolor="white")
                        charts_to_export.append(("04_bitrate.png", fig_bitrate_exp))

                        df_bytes_exp = df_net.melt(
                            id_vars=["Number of bot"],
                            value_vars=["Total Tx Bytes", "Total Rx Bytes"],
                            var_name="Direction", value_name="Bytes"
                        )
                        fig_bytes_exp = px.bar(
                            df_bytes_exp, x="Number of bot", y="Bytes",
                            color="Direction", barmode="group",
                            title="Total Data Transfer",
                            template="plotly_white",
                            color_discrete_sequence=["#11998e", "#38ef7d"]
                        )
                        fig_bytes_exp.update_layout(height=450, paper_bgcolor="white", plot_bgcolor="white")
                        charts_to_export.append(("05_data_transfer.png", fig_bytes_exp))

                    df_tcp_exp = parse_tcp_raw()
                    if not df_tcp_exp.empty:
                        flag_summary_exp = df_tcp_exp.groupby("flags")["count"].sum().reset_index()
                        fig_tcp_exp = px.pie(
                            flag_summary_exp, values="count", names="flags",
                            title="TCP Flags Distribution (SYN vs ACK)",
                            hole=0.4, color_discrete_sequence=["#FF4B4B", "#4facfe", "#f59e0b"]
                        )
                        fig_tcp_exp.update_layout(height=450, paper_bgcolor="white", plot_bgcolor="white")
                        charts_to_export.append(("06_tcp_flags.png", fig_tcp_exp))

                    if not charts_to_export:
                        st.warning("⚠️ ไม่มีข้อมูลสำหรับสร้างกราฟ — กรุณาเพิ่มข้อมูล bot ก่อน")
                    else:
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                            for filename, fig in charts_to_export:
                                img_bytes = fig.to_image(format="png", width=1200, height=500, scale=2)
                                zf.writestr(filename, img_bytes)

                        st.download_button(
                            label=f"⬇️ Download {len(charts_to_export)} Charts (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"bot_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            use_container_width=True
                        )
                        st.success(f"✅ เตรียม {len(charts_to_export)} charts เรียบร้อย — กดปุ่มด้านบนเพื่อดาวน์โหลด")
                except ImportError:
                    st.error("❌ กรุณาติดตั้ง kaleido ก่อน: `pip install kaleido`")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")

    with col2:
        if st.button("📈 Generate PDF Report", help="Create a comprehensive PDF report"):
            with st.spinner("📄 กำลังสร้าง PDF report..."):
                try:
                    from reportlab.lib.pagesizes import A4
                    from reportlab.lib import colors
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.lib.units import cm
                    from reportlab.platypus import (
                        SimpleDocTemplate, Paragraph, Spacer, Table,
                        TableStyle, HRFlowable, Image as RLImage
                    )
                    from reportlab.lib.enums import TA_CENTER, TA_LEFT
                    from reportlab.pdfbase import pdfmetrics
                    from reportlab.pdfbase.ttfonts import TTFont
                    import tempfile

                    pdf_buffer = BytesIO()
                    doc = SimpleDocTemplate(
                        pdf_buffer, pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm
                    )

                    styles = getSampleStyleSheet()
                    style_title = ParagraphStyle(
                        "ReportTitle", parent=styles["Title"],
                        fontSize=20, textColor=colors.HexColor("#667eea"),
                        spaceAfter=6, alignment=TA_CENTER, fontName="Helvetica-Bold"
                    )
                    style_h1 = ParagraphStyle(
                        "H1", parent=styles["Heading1"],
                        fontSize=13, textColor=colors.white,
                        backColor=colors.HexColor("#667eea"),
                        spaceBefore=14, spaceAfter=6,
                        leftIndent=6, fontName="Helvetica-Bold"
                    )
                    style_h2 = ParagraphStyle(
                        "H2", parent=styles["Heading2"],
                        fontSize=11, textColor=colors.HexColor("#4a4f72"),
                        spaceBefore=8, spaceAfter=4, fontName="Helvetica-Bold"
                    )
                    style_body = ParagraphStyle(
                        "Body", parent=styles["Normal"],
                        fontSize=9, textColor=colors.HexColor("#1a1d3a"),
                        spaceAfter=4, leading=14
                    )
                    style_caption = ParagraphStyle(
                        "Caption", parent=styles["Normal"],
                        fontSize=8, textColor=colors.HexColor("#8890b5"),
                        alignment=TA_CENTER, spaceAfter=8
                    )

                    story = []
                    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # ── Cover ──────────────────────────────────────────
                    story.append(Spacer(1, 1.5*cm))
                    story.append(Paragraph("Bot Performance Analytics", style_title))
                    story.append(Paragraph("Comprehensive Dashboard Report", ParagraphStyle(
                        "Sub", parent=styles["Normal"], fontSize=12,
                        textColor=colors.HexColor("#764ba2"), alignment=TA_CENTER
                    )))
                    story.append(Spacer(1, 0.4*cm))
                    story.append(Paragraph(f"Generated: {generated_at}", ParagraphStyle(
                        "Gen", parent=styles["Normal"], fontSize=9,
                        textColor=colors.HexColor("#8890b5"), alignment=TA_CENTER
                    )))
                    story.append(HRFlowable(width="100%", thickness=2,
                                            color=colors.HexColor("#667eea"),
                                            spaceAfter=16))

                    # ── Executive Summary ──────────────────────────────
                    story.append(Paragraph("Executive Summary", style_h1))
                    story.append(Spacer(1, 0.2*cm))

                    summary_data = [
                        ["Metric", "Value"],
                        ["Total Bots Monitored", str(len(df_merged))],
                        ["Avg Mean Delay (ms)",
                         f"{df_merged['Mean Delay (ms)'].mean():.2f}" if "Mean Delay (ms)" in df_merged.columns else "N/A"],
                        ["Avg Packet Loss (%)",
                         f"{df_merged['Packet Loss (%)'].mean():.2f}%" if "Packet Loss (%)" in df_merged.columns else "N/A"],
                        ["Avg CPU Usage (%)",
                         f"{df_merged['Avg CPU (%)'].mean():.2f}%" if "Avg CPU (%)" in df_merged.columns else "N/A"],
                        ["Avg RAM Usage (%)",
                         f"{df_merged['Avg RAM (%)'].mean():.2f}%" if "Avg RAM (%)" in df_merged.columns else "N/A"],
                        ["Total Upload",
                         format_bytes(int(df_net["Total Tx Bytes"].sum())) if not df_net.empty else "N/A"],
                        ["Total Download",
                         format_bytes(int(df_net["Total Rx Bytes"].sum())) if not df_net.empty else "N/A"],
                    ]
                    tbl_summary = Table(summary_data, colWidths=[9*cm, 8*cm])
                    tbl_summary.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667eea")),
                        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
                        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE",   (0, 0), (-1, -1), 9),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                         [colors.HexColor("#f4f6ff"), colors.white]),
                        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#dde3ff")),
                        ("ALIGN",      (1, 0), (1, -1), "CENTER"),
                        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]))
                    story.append(tbl_summary)
                    story.append(Spacer(1, 0.5*cm))

                    # ── Bot Performance Detail ─────────────────────────
                    if not df_merged.empty:
                        story.append(Paragraph("Bot Performance Detail", style_h1))
                        story.append(Spacer(1, 0.2*cm))
                        display_cols = [c for c in [
                            "Number of bot", "Mean Delay (ms)", "Packet Loss (%)",
                            "IP Addresses", "Avg CPU (%)", "Avg RAM (%)"
                        ] if c in df_merged.columns]

                        header = [c.replace(" (%)", "\n(%)").replace(" (ms)", "\n(ms)")
                                  for c in display_cols]
                        rows = [[str(round(row[c], 2)) if isinstance(row[c], float) else str(row[c])
                                 for c in display_cols]
                                for _, row in df_merged.iterrows()]
                        col_w = [17 * cm / len(display_cols)] * len(display_cols)
                        tbl_bot = Table([header] + rows, colWidths=col_w, repeatRows=1)
                        tbl_bot.setStyle(TableStyle([
                            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#764ba2")),
                            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
                            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE",      (0, 0), (-1, -1), 8),
                            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                            ("ROWBACKGROUNDS",(0, 1), (-1, -1),
                             [colors.HexColor("#f4f6ff"), colors.white]),
                            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dde3ff")),
                            ("TOPPADDING",    (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]))
                        story.append(tbl_bot)
                        story.append(Spacer(1, 0.5*cm))

                    # ── Network Analytics ──────────────────────────────
                    if not df_net.empty:
                        story.append(Paragraph("Network Analytics", style_h1))
                        story.append(Spacer(1, 0.2*cm))
                        net_cols = [c for c in df_net.columns]
                        net_header = [c.replace(" (kbps)", "\n(kbps)").replace(" Bytes", "\nBytes")
                                      for c in net_cols]
                        net_rows = [[str(round(row[c], 2)) if isinstance(row[c], float) else str(row[c])
                                     for c in net_cols]
                                    for _, row in df_net.iterrows()]
                        net_col_w = [17 * cm / len(net_cols)] * len(net_cols)
                        tbl_net = Table([net_header] + net_rows, colWidths=net_col_w, repeatRows=1)
                        tbl_net.setStyle(TableStyle([
                            ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#11998e")),
                            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
                            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE",      (0, 0), (-1, -1), 8),
                            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                            ("ROWBACKGROUNDS",(0, 1), (-1, -1),
                             [colors.HexColor("#f0fff8"), colors.white]),
                            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#c3f0e0")),
                            ("TOPPADDING",    (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]))
                        story.append(tbl_net)
                        story.append(Spacer(1, 0.5*cm))

                    # ── Embedded Chart Images ──────────────────────────
                    charts_for_pdf = []
                    if not df_bot.empty:
                        fig_d = px.bar(df_bot, x="Number of bot", y="Mean Delay (ms)",
                                       title="Mean Delay per Bot", template="plotly_white",
                                       color_continuous_scale="RdYlGn_r", color="Mean Delay (ms)")
                        fig_d.update_layout(height=350, paper_bgcolor="white", plot_bgcolor="white")
                        charts_for_pdf.append(("Mean Delay per Bot", fig_d))

                        fig_l = px.bar(df_bot, x="Number of bot", y="Packet Loss (%)",
                                       title="Packet Loss per Bot", template="plotly_white",
                                       color_continuous_scale="RdYlGn_r", color="Packet Loss (%)")
                        fig_l.update_layout(height=350, paper_bgcolor="white", plot_bgcolor="white")
                        charts_for_pdf.append(("Packet Loss per Bot", fig_l))

                    if not df_perf.empty:
                        df_m = df_perf.melt(id_vars=["Number of bot"],
                                            value_vars=["Avg CPU (%)", "Avg RAM (%)"],
                                            var_name="Metric", value_name="Percentage")
                        fig_p = px.bar(df_m, x="Number of bot", y="Percentage",
                                       color="Metric", barmode="group",
                                       title="CPU & RAM Usage per Bot", template="plotly_white",
                                       color_discrete_sequence=["#FF4B4B", "#4B4BFF"])
                        fig_p.update_layout(height=350, paper_bgcolor="white", plot_bgcolor="white")
                        charts_for_pdf.append(("CPU & RAM Usage", fig_p))

                    if not df_net.empty:
                        df_br = df_net.melt(id_vars=["Number of bot"],
                                            value_vars=["Tx Bitrate (kbps)", "Rx Bitrate (kbps)"],
                                            var_name="Direction", value_name="kbps")
                        fig_br = px.bar(df_br, x="Number of bot", y="kbps",
                                        color="Direction", barmode="group",
                                        title="Tx/Rx Bitrate", template="plotly_white",
                                        color_discrete_sequence=["#667eea", "#764ba2"])
                        fig_br.update_layout(height=350, paper_bgcolor="white", plot_bgcolor="white")
                        charts_for_pdf.append(("Tx/Rx Bitrate", fig_br))

                    if charts_for_pdf:
                        story.append(Paragraph("Charts & Visualizations", style_h1))
                        story.append(Spacer(1, 0.3*cm))
                        
                        for idx_c, (chart_title, fig) in enumerate(charts_for_pdf):
                            try:
                                # 1. สร้างภาพเก็บไว้ใน Memory แทนการเซฟลงเครื่อง
                                img_bytes = fig.to_image(format="png", width=900, height=380, scale=2)
                                img_buffer = BytesIO(img_bytes)
                                
                                # 2. นำภาพจาก Memory ไปใส่ใน ReportLab
                                story.append(Paragraph(chart_title, style_h2))
                                rl_img = RLImage(img_buffer, width=17*cm, height=7.2*cm)
                                story.append(rl_img)
                                story.append(Paragraph(
                                    f"Figure: {chart_title} — Generated {generated_at}", style_caption
                                ))
                                story.append(Spacer(1, 0.4*cm))
                            except Exception as e:
                                # ถ้ากราฟไหนมีปัญหา ให้ข้ามไปทำกราฟต่อไปแทนที่จะพังทั้งระบบ
                                print(f"Skipping chart '{chart_title}' due to error: {e}")

                    # ── Footer note ────────────────────────────────────
                    story.append(HRFlowable(width="100%", thickness=1,
                                            color=colors.HexColor("#dde3ff"), spaceBefore=12))
                    story.append(Paragraph(
                        "Bot Performance Analytics Dashboard  •  Pling site/49  •  "
                        "นายพุฒิเมธ บุตรเงิน | นายพชร เสืออ่ำ | นายเฉลิมพร บุญชู",
                        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7.5,
                                       textColor=colors.HexColor("#8890b5"), alignment=TA_CENTER)
                    ))

                    doc.build(story)
                    pdf_bytes = pdf_buffer.getvalue()

                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"bot_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("✅ PDF report พร้อมดาวน์โหลดแล้ว!")

                except ImportError as e:
                    st.error(f"❌ กรุณาติดตั้ง library ที่ต้องการก่อน: `pip install reportlab kaleido`\nError: {e}")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาดในการสร้าง PDF: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    if not bot_net_result and not st.session_state.bot_results:
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">🚀</span>
            <h3>Ready to Start Monitoring</h3>
            <p>ยังไม่มีข้อมูล network — เพิ่มข้อมูล bot เพื่อดู analytics</p>
            <p>กำหนดค่า bot ด้านบน แล้วกด <strong>Add Bot Data</strong> ✨</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="dashboard-footer">
        <div class="footer-title">🤖 Bot Performance Analytics Dashboard</div>
        <div class="footer-tagline">Real-time monitoring &nbsp;•&nbsp; Advanced analytics &nbsp;•&nbsp; Beautiful visualizations</div>
        <div class="footer-divider"></div>
        <div class="footer-team">NT National Telecom</div>
        <div class="footer-team">นักศึกษาสหกิจศึกษามหาวิทยาลัยเทคโนโลยีสุรนารี</div>
        <div class="footer-meta">Last updated: {}</div>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()