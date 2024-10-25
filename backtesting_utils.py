# backtesting_utils.py

import pandas as pd
import matplotlib.pyplot as plt
from bokeh.plotting import output_file
from backtesting import Backtest

def run_backtest(strategy_class, strategy_name, data_file='preprocessed_stock_data.csv', display_plot=True):
    

    try:
        print(f"\nRunning Backtest for {strategy_name}...\n")
        stock_data = pd.read_csv(data_file, index_col='date', parse_dates=True)
        bt = Backtest(stock_data, strategy_class, cash=10000, commission=.002)
        stats = bt.run()
        if display_plot:
            output_file(f"{strategy_name}_backtest.html")
            bt.plot(filename=f"{strategy_name}_backtest.html", open_browser=False)
            print(f"Plot saved to {strategy_name}_backtest.html")

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
