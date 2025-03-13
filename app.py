from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load restaurant dataset
DATASET_PATH = "restaurant_items.csv"
REPORTS_FOLDER = "reports"

if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)

df = pd.read_csv(DATASET_PATH)

# Ensure necessary columns exist
if "Item" not in df.columns or "Selling Price" not in df.columns or "Profit Margin" not in df.columns:
    raise Exception("Dataset must contain 'Item', 'Selling Price', and 'Profit Margin' columns!")

@app.route("/")
def index():
    return render_template("index.html", menu=df.to_dict(orient="records"))

@app.route("/get_menu", methods=["POST"])
def get_menu():
    return jsonify(df.to_dict(orient="records"))

@app.route("/save_report", methods=["POST"])
def save_report():
    data = request.json
    date = data.get("date")
    items = data.get("items")

    if not date or not items:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    report_file = os.path.join(REPORTS_FOLDER, f"{date}.csv")
    report_df = pd.DataFrame(items)
    report_df.to_csv(report_file, index=False)

    return jsonify({"status": "success", "message": "Report saved!"})

@app.route("/get_analysis", methods=["POST"])
def get_analysis():
    start_date = request.json.get("start_date")
    end_date = request.json.get("end_date")

    all_data = []
    for file in os.listdir(REPORTS_FOLDER):
        if file.endswith(".csv"):
            date = file.replace(".csv", "")
            df_report = pd.read_csv(os.path.join(REPORTS_FOLDER, file))
            total_sales = df_report["Total Sales"].sum()
            total_profit = df_report["Total Profit"].sum()
            all_data.append({"date": date, "sales": total_sales, "profit": total_profit})

    return jsonify(sorted(all_data, key=lambda x: x["date"]))

if __name__ == "__main__":
    app.run(debug=True)
