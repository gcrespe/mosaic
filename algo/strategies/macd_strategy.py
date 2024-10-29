# strategies/macd_strategy.py

from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def MACD(close_prices, n_fast=12, n_slow=26):
    """
    Calculate the MACD line.
    """
    ema_fast = pd.Series(close_prices).ewm(span=n_fast, adjust=False).mean()
    ema_slow = pd.Series(close_prices).ewm(span=n_slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    return macd_line.values

def SignalLine(macd_line, n_signal=9):
    """
    Calculate the Signal line.
    """
    signal_line = pd.Series(macd_line).ewm(span=n_signal, adjust=False).mean()
    return signal_line.values

class MACDStrategy(Strategy):
    """
    MACD Strategy:
    - Buys when the MACD Line crosses above the Signal Line.
    - Sells when the MACD Line crosses below the Signal Line.
    """
    # Strategy parameters
    n_fast = 12
    n_slow = 26
    n_signal = 9

    def init(self):
        close_prices = self.data.Close
        # Compute MACD Line
        self.macd_line = self.I(MACD, close_prices, self.n_fast, self.n_slow)
        # Compute Signal Line
        self.signal_line = self.I(SignalLine, self.macd_line, self.n_signal)

    def next(self):
        if crossover(self.macd_line, self.signal_line):
            if not self.position.is_long:
                self.position.close()
                self.buy()
        elif crossover(self.signal_line, self.macd_line):
            if not self.position.is_short:
                self.position.close()
                self.sell()