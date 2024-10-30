from flask import Flask
from algo.backtesting_utils import run_backtest
import pandas as pd
import numpy as np


#backtesting
from algo.strategies.rsi_strategy import RSIStrategy
from algo.strategies.moving_average_strategy import MovingAverageStrategy
from algo.strategies.stochastic_strategy import StochasticStrategy
from algo.strategies.bollinger_bands_strategy import BollingerBandsStrategy
from algo.strategies.macd_strategy import MACDStrategy
from algo.data_preprocessing import get_historical_data

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
    
