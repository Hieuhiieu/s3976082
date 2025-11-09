# student_a_level_2.py
import os
import sqlite3

# ---------- DB path ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

# ---------- shared CSS (unified across all levels) ----------
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

/* FILTERS */
.filters{
  display:flex; gap:14px; align-items:end; flex-wrap:wrap; justify-content:center;
  background:#dcfce7; padding:14px 16px; border-radius:12px;
  margin:18px auto 10px; width:fit-content;
  box-shadow:0 3px 8px rgba(0,0,0,.08);
}
.filters label{display:grid; gap:4px; font-size:.95rem; color:#065f46;}
select{
  padding:9px 12px; height:36px; border-radius:8px;
  border:1px solid #86efac; background:#fff; color:#065f46;
  min-width:220px;
}
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

/* TABLES */
table{
  border-collapse:collapse; width:95%; margin:20px auto; background:#fff;
  border-radius:12px; overflow:hidden; box-shadow:0 4px 10px rgba(0,0,0,.08);
}
th,td{border:1px solid #e5e7eb; padding:10px 14px; text-align:left}
th{background:#bbf7d0; color:#064e3b}
tr:nth-child(even){background:#f9fafb}
</style>
"""

# ---------- helpers ----------
def exec_query(sql: str, params=()):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return rows

def get_first(form_data, key):
    """
    Return the first value for a query param (or None).
    Works for {'k': ['v']} and {'k': 'v'}. Empty string -> None.
    """
    v = form_data.get(key)
    if isinstance(v, list):
        v = v[0] if v else None
    if v in (None, "", "None"):
        return None
    return str(v)

def options_html(options, selected_val):
    """
    Build <option> tags. options: [(value,label), ...]
    Keeps selection even if types differ by normalizing to strings.
    """
    sel = "" if selected_val is None else str(selected_val).strip()
    out = []
    for val, label in options:
        v = "" if val is None else str(val).strip()
        s = ' selected="selected"' if v == sel else ""
        out.append(f'<option value="{v}"{s}>{label}</option>')
    return "\n".join(out)

def td_row(cells):
    return "<tr>" + "".join(f"<td>{'' if c is None else c}</td>" for c in cells) + "</tr>"

# cast coverage -> REAL; ignore blanks
PCT_EXPR = "CAST(NULLIF(TRIM(CAST(V.coverage AS TEXT)), '') AS REAL)"

# ---------- main ----------
def get_page_html(form_data):
    """
    Coverage page (Level 2):
      - Filters: antigen (name), year (year), region (name)
      - Table 1: countries meeting ≥90%
      - Table 2: per-region count meeting ≥90%
    """
    antigen = get_first(form_data, "antigen")
    year    = get_first(form_data, "year")
    region  = get_first(form_data, "region")

    # dropdown sources
    antigen_opts = exec_query("SELECT name, name FROM Antigen ORDER BY name;")
    year_opts    = [(y[0], y[0]) for y in exec_query("SELECT DISTINCT year FROM Vaccination ORDER BY year;")]
    region_opts  = exec_query("SELECT region, region FROM Region ORDER BY region;")

    # ---------- Table 1: Countries meeting ≥90% ----------
    sql1 = f"""
      SELECT
        A.name AS antigen,
        V.year AS year,
        C.name AS country,
        R.region AS region,
        ROUND({PCT_EXPR}, 1) AS pct
      FROM Vaccination V
      JOIN Antigen  A ON A.AntigenID  = V.antigen
      JOIN Country  C ON C.CountryID  = V.country
      LEFT JOIN Region  R ON R.RegionID = C.region
      WHERE {PCT_EXPR} IS NOT NULL AND {PCT_EXPR} >= 90
    """
    p1 = []
    if antigen:
        sql1 += " AND A.name = ?"; p1.append(antigen.strip())
    if year:
        sql1 += " AND V.year = ?"; p1.append(year.strip())
    if region:
        sql1 += " AND R.region = ?"; p1.append(region.strip())
    sql1 += " ORDER BY pct DESC, country;"
    rows1 = exec_query(sql1, tuple(p1))

    # ---------- Table 2: Per-region counts meeting ≥90% ----------
    sql2 = f"""
      SELECT
        A.name   AS antigen,
        V.year   AS year,
        R.region AS region,
        COUNT(DISTINCT C.CountryID) AS countries_met_90
      FROM Vaccination V
      JOIN Antigen  A ON A.AntigenID  = V.antigen
      JOIN Country  C ON C.CountryID  = V.country
      LEFT JOIN Region  R ON R.RegionID = C.region
      WHERE {PCT_EXPR} IS NOT NULL AND {PCT_EXPR} >= 90
    """
    p2 = []
    if antigen:
        sql2 += " AND A.name = ?"; p2.append(antigen.strip())
    if year:
        sql2 += " AND V.year = ?"; p2.append(year.strip())
    if region:
        sql2 += " AND R.region = ?"; p2.append(region.strip())
    sql2 += """
      GROUP BY A.name, V.year, R.region
      ORDER BY countries_met_90 DESC, R.region;
    """
    rows2 = exec_query(sql2, tuple(p2))

    # ---------- HTML ----------
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Coverage</title>
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
      <h1>Vaccination Coverage by Country & Region</h1>
    </div>
  </header>

  <div class="wrap">
    <form action="/page2" method="GET" class="filters">
      <label>Antigen
        <select name="antigen">
          <option value="">All antigens</option>
          {options_html(antigen_opts, antigen)}
        </select>
      </label>
      <label>Year
        <select name="year">
          <option value="">All years</option>
          {options_html(year_opts, year)}
        </select>
      </label>
      <label>Region
        <select name="region">
          <option value="">All regions</option>
          {options_html(region_opts, region)}
        </select>
      </label>
      <button class="btn-apply" type="submit">Apply</button>
      <a class="reset-link" href="/page2">Reset</a>
    </form>

    <h3 style="text-align:center; color:#166534; margin-top:26px;">🌍 Countries Meeting ≥90% Vaccination Target</h3>
    <table>
      <thead>
        <tr><th>Antigen</th><th>Year</th><th>Country</th><th>Region</th><th>% of Target</th></tr>
      </thead>
      <tbody>
        { ( "".join( td_row(r) for r in rows1 ) ) or "<tr><td colspan='5'>No data</td></tr>" }
      </tbody>
    </table>

    <h3 style="text-align:center; color:#166534; margin-top:26px;">🗺 Regional Counts Meeting ≥90%</h3>
    <table>
      <thead>
        <tr><th>Antigen</th><th>Year</th><th>Region</th><th>Countries ≥90%</th></tr>
      </thead>
      <tbody>
        { ( "".join( td_row(r) for r in rows2 ) ) or "<tr><td colspan='4'>No data</td></tr>" }
      </tbody>
    </table>
  </div>
</body>
</html>
"""
