from flask import Blueprint, request, jsonify
from algo.backtesting_utils import run_mean_reversion_backtest
from algo.backtesting_utils import run_enhanced_trend_backtest
from algo.backtesting_utils import run_random_trade_backtest
from algo.data_preprocessing import get_historical_data

backtest_bp = Blueprint('backtest', __name__)

@backtest_bp.route('/historical-data', methods=['GET'])
def get_data():
    """ Get historical market data for backtesting
    ---
    tags:
      - Backtesting
    operationId: getHistoricalData
    summary: Fetch historical market data
    description: Retrieves historical price data for a given symbol and timeframe
    parameters:
      - name: symbol
        in: query
        type: string
        required: true
        description: Stock symbol (e.g., AAPL, GOOGL)
      - name: timeframe
        in: query
        type: string
        required: false
        default: 1Hour
        enum: [1Min, 2Min, 3Min, 5Min, 1Hour, 1Day]
        description: Time interval for the data
      - name: start_date
        in: query
        type: string
        required: false
        description: Start date in YYYY-MM-DD format
      - name: end_date
        in: query
        type: string
        required: false
        description: End date in YYYY-MM-DD format
    responses:
      200:
        description: Historical market data
        schema:
          type: object
          properties:
            timestamp:
              type: string
            open:
              type: number
            high:
              type: number
            low:
              type: number
            close:
              type: number
            volume:
              type: integer
      400:
        description: Invalid parameters
      500:
        description: Server error
    """
    try:
        symbol = request.args.get('symbol')
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
            
        timeframe = request.args.get('timeframe', '1Hour')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        df = get_historical_data(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(df.to_dict(orient='records'))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@backtest_bp.route('/backtest/mean-reversion', methods=['POST'])
def mean_reversion_backtest():
    """ Run Mean Reversion strategy backtest
    ---
    tags:
      - Backtesting
    operationId: runMeanReversionBacktest
    summary: Backtest Mean Reversion strategy
    description: Run a backtest of the Mean Reversion strategy with multiple take-profit levels
    parameters:
      - name: config
        in: body
        required: true
        schema:
          type: object
          properties:
            symbol:
              type: string
              example: AAPL
            timeframe:
              type: string
              enum: [1Min, 2Min, 3Min, 5Min, 1Hour, 1Day]
              example: 1Hour
            start_date:
              type: string
              example: "2020-01-01"
            end_date:
              type: string
              example: "2023-12-31"
            strategy_params:
              type: object
              properties:
                ema_len:
                  type: integer
                  example: 200
                  description: EMA length for trend identification
                rsi_len:
                  type: integer
                  example: 14
                  description: RSI length for oversold/overbought conditions
                risk:
                  type: number
                  example: 0.01
                  description: Risk per trade (1% = 0.01)
                atr_bars:
                  type: integer
                  example: 14
                  description: ATR calculation period
                stop_mult:
                  type: number
                  example: 3.0
                  description: Stop loss multiplier (x ATR)
                tp_mult:
                  type: number
                  example: 5.0
                  description: Final take profit multiplier (x ATR)
                tp1_mult:
                  type: number
                  example: 0.75
                  description: First take profit multiplier (x ATR)
                tp2_mult:
                  type: number
                  example: 1.5
                  description: Second take profit multiplier (x ATR)
                tp_close:
                  type: number
                  example: 0.15
                  description: Percentage of position to close at TP1 and TP2 (15% = 0.15)
    responses:
      200:
        description: Backtest results
        schema:
          type: object
          properties:
            Start:
              type: string
            End:
              type: string
            Duration:
              type: string
            Exposure Time [%]:
              type: number
            Equity Final [$]:
              type: number
            Equity Peak [$]:
              type: number
            Return [%]:
              type: number
            Buy & Hold Return [%]:
              type: number
            Return (Ann.) [%]:
              type: number
            Volatility (Ann.) [%]:
              type: number
            Sharpe Ratio:
              type: number
            Sortino Ratio:
              type: number
            Calmar Ratio:
              type: number
            Max. Drawdown [%]:
              type: number
            Avg. Drawdown [%]:
              type: number
            Max. Drawdown Duration:
              type: string
            Avg. Drawdown Duration:
              type: string
            # Trades:
              type: integer
            Win Rate [%]:
              type: number
            Best Trade [%]:
              type: number
            Worst Trade [%]:
              type: number
            Avg. Trade [%]:
              type: number
            Max. Trade Duration:
              type: string
            Avg. Trade Duration:
              type: string
            Profit Factor:
              type: number
            Expectancy [%]:
              type: number
            SQN:
              type: number
      400:
        description: Invalid parameters
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data or 'symbol' not in data:
            return jsonify({'error': 'Symbol is required'}), 400
            
        # Get historical data
        df = get_historical_data(
            symbol=data['symbol'],
            timeframe=data.get('timeframe', '1Hour'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        
        # Verify DataFrame format
        required_columns = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': 'Data missing required columns'}), 400
        
        # Run backtest with optional strategy parameters
        stats = run_mean_reversion_backtest(
            df, 
            strategy_params=data.get('strategy_params')
        )
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@backtest_bp.route('/backtest/enhanced-trend', methods=['POST'])
def enhanced_trend_backtest():
    """ Run Enhanced Trend-Following & Mean Reversion strategy backtest
    ---
    tags:
      - Backtesting
    operationId: runEnhancedTrendBacktest
    summary: Backtest Enhanced Trend strategy
    description: Run a backtest of the Enhanced Trend-Following & Mean Reversion strategy
    parameters:
      - name: config
        in: body
        required: true
        schema:
          type: object
          properties:
            symbol:
              type: string
              example: AAPL
            timeframe:
              type: string
              enum: [1Min, 2Min, 3Min, 5Min, 1Hour, 1Day]
              example: 1Hour
            start_date:
              type: string
              example: "2020-01-01"
            end_date:
              type: string
              example: "2023-12-31"
            strategy_params:
              type: object
              properties:
                fast_ema_len:
                  type: integer
                  example: 50
                slow_ema_len:
                  type: integer
                  example: 200
                atr_bars:
                  type: integer
                  example: 14
                atr_mult:
                  type: number
                  example: 3.0
                rsi_len:
                  type: integer
                  example: 14
                rsi_upper:
                  type: integer
                  example: 70
                rsi_lower:
                  type: integer
                  example: 30
    responses:
      200:
        description: Backtest results
        schema:
          type: object
          properties:
            Start:
              type: string
            End:
              type: string
            Duration:
              type: string
            Exposure Time [%]:
              type: number
            Equity Final [$]:
              type: number
            Equity Peak [$]:
              type: number
            Return [%]:
              type: number
            Buy & Hold Return [%]:
              type: number
            Return (Ann.) [%]:
              type: number
            Volatility (Ann.) [%]:
              type: number
            Sharpe Ratio:
              type: number
            Sortino Ratio:
              type: number
            Calmar Ratio:
              type: number
            Max. Drawdown [%]:
              type: number
            Avg. Drawdown [%]:
              type: number
            Max. Drawdown Duration:
              type: string
            Avg. Drawdown Duration:
              type: string
            # Trades:
              type: integer
            Win Rate [%]:
              type: number
            Best Trade [%]:
              type: number
            Worst Trade [%]:
              type: number
            Avg. Trade [%]:
              type: number
            Max. Trade Duration:
              type: string
            Avg. Trade Duration:
              type: string
            Profit Factor:
              type: number
            Expectancy [%]:
              type: number
            SQN:
              type: number
      400:
        description: Invalid parameters
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data or 'symbol' not in data:
            return jsonify({'error': 'Symbol is required'}), 400
            
        # Get historical data
        df = get_historical_data(
            symbol=data['symbol'],
            timeframe=data.get('timeframe', '1Hour'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        
        # Verify DataFrame format
        required_columns = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': 'Data missing required columns'}), 400
        
        # Run backtest with optional strategy parameters
        stats = run_enhanced_trend_backtest(
            df, 
            strategy_params=data.get('strategy_params')
        )
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    

@backtest_bp.route('/backtest/random-trade', methods=['POST'])
def random_trade_backtest():
    """ Run Random Trade strategy backtest
    ---
    tags:
      - Backtesting
    operationId: runRandomTradeBacktest
    summary: Backtest Random Trade strategy
    description: Run a backtest of the Random Trade strategy with multiple re-entry attempts
    parameters:
      - name: config
        in: body
        required: true
        schema:
          type: object
          properties:
            symbol:
              type: string
              example: AAPL
              description: Trading symbol/ticker
            timeframe:
              type: string
              enum: [1Min, 2Min, 3Min, 5Min, 1Hour, 1Day]
              example: 1Hour
              description: Timeframe for the backtest
            start_date:
              type: string
              example: "2024-01-01"
              description: Start date for the backtest period
            end_date:
              type: string
              example: "2024-12-31"
              description: End date for the backtest period
            strategy_params:
              type: object
              properties:
                target_profit:
                  type: number
                  example: 0.05
                  description: Target profit percentage (5% = 0.05)
                stop_loss:
                  type: number
                  example: 0.05
                  description: Stop loss percentage (5% = 0.05)
                max_trades:
                  type: integer
                  example: 4
                  description: Maximum number of re-entry attempts
                risk:
                  type: number
                  example: 0.01
                  description: Risk per trade (1% = 0.01)
                min_distance:
                  type: number
                  example: 0.005
                  description: Minimum distance between price levels (0.5% = 0.005)
              required:
                - target_profit
                - stop_loss
                - max_trades
                - risk
                - min_distance
    responses:
      200:
        description: Backtest results
        schema:
          type: object
          properties:
            # ... (rest of the response schema remains the same)
    """
    try:
        data = request.get_json()
        if not data or 'symbol' not in data:
            return jsonify({'error': 'Symbol is required'}), 400
            
        # Validate strategy parameters
        strategy_params = data.get('strategy_params', {})
        required_params = ['target_profit', 'stop_loss', 'max_trades', 'risk', 'min_distance']
        if not all(param in strategy_params for param in required_params):
            return jsonify({'error': f'Missing required strategy parameters. Required: {required_params}'}), 400
            
        df = get_historical_data(
            symbol=data['symbol'],
            timeframe=data.get('timeframe', '1Hour'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        
        required_columns = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            return jsonify({'error': 'Data missing required columns'}), 400
        
        stats = run_random_trade_backtest(
            df, 
            strategy_params=strategy_params
        )
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500