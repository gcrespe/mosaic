# strategies/macd_strategy.py

from backtesting import Strategy
from backtesting.lib import crossover
from indicators import MACD, SignalLine

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

    print("MACD Strategy Parameters:")
    print(f"- Fast EMA Period (n_fast): {n_fast}")
    print(f"- Slow EMA Period (n_slow): {n_slow}")
    print(f"- Signal Line Period (n_signal): {n_signal}")
    print("")

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