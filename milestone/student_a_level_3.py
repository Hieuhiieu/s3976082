# student_a_level_3.py
import os
import sqlite3

# --- DB path (absolute) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

# --- shared CSS (unified across all levels) ---
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

/* FILTERS (aligned with Level 2) */
.filters{
  display:flex; gap:14px; align-items:end; flex-wrap:wrap; justify-content:center;
  background:#dcfce7; padding:14px 16px; border-radius:12px;
  margin:18px auto 10px; width:fit-content;
  box-shadow:0 3px 8px rgba(0,0,0,.08);
}
.filters label{display:grid; gap:4px; font-size:.95rem; color:#065f46;}
select, input[type="number"]{
  padding:9px 12px; height:36px; border-radius:8px;
  border:1px solid #86efac; background:#fff; color:#065f46;
}
select{min-width:220px;}
input[type="number"]{width:120px;}
.btn-apply{
  height:36px; padding:0 16px; border:none; cursor:pointer;
  border-radius:8px; background:var(--g1); color:#fff; transition:.15s;
}
.btn-apply:hover{background:var(--g2);}
.reset-link{
  align-self:center; height:36px; display:inline-flex; align-items:center;
  color:#15803d; text-decoration:none; padding:0 8px;
}
.reset-link:hover{text-decoration:underline;}

/* TABLE */
table{
  border-collapse:collapse; width:95%; margin:20px auto; background:#fff;
  border-radius:12px; overflow:hidden; box-shadow:0 4px 10px rgba(0,0,0,.08);
}
th,td{border:1px solid #e5e7eb; padding:10px 14px; text-align:left}
th{background:#bbf7d0; color:#064e3b}
tr:nth-child(even){background:#f9fafb}

/* highlight top 1 row */
tr.top1 td{
  background:#f0fdf4 !important;
  border-top:2px solid #22c55e;
  border-bottom:2px solid #22c55e;
  font-weight:600;
}
.warn{
  max-width:900px; margin:10px auto; color:#b45309; background:#fffbeb; border:1px solid #fcd34d;
  padding:10px 14px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,.06);
}
</style>
"""

# --- helpers ---
def exec_query(sql: str, params=()):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return rows

def get_first(form_data, key, cast=None):
    v = form_data.get(key)
    if isinstance(v, list):
        v = v[0] if v else None
    if v in (None, "", "None"):
        return None
    if cast:
        try:
            return cast(v)
        except Exception:
            return None
    return v

def options_html(options, selected_val):
    sel = "" if selected_val is None else str(selected_val).strip()
    out = []
    for val, label in options:
        v_str = "" if val is None else str(val).strip()
        s = ' selected="selected"' if v_str == sel else ""
        out.append(f'<option value="{v_str}"{s}>{label}</option>')
    return "\n".join(out)

# coerce text coverage -> REAL, ignore blanks
COVER_REAL = "CAST(NULLIF(TRIM(CAST(coverage AS TEXT)), '') AS REAL)"

def get_page_html(form_data):
    """
    Level 3 — Improvements:
      Inputs:
        - antigen (Antigen.name)
        - start_year, end_year (Vaccination.year)
        - rows (LIMIT)
      Output:
        - Country & Antigen with Start %, End %, and Change (pp), sorted by biggest increase
    """
    antigen_name = get_first(form_data, "antigen")
    start_year   = get_first(form_data, "start_year", int)
    end_year     = get_first(form_data, "end_year", int)
    rows_limit   = get_first(form_data, "rows", int) or 10
    if rows_limit <= 0: rows_limit = 10

    # dropdown data
    antigen_opts = exec_query("SELECT name, name FROM Antigen ORDER BY name;")
    year_vals    = [y[0] for y in exec_query("SELECT DISTINCT year FROM Vaccination ORDER BY year;")]
    year_opts    = [(y, y) for y in year_vals]

    # defaults
    if start_year is None and year_vals:
        start_year = year_vals[0]
    if end_year is None and year_vals:
        end_year = year_vals[-1]

    warning = None
    results = []

    if start_year is not None and end_year is not None and start_year <= end_year:
        # main SQL: join same country+antigen across two years and compute start/end/increase
        sql = f"""
          SELECT
            C.name AS country,
            A.name AS antigen,
            ROUND(CAST(NULLIF(TRIM(CAST(V1.coverage AS TEXT)), '') AS REAL), 1) AS start_pct,
            ROUND(CAST(NULLIF(TRIM(CAST(V2.coverage AS TEXT)), '') AS REAL), 1) AS end_pct,
            ROUND(
              (CAST(NULLIF(TRIM(CAST(V2.coverage AS TEXT)), '') AS REAL)
               -CAST(NULLIF(TRIM(CAST(V1.coverage AS TEXT)), '') AS REAL)), 2
            ) AS change_pp,
            V1.year AS start_year,
            V2.year AS end_year
          FROM Vaccination V1
          JOIN Vaccination V2
            ON V1.country = V2.country AND V1.antigen = V2.antigen
          JOIN Country  C ON C.CountryID = V1.country
          JOIN Antigen  A ON A.AntigenID = V1.antigen
          WHERE V1.year = ? AND V2.year = ?
            AND {COVER_REAL.replace("coverage","V1.coverage")} IS NOT NULL
            AND {COVER_REAL.replace("coverage","V2.coverage")} IS NOT NULL
        """
        params = [start_year, end_year]
        if antigen_name:
            sql += " AND A.name = ?"
            params.append(str(antigen_name).strip())
        sql += " ORDER BY change_pp DESC LIMIT ?"
        params.append(rows_limit)
        results = exec_query(sql, tuple(params))
    else:
        warning = "Please choose a valid start and end year (start ≤ end)."

    # build table rows (highlight first row)
    if results:
        body_html = []
        for idx, r in enumerate(results):
            # r = (country, antigen, start_pct, end_pct, change_pp, start_year, end_year)
            cls = " class='top1'" if idx == 0 else ""
            cells = "".join(f"<td>{'' if c is None else c}</td>" for c in r)
            body_html.append(f"<tr{cls}>{cells}</tr>")
        body_html = "".join(body_html)
    else:
        body_html = "<tr><td colspan='7'>No data</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Improvements</title>
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
      <h1>Biggest Improvements in Vaccination Coverage</h1>
    </div>
  </header>

  <div class="wrap">
    <form action="/page3" method="GET" class="filters">
      <label>Antigen
        <select name="antigen">
          <option value="">All antigens</option>
          {options_html(antigen_opts, antigen_name)}
        </select>
      </label>
      <label>Start year
        <select name="start_year">
          {options_html(year_opts, start_year)}
        </select>
      </label>
      <label>End year
        <select name="end_year">
          {options_html(year_opts, end_year)}
        </select>
      </label>
      <label>Rows to show
        <input type="number" name="rows" min="1" max="100" value="{rows_limit}">
      </label>
      <button class="btn-apply" type="submit">Apply</button>
      <a class="reset-link" href="/page3">Reset</a>
    </form>

    {("<div class='warn'>"+warning+"</div>") if warning else ""}

    <table>
      <thead>
        <tr>
          <th>Country</th>
          <th>Antigen</th>
          <th>Start %</th>
          <th>End %</th>
          <th>Change (pp)</th>
          <th>Start Year</th>
          <th>End Year</th>
        </tr>
      </thead>
      <tbody>
        {body_html}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
