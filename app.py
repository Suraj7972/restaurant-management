from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

CSV_FILE = "items.csv"
SALES_FILE = "sales_data.csv"

# Load items from CSV
def load_items():
    if not os.path.exists(CSV_FILE):
        return []
    
    df = pd.read_csv(CSV_FILE)
    
    if "Item" not in df.columns or "Selling Price" not in df.columns or "Profit" not in df.columns:
        return []
    
    return df.to_dict(orient="records")

# Save daily sales
def save_sales(data):
    df = pd.DataFrame(data)
    
    if os.path.exists(SALES_FILE):
        existing_df = pd.read_csv(SALES_FILE)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_csv(SALES_FILE, index=False)

@app.route("/")
def index():
    items = load_items()
    return render_template("index.html", items=items)

@app.route("/save", methods=["POST"])
def save():
    data = request.json
    save_sales(data)
    return jsonify({"status": "success", "message": "Sales data saved successfully."})

@app.route("/analysis")
def analysis():
    return render_template("analysis.html")

@app.route("/get_sales_data", methods=["POST"])
def get_sales_data():
    if not os.path.exists(SALES_FILE):
        return jsonify([])
    
    df = pd.read_csv(SALES_FILE)
    
    start_date = request.json.get("start_date")
    end_date = request.json.get("end_date")
    
    df["Date"] = pd.to_datetime(df["Date"])
    
    if start_date and end_date:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    
    sales_summary = df.groupby("Date").agg({"Total Sales (₹)": "sum", "Total Profit (₹)": "sum"}).reset_index()
    
    return jsonify(sales_summary.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
