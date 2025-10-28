# student_a_level_2.py
import os
import sqlite3
import pyhtml

# --- Absolute path tới database ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

# ------------------------- helpers -------------------------
def exec_query(sql: str, params=()):
    """Chạy SELECT an toàn (dùng ? placeholders) và trả về list of tuples."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return rows

def get_first(form_data, key, cast=None):
    """Lấy giá trị đầu tiên từ query string (hoặc None)."""
    v = (form_data.get(key) or [None])[0]
    if v in (None, "", "None"):
        return None
    if cast:
        try:
            return cast(v)
        except Exception:
            return None
    return v

def options_html(options, selected_val):
    """Render <option> cho <select>. options: [(value,label),...]"""
    sel = "" if selected_val is None else str(selected_val)
    out = []
    for val, label in options:
        s = ' selected="selected"' if str(val) == sel else ""
        out.append(f'<option value="{val}"{s}>{label}</option>')
    return "\n".join(out)

def td_row(cells):
    return "<tr>" + "".join(f"<td>{'' if c is None else c}</td>" for c in cells) + "</tr>"

# ------------------------- main page -------------------------
def get_page_html(form_data):
    """
    Level 2A:
      - Form filter: antigen / year / region (optional)
      - Table 1: Countries met ≥90% target
      - Table 2: Per-region count meeting ≥90%
    """
    # Lấy filter từ URL (?antigen=&year=&region=)
    antigen = get_first(form_data, "antigen", int)
    year    = get_first(form_data, "year", int)
    region  = get_first(form_data, "region", int)  # optional

    # Dropdown data
    antigen_opts = exec_query("SELECT AntigenID, name FROM Antigen ORDER BY name;")
    year_opts    = [(y[0], y[0]) for y in exec_query("SELECT DISTINCT year FROM Vaccination ORDER BY year;")]
    region_opts  = exec_query("SELECT RegionID, region FROM Region ORDER BY region;")

    # -------- Table 1: Countries met ≥90% target --------
    sql1 = """
      SELECT V.antigen, V.year, C.name AS country, R.region AS region, V.coverage AS percentage_of_target
      FROM Vaccination V
      JOIN Country C ON C.CountryID = V.country
      LEFT JOIN Region R ON R.RegionID = C.region
      WHERE V.coverage >= 90
    """
    p1 = []
    if antigen is not None:
        sql1 += " AND V.antigen = ?"
        p1.append(antigen)
    if year is not None:
        sql1 += " AND V.year = ?"
        p1.append(year)
    if region is not None:
        sql1 += " AND R.RegionID = ?"
        p1.append(region)
    sql1 += " ORDER BY percentage_of_target DESC, country;"
    rows1 = exec_query(sql1, tuple(p1))

    # -------- Table 2: Per-region count meeting ≥90% --------
    sql2 = """
      SELECT V.antigen, V.year, R.region, COUNT(*) AS countries_met_90
      FROM Vaccination V
      JOIN Country C ON C.CountryID = V.country
      LEFT JOIN Region R ON R.RegionID = C.region
      WHERE V.coverage >= 90
    """
    p2 = []
    if antigen is not None:
        sql2 += " AND V.antigen = ?"
        p2.append(antigen)
    if year is not None:
        sql2 += " AND V.year = ?"
        p2.append(year)
    sql2 += """
      GROUP BY V.antigen, V.year, R.region
      ORDER BY countries_met_90 DESC, R.region;
    """
    rows2 = exec_query(sql2, tuple(p2))

    # ------------------------- HTML -------------------------
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Level 2A — Vaccination Rates</title>
  <style>
    body {{
      font-family: "Segoe UI", Roboto, Arial, sans-serif;
      margin: 0;
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

    .filters {{
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      justify-content: center;
      background: #dcfce7;
      padding: 16px;
      border-radius: 12px;
      margin: 20px auto;
      width: fit-content;
      box-shadow: 0 3px 8px rgba(0,0,0,0.1);
    }}
    select, button {{
      padding: 8px 12px;
      border: 1px solid #86efac;
      border-radius: 8px;
      background: white;
      color: #065f46;
    }}
    button {{
      background: #22c55e;
      color: white;
      cursor: pointer;
      border: none;
    }}
    button:hover {{
      background: #15803d;
    }}
    a {{
      text-decoration: none;
      color: #15803d;
      font-weight: 500;
    }}
    a:hover {{
      text-decoration: underline;
    }}

    table {{
      border-collapse: collapse;
      width: 90%;
      margin: 20px auto;
      background: white;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }}
    th, td {{
      border: 1px solid #e5e7eb;
      padding: 10px 14px;
      text-align: left;
    }}
    th {{
      background: #bbf7d0;
      color: #064e3b;
    }}
    tr:nth-child(even) {{
      background: #f9fafb;
    }}

    h3 {{
      text-align: center;
      color: #166534;
      margin-top: 30px;
    }}

    .footer {{
      text-align: center;
      margin: 30px 0;
    }}
    .footer a {{
      background: #bbf7d0;
      color: #065f46;
      padding: 8px 14px;
      border-radius: 8px;
      transition: 0.2s;
      margin: 0 5px;
    }}
    .footer a:hover {{
      background: #22c55e;
      color: white;
    }}
  </style>
</head>
<body>
  <header>
    <h1>💉 Vaccination Coverage by Country & Region</h1>
  </header>

  <form action="/page2" method="GET" class="filters">
    <label>Antigen
      <select name="antigen">
        <option value="">All</option>
        {options_html(antigen_opts, antigen)}
      </select>
    </label>

    <label>Year
      <select name="year">
        <option value="">All</option>
        {options_html(year_opts, year)}
      </select>
    </label>

    <label>Region
      <select name="region">
        <option value="">All regions</option>
        {options_html(region_opts, region)}
      </select>
    </label>

    <button type="submit">Apply</button>
    <a href="/page2">Reset</a>
  </form>

  <h3>🌍 Countries Meeting ≥90% Vaccination Target</h3>
  <table>
    <thead>
      <tr><th>Antigen</th><th>Year</th><th>Country</th><th>Region</th><th>% of Target</th></tr>
    </thead>
    <tbody>
      { ( "".join( td_row(r) for r in rows1 ) ) or "<tr><td colspan='5'>No data</td></tr>" }
    </tbody>
  </table>

  <h3>🗺️ Regional Counts Meeting ≥90%</h3>
  <table>
    <thead>
      <tr><th>Antigen</th><th>Year</th><th>Region</th><th>Countries ≥90%</th></tr>
    </thead>
    <tbody>
      { ( "".join( td_row(r) for r in rows2 ) ) or "<tr><td colspan='4'>No data</td></tr>" }
    </tbody>
  </table>

  <div class="footer">
    <a href="/">← Back to Level 1A</a>
    <a href="/page3">→ Go to Level 3A</a>
  </div>
</body>
</html>"""
    return page_html
