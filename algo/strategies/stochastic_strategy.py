# strategies/stochastic_strategy.py

from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

def StochasticOscillator(high_prices, low_prices, close_prices, n=14):
    """
    Calculate the Stochastic Oscillator (%K and %D lines).
    """
    lowest_low = pd.Series(low_prices).rolling(window=n).min()
    highest_high = pd.Series(high_prices).rolling(window=n).max()
    percent_k = 100 * (close_prices - lowest_low) / (highest_high - lowest_low)
    percent_d = percent_k.rolling(window=3).mean()
    return percent_k.values, percent_d.values

class StochasticStrategy(Strategy):
    """
    Stochastic Oscillator Strategy:
    - Buys when %K crosses above %D below the oversold threshold.
    - Sells when %K crosses below %D above the overbought threshold.
    """
    # Strategy parameters
    n = 14
    overbought = 80
    oversold = 20

    def init(self):
        high_prices = self.data.High
        low_prices = self.data.Low
        close_prices = self.data.Close
        self.percent_k, self.percent_d = self.I(
            StochasticOscillator, high_prices, low_prices, close_prices, self.n)

    def next(self):
        if crossover(self.percent_k, self.percent_d) and self.percent_k[-1] < self.oversold:
            if not self.position.is_long:
                self.position.close()
                self.buy()
        elif crossover(self.percent_d, self.percent_k) and self.percent_k[-1] > self.overbought:
            if not self.position.is_short:
                self.position.close()
                self.sell()