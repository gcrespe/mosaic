from flask import Flask
from algo.backtesting_utils import run_backtest

#backtesting
from algo.strategies.rsi_strategy import RSIStrategy
from algo.strategies.moving_average_strategy import MovingAverageStrategy
from algo.strategies.stochastic_strategy import StochasticStrategy
from algo.strategies.bollinger_bands_strategy import BollingerBandsStrategy
from algo.strategies.macd_strategy import MACDStrategy

app = Flask(__name__)

@app.route('/backtesting/rsi')
def rsi_backtest():
    stats = run_backtest(RSIStrategy, "RSI Strategy")
    return stats

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return "404"

# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return "500"