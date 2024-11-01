from flask import Flask, request, jsonify
from algo.backtesting_utils import run_backtest
import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi
import os

#backtesting
from algo.strategies.rsi_strategy import RSIStrategy
from algo.data_preprocessing import get_historical_data

# Alpaca API credentials (use paper trading endpoint)
ALPACA_API_KEY = 'PK4FAV3XHGPBEST2A5I7'
ALPACA_SECRET_KEY = 'eYz4F5ugsMgiS8qkXiAwpwlwpCE3noRs0u014FdD'
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets/'

# Initialize Alpaca API client
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version='v2')


app = Flask(__name__)

@app.route('/backtesting/rsi')
def rsi_backtest():

    ticker = 'AAPL'  # You can change this to any valid ticker symbol
    multiplier = 1
    timespan = 'hour'  # Fetch hourly data
    start_date = '2020-09-01'  # Adjust as needed

    get_historical_data(ticker, multiplier, timespan, start_date)
    
    stats = run_backtest(RSIStrategy, "RSI Strategy")
    return pd.Series(stats).to_json()

@app.route('/webhook/alpaca-tradingview', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data received'}), 400

    #TradingView
    side = data.get('side')  # "buy" or "sell"
    symbol = data.get('symbol')  # e.g., "SPY"
    order_type = data.get('type', 'market')  # e.g., "market"
    qty = data.get('qty')  # number of shares to trade
    time_in_force = data.get('time_in_force', 'gtc')
    order_class = data.get('order_class', 'bracket')
    price = data.get('price')

    try:

        if(side == "sell"): 
        # Place a bracket order
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                order_class=order_class,
                take_profit={'limit_price': round((price - (price * 0.03)), 00)},
                stop_loss={
                    'stop_price': round((price + (price * 0.02)), 00),
                    'limit_price': round((price + (price * 0.02)), 00)
                }
            )
        else:
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                order_class=order_class,
                take_profit={'limit_price': round(price + (price * 0.03), 00)},
                stop_loss={
                    'stop_price': round(price - (price * 0.02), 00),
                    'limit_price': round(price - (price * 0.02), 00)
                }
            )
        return jsonify({'message': f'{side.capitalize()} order placed for {qty} shares of {symbol} with bracket'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return "404"

# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return "500"


def serialize(value):
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    elif isinstance(value, pd.Timedelta):
        return str(value)
    elif isinstance(value, np.float64) or isinstance(value, np.int64):
        return float(value)
    elif isinstance(value, pd.DataFrame):
        # Para DataFrames que estão dentro de outros objetos, convertê-los também
        return value.to_dict(orient='list')
    else:
        return value
    
