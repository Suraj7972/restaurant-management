from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Load dataset
DATA_FILE = "restaurant_items.csv"
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def load_menu():
    df = pd.read_csv(DATA_FILE)
    df["Selling Price"] = df["Selling Price"].astype(float)
    df["Profit"] = df["Profit"].astype(float)
    df["Quantity Sold"] = 0  # Ensure quantity starts at 0
    return df

def save_report(date, data):
    report_file = os.path.join(REPORTS_DIR, f"{date}.csv")
    df = pd.DataFrame(data)
    df.to_csv(report_file, index=False)

def load_report(date):
    report_file = os.path.join(REPORTS_DIR, f"{date}.csv")
    if os.path.exists(report_file):
        return pd.read_csv(report_file).to_dict(orient='records')
    return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_menu', methods=['GET'])
def get_menu():
    df = load_menu()
    return jsonify(df.to_dict(orient='records'))

@app.route('/save_report', methods=['POST'])
def save_daily_report():
    data = request.json
    date = data.get("date")
    items = data.get("items")
    if not date or not items:
        return jsonify({"error": "Invalid data"}), 400
    save_report(date, items)
    return jsonify({"message": "Report saved successfully!"})

@app.route('/get_report', methods=['GET'])
def get_report():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Date is required"}), 400
    report = load_report(date)
    return jsonify(report)

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/get_analysis', methods=['GET'])
def get_analysis():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not start_date or not end_date:
        return jsonify({"error": "Start and end date required"}), 400
    
    reports = []
    for file in os.listdir(REPORTS_DIR):
        if file.endswith('.csv'):
            file_date = file.replace('.csv', '')
            if start_date <= file_date <= end_date:
                df = pd.read_csv(os.path.join(REPORTS_DIR, file))
                df['Date'] = file_date
                reports.append(df)
    
    if reports:
        result_df = pd.concat(reports, ignore_index=True)
        return jsonify(result_df.to_dict(orient='records'))
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
