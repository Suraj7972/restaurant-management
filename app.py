from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load dataset
DATA_FILE = "restaurant_items.csv"
MENU_FILE = "restaurant_items.csv"

# Ensure the CSV file exists
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Item", "Quantity Sold", "Total Sales", "Total Profit"]).to_csv(DATA_FILE, index=False)

# Load menu data
menu_df = pd.read_csv(MENU_FILE)

@app.route('/')
def index():
    return render_template('index.html', menu=menu_df.to_dict(orient="records"))

@app.route('/get_menu')
def get_menu():
    return jsonify(menu_df.to_dict(orient="records"))

@app.route('/save_sales', methods=['POST'])
def save_sales():
    data = request.json
    date = data.get('date')
    items = data.get('items')

    sales_records = []
    total_sales = 0
    total_profit = 0

    for item in items:
        name = item['name']
        quantity = int(item['quantity'])
        selling_price = float(item['selling_price'])
        profit_per_item = float(item['profit'])

        total_item_sales = quantity * selling_price
        total_item_profit = quantity * profit_per_item

        total_sales += total_item_sales
        total_profit += total_item_profit

        sales_records.append([date, name, quantity, total_item_sales, total_item_profit])

    df = pd.DataFrame(sales_records, columns=["Date", "Item", "Quantity Sold", "Total Sales", "Total Profit"])
    df.to_csv(DATA_FILE, mode='a', header=False, index=False)

    return jsonify({"message": "Sales saved successfully!", "total_sales": total_sales, "total_profit": total_profit})

@app.route('/analysis')
def analysis():
    df = pd.read_csv(DATA_FILE)
    return render_template('analysis.html', sales_data=df.to_dict(orient="records"))

@app.route('/get_analysis', methods=['GET'])
def get_analysis():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    
    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    
    return jsonify(filtered_df.to_dict(orient="records"))

if __name__ == '__main__':
    app.run(debug=True)
