# student_a_level_1.py
import os
import pyhtml

# --- Absolute path to the database ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

def fmt_int(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return str(x)

# --- Shared CSS (unified style for Level 1/2/3) ---
COMMON_CSS = """
<style>
:root{
  --g1:#22c55e; --g2:#16a34a;
  --ink:#064e3b;
  --bg1:#bbf7d0; --bg2:#f0fdf4;
  --card:#ffffff;
}
*{box-sizing:border-box}
body{
  margin:0; font-family:"Segoe UI", Roboto, Arial, sans-serif;
  background:linear-gradient(135deg,var(--bg1),var(--bg2));
  color:var(--ink); min-height:100vh;
}
/* NAVBAR */
header{
  background:linear-gradient(90deg,var(--g1),var(--g2));
  color:#fff; box-shadow:0 2px 10px rgba(0,0,0,.15);
}
.wrap{max-width:1100px; margin:0 auto; padding:0 22px;}
.topbar{
  display:flex; align-items:center; justify-content:space-between;
  padding:14px 0 8px;
}
.brand{margin:0; font-size:1.35rem; font-weight:600;}
nav a{
  color:#e7f8ee; text-decoration:none; margin-left:14px;
  padding:8px 12px; border-radius:10px; transition:.2s;
}
nav a:hover{background:rgba(255,255,255,.15); color:#fff;}
.hero{padding:8px 0 18px;}
.hero h1{margin:8px 0 0; font-size:2rem;}

/* SUMMARY */
.summary{
  background:#dcfce7; border:1px solid #86efac; color:#065f46;
  padding:14px 16px; border-radius:12px; margin:18px 0 6px;
  box-shadow:0 3px 8px rgba(0,0,0,.08);
  line-height:1.5;
}

/* CARDS */
.cardbox{
  display:grid; gap:22px;
  grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  margin:20px 0 10px;
}
.card{
  background:var(--card); border-radius:14px; padding:20px;
  box-shadow:0 4px 10px rgba(0,0,0,.08);
  border-top:5px solid var(--g1);
  text-align:center; transition:.2s;
}
.card:hover{transform:translateY(-6px); box-shadow:0 8px 18px rgba(0,0,0,.12);}
.card b{display:block; font-size:1.05rem; color:#166534; margin-bottom:6px;}
.card .value{font-size:1.25rem; font-weight:600; color:#065f46}

/* TAGS (diseases) */
.tags{margin-top:8px;}
.tags span{
  display:inline-block; background:#dcfce7; border:1px solid #86efac;
  color:#065f46; padding:6px 10px; border-radius:999px; margin:4px 5px;
  font-size:.92rem; transition:.2s;
}
.tags span:hover{background:#86efac; color:#fff}

/* TABLE (kept for any future additions) */
table{
  border-collapse:collapse; width:95%; margin:20px auto; background:#fff;
  border-radius:12px; overflow:hidden; box-shadow:0 4px 10px rgba(0,0,0,.08);
}
th,td{border:1px solid #e5e7eb; padding:10px 14px; text-align:left}
th{background:#bbf7d0; color:#064e3b}
tr:nth-child(even){background:#f9fafb}
</style>
"""

# --- HTML page ---
def get_page_html(form_data):
    """
    Level 1 — Overview:
      - Timeframe (min/max YearID)
      - Total vaccine doses
      - Total infection cases
      - Disease list
    """
    # --- SQL queries ---
    q_years   = "SELECT MIN(YearID), MAX(YearID) FROM YearDate;"
    q_doses   = "SELECT COALESCE(SUM(doses),0) FROM Vaccination;"
    q_cases   = "SELECT COALESCE(SUM(cases),0) FROM InfectionData;"
    q_disease = "SELECT description FROM Infection_Type ORDER BY description;"

    # --- Extract info from DB ---
    minY, maxY   = pyhtml.get_results_from_query(DB_PATH, q_years)[0]
    total_doses  = pyhtml.get_results_from_query(DB_PATH, q_doses)[0][0]
    total_cases  = pyhtml.get_results_from_query(DB_PATH, q_cases)[0][0]
    diseases     = [row[0] for row in pyhtml.get_results_from_query(DB_PATH, q_disease)]

    # --- HTML ---
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Overview</title>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  {COMMON_CSS}
</head>
<body>
  <!-- NAVBAR -->
  <header>
    <div class="wrap topbar">
      <h2 class="brand">🌿 Immunisation Insights</h2>
      <nav>
        <a href="/">Overview</a>
        <a href="/page2">Coverage</a>
        <a href="/page3">Improvements</a>
      </nav>
    </div>
    <div class="wrap hero">
      <h1>Global Immunisation Overview</h1>
    </div>
  </header>

  <div class="wrap">
    <!-- SUMMARY (longer, friendly, explains app purpose) -->
    <div class="summary">
      <strong>About this dashboard.</strong> This site explores preventable infectious diseases using
      official immunisation records and infection data. Use the tabs to navigate:
      <em>Overview</em> gives you the big picture (time range, total vaccine doses and total cases);
      <em>Coverage</em> lets you filter by antigen, year and region to find countries meeting the ≥90% target;
      and <em>Improvements</em> compares start–end years to highlight where coverage improved the most.
      All figures are computed directly in SQL to ensure accuracy and reproducibility.
    </div>

    <!-- KPI CARDS -->
    <div class="cardbox">
      <div class="card">
        <b>📅 Timeframe</b>
        <span class="value">{minY} – {maxY}</span>
      </div>
      <div class="card">
        <b>💉 Total vaccine doses</b>
        <span class="value">{fmt_int(total_doses)}</span>
      </div>
      <div class="card">
        <b>🦠 Total infection cases</b>
        <span class="value">{fmt_int(total_cases)}</span>
      </div>
      <div class="card">
        <b>🩺 Diseases</b>
        <div class="tags">
          {''.join(f'<span>{d}</span>' for d in diseases)}
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""
