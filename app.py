from flask import Flask, render_template, request
import pandas as pd
import os
import glob

app = Flask(__name__)

REPORTS_FOLDER = "daily_reports"
ITEMS_CSV = "restaurant_items.csv"

# Ensure reports folder exists
if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)

def load_items():
    """Load restaurant items from CSV file."""
    if not os.path.exists(ITEMS_CSV):
        print("Error: restaurant_items.csv is missing!")
        return pd.DataFrame(columns=["Item", "Selling Price", "Profit"])
    
    df = pd.read_csv(ITEMS_CSV)

    expected_columns = {"Item", "Selling Price", "Profit"}
    actual_columns = set(df.columns.str.strip())

    if not expected_columns.issubset(actual_columns):
        print(f"Error: CSV file columns do not match! Found: {actual_columns}")
        return pd.DataFrame(columns=["Item", "Selling Price", "Profit"])

    return df

@app.route("/", methods=["GET", "POST"])
def index():
    items = load_items()
    saved_message = None

    if request.method == "POST":
        selected_date = request.form.get("date")
        if not selected_date:
            return "Please select a date.", 400

        sales_data = []
        total_sales = 0
        total_profit = 0

        for index, row in items.iterrows():
            quantity = request.form.get(f"quantity_{index}", 0)
            quantity = int(quantity) if quantity else 0

            item_sales = quantity * row["Selling Price"]
            item_profit = quantity * row["Profit"]

            total_sales += item_sales
            total_profit += item_profit

            sales_data.append([selected_date, row["Item"], row["Selling Price"], row["Profit"], quantity, item_sales, item_profit])

        # Save report to CSV
        report_file = os.path.join(REPORTS_FOLDER, f"{selected_date}.csv")
        df_report = pd.DataFrame(sales_data, columns=["Date", "Item", "Selling Price", "Profit", "Quantity Sold", "Total Sales", "Total Profit"])
        df_report.to_csv(report_file, index=False)

        saved_message = f"Report for {selected_date} saved successfully!"

    return render_template("index.html", data=items, message=saved_message)

@app.route("/analysis", methods=["GET", "POST"])
def analysis():
    total_sales = None
    total_profit = None
    dates = []
    sales = []
    profits = []

    if request.method == "POST":
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        report_files = sorted(glob.glob(os.path.join(REPORTS_FOLDER, "*.csv")))

        for report_file in report_files:
            date = os.path.basename(report_file).replace(".csv", "")
            if start_date <= date <= end_date:
                df = pd.read_csv(report_file)
                dates.append(date)
                sales.append(df["Total Sales"].sum())
                profits.append(df["Total Profit"].sum())

        total_sales = sum(sales)
        total_profit = sum(profits)

    return render_template("analysis.html", total_sales=total_sales, total_profit=total_profit, dates=dates, sales=sales, profits=profits)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port, debug=False)
