from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from algo.config.alpaca_config import stock_client
import pandas as pd

def get_historical_data(symbol, timeframe='1Hour', start_date=None, end_date=None):
    """
    Fetch historical data and store it for backtesting
    """
    # Create TimeFrame instances correctly
    if timeframe == '1Min':
        tf = TimeFrame.Minute
    elif timeframe == '2Min':
        tf = TimeFrame(2, 'Min')
    elif timeframe == '3Min':
        tf = TimeFrame(3, 'Min')
    elif timeframe == '5Min':
        tf = TimeFrame(5, 'Min')
    elif timeframe == '1Hour':
        tf = TimeFrame.Hour
    elif timeframe == '1Day':
        tf = TimeFrame.Day
    else:
        raise ValueError(f"Invalid timeframe: {timeframe}")
    
    # Parse dates
    start = pd.Timestamp(start_date).tz_localize('UTC') if start_date else pd.Timestamp('2020-01-01').tz_localize('UTC')
    end = pd.Timestamp(end_date).tz_localize('UTC') if end_date else pd.Timestamp.now(tz='UTC')
    
    # Create request parameters
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=tf,
        start=start,
        end=end
    )
    
    try:
        # Get the data
        bars = stock_client.get_stock_bars(request_params)
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'Open': bar.open,
                'High': bar.high,
                'Low': bar.low,
                'Close': bar.close,
                'Volume': bar.volume,
                'Timestamp': bar.timestamp
            }
            for bar in bars.data[symbol]
        ])
        
        # Set the index to Timestamp
        df.set_index('Timestamp', inplace=True)
        
        # Sort index
        df.sort_index(inplace=True)
        
        return df
    
    except Exception as e:
        raise Exception(f"Error fetching data: {str(e)}")