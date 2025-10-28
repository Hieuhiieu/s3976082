# student_a_level_3.py
import os
import sqlite3
import pyhtml

# --- Absolute path to database ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "immunisation.db")

# ------------------------- helpers -------------------------
def exec_query(sql: str, params=()):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return rows

def get_first(form_data, key, cast=None):
    """
    Get first value of query param 'key'. Works for {'k':['v']} and {'k':'v'}.
    Empty string -> None. Optionally cast (e.g., int).
    """
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
    """
    Render <option> for <select>. options: [(value,label),...]
    Handles type differences (int/str) safely.
    """
    sel = "" if selected_val is None else str(selected_val).strip()
    out = []
    for val, label in options:
        v_str = "" if val is None else str(val).strip()
        s = ' selected="selected"' if v_str == sel else ""
        out.append(f'<option value="{v_str}"{s}>{label}</option>')
    return "\n".join(out)

def td_row(cells):
    return "<tr>" + "".join(f"<td>{'' if c is None else c}</td>" for c in cells) + "</tr>"

# Safely coerce coverage text->REAL and ignore blanks
COVER_REAL = "CAST(NULLIF(TRIM(CAST(coverage AS TEXT)), '') AS REAL)"

# ------------------------- main page -------------------------
def get_page_html(form_data):
    """
    Level 3A — Improvement in vaccination coverage:
      Inputs:
        - antigen (by name)
        - start_year
        - end_year
        - top_n (how many countries to list)
      Output:
        - Table of countries with largest (end - start) coverage increase
    """

    # --- read filters ---
    antigen_name = get_first(form_data, "antigen")     # e.g. "DTP-containing vaccine, 3rd dose"
    start_year   = get_first(form_data, "start_year", int)
    end_year     = get_first(form_data, "end_year", int)
    top_n        = get_first(form_data, "top_n", int)

    # defaults (so the page shows something on first load)
    if top_n is None:      top_n = 10

    # dropdown sources
    antigen_opts = exec_query("SELECT name, name FROM Antigen ORDER BY name;")  # value=label=name
    year_vals    = [y[0] for y in exec_query("SELECT DISTINCT year FROM Vaccination ORDER BY year;")]
    year_opts    = [(y, y) for y in year_vals]

    # If no years chosen yet, pick a sensible default range
    if start_year is None and year_vals:
        start_year = year_vals[0]
    if end_year is None and year_vals:
        end_year = year_vals[-1]

    rows = []
    warning = None

    # Only run when we have both years and a valid order (start <= end)
    if start_year is not None and end_year is not None and start_year <= end_year:
        # Build query: join same country+antigen across the two chosen years, compute end−start
        sql = f"""
            SELECT
                C.name AS country,
                A.name AS antigen,
                ROUND(
                    (CAST(NULLIF(TRIM(CAST(V2.coverage AS TEXT)), '') AS REAL)
                   -CAST(NULLIF(TRIM(CAST(V1.coverage AS TEXT)), '') AS REAL)
                    ), 2
                ) AS rate_increase,
                V1.year AS start_year,
                V2.year AS end_year
            FROM Vaccination V1
            JOIN Vaccination V2
              ON V1.country = V2.country
             AND V1.antigen = V2.antigen
            JOIN Country  C ON C.CountryID  = V1.country
            JOIN Antigen  A ON A.AntigenID  = V1.antigen
            WHERE V1.year = ?
              AND V2.year = ?
              AND {COVER_REAL.replace("coverage", "V1.coverage")} IS NOT NULL
              AND {COVER_REAL.replace("coverage", "V2.coverage")} IS NOT NULL
        """
        params = [start_year, end_year]

        # Optional antigen filter by name (matches Antigen.name)
        if antigen_name:
            sql += " AND A.name = ?"
            params.append(antigen_name.strip())

        sql += """
            ORDER BY rate_increase DESC
            LIMIT ?
        """
        params.append(top_n if isinstance(top_n, int) and top_n > 0 else 10)

        rows = exec_query(sql, tuple(params))
    else:
        warning = "Please choose a valid start and end year (start ≤ end)."

    # ------------------------- HTML -------------------------
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Level 3A — Improvement Analysis</title>
  <style>
    body {{
      font-family: "Segoe UI", Roboto, Arial, sans-serif;
      margin: 0;
      background: linear-gradient(135deg, #cffafe 0%, #ecfeff 100%);
      color: #0e7490;
      min-height: 100vh;
    }}
    header {{
      text-align: center;
      padding: 40px 20px 20px;
      background: linear-gradient(90deg, #06b6d4, #0891b2);
      color: white;
      box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }}
    header h1 {{ margin: 0; font-size: 2rem; letter-spacing: .5px; }}

    .filters {{
      display: flex; gap: 12px; align-items: end; flex-wrap: wrap; justify-content: center;
      background: #e0f2fe; padding: 16px; border-radius: 12px; margin: 20px auto; width: fit-content;
      box-shadow: 0 3px 8px rgba(0,0,0,0.08);
    }}
    .filters label {{ display: grid; gap: 4px; font-size: .95rem; color: #075985; }}
    select, input[type="number"], button {{
      padding: 8px 12px; border: 1px solid #7dd3fc; border-radius: 8px; background: white; color: #075985;
    }}
    input[type="number"] {{ width: 90px; }}
    button {{ background: #06b6d4; color: white; cursor: pointer; border: none; }}
    button:hover {{ background: #0ea5e9; }}
    a {{ text-decoration: none; color: #0ea5e9; font-weight: 500; }}
    a:hover {{ text-decoration: underline; }}

    .warn {{
      max-width: 900px; margin: 0 auto; color: #b45309; background: #fffbeb; border: 1px solid #fcd34d;
      padding: 10px 14px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }}

    table {{
      border-collapse: collapse; width: 90%; margin: 20px auto; background: white;
      border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }}
    th, td {{ border: 1px solid #e5e7eb; padding: 10px 14px; text-align: left; }}
    th {{ background: #bae6fd; color: #075985; }}
    tr:nth-child(even) {{ background: #f9fafb; }}

    .footer {{ text-align: center; margin: 30px 0; }}
    .footer a {{
      background: #bae6fd; color: #075985; padding: 8px 14px; border-radius: 8px; transition: .2s; margin: 0 5px;
    }}
    .footer a:hover {{ background: #06b6d4; color: white; }}
  </style>
</head>
<body>
  <header>
    <h1>📈 Level 3A — Biggest Improvements in Vaccination Coverage</h1>
  </header>

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

    <label>Top N
      <input type="number" name="top_n" min="1" max="100" value="{top_n or 10}">
    </label>

    <button type="submit">Apply</button>
    <a href="/page3">Reset</a>
  </form>

  {"<div class='warn'>"+warning+"</div>" if warning else ""}

  <table>
    <thead>
      <tr>
        <th>Country</th>
        <th>Antigen</th>
        <th>Increase (end − start)</th>
        <th>Start Year</th>
        <th>End Year</th>
      </tr>
    </thead>
    <tbody>
      { ( "".join( td_row(r) for r in rows ) ) or "<tr><td colspan='5'>No data</td></tr>" }
    </tbody>
  </table>

  <div class="footer">
    <a href="/">← Back to Level 1A</a>
    <a href="/page2">← Back to Level 2A</a>
  </div>
</body>
</html>"""
    return page_html
