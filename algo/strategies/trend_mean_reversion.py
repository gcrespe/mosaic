from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

class EnhancedTrendStrategy(Strategy):
    # Define parameters with the same defaults as the TradingView strategy
    fast_ema_len = 50
    slow_ema_len = 200
    atr_bars = 14
    atr_mult = 3.0
    rsi_len = 14
    rsi_upper = 70
    rsi_lower = 30
    risk_pct = 0.01  # 1% risk per trade

    def init(self):
        # Calculate EMAs using pandas
        close = pd.Series(self.data.Close)
        self.fast_ema = self.I(lambda x: x.ewm(span=self.fast_ema_len, adjust=False).mean(), close)
        self.slow_ema = self.I(lambda x: x.ewm(span=self.slow_ema_len, adjust=False).mean(), close)
        
        # Calculate ATR
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        close = pd.Series(self.data.Close)
        
        def calculate_atr(high, low, close, length):
            tr = pd.DataFrame()
            tr['h-l'] = high - low
            tr['h-pc'] = abs(high - close.shift(1))
            tr['l-pc'] = abs(low - close.shift(1))
            tr['tr'] = tr.max(axis=1)
            return tr['tr'].rolling(length).mean()
        
        self.atr = self.I(lambda: calculate_atr(high, low, close, self.atr_bars))
        
        # Calculate RSI
        def calculate_rsi(close, length):
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        self.rsi = self.I(lambda: calculate_rsi(close, self.rsi_len))

    def next(self):
        # Skip if not enough data or if indicators are not yet calculated
        if (len(self.data) < self.slow_ema_len or 
            np.isnan(self.fast_ema[-1]) or 
            np.isnan(self.slow_ema[-1]) or 
            np.isnan(self.atr[-1]) or 
            np.isnan(self.rsi[-1])):
            return
        
        # Calculate position size based on ATR and risk percentage
        price = self.data.Close[-1]
        stop_distance = self.atr[-1] * self.atr_mult
        
        # Ensure stop distance is valid
        if stop_distance <= 0:
            return
            
        # Calculate position size in units
        risk_amount = self.equity * self.risk_pct
        size = max(1, int(risk_amount / (price * stop_distance)))  # Minimum 1 unit
        
        # Check for bullish crossover with RSI filter
        if (crossover(self.fast_ema, self.slow_ema) and 
            self.rsi[-1] < self.rsi_upper and 
            not self.position):
            
            # Calculate stop loss level
            stop_price = price - stop_distance
            
            # Enter long position with stop loss
            self.buy(size=size, sl=stop_price)
        
        # Check for bearish crossover with RSI filter
        elif (crossover(self.slow_ema, self.fast_ema) and 
              self.rsi[-1] > self.rsi_lower and 
              not self.position):
            
            # Calculate stop loss level
            stop_price = price + stop_distance
            
            # Enter short position with stop loss
            self.sell(size=size, sl=stop_price)