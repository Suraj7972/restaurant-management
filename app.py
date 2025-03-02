from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load items data
CSV_FILE = "items.csv"
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["Item", "Selling Price", "Profit"])

# Ensure data is valid
df.fillna(0, inplace=True)
items = df.to_dict(orient="records")

SALES_DATA_FILE = "sales_data.csv"

@app.route("/")
def index():
    return render_template("index.html", items=items)

@app.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data received"}), 400

    df_sales = pd.DataFrame(data)
    if os.path.exists(SALES_DATA_FILE):
        df_existing = pd.read_csv(SALES_DATA_FILE)
        df_sales = pd.concat([df_existing, df_sales], ignore_index=True)

    df_sales.to_csv(SALES_DATA_FILE, index=False)
    return jsonify({"message": "Report saved successfully!"})

@app.route("/analysis")
def analysis():
    if os.path.exists(SALES_DATA_FILE):
        df = pd.read_csv(SALES_DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        df_summary = df.groupby("Date")[["Total Sales (₹)", "Total Profit (₹)"]].sum().reset_index()
        sales_data = df_summary.to_dict(orient="records")
    else:
        sales_data = []

    return render_template("analysis.html", sales_data=sales_data)

if __name__ == "__main__":
    app.run(debug=True)
