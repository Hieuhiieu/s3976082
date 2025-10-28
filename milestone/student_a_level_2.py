# student_a_level_2.py
import os
import sqlite3
import pyhtml

# --- Absolute path tới database (không phụ thuộc thư mục chạy lệnh) ---
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
  <title>Level 2A — Vaccination</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 24px; }}
    .filters {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin: 10px 0 16px; }}
    select, button {{ padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 8px; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; }}
    th {{ background: #f7f7f7; }}
    h1 {{ margin: 0 0 12px; }}
    a {{ text-decoration: none; color: #2563eb; }}
  </style>
</head>
<body>
  <h1>Vaccination rates by country & region</h1>

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

    <label>Region (optional)
      <select name="region">
        <option value="">All regions</option>
        {options_html(region_opts, region)}
      </select>
    </label>

    <button type="submit">Apply</button>
    <span style="margin-left:8px"><a href="/page2">Reset</a></span>
    <span style="margin-left:16px"><a href="/">← Back to Level 1A</a></span>
  </form>

  <h3>Countries met ≥90% target</h3>
  <table>
    <thead>
      <tr><th>Antigen</th><th>Year</th><th>Country</th><th>Region</th><th>% of target</th></tr>
    </thead>
    <tbody>
      { ( "".join( td_row(r) for r in rows1 ) ) or "<tr><td colspan='5'>No data</td></tr>" }
    </tbody>
  </table>

  <h3>Per-region count meeting ≥90%</h3>
  <table>
    <thead>
      <tr><th>Antigen</th><th>Year</th><th>Region</th><th>Countries met 90%</th></tr>
    </thead>
    <tbody>
      { ( "".join( td_row(r) for r in rows2 ) ) or "<tr><td colspan='4'>No data</td></tr>" }
    </tbody>
  </table>
</body>
</html>"""
    return page_html
