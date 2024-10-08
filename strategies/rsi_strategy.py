# strategies/rsi_strategy.py

from backtesting import Strategy
from backtesting.lib import crossover
from indicators import RSI

class RSIStrategy(Strategy):
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30

    print(f"RSI Strategy Parameters:")
    print(f"- RSI Period: {rsi_period}")
    print(f"- RSI Overbought: {rsi_overbought}")
    print(f"- RSI Oversold: {rsi_oversold}")
    print("")

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