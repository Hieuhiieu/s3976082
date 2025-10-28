# student_a_level_1.py
import os
import pyhtml  # dùng hàm pyhtml.get_results_from_query(DB_PATH, sql)

# --- Xác định đường dẫn database ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

# --- Hàm định dạng số ---
def fmt_int(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return str(x)

# --- Hàm chính tạo HTML ---
def get_page_html(form_data):
    """
    Level 1A — Overview:
      - Timeframe (min/max YearID)
      - Total vaccine doses
      - Total infection cases
      - Disease list
    """

    # --- Truy vấn SQL ---
    q_years   = "SELECT MIN(YearID), MAX(YearID) FROM YearDate;"
    q_doses   = "SELECT COALESCE(SUM(doses),0) FROM Vaccination;"
    q_cases   = "SELECT COALESCE(SUM(cases),0) FROM InfectionData;"
    q_disease = "SELECT description FROM Infection_Type ORDER BY description;"

    # --- Lấy dữ liệu từ DB ---
    minY, maxY   = pyhtml.get_results_from_query(DB_PATH, q_years)[0]
    total_doses  = pyhtml.get_results_from_query(DB_PATH, q_doses)[0][0]
    total_cases  = pyhtml.get_results_from_query(DB_PATH, q_cases)[0][0]
    diseases     = [row[0] for row in pyhtml.get_results_from_query(DB_PATH, q_disease)]

    # --- HTML với tone xanh lá bắt mắt hơn ---
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Level 1A — Overview</title>
  <style>
    body {{
      font-family: "Segoe UI", Roboto, Arial, sans-serif;
      margin: 0;
      padding: 0;
      background: linear-gradient(135deg, #bbf7d0 0%, #f0fdf4 100%);
      color: #064e3b;
      min-height: 100vh;
    }}

    header {{
      text-align: center;
      padding: 40px 20px 20px;
      background: linear-gradient(90deg, #22c55e, #16a34a);
      color: white;
      box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }}
    header h1 {{
      margin: 0;
      font-size: 2rem;
      letter-spacing: 0.5px;
    }}
    header small {{
      display: block;
      margin-top: 6px;
      color: #dcfce7;
    }}

    .grid {{
      display: grid;
      gap: 20px;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      margin: 30px auto;
      max-width: 1000px;
      padding: 0 20px;
    }}

    .card {{
      background: white;
      border-radius: 14px;
      padding: 20px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
      border-top: 5px solid #22c55e;
      transition: all 0.25s ease;
      text-align: center;
    }}
    .card:hover {{
      transform: translateY(-6px);
      box-shadow: 0 8px 18px rgba(0,0,0,0.12);
    }}
    .card b {{
      display: block;
      color: #166534;
      font-size: 1.1rem;
      margin-bottom: 6px;
    }}
    .card span.value {{
      font-size: 1.3rem;
      font-weight: 600;
      color: #065f46;
    }}

    .tags {{
      margin-top: 6px;
    }}
    .tags span {{
      display: inline-block;
      background: #dcfce7;
      border: 1px solid #86efac;
      color: #065f46;
      padding: 5px 10px;
      border-radius: 999px;
      margin: 3px 4px;
      font-size: 0.9em;
      transition: 0.2s;
    }}
    .tags span:hover {{
      background: #86efac;
      color: white;
    }}

    .footer {{
      text-align: center;
      margin: 30px 0;
      color: #166534;
      font-weight: 500;
      display: flex;
      justify-content: center;
      gap: 16px;
    }}
    .footer a {{
      color: #15803d;
      text-decoration: none;
      background: #bbf7d0;
      padding: 10px 18px;
      border-radius: 8px;
      transition: 0.2s;
      box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }}
    .footer a:hover {{
      background: #22c55e;
      color: white;
      transform: translateY(-2px);
      box-shadow: 0 4px 10px rgba(0,0,0,0.12);
    }}
  </style>
</head>
<body>
  <header>
    <h1>🌿 Investigating Preventable Infectious Diseases</h1>
    <small>Live data from <code>immunisation.db</code></small>
  </header>

  <div class="grid">
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

  <div class="footer">
    <a href="/page2">→ Go to Level 2A</a>
    <a href="/page3">→ Go to Level 3A</a>
  </div>
</body>
</html>"""
    return page_html
    