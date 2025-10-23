
from flask import Flask, render_template, request, g
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), 'immunisation.db')
app = Flask(__name__)

def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    min_year = db.execute('SELECT MIN(YearID) AS y FROM YearDate').fetchone()['y']
    max_year = db.execute('SELECT MAX(YearID) AS y FROM YearDate').fetchone()['y']
    total_doses = db.execute('SELECT COALESCE(SUM(doses),0) AS s FROM Vaccination').fetchone()['s']
    total_cases = db.execute('SELECT COALESCE(SUM(cases),0) AS s FROM InfectionData').fetchone()['s']
    diseases = [row['description'] for row in db.execute('SELECT description FROM Infection_Type ORDER BY description')]
    return render_template('index.html',
                           min_year=min_year, max_year=max_year,
                           total_doses=total_doses, total_cases=total_cases,
                           diseases=diseases)

@app.route('/vaccination', methods=['GET','POST'])
def vaccination_view():
    db = get_db()
    antigens = db.execute('SELECT AntigenID, name FROM Antigen ORDER BY name').fetchall()
    years = [row['year'] for row in db.execute('SELECT DISTINCT year FROM Vaccination ORDER BY year')]
    regions = db.execute('SELECT RegionID, region FROM Region ORDER BY region').fetchall()

    selected = {'antigen':'', 'year':'', 'region':''}
    table1 = []
    table2 = []

    if request.method == 'POST':
        selected['antigen'] = request.form.get('antigen','')
        selected['year'] = request.form.get('year','')
        selected['region'] = request.form.get('region','')
        params = {'antigen': selected['antigen'], 'year': selected['year']}

        base_sql = '''
        SELECT V.antigen, V.year, C.name AS country, R.region AS region, V.coverage AS percentage_of_target
        FROM Vaccination V
        JOIN Country C ON C.CountryID = V.country
        LEFT JOIN Region R ON R.RegionID = C.region
        WHERE V.antigen = :antigen AND V.year = :year AND V.coverage >= 90
        '''
        if selected['region']:
            base_sql += ' AND R.RegionID = :region'
            params['region'] = selected['region']
        base_sql += ' ORDER BY percentage_of_target DESC, country'

        table1 = db.execute(base_sql, params).fetchall()
        table2 = db.execute('''
            SELECT V.antigen, V.year, COUNT(*) AS countries_met_90, R.region
            FROM Vaccination V
            JOIN Country C ON C.CountryID = V.country
            LEFT JOIN Region R ON R.RegionID = C.region
            WHERE V.antigen = :antigen AND V.year = :year AND V.coverage >= 90
            GROUP BY V.antigen, V.year, R.region
            ORDER BY countries_met_90 DESC, R.region
        ''', params).fetchall()

    return render_template('vaccination.html',
                           antigens=antigens, years=years, regions=regions,
                           selected=selected, table1=table1, table2=table2)

if __name__ == '__main__':
    app.run(debug=True)
