"""
app.py - HomeIQ: UK Rent vs. Buy Analyser
Run:     streamlit run app.py
Install: pip install streamlit plotly pandas numpy requests openai fpdf2
"""

import numpy as np
import pandas as pd
import streamlit as st
import requests
from io import StringIO
import openai
from fpdf import FPDF
from datetime import date

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="HomeIQ - Rent vs Buy UK", page_icon="logo.png", layout="wide")

# ── Global CSS — Premium Dark Theme ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --navy:      #0a0e1a;
    --navy-2:    #111827;
    --navy-3:    #1a2235;
    --navy-4:    #243048;
    --gold:      #c9a84c;
    --gold-light:#e8c97a;
    --gold-dim:  #7a6030;
    --cream:     #f5f0e8;
    --white:     #ffffff;
    --muted:     #8899aa;
}

.stApp, [data-testid="stAppViewContainer"] {
    background: var(--navy) !important;
    font-family: 'DM Sans', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.stDeployButton { display: none !important; }

[data-testid="stSidebar"] {
    background: #0d1526 !important;
    border-right: 1px solid #2a3550 !important;
}
[data-testid="stSidebar"] * {
    color: #dde6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stToggle label {
    color: #b0c0d0 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stSidebar"] h1 {
    font-family: 'Playfair Display', serif !important;
    color: var(--gold) !important;
    font-size: 22px !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput > div > div > input,
[data-testid="stSidebar"] input {
    background: #1a2640 !important;
    border: 1px solid #2a3550 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}

/* ── Selectbox dropdown popover ── */
[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="popover"],
div[data-baseweb="select"] ul,
div[data-baseweb="menu"] {
    background: #1a2640 !important;
    border: 1px solid #2a3550 !important;
    border-radius: 8px !important;
}
div[data-baseweb="menu"] li,
div[data-baseweb="option"] {
    background: #1a2640 !important;
    color: #f5f0e8 !important;
}
div[data-baseweb="option"]:hover,
div[data-baseweb="option"][aria-selected="true"] {
    background: #243048 !important;
    color: #c9a84c !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
[data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
[data-testid="stSidebar"] .stSlider span {
    color: #b0c0d0 !important;
    font-size: 13px !important;
}

.stMarkdown, .stText, p, li, span, label, div {
    color: var(--cream) !important;
    font-family: 'DM Sans', sans-serif !important;
}
h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    color: var(--white) !important;
}

/* ── Dataframe / table text ── */
[data-testid="stDataFrame"] {
    background: var(--navy-3) !important;
}
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th {
    color: #ffffff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
[data-testid="stDataFrame"] thead th {
    background: var(--navy-4) !important;
    color: var(--gold) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Caption / small text ── */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #aabbcc !important;
    font-size: 13px !important;
}

/* ── Tab content text ── */
[data-testid="stTabContent"] p,
[data-testid="stTabContent"] span,
[data-testid="stTabContent"] div {
    color: var(--cream) !important;
}

/* ── Table (st.table) ── */
table { width: 100%; border-collapse: collapse; }
table td, table th {
    color: var(--white) !important;
    background: var(--navy-3) !important;
    border: 1px solid var(--navy-4) !important;
    padding: 8px 12px !important;
    font-size: 13px !important;
}
table thead th {
    background: var(--navy-4) !important;
    color: var(--gold) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

[data-testid="stMetric"] {
    background: var(--navy-3) !important;
    border: 1px solid var(--navy-4) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
    color: var(--white) !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 28px !important;
}

[data-testid="stTabs"] [role="tablist"] {
    background: var(--navy-2) !important;
    border-bottom: 1px solid var(--navy-4) !important;
    gap: 4px;
    padding: 4px 8px 0;
}
[data-testid="stTabs"] [role="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500;
    padding: 10px 18px !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.2s;
}
[data-testid="stTabs"] [role="tab"]:hover { color: var(--gold-light) !important; background: var(--navy-3) !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: var(--navy-3) !important;
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}
[data-testid="stTabContent"] {
    background: var(--navy-2) !important;
    border: 1px solid var(--navy-4) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    padding: 24px !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--gold), var(--gold-dim)) !important;
    color: var(--navy) !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(201,168,76,0.35) !important;
}
.stDownloadButton > button {
    background: var(--navy-3) !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold-dim) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

[data-testid="stAlert"] {
    background: var(--navy-3) !important;
    border-radius: 10px !important;
    border-left-width: 3px !important;
}
[data-testid="stDataFrame"] {
    background: var(--navy-3) !important;
    border: 1px solid var(--navy-4) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] {
    background: var(--navy-3) !important;
    border: 1px solid var(--navy-4) !important;
    border-radius: 10px !important;
}
hr { border-color: var(--navy-4) !important; margin: 24px 0 !important; }
[data-testid="stChatMessage"] {
    background: var(--navy-3) !important;
    border: 1px solid var(--navy-4) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--navy-3) !important;
    border: 1px solid var(--navy-4) !important;
    color: var(--white) !important;
    border-radius: 10px !important;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--navy-2); }
::-webkit-scrollbar-thumb { background: var(--navy-4); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ───────────────────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor="#111827", plot_bgcolor="#1a2235",
    font=dict(color="#f5f0e8", family="DM Sans"),
    xaxis=dict(gridcolor="#243048", linecolor="#243048"),
    yaxis=dict(gridcolor="#243048", linecolor="#243048"),
    legend=dict(
        bgcolor="rgba(26,34,53,0.9)",
        bordercolor="#2a3550",
        borderwidth=1,
        font=dict(color="#f5f0e8", size=12),
    ),
)
C = dict(gold="#c9a84c", green="#2dd4a0", red="#f87171", blue="#60a5fa", muted="#8899aa")

# ── Live Data: Bank of England & ONS ──────────────────────────────────────
@st.cache_data(show_spinner="Fetching live data from Bank of England & ONS...", ttl=3600)
def fetch_live_data():
    data = {}

    # ── Bank of England: Base Rate (IUMBEDR) ──
    try:
        boe_url = (
            "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp"
            "?csv.x=yes&Datefrom=01/Jan/2020&Dateto=now"
            "&SeriesCodes=IUMBEDR&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N"
        )
        resp = requests.get(boe_url, timeout=10)
        resp.raise_for_status()
        df_boe = pd.read_csv(StringIO(resp.text), skiprows=1, names=["DATE", "base_rate"])
        df_boe["DATE"] = pd.to_datetime(df_boe["DATE"], dayfirst=True, errors="coerce")
        df_boe["base_rate"] = pd.to_numeric(df_boe["base_rate"], errors="coerce")
        df_boe = df_boe.dropna()
        data["base_rate_current"] = round(float(df_boe["base_rate"].iloc[-1]), 2)
    except Exception:
        data["base_rate_current"] = 3.75

    # ── Bank of England: 2yr & 5yr Fixed Mortgage Rates ──
    try:
        mort_url = (
            "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp"
            "?csv.x=yes&Datefrom=01/Jan/2020&Dateto=now"
            "&SeriesCodes=IUMBV34,IUMBV42&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N"
        )
        resp = requests.get(mort_url, timeout=10)
        resp.raise_for_status()
        df_mort = pd.read_csv(StringIO(resp.text), skiprows=1, names=["DATE", "rate_2yr", "rate_5yr"])
        df_mort["DATE"] = pd.to_datetime(df_mort["DATE"], dayfirst=True, errors="coerce")
        df_mort["rate_2yr"] = pd.to_numeric(df_mort["rate_2yr"], errors="coerce")
        df_mort["rate_5yr"] = pd.to_numeric(df_mort["rate_5yr"], errors="coerce")
        df_mort = df_mort.dropna(subset=["DATE"])
        data["rate_2yr_current"] = round(float(df_mort["rate_2yr"].dropna().iloc[-1]), 2)
        data["rate_5yr_current"] = round(float(df_mort["rate_5yr"].dropna().iloc[-1]), 2)
    except Exception:
        data["rate_2yr_current"] = 4.2
        data["rate_5yr_current"] = 4.4

    # ── ONS: CPI Inflation (D7G7 = CPI 12-month rate) ──
    try:
        ons_cpi_url = "https://api.ons.gov.uk/v1/datasets/mm23/timeseries/D7G7/data"
        resp = requests.get(ons_cpi_url, timeout=10)
        resp.raise_for_status()
        ons_data = resp.json()
        months = ons_data.get("months", [])
        df_cpi = pd.DataFrame(months)[["date", "value"]].rename(columns={"date": "DATE", "value": "cpi"})
        df_cpi["DATE"] = pd.to_datetime(df_cpi["DATE"], format="%Y %b", errors="coerce")
        df_cpi["cpi"] = pd.to_numeric(df_cpi["cpi"], errors="coerce")
        df_cpi = df_cpi.dropna().sort_values("DATE")
        data["cpi_current"] = round(float(df_cpi["cpi"].iloc[-1]), 1)
    except Exception:
        data["cpi_current"] = 3.0

    # ── ONS: Average Weekly Earnings growth (KAB9) ──
    try:
        ons_earn_url = "https://api.ons.gov.uk/v1/datasets/lms/timeseries/KAB9/data"
        resp = requests.get(ons_earn_url, timeout=10)
        resp.raise_for_status()
        earn_data = resp.json()
        months = earn_data.get("months", [])
        df_earn = pd.DataFrame(months)[["date", "value"]].rename(columns={"date": "DATE", "value": "earnings_growth"})
        df_earn["DATE"] = pd.to_datetime(df_earn["DATE"], format="%Y %b", errors="coerce")
        df_earn["earnings_growth"] = pd.to_numeric(df_earn["earnings_growth"], errors="coerce")
        df_earn = df_earn.dropna().sort_values("DATE")
        data["earnings_growth_current"] = round(float(df_earn["earnings_growth"].iloc[-1]), 1)
    except Exception:
        data["earnings_growth_current"] = 5.9

    return data

live = fetch_live_data()

# ── Region config ──────────────────────────────────────────────────────────
REGIONS = {
    "London":        {"avg_price": 520000, "rental_yield": 3.2},
    "South East":    {"avg_price": 380000, "rental_yield": 3.8},
    "South West":    {"avg_price": 310000, "rental_yield": 4.1},
    "East Midlands": {"avg_price": 230000, "rental_yield": 4.6},
    "West Midlands": {"avg_price": 245000, "rental_yield": 4.5},
    "Yorkshire":     {"avg_price": 200000, "rental_yield": 5.0},
    "North West":    {"avg_price": 210000, "rental_yield": 5.2},
    "North East":    {"avg_price": 155000, "rental_yield": 5.8},
    "Wales":         {"avg_price": 195000, "rental_yield": 4.8},
    "Scotland":      {"avg_price": 195000, "rental_yield": 4.7},
}

# ── Financial helpers ──────────────────────────────────────────────────────
def compute_stamp_duty(price, ftb):
    if ftb:
        if price <= 425000: return 0
        elif price <= 625000: return round((price - 425000) * 0.05)
    bands = [(250000, 0.0), (675000, 0.05), (925000, 0.10), (1500000, 0.12)]
    tax, prev = 0.0, 0.0
    for threshold, rate in bands:
        if price <= prev: break
        tax += (min(price, threshold) - prev) * rate
        prev = threshold
    return round(tax)

def run_analysis(price, deposit_pct, mortgage_rate, monthly_rent, appreciation, horizon, ftb):
    deposit = price * deposit_pct / 100
    loan = price - deposit
    stamp_duty = compute_stamp_duty(price, ftb)
    r = mortgage_rate / 100 / 12
    n = 25 * 12
    monthly_mortgage = loan * (r * (1 + r)**n) / ((1 + r)**n - 1)
    records = []
    cum_rent, cum_buy = 0.0, deposit + stamp_duty
    prop_value, loan_balance = price, loan
    for year in range(1, horizon + 1):
        cum_rent += monthly_rent * 12
        cum_buy += monthly_mortgage * 12 + prop_value * 0.01
        prop_value *= (1 + appreciation / 100)
        interest = loan_balance * (mortgage_rate / 100)
        principal = min(monthly_mortgage * 12 - interest, loan_balance)
        loan_balance = max(0, loan_balance - principal)
        equity = prop_value - loan_balance
        records.append({"Year": year,
                        "Renting (total paid)": round(cum_rent),
                        "Buying (total paid)": round(cum_buy),
                        "Equity gained": round(equity),
                        "Property value": round(prop_value)})
    return pd.DataFrame(records), round(monthly_mortgage), stamp_duty

def check_affordability(gross_income, partner_income, property_price, deposit_pct,
                         monthly_expenses, monthly_rent, mortgage_rate):
    total_income = gross_income + partner_income
    loan = property_price * (1 - deposit_pct / 100)
    r = mortgage_rate / 100 / 12
    n = 25 * 12
    monthly_mortgage = loan * (r*(1+r)**n) / ((1+r)**n - 1)
    r_stress = (mortgage_rate + 3.0) / 100 / 12
    monthly_mortgage_stressed = loan * (r_stress*(1+r_stress)**n) / ((1+r_stress)**n - 1)
    net_monthly = total_income * 0.70 / 12
    stressed_disp = net_monthly - monthly_mortgage_stressed - monthly_expenses
    return {
        "loan": round(loan),
        "total_income": round(total_income),
        "max_mortgage_4x": round(total_income * 4),
        "max_mortgage_45x": round(total_income * 4.5),
        "max_mortgage_5x": round(total_income * 5),
        "monthly_mortgage": round(monthly_mortgage),
        "monthly_mortgage_stressed": round(monthly_mortgage_stressed),
        "net_monthly": round(net_monthly),
        "disposable_buying": round(net_monthly - monthly_mortgage - monthly_expenses),
        "disposable_renting": round(net_monthly - monthly_rent - monthly_expenses),
        "stressed_disposable": round(stressed_disp),
        "affordable_4x": loan <= total_income * 4,
        "affordable_45x": loan <= total_income * 4.5,
        "affordable_5x": loan <= total_income * 5,
        "passes_stress_test": stressed_disp > 0,
    }

# ── PDF export ─────────────────────────────────────────────────────────────
def generate_pdf(region, property_price, deposit_pct, mortgage_rate, monthly_rent,
                 appreciation, horizon, ftb, df, monthly_mortgage, stamp_duty, breakeven):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(10, 14, 26)
    pdf.rect(0, 0, 210, 35, "F")
    pdf.set_text_color(201, 168, 76)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(10, 8)
    pdf.cell(0, 12, "HomeIQ - Rent vs. Buy Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(180, 180, 180)
    pdf.set_xy(10, 22)
    pdf.cell(0, 8, f"Generated {date.today().strftime('%d %B %Y')}  |  Region: {region}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)
    verdict_text = f"BUYING WINS after Year {breakeven}" if breakeven else "RENTING IS MORE COST-EFFECTIVE within this horizon"
    pdf.set_fill_color(220, 255, 220) if breakeven else pdf.set_fill_color(255, 245, 200)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_x(10)
    pdf.cell(190, 12, f"  Verdict: {verdict_text}", ln=True, fill=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Live Market Context", ln=True)
    pdf.set_font("Helvetica", "", 10)
    live_rows = [
        ("BoE Base Rate", f"{live['base_rate_current']}%"),
        ("2-Year Fixed Rate", f"{live['rate_2yr_current']}%"),
        ("5-Year Fixed Rate", f"{live['rate_5yr_current']}%"),
        ("CPI Inflation", f"{live['cpi_current']}%"),
        ("Avg Earnings Growth", f"{live['earnings_growth_current']}%"),
    ]
    for i, (label, value) in enumerate(live_rows):
        pdf.set_fill_color(248, 248, 255) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        pdf.set_x(10)
        pdf.cell(100, 8, f"  {label}", border="B", fill=True)
        pdf.cell(90, 8, f"  {value}", border="B", fill=True, ln=True)
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Your Analysis", ln=True)
    pdf.set_font("Helvetica", "", 10)
    figures = [
        ("Property Price", f"£{property_price:,}"),
        ("Deposit", f"£{int(property_price*deposit_pct/100):,} ({deposit_pct}%)"),
        ("Stamp Duty", f"£{stamp_duty:,}" + (" (FTB relief)" if ftb else "")),
        ("Monthly Mortgage", f"£{monthly_mortgage:,}"),
        ("Monthly Rent", f"£{monthly_rent:,}"),
        ("Assumed Appreciation", f"{appreciation}% / yr"),
        ("Horizon", f"{horizon} years"),
        ("Break-even", "Year " + str(breakeven) if breakeven else "Not reached"),
        (f"Property Value (Yr {horizon})", f"£{df['Property value'].iloc[-1]:,.0f}"),
        (f"Equity (Yr {horizon})", f"£{df['Equity gained'].iloc[-1]:,.0f}"),
        (f"Total Rent (Yr {horizon})", f"£{df['Renting (total paid)'].iloc[-1]:,.0f}"),
        (f"Total Buy Cost (Yr {horizon})", f"£{df['Buying (total paid)'].iloc[-1]:,.0f}"),
    ]
    for i, (label, value) in enumerate(figures):
        pdf.set_fill_color(248, 248, 255) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        pdf.set_x(10)
        pdf.cell(100, 8, f"  {label}", border="B", fill=True)
        pdf.cell(90, 8, f"  {value}", border="B", fill=True, ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Year-by-Year Breakdown", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(10, 14, 26)
    pdf.set_text_color(201, 168, 76)
    headers = ["Year", "Rent Paid", "Buy Cost", "Equity", "Property Value"]
    col_w = [15, 45, 45, 45, 45]
    for h, w in zip(headers, col_w):
        pdf.cell(w, 8, h, fill=True, border=1)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 9)
    for i, row in df.iterrows():
        pdf.set_fill_color(248, 248, 255) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        vals = [str(int(row["Year"])),
                f"£{row['Renting (total paid)']:,.0f}",
                f"£{row['Buying (total paid)']:,.0f}",
                f"£{row['Equity gained']:,.0f}",
                f"£{row['Property value']:,.0f}"]
        for v, w in zip(vals, col_w):
            pdf.cell(w, 7, v, border=1, fill=True)
        pdf.ln()
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 5, "Disclaimer: Illustrative purposes only. Not financial advice. "
                   "Data sourced from Bank of England and ONS public APIs.")
    return bytes(pdf.output())


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h1>HomeIQ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8899aa;font-size:12px;margin-top:-12px;'>UK Property Intelligence</p>",
                unsafe_allow_html=True)
    st.divider()

    region = st.selectbox("UK Region", list(REGIONS.keys()))
    default_price = REGIONS[region]["avg_price"]
    first_time_buyer = st.toggle("First-time buyer", value=False,
                                  help="No stamp duty on properties up to £425,000.")
    property_price = st.number_input("Property Price (£)", 50000, 2000000, value=default_price, step=5000)
    deposit_pct = st.slider("Deposit (%)", 5, 50, 20)

    # Pre-fill mortgage rate from BoE 5yr live data
    default_rate = live["rate_5yr_current"]
    mortgage_rate = st.slider("Mortgage Rate (%)", 1.0, 10.0, float(default_rate), 0.1,
                               help=f"BoE live 5-yr fixed rate: {live['rate_5yr_current']}%")
    monthly_rent = st.number_input("Monthly Rent (£)", 300, 10000,
                                    value=int(property_price * REGIONS[region]["rental_yield"] / 100 / 12), step=50)
    appreciation = st.slider("Assumed Annual Appreciation (%)", 0.0, 10.0, 3.5, 0.1,
                              help="UK long-run average is ~3-4%. Adjust to your expectation.")
    horizon = st.slider("Years to analyse", 5, 30, 15)

    st.divider()
    # Live data mini-dashboard in sidebar
    st.markdown("<p style='color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:0.1em;'>Live Market Data</p>",
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
        <div style="background:#1a2235;border:1px solid #243048;border-radius:8px;padding:10px;">
            <div style="color:#8899aa;font-size:9px;text-transform:uppercase;letter-spacing:0.08em;">BoE Base Rate</div>
            <div style="font-family:'Playfair Display',serif;font-size:20px;color:#c9a84c;font-weight:700;">{live['base_rate_current']}%</div>
        </div>
        <div style="background:#1a2235;border:1px solid #243048;border-radius:8px;padding:10px;">
            <div style="color:#8899aa;font-size:9px;text-transform:uppercase;letter-spacing:0.08em;">CPI Inflation</div>
            <div style="font-family:'Playfair Display',serif;font-size:20px;color:#60a5fa;font-weight:700;">{live['cpi_current']}%</div>
        </div>
        <div style="background:#1a2235;border:1px solid #243048;border-radius:8px;padding:10px;">
            <div style="color:#8899aa;font-size:9px;text-transform:uppercase;letter-spacing:0.08em;">2yr Fixed</div>
            <div style="font-family:'Playfair Display',serif;font-size:20px;color:#f87171;font-weight:700;">{live['rate_2yr_current']}%</div>
        </div>
        <div style="background:#1a2235;border:1px solid #243048;border-radius:8px;padding:10px;">
            <div style="color:#8899aa;font-size:9px;text-transform:uppercase;letter-spacing:0.08em;">Earnings Growth</div>
            <div style="font-family:'Playfair Display',serif;font-size:20px;color:#2dd4a0;font-weight:700;">{live['earnings_growth_current']}%</div>
        </div>
    </div>
    <div style="color:#8899aa;font-size:10px;">Live data: Bank of England IADB & ONS API</div>
    """, unsafe_allow_html=True)

# Load API keys from Streamlit secrets (set in .streamlit/secrets.toml locally,
# or in the Streamlit Community Cloud dashboard when deployed)
OPENAI_KEY = st.secrets["OPENAI_KEY"]
RAPIDAPI_KEY = st.secrets["RAPIDAPI_KEY"]

# ── Compute analysis ───────────────────────────────────────────────────────
df, monthly_mortgage, stamp_duty = run_analysis(
    property_price, deposit_pct, mortgage_rate,
    monthly_rent, appreciation, horizon, first_time_buyer
)
breakeven = None
for _, row in df.iterrows():
    # Net cost of buying = total paid - equity built above initial deposit
    initial_deposit = property_price * deposit_pct / 100
    net_buying_cost = row["Buying (total paid)"] - (row["Equity gained"] - initial_deposit)
    if net_buying_cost < row["Renting (total paid)"]:
        breakeven = int(row["Year"])
        break

# ── Hero header ────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#111827 0%,#1a2235 50%,#111827 100%);
            border:1px solid #243048;border-radius:16px;padding:40px 48px;
            margin-bottom:32px;position:relative;overflow:hidden;">
    <div style="position:absolute;top:-60px;right:-60px;width:240px;height:240px;
                background:radial-gradient(circle,rgba(201,168,76,0.12) 0%,transparent 70%);border-radius:50%;"></div>
    <div style="font-family:'Playfair Display',serif;font-size:13px;color:#c9a84c;
                letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;">
        UK Property Intelligence
    </div>
    <h1 style="font-family:'Playfair Display',serif;font-size:42px;color:#ffffff;
               margin:0 0 12px 0;font-weight:900;line-height:1.1;">
        Should You Rent<br>or Buy in {region}?
    </h1>
    <p style="color:#8899aa;font-size:15px;max-width:580px;line-height:1.6;margin:0;">
        Powered by live <strong style="color:#c9a84c;">Bank of England</strong> and
        <strong style="color:#c9a84c;">ONS</strong> data. Adjust your inputs on the left
        and explore your personalised financial forecast below.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Key metrics ────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Monthly Mortgage", f"£{monthly_mortgage:,}", f"£{monthly_mortgage - monthly_rent:+,} vs rent")
c2.metric("Deposit Required", f"£{int(property_price * deposit_pct / 100):,}")
c3.metric("Stamp Duty", f"£{stamp_duty:,}", "FTB relief ✅" if first_time_buyer else None)
c4.metric("Break-even", f"Year {breakeven}" if breakeven else "Beyond horizon",
          "Buying wins ✅" if breakeven else "Renting wins ⚠️",
          delta_color="normal" if breakeven else "inverse")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────
tab_verdict, tab_analysis, tab_afford, tab_wait, tab_ai = st.tabs([
    "① Verdict", "② Deep Analysis", "③ Can I Afford This?", "④ Cost of Waiting", "⑤ AI Advisor"
])

# ── TAB 1: Verdict ─────────────────────────────────────────────────────────
with tab_verdict:
    st.markdown("<div style='color:#8899aa;font-size:13px;margin-bottom:20px;'>Start here. Adjust your inputs in the sidebar and see your personalised rent vs buy verdict below.</div>", unsafe_allow_html=True)
    if breakeven:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d2b1f,#1a3a2a);border:1px solid #2dd4a044;
                    border-left:4px solid #2dd4a0;border-radius:12px;padding:20px 24px;margin-bottom:24px;">
            <div style="font-family:'Playfair Display',serif;font-size:18px;color:#2dd4a0;font-weight:700;">
                Buying becomes the smarter choice after Year {breakeven}</div>
            <div style="color:#8899aa;font-size:14px;margin-top:6px;">
                With an assumed appreciation of <strong style="color:#c9a84c;">{appreciation}%/yr</strong>,
                if you plan to stay longer than {breakeven} years, buying builds more wealth than renting.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#2b1a0d,#3a2a1a);border:1px solid #f8717144;
                    border-left:4px solid #f87171;border-radius:12px;padding:20px 24px;margin-bottom:24px;">
            <div style="font-family:'Playfair Display',serif;font-size:18px;color:#f87171;font-weight:700;">
                Renting is more cost-effective within {horizon} years</div>
            <div style="color:#8899aa;font-size:14px;margin-top:6px;">
                Try increasing your deposit, adjusting appreciation, or choosing a lower price point.
            </div>
        </div>""", unsafe_allow_html=True)

    # ── AI-Generated Personalised Verdict ─────────────────────────────────
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:18px;color:#fff;margin-bottom:8px;'>🤖 AI Analysis</div>", unsafe_allow_html=True)

    # Build a cache key from all inputs — regenerate only when inputs change
    verdict_cache_key = f"{region}_{property_price}_{deposit_pct}_{mortgage_rate}_{monthly_rent}_{appreciation}_{horizon}_{first_time_buyer}"

    if st.session_state.get("verdict_cache_key") != verdict_cache_key:
        verdict_prompt = f"""You are a concise, expert UK property financial advisor. 
Write a 4-5 sentence plain-English analysis of this person's rent vs buy situation.
Reference their specific numbers directly. Be honest about trade-offs.
Do NOT use bullet points or headers — write flowing prose only.
Do NOT start with "Based on" — vary your opening.

USER'S SITUATION:
- Region: {region}
- Property price: £{property_price:,}
- Deposit: {deposit_pct}% (£{int(property_price * deposit_pct / 100):,})
- Mortgage rate: {mortgage_rate}%
- Monthly mortgage: £{monthly_mortgage:,}
- Monthly rent alternative: £{monthly_rent:,}
- Stamp duty: £{stamp_duty:,} {"(FTB relief applied)" if first_time_buyer else ""}
- Assumed annual appreciation: {appreciation}%
- Analysis horizon: {horizon} years
- Break-even year: {"Year " + str(breakeven) if breakeven else "Not reached within horizon"}
- Property value at year {horizon}: £{df['Property value'].iloc[-1]:,.0f}
- Equity at year {horizon}: £{df['Equity gained'].iloc[-1]:,.0f}
- Total rent over {horizon} years: £{df['Renting (total paid)'].iloc[-1]:,.0f}
- Total buying cost over {horizon} years: £{df['Buying (total paid)'].iloc[-1]:,.0f}

LIVE MARKET CONTEXT:
- BoE base rate: {live['base_rate_current']}%
- CPI inflation: {live['cpi_current']}%
- 2yr fixed rate: {live['rate_2yr_current']}%
- 5yr fixed rate: {live['rate_5yr_current']}%
- Average earnings growth: {live['earnings_growth_current']}%"""

        with st.spinner("Generating your personalised analysis..."):
            try:
                client = openai.OpenAI(api_key=OPENAI_KEY)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": verdict_prompt}],
                    max_tokens=300,
                    temperature=0.7,
                )
                ai_verdict = response.choices[0].message.content
            except Exception as e:
                ai_verdict = f"AI analysis unavailable: {str(e)}"

        st.session_state.ai_verdict = ai_verdict
        st.session_state.verdict_cache_key = verdict_cache_key

    ai_verdict = st.session_state.get("ai_verdict", "")
    if ai_verdict:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#111827,#1a2235);border:1px solid #c9a84c44;
                    border-left:4px solid #c9a84c;border-radius:12px;padding:24px 28px;margin-bottom:28px;">
            <div style="color:#f5f0e8;font-size:15px;line-height:1.8;font-family:'DM Sans',sans-serif;">
                {ai_verdict}
            </div>
            <div style="color:#8899aa;font-size:11px;margin-top:16px;border-top:1px solid #243048;padding-top:10px;">
                ⚡ Generated by GPT-4o · Powered by live BoE & ONS data · Not financial advice
            </div>
        </div>""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div style='color:#c9a84c;font-size:12px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;'>🏠 Buying</div>", unsafe_allow_html=True)
        st.table(pd.DataFrame({
            "": ["Property Price", "Deposit", "Stamp Duty", "Monthly Mortgage", "Appreciation", f"Value (Yr {horizon})", f"Equity (Yr {horizon})"],
            "Value": [f"£{property_price:,}", f"£{int(property_price*deposit_pct/100):,} ({deposit_pct}%)",
                      f"£{stamp_duty:,}", f"£{monthly_mortgage:,}", f"{appreciation}% / yr",
                      f"£{df['Property value'].iloc[-1]:,.0f}", f"£{df['Equity gained'].iloc[-1]:,.0f}"]
        }).set_index(""))
    with col_b:
        st.markdown("<div style='color:#60a5fa;font-size:12px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;'>🏢 Renting</div>", unsafe_allow_html=True)
        st.table(pd.DataFrame({
            "": ["Monthly Rent", f"Total Rent (Yr {horizon})", "Mortgage Rate", "Horizon"],
            "Value": [f"£{monthly_rent:,}", f"£{df['Renting (total paid)'].iloc[-1]:,.0f}",
                      f"{mortgage_rate}%", f"{horizon} years"]
        }).set_index(""))

    st.divider()
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:18px;color:#fff;margin-bottom:8px;'>📄 Export Report</div>", unsafe_allow_html=True)
    st.write("Download a formatted PDF summary including live market data from the Bank of England and ONS.")
    if st.button("Generate PDF Report"):
        st.session_state.pdf_bytes = generate_pdf(
            region, property_price, deposit_pct, mortgage_rate, monthly_rent,
            appreciation, horizon, first_time_buyer, df, monthly_mortgage, stamp_duty, breakeven)
        st.session_state.pdf_filename = f"homeiq_{region.lower().replace(' ', '_')}_{date.today()}.pdf"
    if "pdf_bytes" in st.session_state:
        st.download_button(
            "⬇ Download PDF Report",
            data=st.session_state.pdf_bytes,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            key="pdf_dl"
        )

# ── TAB 2: Deep Analysis ───────────────────────────────────────────────────
with tab_analysis:
    st.markdown("<div style='color:#8899aa;font-size:13px;margin-bottom:20px;'>See how the numbers evolve year by year — and exactly when buying overtakes renting.</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:20px;color:#fff;margin-bottom:4px;'>Cumulative Cost Over Time</div>", unsafe_allow_html=True)
    st.caption("Total money spent renting vs buying year by year.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Renting (total paid)"], name="Total Rent Paid",
                              line=dict(color=C["red"], width=3),
                              fill="tozeroy", fillcolor="rgba(248,113,113,0.06)"))
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Buying (total paid)"], name="Total Buying Cost",
                              line=dict(color=C["blue"], width=3),
                              fill="tozeroy", fillcolor="rgba(96,165,250,0.06)"))
    fig.add_trace(go.Scatter(x=df["Year"], y=df["Equity gained"], name="Equity Built",
                              line=dict(color=C["green"], width=2, dash="dash")))
    if breakeven:
        fig.add_vline(x=breakeven, line_dash="dash", line_color=C["gold"],
                      annotation_text=f"Break-even: Year {breakeven}",
                      annotation_font_color=C["gold"], annotation_position="top left")
    fig.update_layout(**PLOT_THEME, xaxis_title="Year", yaxis_title="Amount (£)",
                      yaxis_tickprefix="£", yaxis_tickformat=",", height=460)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:20px;color:#fff;margin-bottom:4px;'>Year-by-Year Breakdown</div>", unsafe_allow_html=True)
    st.caption("All figures in £. Buying total includes mortgage payments, upfront costs, and 1% annual maintenance.")
    st.dataframe(df.set_index("Year").style.format("£{:,.0f}"), use_container_width=True)

# ── TAB 3: Can I Afford This? ──────────────────────────────────────────────
with tab_afford:
    st.markdown("<div style='color:#8899aa;font-size:13px;margin-bottom:20px;'>Check whether a lender would approve your mortgage, how much you'd have left each month, and whether your budget is realistic for your target area.</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:20px;color:#fff;margin-bottom:8px;'>Lender Approval & Monthly Budget</div>", unsafe_allow_html=True)
    st.write("Check whether lenders would approve your mortgage and how much you would have left to live on each month.")
    col1, col2 = st.columns(2)
    with col1:
        gross_income = st.number_input("Your Annual Gross Income (£)", 10000, 500000, 50000, 1000)
        monthly_expenses = st.number_input("Monthly Living Expenses (£)", 0, 10000, 1500, 50,
                                            help="Food, transport, bills — not rent or mortgage.")
    with col2:
        partner_income = st.number_input("Partner's Annual Gross Income (£)", 0, 500000, 0, 1000)

    if st.button("Check Affordability", key="afford_btn"):
        st.session_state.afford_result = check_affordability(
            gross_income, partner_income, property_price,
            deposit_pct, monthly_expenses, monthly_rent, mortgage_rate)
        st.session_state.afford_inputs = dict(mortgage_rate=mortgage_rate, monthly_rent=monthly_rent,
                                               monthly_expenses=monthly_expenses)

    if "afford_result" in st.session_state:
        r = st.session_state.afford_result
        _mr = st.session_state.afford_inputs["mortgage_rate"]
        _rent = st.session_state.afford_inputs["monthly_rent"]
        _exp = st.session_state.afford_inputs["monthly_expenses"]
        st.divider()
        st.markdown("<div style='font-family:Playfair Display,serif;font-size:18px;color:#fff;margin-bottom:8px;'>Lender Approval</div>", unsafe_allow_html=True)
        a1, a2, a3 = st.columns(3)
        a1.metric("Max at 4x income", f"£{r['max_mortgage_4x']:,}",
                  "Approved" if r["affordable_4x"] else "Too high",
                  delta_color="normal" if r["affordable_4x"] else "inverse")
        a2.metric("Max at 4.5x income", f"£{r['max_mortgage_45x']:,}",
                  "Approved" if r["affordable_45x"] else "Too high",
                  delta_color="normal" if r["affordable_45x"] else "inverse")
        a3.metric("Max at 5x income", f"£{r['max_mortgage_5x']:,}",
                  "Possible (FTB)" if r["affordable_5x"] else "Too high",
                  delta_color="normal" if r["affordable_5x"] else "inverse")
        st.divider()
        st.markdown("<div style='font-family:Playfair Display,serif;font-size:18px;color:#fff;margin-bottom:8px;'>Monthly Budget</div>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        for col, label, payment, disp_key in [
            (b1, "If you buy", r["monthly_mortgage"], "disposable_buying"),
            (b2, "If you rent", _rent, "disposable_renting"),
        ]:
            with col:
                st.markdown(f"<div style='color:#8899aa;font-size:12px;text-transform:uppercase;margin-bottom:8px;'>{label}</div>", unsafe_allow_html=True)
                fig_w = go.Figure(go.Waterfall(
                    orientation="v", measure=["absolute", "relative", "relative", "total"],
                    x=["Net Income", "Housing", "Expenses", "Disposable"],
                    y=[r["net_monthly"], -payment, -_exp, 0],
                    connector={"line": {"color": "#243048"}},
                    decreasing={"marker": {"color": C["red"]}},
                    increasing={"marker": {"color": C["green"]}},
                    totals={"marker": {"color": C["gold"]}},
                ))
                fig_w.update_layout(**PLOT_THEME, height=280, showlegend=False,
                                     yaxis_tickprefix="£", yaxis_tickformat=",")
                st.plotly_chart(fig_w, use_container_width=True)
                disp = r[disp_key]
                st.metric("Monthly Disposable", f"£{disp:,}",
                          delta_color="normal" if disp > 0 else "inverse")
        st.divider()
        st.markdown("<div style='font-family:Playfair Display,serif;font-size:18px;color:#fff;margin-bottom:8px;'>Stress Test</div>", unsafe_allow_html=True)
        st.caption(f"Lenders must verify you can afford payments if rates rise to {_mr + 3:.1f}%.")
        s1, s2 = st.columns(2)
        s1.metric("Stressed Monthly Payment", f"£{r['monthly_mortgage_stressed']:,}", f"at {_mr+3:.1f}%")
        s2.metric("Disposable After Stress", f"£{r['stressed_disposable']:,}",
                  "Passes" if r["passes_stress_test"] else "Fails",
                  delta_color="normal" if r["passes_stress_test"] else "inverse")
        st.divider()
        if r["affordable_45x"] and r["passes_stress_test"]:
            st.markdown("""<div style="background:linear-gradient(135deg,#0d2b1f,#1a3a2a);border-left:4px solid #2dd4a0;border-radius:12px;padding:18px 24px;">
                <div style="font-family:'Playfair Display',serif;font-size:16px;color:#2dd4a0;font-weight:700;">This property looks affordable</div>
                <div style="color:#8899aa;font-size:13px;margin-top:4px;">You meet standard lender criteria and pass the stress test.</div></div>""", unsafe_allow_html=True)
        elif r["affordable_5x"] and r["passes_stress_test"]:
            st.markdown("""<div style="background:linear-gradient(135deg,#2b2000,#3a2e00);border-left:4px solid #c9a84c;border-radius:12px;padding:18px 24px;">
                <div style="font-family:'Playfair Display',serif;font-size:16px;color:#c9a84c;font-weight:700;">Borderline affordability</div>
                <div style="color:#8899aa;font-size:13px;margin-top:4px;">Some lenders may approve at 5x income, but options will be limited.</div></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background:linear-gradient(135deg,#2b0d0d,#3a1a1a);border-left:4px solid #f87171;border-radius:12px;padding:18px 24px;">
                <div style="font-family:'Playfair Display',serif;font-size:16px;color:#f87171;font-weight:700;">This property may be out of reach</div>
                <div style="color:#8899aa;font-size:13px;margin-top:4px;">Consider a lower price point or a larger deposit.</div></div>""", unsafe_allow_html=True)

# ── Local Market Check ────────────────────────────────────────────────────
    st.divider()
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:20px;color:#fff;margin-bottom:4px;'>📍 Local Market Check</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#8899aa;font-size:14px;margin-bottom:16px;'>Enter a target postcode to see what properties have actually sold for in that area — and whether your budget is realistic.</div>", unsafe_allow_html=True)

    postcode_input = st.text_input("Target Postcode", placeholder="e.g. SW1A 1AA", max_chars=10)

    check_clicked = st.button("Check Local Market", key="local_market_btn")
    if check_clicked and not postcode_input:
        st.warning("Please enter a postcode.")

    if check_clicked and postcode_input:
        postcode_clean = postcode_input.strip().upper().replace(" ", "%20")
        with st.spinner(f"Fetching sold prices for {postcode_input.strip().upper()}..."):
            try:
                headers = {
                    "x-rapidapi-host": "uk-property-data.p.rapidapi.com",
                    "x-rapidapi-key": RAPIDAPI_KEY
                }
                list_url = f"https://uk-property-data.p.rapidapi.com/ListProperties?postcode={postcode_clean}"
                list_data = requests.get(list_url, headers=headers, timeout=10).json()

                if isinstance(list_data, list):
                    properties = list_data
                elif isinstance(list_data, dict):
                    properties = list_data.get("properties", list_data.get("data", []))
                else:
                    properties = []

                sold_records = []
                for prop in (properties or [])[:8]:
                    pid = prop.get("pid") or prop.get("id")
                    if not pid:
                        continue
                    d_data = requests.get(f"https://uk-property-data.p.rapidapi.com/GetProperty?pid={pid}",
                                          headers=headers, timeout=10).json()
                    address = d_data.get("address", prop.get("address", "Unknown"))
                    tenure = d_data.get("tenure", "Unknown")
                    for sale in d_data.get("sales", []):
                        price = sale.get("price") or sale.get("amount")
                        date_str = sale.get("date") or sale.get("sale_date")
                        if price and date_str:
                            sold_records.append({"address": address, "price": int(price),
                                                  "date": pd.to_datetime(date_str, errors="coerce"),
                                                  "tenure": tenure})
                st.session_state.sold_records = sold_records
                st.session_state.sold_postcode = postcode_input.strip().upper()

            except Exception as e:
                st.error(f"Could not fetch property data: {str(e)}")
                st.session_state.sold_records = []

    # ── Render results from session state ─────────────────────────────────
    if st.session_state.get("sold_records") is not None:
        sold_records = st.session_state.sold_records
        postcode_label = st.session_state.get("sold_postcode", "")

        if not sold_records:
            st.warning("No sold price history found for that postcode. Try a nearby postcode.")
        else:
            df_sold = pd.DataFrame(sold_records).dropna(subset=["date"]).sort_values("date")
            prices = df_sold["price"]
            median_price = int(prices.median())
            avg_price = int(prices.mean())
            min_price = int(prices.min())
            max_price = int(prices.max())
            pct_rank = round((prices < property_price).sum() / len(prices) * 100)

            st.divider()
            st.markdown(f"<div style='font-family:Playfair Display,serif;font-size:17px;color:#fff;margin-bottom:12px;'>Sold Prices in {postcode_label} — {len(df_sold)} transactions found</div>", unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Median Sold Price", f"£{median_price:,}")
            m2.metric("Average Sold Price", f"£{avg_price:,}")
            m3.metric("Lowest Sale", f"£{min_price:,}")
            m4.metric("Highest Sale", f"£{max_price:,}")

            if pct_rank >= 75:
                bc, bi, bt = "#2dd4a0", "✅", f"Your budget of £{property_price:,} is in the top {100-pct_rank}% for this postcode — strong buying position."
            elif pct_rank >= 40:
                bc, bi, bt = "#c9a84c", "⚠️", f"Your budget of £{property_price:,} sits around the median for this postcode — expect moderate competition."
            else:
                bc, bi, bt = "#f87171", "❌", f"Your budget of £{property_price:,} is below {100-pct_rank}% of sold prices here — you may struggle to find a property in this area."

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a2235,#243048);border-left:4px solid {bc};
                        border-radius:12px;padding:18px 24px;margin:16px 0;">
                <div style="font-family:'Playfair Display',serif;font-size:16px;color:{bc};font-weight:700;margin-bottom:6px;">
                    {bi} Budget Reality Check</div>
                <div style="color:#f5f0e8;font-size:14px;line-height:1.6;">{bt}</div>
                <div style="color:#8899aa;font-size:12px;margin-top:8px;">
                    Your budget ranks higher than {pct_rank}% of sold prices in this postcode.</div>
            </div>""", unsafe_allow_html=True)

            st.markdown("<div style='font-family:Playfair Display,serif;font-size:16px;color:#fff;margin:16px 0 8px;'>Sold Price History</div>", unsafe_allow_html=True)
            fig_sold = go.Figure()
            fig_sold.add_trace(go.Scatter(
                x=df_sold["date"], y=df_sold["price"], mode="markers", name="Sold Price",
                marker=dict(color=C["gold"], size=9, opacity=0.85, line=dict(color="#111827", width=1)),
                hovertemplate="<b>%{text}</b><br>£%{y:,.0f}<br>%{x|%b %Y}<extra></extra>",
                text=df_sold["address"]
            ))
            if len(df_sold) >= 3:
                df_sold["ts"] = df_sold["date"].astype(np.int64) // 10**9
                z = np.polyfit(df_sold["ts"], df_sold["price"], 1)
                trend_y = np.poly1d(z)(df_sold["ts"])
                fig_sold.add_trace(go.Scatter(x=df_sold["date"], y=trend_y, mode="lines", name="Trend",
                                               line=dict(color=C["green"], width=2, dash="dot")))
                years_span = (df_sold["date"].max() - df_sold["date"].min()).days / 365.25
                if years_span > 0.5 and trend_y[0] > 0:
                    implied = round(((trend_y[-1] / trend_y[0]) ** (1 / years_span) - 1) * 100, 1)
                    if 0 < implied < 20:
                        st.markdown(f"""
                        <div style="background:#1a2235;border:1px solid #2dd4a044;border-radius:10px;padding:14px 18px;margin-top:8px;">
                            <span style="color:#8899aa;font-size:12px;">📈 Implied annual appreciation from sold data: </span>
                            <span style="font-family:'Playfair Display',serif;font-size:18px;color:#2dd4a0;font-weight:700;">{implied}%/yr</span>
                            <span style="color:#8899aa;font-size:12px;margin-left:8px;">— consider updating your appreciation slider to reflect this.</span>
                        </div>""", unsafe_allow_html=True)

            fig_sold.add_hline(y=property_price, line_dash="dash", line_color=C["blue"],
                                annotation_text=f"Your budget: £{property_price:,}",
                                annotation_font_color=C["blue"])
            fig_sold.update_layout(**PLOT_THEME, height=380, yaxis_title="Sale Price (£)",
                                   yaxis_tickprefix="£", yaxis_tickformat=",")
            st.plotly_chart(fig_sold, use_container_width=True)

            st.markdown("<div style='font-family:Playfair Display,serif;font-size:16px;color:#fff;margin:16px 0 8px;'>Recent Transactions</div>", unsafe_allow_html=True)
            df_display = df_sold.sort_values("date", ascending=False).head(10).copy()
            df_display["date"] = df_display["date"].dt.strftime("%b %Y")
            df_display["price"] = df_display["price"].apply(lambda x: f"£{x:,}")
            cols_show = [c for c in ["address", "price", "date", "tenure"] if c in df_display.columns]
            df_display.columns = [c.title() for c in df_display.columns]
            st.dataframe(df_display[[c.title() for c in cols_show]].reset_index(drop=True),
                         use_container_width=True, hide_index=True)



# ── TAB 5: AI Advisor ──────────────────────────────────────────────────────
with tab_ai:
    st.markdown("<div style='color:#8899aa;font-size:13px;margin-bottom:20px;'>Your personal property advisor. Ask anything — I have your full numbers and live market data in context.</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:20px;color:#fff;margin-bottom:4px;'>AI Property Advisor</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#8899aa;font-size:14px;margin-bottom:16px;'>Try: <em style='color:#c9a84c;'>\"Should I fix for 2 or 5 years?\"</em> or <em style='color:#c9a84c;'>\"What does the current inflation mean for me?\"</em></div>", unsafe_allow_html=True)

    system_ctx = f"""You are HomeIQ's AI property advisor — a warm, knowledgeable UK property and financial expert.
You have the user's full analysis AND live market data. Always reference their specific numbers. Be concise and clear.

LIVE MARKET DATA (fetched today from BoE and ONS):
- BoE Base Rate: {live['base_rate_current']}%
- 2-Year Fixed Mortgage Rate: {live['rate_2yr_current']}%
- 5-Year Fixed Mortgage Rate: {live['rate_5yr_current']}%
- CPI Inflation: {live['cpi_current']}%
- Average Earnings Growth: {live['earnings_growth_current']}%

USER ANALYSIS:
- Region: {region} | Price: £{property_price:,} | Deposit: {deposit_pct}% (£{int(property_price*deposit_pct/100):,})
- Mortgage rate used: {mortgage_rate}% | Monthly mortgage: £{monthly_mortgage:,} | Monthly rent: £{monthly_rent:,}
- First-time buyer: {first_time_buyer} | Stamp duty: £{stamp_duty:,}
- Assumed appreciation: {appreciation}%/yr | Horizon: {horizon}yr
- Break-even: {"Year "+str(breakeven) if breakeven else "Not within horizon"}
- Property value (yr {horizon}): £{df['Property value'].iloc[-1]:,.0f}
- Equity (yr {horizon}): £{df['Equity gained'].iloc[-1]:,.0f}
"""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Ask your property advisor..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = openai.OpenAI(api_key=OPENAI_KEY)
                    messages = [{"role": "system", "content": system_ctx}] + [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_history
                    ]
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=600,
                    )
                    reply = response.choices[0].message.content
                except Exception as e:
                    reply = f"Sorry, I encountered an error: {str(e)}"
            st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

    if st.session_state.chat_history:
        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()



# ── TAB 4: Cost of Waiting ────────────────────────────────────────────────
with tab_wait:
    st.markdown("<div style='color:#8899aa;font-size:13px;margin-bottom:20px;'>Thinking of waiting for rates to drop or prices to fall? This tool quantifies exactly what that decision costs you.</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:20px;color:#fff;margin-bottom:16px;'>Cost of Waiting Calculator</div>", unsafe_allow_html=True)

    # ── Waiting scenario assumptions ──────────────────────────────────────
    w1, w2 = st.columns(2)
    with w1:
        price_growth_pa = st.slider(
            "Assumed annual house price growth (%)", 0.0, 8.0, float(appreciation), 0.5,
            help="How much you expect property prices to rise each year you wait.")
        rent_inflation_pa = st.slider(
            "Assumed annual rent increase (%)", 0.0, 8.0, float(round(live["cpi_current"], 1)), 0.5,
            help="Pre-filled with live ONS CPI. Rents tend to track inflation closely.")
    with w2:
        rate_drop_per_year = st.slider(
            "Expected mortgage rate drop per year of waiting (%)", 0.0, 1.0, 0.25, 0.05,
            help="Based on BoE base rate trend. 0.25% per year is a conservative expectation if cuts continue.")
        max_wait = st.slider("Maximum years to model", 1, 5, 3)

    st.divider()

    # ── Core calculation ──────────────────────────────────────────────────
    def cost_of_waiting(wait_years, price_growth_pa, rent_inflation_pa, rate_drop_per_year,
                         base_price, base_rate, base_rent, deposit_pct, horizon, ftb):
        """
        Calculate the net financial impact of waiting `wait_years` before buying.
        Returns a dict of key figures for the delayed-purchase scenario.
        """
        # Future property price after waiting
        future_price = base_price * ((1 + price_growth_pa / 100) ** wait_years)

        # Future mortgage rate (drops as BoE cuts)
        future_rate = max(1.0, base_rate - rate_drop_per_year * wait_years)

        # Stamp duty on future price
        future_stamp = compute_stamp_duty(future_price, ftb)

        # Deposit amount (same % of higher price)
        future_deposit = future_price * deposit_pct / 100

        # Monthly mortgage on delayed purchase
        future_loan = future_price - future_deposit
        r = future_rate / 100 / 12
        n = 25 * 12
        future_monthly_mortgage = future_loan * (r * (1 + r)**n) / ((1 + r)**n - 1)

        # Rent paid while waiting
        rent_paid_waiting = 0.0
        monthly = base_rent
        for yr in range(wait_years):
            rent_paid_waiting += monthly * 12
            monthly *= (1 + rent_inflation_pa / 100)

        # Additional deposit needed (same % of higher price)
        extra_deposit_needed = future_deposit - (base_price * deposit_pct / 100)

        # Net cost of waiting = what you've spent renting + extra upfront - any mortgage saving
        monthly_saving_from_rate_drop = (
            (base_price * (1 - deposit_pct/100)) * (base_rate / 100 / 12) * (1 + base_rate/100/12)**(25*12) /
            ((1 + base_rate/100/12)**(25*12) - 1) -
            future_monthly_mortgage
        )
        annual_mortgage_saving = monthly_saving_from_rate_drop * 12
        total_mortgage_saving_over_horizon = annual_mortgage_saving * horizon

        net_cost = rent_paid_waiting + extra_deposit_needed - total_mortgage_saving_over_horizon

        return {
            "wait_years": wait_years,
            "future_price": round(future_price),
            "future_rate": round(future_rate, 2),
            "future_monthly_mortgage": round(future_monthly_mortgage),
            "rent_paid_waiting": round(rent_paid_waiting),
            "extra_deposit_needed": round(extra_deposit_needed),
            "monthly_mortgage_saving": round(monthly_saving_from_rate_drop),
            "total_mortgage_saving": round(total_mortgage_saving_over_horizon),
            "net_cost": round(net_cost),
            "price_increase": round(future_price - base_price),
            "future_stamp": round(future_stamp),
            "extra_stamp": round(future_stamp - stamp_duty),
        }

    scenarios = [cost_of_waiting(
        w, price_growth_pa, rent_inflation_pa, rate_drop_per_year,
        property_price, mortgage_rate, monthly_rent, deposit_pct, horizon, first_time_buyer
    ) for w in range(1, max_wait + 1)]

    # ── Summary metric cards ───────────────────────────────────────────────
    cols = st.columns(max_wait)
    for i, s in enumerate(scenarios):
        with cols[i]:
            net = s["net_cost"]
            color = "#f87171" if net > 0 else "#2dd4a0"
            label = "Net cost of waiting" if net > 0 else "Net saving from waiting"
            st.markdown(f"""
            <div style="background:#1a2235;border:1px solid {'#f8717144' if net > 0 else '#2dd4a044'};
                        border-top:3px solid {color};border-radius:12px;padding:18px;text-align:center;">
                <div style="color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:6px;">
                    Wait {s['wait_years']} Year{'s' if s['wait_years']>1 else ''}</div>
                <div style="font-family:'Playfair Display',serif;font-size:28px;color:{color};font-weight:900;">
                    {'–' if net < 0 else '+'}£{abs(net):,.0f}</div>
                <div style="color:#8899aa;font-size:11px;margin-top:4px;">{label}</div>
                <div style="margin-top:12px;display:grid;grid-template-columns:1fr 1fr;gap:6px;text-align:left;">
                    <div style="color:#8899aa;font-size:10px;">New price</div>
                    <div style="color:#f5f0e8;font-size:10px;text-align:right;">£{s['future_price']:,}</div>
                    <div style="color:#8899aa;font-size:10px;">New rate</div>
                    <div style="color:#f5f0e8;font-size:10px;text-align:right;">{s['future_rate']}%</div>
                    <div style="color:#8899aa;font-size:10px;">Rent paid</div>
                    <div style="color:#f87171;font-size:10px;text-align:right;">£{s['rent_paid_waiting']:,}</div>
                    <div style="color:#8899aa;font-size:10px;">Price rise</div>
                    <div style="color:#f87171;font-size:10px;text-align:right;">+£{s['price_increase']:,}</div>
                    <div style="color:#8899aa;font-size:10px;">Rate saving</div>
                    <div style="color:#2dd4a0;font-size:10px;text-align:right;">£{s['monthly_mortgage_saving']:+,}/mo</div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Waterfall chart: what makes up the cost ───────────────────────────
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:18px;color:#fff;margin-bottom:8px;'>What Makes Up the Cost of Waiting?</div>", unsafe_allow_html=True)
    st.caption("Break down of the financial components for each delay scenario.")

    wait_labels = [f"Wait {s['wait_years']}yr" for s in scenarios]
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Rent Paid While Waiting", x=wait_labels,
                              y=[s["rent_paid_waiting"] for s in scenarios],
                              marker_color=C["red"], text=[f"£{s['rent_paid_waiting']:,.0f}" for s in scenarios],
                              textposition="auto"))
    fig_bar.add_trace(go.Bar(name="Higher Purchase Price", x=wait_labels,
                              y=[s["price_increase"] for s in scenarios],
                              marker_color="rgba(248,113,113,0.65)", text=[f"£{s['price_increase']:,.0f}" for s in scenarios],
                              textposition="auto"))
    fig_bar.add_trace(go.Bar(name="Rate Drop Saving (over horizon)", x=wait_labels,
                              y=[-s["total_mortgage_saving"] for s in scenarios],
                              marker_color=C["green"], text=[f"-£{s['total_mortgage_saving']:,.0f}" for s in scenarios],
                              textposition="auto"))
    fig_bar.update_layout(**PLOT_THEME, barmode="relative", height=380,
                           yaxis_title="£", yaxis_tickprefix="£", yaxis_tickformat=",")
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Net cost trend line ───────────────────────────────────────────────
    st.markdown("<div style='font-family:Playfair Display,serif;font-size:18px;color:#fff;margin-bottom:8px;'>Net Cost of Each Year of Delay</div>", unsafe_allow_html=True)
    fig_net = go.Figure()
    net_costs = [0] + [s["net_cost"] for s in scenarios]
    x_labels = ["Buy Now"] + [f"Wait {s['wait_years']}yr" for s in scenarios]
    colors_net = [C["gold"]] + [C["red"] if n > 0 else C["green"] for n in net_costs[1:]]
    fig_net.add_trace(go.Scatter(
        x=x_labels, y=net_costs, mode="lines+markers+text",
        line=dict(color=C["gold"], width=2.5, dash="dot"),
        marker=dict(color=colors_net, size=12, line=dict(color="#111827", width=2)),
        text=[f"£{abs(n):,.0f}" if n != 0 else "Baseline" for n in net_costs],
        textposition="top center", textfont=dict(color="#f5f0e8", size=11)
    ))
    fig_net.add_hline(y=0, line_dash="dash", line_color=C["muted"],
                       annotation_text="Break-even", annotation_font_color=C["muted"])
    fig_net.update_layout(**PLOT_THEME, height=320, showlegend=False,
                           yaxis_title="Net Cost of Waiting (£)",
                           yaxis_tickprefix="£", yaxis_tickformat=",")
    st.plotly_chart(fig_net, use_container_width=True)

    # ── Verdict insight card ───────────────────────────────────────────────
    st.divider()
    s1 = scenarios[0]
    if s1["net_cost"] > 0:
        verdict_color = "#f87171"
        verdict_icon = "❌"
        verdict_title = f"Waiting is likely to cost you money"
        verdict_body = (
            f"Even with the BoE rate dropping by <strong style='color:#c9a84c;'>{rate_drop_per_year}% per year</strong>, "
            f"the combination of rent paid (£{s1['rent_paid_waiting']:,}) and higher purchase price "
            f"(+£{s1['price_increase']:,}) outweighs the mortgage savings of "
            f"£{s1['monthly_mortgage_saving']:,}/month. "
            f"Based on current market data, buying sooner is the stronger financial decision."
        )
    else:
        verdict_color = "#2dd4a0"
        verdict_icon = "✅"
        verdict_title = "Waiting one year could be worth it"
        verdict_body = (
            f"If the BoE cuts rates by <strong style='color:#c9a84c;'>{rate_drop_per_year}% per year</strong> "
            f"as modelled, the mortgage savings of £{abs(s1['monthly_mortgage_saving']):,}/month over {horizon} years "
            f"outweigh the rent paid and price increase. However, this depends heavily on rates actually falling — "
            f"monitor the BoE base rate (currently <strong style='color:#c9a84c;'>{live['base_rate_current']}%</strong>) closely."
        )

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a2235,#243048);border:1px solid {verdict_color}44;
                border-left:4px solid {verdict_color};border-radius:12px;padding:24px;">
        <div style="font-family:'Playfair Display',serif;font-size:18px;color:{verdict_color};font-weight:700;margin-bottom:8px;">
            {verdict_icon} {verdict_title}</div>
        <div style="color:#8899aa;font-size:14px;line-height:1.7;">{verdict_body}</div>
        <div style="margin-top:16px;display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
            <div style="background:#111827;border-radius:8px;padding:12px;">
                <div style="color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:0.08em;">BoE Rate Now</div>
                <div style="font-family:'Playfair Display',serif;font-size:20px;color:#c9a84c;font-weight:700;">{live['base_rate_current']}%</div>
            </div>
            <div style="background:#111827;border-radius:8px;padding:12px;">
                <div style="color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:0.08em;">House Price Growth</div>
                <div style="font-family:'Playfair Display',serif;font-size:20px;color:#f87171;font-weight:700;">{price_growth_pa}%/yr</div>
            </div>
            <div style="background:#111827;border-radius:8px;padding:12px;">
                <div style="color:#8899aa;font-size:10px;text-transform:uppercase;letter-spacing:0.08em;">Rent Inflation</div>
                <div style="font-family:'Playfair Display',serif;font-size:20px;color:#60a5fa;font-weight:700;">{rent_inflation_pa}%/yr</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:32px 0 16px;color:#243048;font-size:12px;">
    HomeIQ · Live data: Bank of England IADB & ONS API · Not financial advice
</div>
""", unsafe_allow_html=True)
