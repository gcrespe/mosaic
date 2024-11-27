import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient

# Alpaca API credentials (use paper trading endpoint)
ALPACA_API_KEY = 'PKUCVU4D283LXUBAGO3J'
ALPACA_SECRET_KEY = 'efZtmuxXA0EdhYZC4gXwQnrxEN4nPDPNkpUPDaJH'
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets/'

# Initialize Alpaca API clients
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version='v2')
trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
stock_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)