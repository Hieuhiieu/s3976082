# student_a_level_1.py
import os
import pyhtml  # dùng hàm pyhtml.get_results_from_query(DB_PATH, sql)

# Tạo đường dẫn tuyệt đối tới file DB, không phụ thuộc thư mục chạy lệnh
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

def fmt_int(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return str(x)

def get_page_html(form_data):
    """
    Level 1A — Overview:
      - Timeframe (min/max YearID)
      - Total vaccine doses
      - Total infection cases
      - Disease list
    """
    # --- SQL (điều chỉnh tên cột nếu schema lớp bạn khác) ---
    q_years   = "SELECT MIN(YearID), MAX(YearID) FROM YearDate;"
    q_doses   = "SELECT COALESCE(SUM(doses),0) FROM Vaccination;"
    q_cases   = "SELECT COALESCE(SUM(cases),0) FROM InfectionData;"
    q_disease = "SELECT description FROM Infection_Type ORDER BY description;"

    # --- Query DB ---
    minY, maxY   = pyhtml.get_results_from_query(DB_PATH, q_years)[0]
    total_doses  = pyhtml.get_results_from_query(DB_PATH, q_doses)[0][0]
    total_cases  = pyhtml.get_results_from_query(DB_PATH, q_cases)[0][0]
    diseases     = [row[0] for row in pyhtml.get_results_from_query(DB_PATH, q_disease)]

    # --- HTML ---
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Level 1A — Overview</title>
  <style>
    body {{ font-family: system-ui,-apple-system,Segoe UI,Roboto,Arial; margin: 24px; }}
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit,minmax(240px,1fr)); margin-top: 12px; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px; background: #fff; }}
    h1 {{ margin-bottom: 6px; }}
    small {{ color:#6b7280; }}
    .tags span {{ display:inline-block; background:#eef2ff; border:1px solid #e5e7eb; padding:2px 8px; border-radius: 999px; margin:2px 4px 0 0; }}
    a {{ text-decoration:none; color:#2563eb; }}
  </style>
</head>
<body>
  <h1>Investigating Preventable Infectious Diseases</h1>
  <small>Figures computed live from <code>database/immunisation.db</code></small>

  <div class="grid">
    <div class="card"><b>Timeframe</b><br>{minY} – {maxY}</div>
    <div class="card"><b>Total vaccine doses</b><br>{fmt_int(total_doses)}</div>
    <div class="card"><b>Total infection cases</b><br>{fmt_int(total_cases)}</div>
    <div class="card">
      <b>Diseases</b><br>
      <div class="tags">{''.join(f'<span>{d}</span>' for d in diseases)}</div>
    </div>
  </div>

  <p style="margin-top:16px"><a href="/page2">→ Go to Level 2A</a></p>
</body>
</html>"""
    return page_html
