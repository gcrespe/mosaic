# strategies/bollinger_bands_strategy.py

from backtesting import Strategy
from backtesting.lib import crossover
from indicators import BollingerBands

class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands Strategy:
    - Buys when the price crosses above the Lower Band.
    - Sells when the price crosses below the Upper Band.
    """
    # Strategy parameters
    n = 20       # Period for moving average
    n_std = 2    # Number of standard deviations

    print("Bollinger Bands Strategy Parameters:")
    print(f"- Period (n): {n}")
    print(f"- Standard Deviations (n_std): {n_std}")
    print("")

    def init(self):
        close_prices = self.data.Close
        self.upper_band, self.middle_band, self.lower_band = self.I(
            BollingerBands, close_prices, self.n, self.n_std)

    def next(self):
        price = self.data.Close[-1]
        if crossover(price, self.lower_band):
            if not self.position.is_long:
                self.position.close()
                self.buy()
        elif crossover(self.upper_band, price):
            if not self.position.is_short:
                self.position.close()
                self.sell()
