from flask import Blueprint, request, jsonify
from algo.config.alpaca_config import trading_client, stock_client
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType, OrderClass
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
import pytz

trading_bp = Blueprint('trading', __name__)

@trading_bp.route('/order/tradingview-signal', methods=['POST'])
def alpaca_tradingview_webhook():
    """ Webhook used in TradingView to convert different strategies signals to orders
    ---
    tags:
      - Alpaca
    operationId: orderTradingviewSignalWithAlpaca
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
    
    # Your existing webhook logic here
    side = data.get('side')
    symbol = data.get('symbol')
    order_type = data.get('type', 'market')
    qty = data.get('qty')
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
        
        order_response = trading_client.submit_order(order_data=market_order_data)

        return jsonify({
            "symbol": order_response.symbol,
            "id": order_response.id,
            "type": order_response.type,
            "class": order_response.order_class,
            "filled_at": order_response.filled_at,
            "qty": order_response.qty,
            "filled_qty": order_response.filled_qty,
            "filled_avg_price": order_response.filled_avg_price,
            "status": order_response.status,
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    

@trading_bp.route('/stocks/available', methods=['GET'])
def get_available_stocks():
    """ Retrieve list of available stocks and their trading information from Alpaca
    ---
    tags:
      - Alpaca
    operationId: getAvailableStocksFromAlpaca
    parameters:
      - name: min_price
        in: query
        type: number
        format: float
        description: Minimum stock price filter
        required: false
      - name: max_price
        in: query
        type: number
        format: float
        description: Maximum stock price filter
        required: false
      - name: min_volume
        in: query
        type: integer
        format: int64
        description: Minimum 24h volume filter
        required: false
    responses:
      200:
        description: List of available stocks with their information
        schema:
          type: object
          properties:
            stocks:
              type: array
              items:
                type: object
                properties:
                  symbol:
                    type: string
                    example: 'AAPL'
                  name:
                    type: string
                    example: 'Apple Inc.'
                  price:
                    type: number
                    format: float
                    example: 189.84
                  change_24h:
                    type: number
                    format: float
                    example: 1.24
                  volume_24h:
                    type: integer
                    format: int64
                    example: 12450789
                  market_cap:
                    type: number
                    format: float
                    example: 2950000000000
                  status:
                    type: string
                    example: 'active'
                  tradable:
                    type: boolean
                    example: true
                  marginable:
                    type: boolean
                    example: true
                  shortable:
                    type: boolean
                    example: true
                  easy_to_borrow:
                    type: boolean
                    example: true
                  high_24h:
                    type: number
                    format: float
                    example: 190.25
                  low_24h:
                    type: number
                    format: float
                    example: 188.50
                  vwap_24h:
                    type: number
                    format: float
                    example: 189.45
                  trade_count_24h:
                    type: integer
                    format: int64
                    example: 50000
      500:
        description: Error processing request
        schema:
          type: object
          properties:
            message:
              type: string
              example: 'Error: Failed to fetch data'
    """
    try:
        print("\n=== Starting stock retrieval ===")
        
        # Get all assets and filter
        assets = [
            asset for asset in trading_client.get_all_assets()
            if asset.status == 'active' 
            and asset.tradable 
            and asset.asset_class == 'us_equity'
            and '/' not in asset.symbol 
            and asset.symbol.isalpha()
        ]  # Remove the [:20] limit
        
        print(f"Found {len(assets)} tradable assets")

        # Set up time range
        current_time = datetime.now(pytz.UTC)
        end = current_time - timedelta(days=1)  # Yesterday
        start = end - timedelta(days=1)  # Day before yesterday
        print(f"Requesting data from {start} to {end}")

        CHUNK_SIZE = 100  # Increased chunk size for efficiency
        stocks_data = []
        
        for i in range(0, len(assets), CHUNK_SIZE):
            chunk = assets[i:i + CHUNK_SIZE]
            chunk_symbols = [asset.symbol for asset in chunk]
            print(f"\nProcessing chunk {i//CHUNK_SIZE + 1}/{(len(assets) + CHUNK_SIZE - 1)//CHUNK_SIZE}")
            
            try:
                request_params = StockBarsRequest(
                    symbol_or_symbols=chunk_symbols,
                    timeframe=TimeFrame.Day,
                    start=start,
                    end=end,
                    limit=1,
                    feed='iex'
                )
                
                bars = stock_client.get_stock_bars(request_params)
                bars_dict = bars.data if hasattr(bars, 'data') else {}
                
                for asset in chunk:
                    try:
                        if asset.symbol not in bars_dict:
                            continue
                            
                        symbol_bars = bars_dict[asset.symbol]
                        if not symbol_bars:
                            continue
                            
                        latest_bar = symbol_bars[0]
                        
                        stocks_data.append({
                            "symbol": asset.symbol,
                            "name": asset.name,
                            "price": latest_bar.close,
                            "change_24h": ((latest_bar.close - latest_bar.open) / latest_bar.open * 100) 
                                if latest_bar.open > 0 else 0,
                            "volume_24h": latest_bar.volume,
                            "market_cap": asset.market_cap if hasattr(asset, 'market_cap') else None,
                            "status": asset.status,
                            "tradable": asset.tradable,
                            "marginable": asset.marginable,
                            "shortable": asset.shortable,
                            "easy_to_borrow": asset.easy_to_borrow,
                            "last_updated": latest_bar.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "high_24h": latest_bar.high,
                            "low_24h": latest_bar.low
                        })
                        
                    except Exception as e:
                        print(f"Error processing {asset.symbol}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error processing chunk: {str(e)}")
                continue

            print(f"Processed {len(stocks_data)} stocks so far")

        # Sort by market cap if available, then by volume
        stocks_data.sort(
            key=lambda x: (
                float('-inf') if x.get('market_cap') is None else float(x.get('market_cap')),
                float('-inf') if x.get('volume_24h') is None else float(x.get('volume_24h'))
            ), 
            reverse=True
        )

        print(f"\nRetrieved data for {len(stocks_data)} stocks")

        return jsonify({
            "stocks": stocks_data,
            "count": len(stocks_data),
            "last_updated": datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        }), 200
    
    except Exception as e:
        print(f"Main error: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500