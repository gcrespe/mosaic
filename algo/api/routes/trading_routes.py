from flask import Blueprint, request, jsonify
from algo.config.alpaca_config import trading_client
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType, OrderClass

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