# backtesting_utils.py

import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any
from backtesting import Backtest
from algo.strategies.trend_mean_reversion import EnhancedTrendStrategy
import os

def run_mean_reversion_backtest(data: pd.DataFrame, 
                              strategy_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run backtest for the Mean Reversion Strategy
    """
    from algo.strategies.mean_reversion_strategy import MeanReversionStrategy
    
    # Create backtest instance
    bt = Backtest(data, 
                  MeanReversionStrategy, 
                  cash=100000,
                  commission=.002,
                  exclusive_orders=True)
    
    # Run backtest with optional parameters
    stats = bt.run(**strategy_params)
    
    # Return statistics with rounded values
    return {
        'Start': str(stats['Start']),
        'End': str(stats['End']),
        'Duration': str(stats['Duration']),
        'Exposure Time [%]': round(stats['Exposure Time [%]'], 3),
        'Equity Final [$]': round(stats['Equity Final [$]'], 3),
        'Equity Peak [$]': round(stats['Equity Peak [$]'], 3),
        'Return [%]': round(stats['Return [%]'], 3),
        'Buy & Hold Return [%]': round(stats['Buy & Hold Return [%]'], 3),
        'Return (Ann.) [%]': round(stats['Return (Ann.) [%]'], 3),
        'Volatility (Ann.) [%]': round(stats['Volatility (Ann.) [%]'], 3),
        'Sharpe Ratio': round(stats['Sharpe Ratio'], 3),
        'Sortino Ratio': round(stats['Sortino Ratio'], 3),
        'Calmar Ratio': round(stats['Calmar Ratio'], 3),
        'Max. Drawdown [%]': round(stats['Max. Drawdown [%]'], 3),
        'Avg. Drawdown [%]': round(stats['Avg. Drawdown [%]'], 3),
        'Max. Drawdown Duration': str(stats['Max. Drawdown Duration']),
        'Avg. Drawdown Duration': str(stats['Avg. Drawdown Duration']),
        '# Trades': stats['# Trades'],
        'Win Rate [%]': round(stats['Win Rate [%]'], 3),
        'Best Trade [%]': round(stats['Best Trade [%]'], 3),
        'Worst Trade [%]': round(stats['Worst Trade [%]'], 3),
        'Avg. Trade [%]': round(stats['Avg. Trade [%]'], 3),
        'Max. Trade Duration': str(stats['Max. Trade Duration']),
        'Avg. Trade Duration': str(stats['Avg. Trade Duration']),
        'Profit Factor': round(stats['Profit Factor'], 3),
        'Expectancy [%]': round(stats['Expectancy [%]'], 3),
        'SQN': round(stats['SQN'], 3)
    }

def run_enhanced_trend_backtest(data: pd.DataFrame, 
                              strategy_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run backtest for the Enhanced Trend Strategy
    
    Args:
        data: DataFrame with OHLCV data
        strategy_params: Dictionary of strategy parameters to override defaults
    
    Returns:
        Dictionary containing backtest statistics
    """
    
    
    # Create backtest instance with proper initial settings
    bt = Backtest(data, 
                  EnhancedTrendStrategy, 
                  cash=100000,  # Starting with $100k
                  commission=.002,  # 0.2% commission per trade
                  exclusive_orders=True,
                  trade_on_close=False)
    
    # Run backtest with optional parameters
    stats = bt.run(**strategy_params)
    
    # Return all statistics with rounded values
    return {
        'Start': str(stats['Start']),
        'End': str(stats['End']),
        'Duration': str(stats['Duration']),
        'Exposure Time [%]': round(stats['Exposure Time [%]'], 3),
        'Equity Final [$]': round(stats['Equity Final [$]'], 3),
        'Equity Peak [$]': round(stats['Equity Peak [$]'], 3),
        'Return [%]': round(stats['Return [%]'], 3),
        'Buy & Hold Return [%]': round(stats['Buy & Hold Return [%]'], 3),
        'Return (Ann.) [%]': round(stats['Return (Ann.) [%]'], 3),
        'Volatility (Ann.) [%]': round(stats['Volatility (Ann.) [%]'], 3),
        'Sharpe Ratio': round(stats['Sharpe Ratio'], 3),
        'Sortino Ratio': round(stats['Sortino Ratio'], 3),
        'Calmar Ratio': round(stats['Calmar Ratio'], 3),
        'Max. Drawdown [%]': round(stats['Max. Drawdown [%]'], 3),
        'Avg. Drawdown [%]': round(stats['Avg. Drawdown [%]'], 3),
        'Max. Drawdown Duration': str(stats['Max. Drawdown Duration']),
        'Avg. Drawdown Duration': str(stats['Avg. Drawdown Duration']),
        '# Trades': stats['# Trades'],
        'Win Rate [%]': round(stats['Win Rate [%]'], 3),
        'Best Trade [%]': round(stats['Best Trade [%]'], 3),
        'Worst Trade [%]': round(stats['Worst Trade [%]'], 3),
        'Avg. Trade [%]': round(stats['Avg. Trade [%]'], 3),
        'Max. Trade Duration': str(stats['Max. Trade Duration']),
        'Avg. Trade Duration': str(stats['Avg. Trade Duration']),
        'Profit Factor': round(stats['Profit Factor'], 3),
        'Expectancy [%]': round(stats['Expectancy [%]'], 3),
        'SQN': round(stats['SQN'], 3),
        '_strategy': str(stats['_strategy'])
    }

def run_random_trade_backtest(data: pd.DataFrame, 
                            strategy_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run backtest for the Random Trade Strategy
    
    Args:
        data: DataFrame with OHLCV data
        strategy_params: Dictionary of strategy parameters to override defaults
        
    Returns:
        Dictionary containing backtest statistics
    """
    from algo.strategies.random_trade_strategy import RandomTradeStrategy
    
    # Create backtest instance
    bt = Backtest(data, 
                  RandomTradeStrategy, 
                  cash=100000,
                  commission=.002,
                  exclusive_orders=True)
    
    # Run backtest with optional parameters
    stats = bt.run(**strategy_params)
    
    # Return statistics with rounded values
    return {
        'Start': str(stats['Start']),
        'End': str(stats['End']),
        'Duration': str(stats['Duration']),
        'Exposure Time [%]': round(stats['Exposure Time [%]'], 3),
        'Equity Final [$]': round(stats['Equity Final [$]'], 3),
        'Equity Peak [$]': round(stats['Equity Peak [$]'], 3),
        'Return [%]': round(stats['Return [%]'], 3),
        'Buy & Hold Return [%]': round(stats['Buy & Hold Return [%]'], 3),
        'Return (Ann.) [%]': round(stats['Return (Ann.) [%]'], 3),
        'Volatility (Ann.) [%]': round(stats['Volatility (Ann.) [%]'], 3),
        'Sharpe Ratio': round(stats['Sharpe Ratio'], 3),
        'Sortino Ratio': round(stats['Sortino Ratio'], 3),
        'Calmar Ratio': round(stats['Calmar Ratio'], 3),
        'Max. Drawdown [%]': round(stats['Max. Drawdown [%]'], 3),
        'Avg. Drawdown [%]': round(stats['Avg. Drawdown [%]'], 3),
        'Max. Drawdown Duration': str(stats['Max. Drawdown Duration']),
        'Avg. Drawdown Duration': str(stats['Avg. Drawdown Duration']),
        '# Trades': stats['# Trades'],
        'Win Rate [%]': round(stats['Win Rate [%]'], 3),
        'Best Trade [%]': round(stats['Best Trade [%]'], 3),
        'Worst Trade [%]': round(stats['Worst Trade [%]'], 3),
        'Avg. Trade [%]': round(stats['Avg. Trade [%]'], 3),
        'Max. Trade Duration': str(stats['Max. Trade Duration']),
        'Avg. Trade Duration': str(stats['Avg. Trade Duration']),
        'Profit Factor': round(stats['Profit Factor'], 3),
        'Expectancy [%]': round(stats['Expectancy [%]'], 3),
        'SQN': round(stats['SQN'], 3)
    }

def run_backtest(strategy_class, strategy_name):
    print("Working Directory: {}".format(os.getcwd()))

    try:
        print(f"\nRunning Backtest for {strategy_name}...\n")
        stock_data = pd.read_csv('preprocessed_stock_data.csv', index_col='date', parse_dates=True)
        bt = Backtest(stock_data, strategy_class, cash=10000, commission=.002)
        stats = bt.run()
        # if display_plot:
        #     output_file(f"{strategy_name}_backtest.html")
        #     bt.plot(filename=f"{strategy_name}_backtest.html", open_browser=False)
        #     print(f"Plot saved to {strategy_name}_backtest.html")

        print(f"Statistics for {strategy_name}:\n")
        print(stats)
        print("-" * 80)

        return stats
    except Exception as e:
        print(f"An error occurred during backtesting of {strategy_name}: {e}")
        return None

def compare_backtests(strategies, data_file='preprocessed_stock_data.csv'):
    stats_list = []
    equity_curves = pd.DataFrame()

    for strategy_class, strategy_name in strategies:
        stats = run_backtest(strategy_class, strategy_name, data_file, False)
        if stats is not None:
            stats['_strategy'] = strategy_name
            stats_list.append(stats)

            equity_curve = stats['_equity_curve']['Equity']
            equity_curve.reset_index(drop=True, inplace=True)
            equity_curves[strategy_name] = equity_curve
        else:
            print(f"Skipping {strategy_name} due to errors.")

    if stats_list:
        stats_df = pd.DataFrame(stats_list)
        stats_df.set_index('_strategy', inplace=True)
        stats_df = stats_df[['Return [%]', 'Sharpe Ratio', 'Max. Drawdown [%]', '# Trades', 'Win Rate [%]', 'Profit Factor']]

        print("\nComparison of Strategies:\n")
        print(stats_df)

        # Plot equity curves
        plt.figure(figsize=(12, 6))
        for column in equity_curves.columns:
            print(f"Plotting equity curve for {column}")
            plt.plot(equity_curves[column], label=column)
        plt.title('Equity Curves Comparison')
        plt.xlabel('Time')
        plt.ylabel('Equity')
        plt.legend()
        plt.grid(True)
        plt.savefig('equity_curves_comparison.png')
        print("Equity curves comparison plot saved as 'equity_curves_comparison.png'")
    else:
        print("No valid backtest results to compare.")
