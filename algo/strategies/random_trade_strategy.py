from backtesting import Strategy
import random
import pandas as pd

class RandomTradeStrategy(Strategy):
    # Define parameters - adjusted for more frequent trading
    target_profit = 0.02    # 2% - smaller target for quicker trades
    stop_loss = 0.015      # 1.5% - tighter stop loss
    max_trades = 4         # Keep max trades the same
    risk = 0.01           # 1% risk per trade
    min_distance = 0.002  # 0.2% - smaller minimum distance for more opportunities

    def init(self):
        self.trade_count = 0
        self.entry_price = 0
        self.current_direction = None

    def calculate_order_levels(self, price: float, direction: str) -> tuple:
        """Calculate order levels with simplified logic"""
        if direction == 'long':
            stop_level = price * (1 - self.stop_loss)
            tp_level = price * (1 + self.target_profit)
            limit_price = price * (1 + self.min_distance)
        else:  # short
            stop_level = price * (1 + self.stop_loss)
            tp_level = price * (1 - self.target_profit)
            limit_price = price * (1 - self.min_distance)

        return stop_level, tp_level, limit_price

    def next(self):
        price = self.data.Close[-1]
        risk_amount = self.equity * self.risk
        
        # If we're not in a position, enter randomly
        if not self.position:
            self.trade_count = 0
            self.current_direction = 'long' if random.choice([True, False]) else 'short'
            
            try:
                stop_level, tp_level, limit_price = self.calculate_order_levels(
                    price, self.current_direction)
                
                # Calculate position size
                stop_distance = abs(price - stop_level)
                if stop_distance <= self.min_distance * price:
                    return
                    
                size = max(1, int(risk_amount / stop_distance))
                
                # Enter position
                if self.current_direction == 'long':
                    self.buy(size=size, sl=stop_level, tp=tp_level, limit=limit_price)
                else:
                    self.sell(size=size, sl=stop_level, tp=tp_level, limit=limit_price)
                
                self.entry_price = price
                
            except AssertionError:
                return
        
        # If we're in a position and hit stop loss
        elif self.position and self.trade_count < self.max_trades:
            price_change = (price - self.entry_price) / self.entry_price
            if (self.current_direction == 'long' and price_change <= -self.stop_loss) or \
               (self.current_direction == 'short' and price_change >= self.stop_loss):
                
                self.trade_count += 1
                
                try:
                    stop_level, tp_level, limit_price = self.calculate_order_levels(
                        price, self.current_direction)
                    
                    stop_distance = abs(price - stop_level)
                    if stop_distance <= self.min_distance * price:
                        return
                        
                    size = max(1, int(risk_amount / stop_distance))
                    
                    if self.current_direction == 'long':
                        self.buy(size=size, sl=stop_level, tp=tp_level, limit=limit_price)
                    else:
                        self.sell(size=size, sl=stop_level, tp=tp_level, limit=limit_price)
                    
                    self.entry_price = price
                    
                except AssertionError:
                    return