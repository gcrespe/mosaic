# strategies/rsi_strategy.py

from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

def RSI(array, period):
    """
    Calculate the Relative Strength Index (RSI).
    """
    delta = np.diff(array)
    gain = np.maximum(delta, 0)
    loss = -np.minimum(delta, 0)
    gain = np.insert(gain, 0, 0)
    loss = np.insert(loss, 0, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.values

class RSIStrategy(Strategy):
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30

    def init(self):
        close_prices = self.data.Close
        self.rsi = self.I(RSI, close_prices, self.rsi_period)

    def next(self):
        if crossover(self.rsi, self.rsi_oversold):
            if not self.position.is_long:
                self.position.close()
                self.buy()
        elif crossover(self.rsi_overbought, self.rsi):
            if not self.position.is_short:
                self.position.close()
                self.sell()