from backtesting import Strategy
import pandas as pd

class MeanReversionStrategy(Strategy):
    # Define parameters
    ema_len = 200
    rsi_len = 14
    risk = 0.01  # 1%
    atr_bars = 14
    stop_mult = 3.0
    tp_mult = 5.0
    tp1_mult = 0.75
    tp2_mult = 1.5
    tp_close = 0.15  # 15%

    def init(self):
        # Calculate EMA
        close = pd.Series(self.data.Close)
        self.ema = self.I(lambda x: x.ewm(span=self.ema_len, adjust=False).mean(), close)
        
        # Calculate RSI
        def calculate_rsi(close, length):
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        self.rsi = self.I(lambda: calculate_rsi(close, self.rsi_len))
        
        # Calculate ATR
        high = pd.Series(self.data.High)
        low = pd.Series(self.data.Low)
        
        def calculate_atr(high, low, close, length):
            tr = pd.DataFrame()
            tr['h-l'] = high - low
            tr['h-pc'] = abs(high - close.shift(1))
            tr['l-pc'] = abs(low - close.shift(1))
            tr['tr'] = tr.max(axis=1)
            return tr['tr'].rolling(length).mean()
        
        self.atr = self.I(lambda: calculate_atr(high, low, close, self.atr_bars))

    def next(self):
        # Skip if not enough data
        if len(self.data) < self.ema_len:
            return
            
        price = self.data.Close[-1]
        prev_price = self.data.Close[-2]
        open_price = self.data.Open[-1]
        prev_open = self.data.Open[-2]
        
        # Engulfing patterns
        bullish_eng = (open_price <= prev_price and 
                      price > prev_open and 
                      prev_open > prev_price)
        
        bearish_eng = (open_price >= prev_price and 
                      price < prev_open and 
                      prev_open < prev_price)
        
        # Entry conditions
        go_long = (bullish_eng and 
                  price < self.ema[-1] and 
                  self.rsi[-2] < 30)
        
        go_short = (bearish_eng and 
                   price > self.ema[-1] and 
                   self.rsi[-2] > 70)
        
        # Calculate ATR value
        atr = self.atr[-1]
        
        # Calculate position size based on risk
        risk_amount = self.equity * self.risk
        
        if go_long and not self.position:
            # Calculate stop and targets for long
            stop_level = price - atr * self.stop_mult  # Closer stop
            tp_level = price + atr * self.tp_mult      # Furthest target
            tp1_level = price + atr * self.tp1_mult    # Closest target
            tp2_level = price + atr * self.tp2_mult    # Middle target
            
            # Calculate stop distance and size
            stop_distance = abs(price - stop_level)
            if stop_distance <= 0:
                return
                
            size = max(1, int(risk_amount / stop_distance))
            
            # Adjust limit price to be slightly above the current price
            limit_price = price + 0.01  # Set limit price slightly above the current price
            
            # Ensure limit price is below TP and above SL
            if limit_price >= tp_level or limit_price <= stop_level:
                limit_price = stop_level + 0.01  # Adjust limit price to be just above SL
            
            # Split position for different targets
            main_size = int(size * (1 - self.tp_close))
            tp_size = int(size * self.tp_close / 2)
            
            # Enter long positions
            if main_size > 0:
                self.buy(size=main_size, sl=stop_level, tp=tp_level, limit=limit_price)
            if tp_size > 0:
                self.buy(size=tp_size, sl=stop_level, tp=tp1_level, limit=limit_price)
                self.buy(size=tp_size, sl=stop_level, tp=tp2_level, limit=limit_price)
            
        elif go_short and not self.position:
            # Calculate stop and targets for short
            stop_level = price + atr * self.stop_mult  # Closer stop
            tp_level = price - atr * self.tp_mult      # Furthest target
            tp1_level = price - atr * self.tp1_mult    # Closest target
            tp2_level = price - atr * self.tp2_mult    # Middle target
            
            # Calculate stop distance and size
            stop_distance = abs(price - stop_level)
            if stop_distance <= 0:
                return
                
            size = max(1, int(risk_amount / stop_distance))
            
            # Adjust limit price to be slightly below the current price
            limit_price = price - 0.01  # Set limit price slightly below the current price
            
            # Ensure limit price is above TP and below SL
            if limit_price <= tp_level or limit_price >= stop_level:
                limit_price = stop_level - 0.01  # Adjust limit price to be just below SL
            
            # Split position for different targets
            main_size = int(size * (1 - self.tp_close))
            tp_size = int(size * self.tp_close / 2)
            
            # Enter short positions
            if main_size > 0:
                self.sell(size=main_size, sl=stop_level, tp=tp_level, limit=limit_price)
            if tp_size > 0:
                self.sell(size=tp_size, sl=stop_level, tp=tp2_level, limit=limit_price)
                self.sell(size=tp_size, sl=stop_level, tp=tp1_level, limit=limit_price)
        
        # Additional exit conditions
        if self.position.is_long:
            if price > self.ema[-1]:
                self.position.close()
            
        elif self.position.is_short:
            if price < self.ema[-1]:
                self.position.close()