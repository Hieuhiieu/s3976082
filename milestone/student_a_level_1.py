# student_a_level_1.py
import os
import pyhtml 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

def fmt_int(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return str(x)

def get_page_html(form_data):

    q_years   = "SELECT MIN(YearID), MAX(YearID) FROM YearDate;"
    q_doses   = "SELECT COALESCE(SUM(doses),0) FROM Vaccination;"
    q_cases   = "SELECT COALESCE(SUM(cases),0) FROM InfectionData;"
    q_disease = "SELECT description FROM Infection_Type ORDER BY description;"

    minY, maxY   = pyhtml.get_results_from_query(DB_PATH, q_years)[0]
    total_doses  = pyhtml.get_results_from_query(DB_PATH, q_doses)[0][0]
    total_cases  = pyhtml.get_results_from_query(DB_PATH, q_cases)[0][0]
    diseases     = [row[0] for row in pyhtml.get_results_from_query(DB_PATH, q_disease)]

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Overview</title>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <style>
    :root {{
      --green-1:#22c55e; --green-2:#16a34a; --ink:#064e3b;
      --bg1:#bbf7d0; --bg2:#f0fdf4;
    }}
    body {{
      font-family: "Segoe UI", Roboto, Arial, sans-serif;
      margin: 0;
      background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
      color: var(--ink);
      min-height: 100vh;
    }}

    header {{
      background: linear-gradient(90deg, var(--green-1), var(--green-2));
      color: white;
      box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 0 20px; }}
    .topbar {{
      display: flex; justify-content: space-between; align-items: center;
      padding: 16px 0 10px;
    }}
    .brand {{ font-size: 1.35rem; font-weight: 600; }}
    nav a {{
      color: #e6f9ec; text-decoration: none; margin-left: 14px;
      padding: 8px 12px; border-radius: 8px; transition:.2s;
    }}
    nav a:hover {{ background: rgba(255,255,255,.20); }}

    .hero {{ padding: 5px 0 22px; }}
    .hero h1 {{ margin: 6px 0 10px; font-size: 2rem; }}
    .summary {{
      margin-top: 10px;
      background: rgba(255,255,255,.20);
      border: 1px solid rgba(255,255,255,.30);
      padding: 14px;
      border-radius: 12px;
      line-height: 1.45;
      font-size: 0.97rem;
    }}

    .grid-3 {{
      display: grid; gap: 20px;
      grid-template-columns: repeat(3, 1fr);
      margin-top: 26px;
    }}
    @media (max-width: 900px) {{
      .grid-3 {{ grid-template-columns: 1fr; }}
    }}

    .card {{
      background: white;
      border-radius: 14px;
      padding: 20px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
      border-top: 5px solid var(--green-1);
      text-align: center;
      transition: .25s;
    }}
    .card:hover {{
      transform: translateY(-5px);
      box-shadow: 0 8px 18px rgba(0,0,0,0.14);
    }}
    .card b {{ display:block; color:#166534; margin-bottom:6px; }}
    .card .value {{ font-size:1.35rem; font-weight:700; color:#065f46; }}

    .tags span {{
      display:inline-block; padding:6px 12px;
      background:#dcfce7; border:1px solid #86efac;
      border-radius:999px; margin:4px 6px 0 0;
      font-size:.95rem; color:#065f46;
      transition:.2s;
    }}
    .tags span:hover {{ background:#22c55e; color:white; }}
  </style>
</head>
<body>
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
    <h1>Investigating Preventable Infectious Diseases</h1>
    <div class="summary">
      This interactive dashboard provides a clear and trustworthy overview of global immunisation data.
      It allows users to explore how vaccination efforts have changed over time, uncover trends in
      infection rates, and analyse coverage differences between diseases. From a high-level summary to 
      deeper analytical views, this system is designed to support public health decision-making, 
      research, and education. Use the menu above to move between overview statistics, comparative analysis 
      and improvement tracking across multiple countries and antigens.
    </div>
  </div>
</header>

<main class="wrap">
  <section class="grid-3">
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
  </section>

  <section style="margin-top:24px;">
    <div class="card" style="text-align:left">
      <b>🩺 Diseases</b>
      <div class="tags">
        {''.join(f'<span>{d}</span>' for d in diseases)}
      </div>
    </div>
  </section>
</main>
</body>
</html>"""

    return page_html
