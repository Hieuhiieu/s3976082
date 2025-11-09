# student_a_level_3.py
import os
import sqlite3
import pyhtml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

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
        try: return cast(v)
        except: return None
    return v

def options_html(options, selected_val):
    sel = "" if selected_val is None else str(selected_val).strip()
    out = []
    for val, label in options:
        v = "" if val is None else str(val).strip()
        s = ' selected="selected"' if v == sel else ""
        out.append(f'<option value="{v}"{s}>{label}</option>')
    return "\n".join(out)

def td_row(cells):
    return "<tr>" + "".join(f"<td>{'' if c is None else c}</td>" for c in cells) + "</tr>"

COVER_REAL = "CAST(NULLIF(TRIM(CAST(coverage AS TEXT)), '') AS REAL)"

def get_page_html(form_data):

    antigen_name = get_first(form_data, "antigen")
    start_year   = get_first(form_data, "start_year", int)
    end_year     = get_first(form_data, "end_year", int)
    top_n        = get_first(form_data, "display_n", int)

    if top_n is None: top_n = 10

    antigen_opts = exec_query("SELECT name, name FROM Antigen ORDER BY name;")
    year_vals    = [y[0] for y in exec_query("SELECT DISTINCT year FROM Vaccination ORDER BY year;")]
    year_opts    = [(y, y) for y in year_vals]

    if start_year is None and year_vals: start_year = year_vals[0]
    if end_year is None and year_vals:   end_year   = year_vals[-1]

    rows = []
    warning = None

    if start_year is not None and end_year is not None and start_year <= end_year:
        sql = f"""
        SELECT
            C.name AS country,
            A.name AS antigen,
            ROUND({COVER_REAL.replace("coverage","V1.coverage")},2) AS start_pct,
            ROUND({COVER_REAL.replace("coverage","V2.coverage")},2) AS end_pct,
            ROUND(
                ({COVER_REAL.replace("coverage","V2.coverage")}
                 - {COVER_REAL.replace("coverage","V1.coverage")}),2
            ) AS increase,
            V1.year AS start_year,
            V2.year AS end_year
        FROM Vaccination V1
        JOIN Vaccination V2
            ON V1.country = V2.country
           AND V1.antigen = V2.antigen
        JOIN Country C ON C.CountryID = V1.country
        JOIN Antigen A ON A.AntigenID = V1.antigen
        WHERE V1.year = ?
          AND V2.year = ?
          AND {COVER_REAL.replace("coverage","V1.coverage")} IS NOT NULL
          AND {COVER_REAL.replace("coverage","V2.coverage")} IS NOT NULL
        """
        params = [start_year, end_year]

        if antigen_name:
            sql += " AND A.name = ?"
            params.append(antigen_name.strip())

        sql += " ORDER BY increase DESC LIMIT ?"
        params.append(top_n if top_n > 0 else 10)

        rows = exec_query(sql, tuple(params))
    else:
        warning = "⚠️ Please choose a valid start and end year (start ≤ end)."

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Improvements in Vaccination Coverage</title>

<style>
  body {{
    font-family: "Segoe UI", Roboto, Arial, sans-serif;
    margin: 0;
    background: linear-gradient(135deg, #bbf7d0 0%, #e8ffef 100%);
    color: #064e3b;
    min-height: 100vh;
  }}

  .navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 60px;
    background: #16a34a;
    color: white;
    font-weight: 600;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }}
  .navbar a {{
    color: white;
    text-decoration: none;
    margin-left: 24px;
    font-weight: 500;
  }}
  .navbar a:hover {{ text-decoration: underline; }}

  header {{
    text-align: center;
    padding: 35px 20px 10px;
    font-size: 1.8rem;
    font-weight: 700;
    color: #064e3b;
  }}

  .filters {{
    display: flex;
    gap: 10px;
    align-items: end;
    justify-content: center;
    flex-wrap: wrap;
    background: #dcfce7;
    padding: 16px;
    border-radius: 12px;
    margin: 10px auto 15px;
    width: fit-content;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08);
  }}

  :root {{ --ctl-w: 160px; --ctl-h: 32px; }}

  .filters select,
  .filters input[type="number"] {{
    width: var(--ctl-w);
    height: var(--ctl-h);
    padding: 6px 8px;
    border: 1px solid #86efac;
    border-radius: 8px;
    background: white;
    color: #065f46;
    font: inherit;
    box-sizing: border-box;
  }}

  .filters button {{
    height: var(--ctl-h);
    background: #22c55e;
    border: none;
    color: white;
    padding: 0 16px;
    border-radius: 8px;
    cursor: pointer;
  }}
  .filters button:hover {{ background: #15803d; }}

  table {{
    border-collapse: collapse;
    width: 92%;
    margin: 20px auto;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
  }}
  th, td {{
    border: 1px solid #e5e7eb;
    padding: 12px 14px;
    text-align: left;
  }}
  th {{
    background: #86efac;
    color: #064e3b;
    font-weight: 600;
  }}
  tr:nth-child(even) {{ background: #f9fafb; }}
</style>
</head>

<body>

<div class="navbar">
  <div>🌿 Immunisation Insights</div>
  <div>
    <a href="/">Overview</a>
    <a href="/page2">Coverage</a>
    <a href="/page3">Improvements</a>
  </div>
</div>

<header>Improvements in Vaccination Coverage</header>

<form class="filters" action="/page3" method="GET">

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

  <label>Results to display
    <input type="number" name="display_n" min="1" max="100" value="{top_n}">
  </label>

  <button type="submit">Apply</button>
  <a href="/page3" style="text-decoration:none;"><button type="button" style="background:#bbf7d0;color:#064e3b;border:1px solid #86efac;">Reset</button></a>
</form>

{"<div class='warn'>"+warning+"</div>" if warning else ""}

<table>
  <thead>
    <tr>
      <th>Country</th>
      <th>Antigen</th>
      <th>Start %</th>
      <th>End %</th>
      <th>Increase</th>
      <th>Start Year</th>
      <th>End Year</th>
    </tr>
  </thead>
  <tbody>
    {( "".join( td_row(r) for r in rows ) ) or "<tr><td colspan='7' style='text-align:center'>No data</td></tr>"}
  </tbody>
</table>

</body>
</html>"""
    return page_html
