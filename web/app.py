#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
import duckdb
import pandas as pd

app = Flask(__name__)


DUCKDB_FILE = '/Users/anthonynie/usefultool/duckdb_research/test.duckdb'

@app.route('/')
def fullscan():
    return render_template('fullscan.html')

@app.route('/fullscan')
def top_sql():
    conn = duckdb.connect(DUCKDB_FILE)
    df = conn.execute('select * from tablefullscan order by digestExecSumXactRows DESC limit 10').df()
    conn.close()
    return df.to_json(orient='records')

@app.route('/sql_details', methods=['POST'])
def sql_details():
    table_name = request.json.get('tablename')
    conn = duckdb.connect(DUCKDB_FILE)
    query = '''
        SELECT 
            plansCSV.tablename,
            plansCSV.digestID,
            plansCSV.digestExecCountXactRows,
            statementsCSV.digest_text,
            statementsCSV.plan
        FROM 
            plansCSV
        JOIN 
            statementsCSV
        ON 
            statementsCSV.digestID = plansCSV.digestID
        WHERE 
            plansCSV.tablename = ? 
            AND plansCSV.digestTableFullScan = 1
        order by digestExecCountXactRows DESC
    '''
    df = conn.execute(query, (table_name,)).df()
    conn.close()
    return df.to_json(orient='records')

@app.route('/workload_summary')
def workload_summary():
    conn = duckdb.connect(DUCKDB_FILE)
    # Sample query to get the statement counts
    query = '''
    SELECT 
        SUM(CASE WHEN stmt_type = 'Select' THEN exec_count ELSE 0 END) AS select_count,
        SUM(CASE WHEN stmt_type = 'Insert' THEN exec_count ELSE 0 END) AS insert_count,
        SUM(CASE WHEN stmt_type = 'Delete' THEN exec_count ELSE 0 END) AS delete_count,
        SUM(CASE WHEN stmt_type = 'Update' THEN exec_count ELSE 0 END) AS update_count,
    FROM statementsCSV;
    '''
    df = conn.execute(query).df()
    data = df.to_dict(orient='records')[0]
    conn.close()
    return render_template('workload_summary.html', data=data)

@app.route('/top_tables')
def top_tables():
    return render_template('top_tables.html')

@app.route('/tidb_tasks')
def tidb_tasks():
    return render_template('tidb_tasks.html')

@app.route('/tikv_tasks')
def tikv_tasks():
    return render_template('tikv_tasks.html')

if __name__ == '__main__':
    app.run(debug=True,port=4001)

