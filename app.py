from flask import Flask, request, redirect, jsonify
from algo.backtesting_utils import run_backtest
import pandas as pd
import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType, OrderClass
from flasgger import Swagger
#backtesting
from algo.strategies.rsi_strategy import RSIStrategy
from algo.data_preprocessing import get_historical_data

# Alpaca API credentials (use paper trading endpoint)
ALPACA_API_KEY = 'PKTAVXT2KV81VZ9SMAH0'
ALPACA_SECRET_KEY = 'af3ZPiFWidZRx3Z66EcMt4mdQ2C724nahSStqleb'
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets/'

# Initialize Alpaca API client
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version='v2')

trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)

app = Flask(__name__)

swagger = Swagger(app, template={
    "info": {
        "title": "Mosaic Trading API",
        "description": "Trading api built with Flask and using Alpaca as broker",
        "version": "1.0.0"
    }
})

@app.route('/webhook/alpaca-tradingview', methods=['POST'])
def alpacaTradingviewWebhook():
    """ Webhook used in TradingView to convert different strategies signals to orders
    ---
    controller:
      - name: 'Alpaca'
    parameters:
      - name: order
        in: body
        type: TradingViewWebhookOrderRequest
        schema:
          $ref: '#/definitions/TradingViewWebhookOrderRequest'
        required: true
    definitions:
      TradingViewWebhookOrderRequest:
        type: object
        properties:
          side:
            type: string
            example: 'buy'
          symbol:
            type: string
            example: 'SPY'
          order_type:
            type: string
            example: 'market'
          time_in_force:
            type: string
            example: 'gtc'
          qty:
            type: integer
            example: 1
          order_class:
            type: string
            example: 'bracket'
      TradingViewWebhookOrderResponse:
        type: object
        properties:
          side:
            type: String
          ticker:
            type: String
          qty:
            type: int
          order_class:
            type: String
          price:
            type: float
    responses:
      200:
        description: JSON containing the operation values
        schema:
          $ref: '#/definitions/TradingViewWebhookOrderResponse'
        examples:
          order: {'side': 'buy', 'ticket':'SPY', 'qty': 1, 'order_class': 'bracket', 'price': 569.78}
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data received'}), 400
    
    app.logger.info('Order data: %s', request.get_json())

    #TradingView
    side = data.get('side')  # "buy" or "sell"
    symbol = data.get('symbol')  # e.g., "SPY"
    order_type = data.get('type', 'market')  # e.g., "market"
    qty = data.get('qty')  # number of shares to trade
    time_in_force = data.get('time_in_force', 'gtc')
    order_class = data.get('order_class', 'simple')

    try:
        market_order_data = MarketOrderRequest(
                              symbol=symbol,
                              qty=float(qty),
                              side=OrderSide(side),
                              time_in_force=TimeInForce(time_in_force),
                              type=OrderType(order_type),
                              order_class=OrderClass(order_class),
                              
                            )
        
        order_response = trading_client.submit_order(  
            order_data=market_order_data
        )

        json_response = jsonify({
            "symbol": order_response.symbol,
            "id": order_response.id,
            "type": order_response.type,
            "class": order_response.order_class,
            "filled_at": order_response.filled_at,
            "qty": order_response.qty,
            "filled_qty": order_response.filled_qty,
            "filled_avg_price": order_response.filled_avg_price,
            "status": order_response.status,

        })

        app.logger.info("Order response %s", json_response)

        return json_response, 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    

@app.get("/")
def apidocs():
    return redirect("/apidocs")

@app.route('/backtesting/rsi')
def rsi_backtest():

    ticker = 'AAPL'  # You can change this to any valid ticker symbol
    multiplier = 1
    timespan = 'hour'  # Fetch hourly data
    start_date = '2020-09-01'  # Adjust as needed

    get_historical_data(ticker, multiplier, timespan, start_date)
    
    stats = run_backtest(RSIStrategy, "RSI Strategy")
    return pd.Series(stats).to_json()

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return "404"

# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return "500"