# strategies/stochastic_strategy.py

from backtesting import Strategy
from backtesting.lib import crossover
from indicators import StochasticOscillator

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

    print("Stochastic Strategy Parameters:")
    print(f"- Period (n): {n}")
    print(f"- Overbought Threshold: {overbought}")
    print(f"- Oversold Threshold: {oversold}")
    print("")

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