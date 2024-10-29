# strategies/moving_average_strategy.py

from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd

def SMA(values, n):
    """
    Simple Moving Average of `values`, `n` periods.
    """
    return pd.Series(values).rolling(n).mean().values


class MovingAverageStrategy(Strategy):
    short_window = 5
    long_window = 15

    def init(self):
        self.short_mavg = self.I(SMA, self.data.Close, self.short_window)
        self.long_mavg = self.I(SMA, self.data.Close, self.long_window)

    def next(self):
        if crossover(self.short_mavg, self.long_mavg):
            if not self.position.is_long:
                self.position.close()
                self.buy()
        elif crossover(self.long_mavg, self.short_mavg):
            if not self.position.is_short:
                self.position.close()
                self.sell()