from flask import Flask, jsonify
from flasgger import Swagger
import requests
import time
import os

app = Flask(__name__)
# Initialize Swagger
swagger = Swagger(app)

API_KEY = os.environ.get("N8I304DMB8HY7XLK")
BASE_URL = "https://www.alphavantage.co/query"

price_cache = {}
CACHE_DURATION = 60 

def fetch_alpha_price(symbol):
    current_time = time.time()
    if symbol in price_cache:
        cached_data = price_cache[symbol]
        if current_time - cached_data['timestamp'] < CACHE_DURATION:
            return cached_data['price']

    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": API_KEY}
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price = float(data["Global Quote"]["05. price"])
            price_cache[symbol] = {"price": price, "timestamp": current_time}
            return price
    except Exception:
        return None

@app.route('/api/stock/<ticker>')
def get_stock(ticker):
    """
    Get Real-Time Stock Price
    This endpoint returns the latest price for a given stock ticker.
    ---
    parameters:
      - name: ticker
        in: path
        type: string
        required: true
        description: The stock symbol (e.g., AAPL, RELIANCE.BSE)
    responses:
      200:
        description: A successful response with stock data
      400:
        description: Invalid ticker or API limit reached
    """
    ticker = ticker.upper()
    price = fetch_alpha_price(ticker)
    
    if price:
        return jsonify({
            "ticker": ticker,
            "price": round(price, 2),
            "status": "success"
        })
    return jsonify({"status": "error", "message": "API limit reached"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)