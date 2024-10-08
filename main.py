# main.py

import os
import pandas as pd

# Import data preprocessing functions
from data_preprocessing import get_historical_data, preprocess_data

# Import strategy classes
from strategies.rsi_strategy import RSIStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from strategies.stochastic_strategy import StochasticStrategy
from strategies.bollinger_bands_strategy import BollingerBandsStrategy
from strategies.macd_strategy import MACDStrategy

# Import backtesting utilities
from backtesting_utils import compare_backtests

def main():
    # Step 1: Data Gathering and Preprocessing
    ticker = 'AAPL'  # You can change this to any valid ticker symbol
    multiplier = 1
    timespan = 'hour'  # Fetch hourly data
    start_date = '2023-09-01'  # Adjust as needed
    end_date = '2023-10-01'    # Adjust as needed

    # Check if the data file already exists
    data_file = 'preprocessed_stock_data.csv'
    if not os.path.exists(data_file):
        print("Fetching and preprocessing data...")
        stock_data = get_historical_data(ticker, multiplier, timespan, start_date, end_date)
        if stock_data is not None:
            stock_data = preprocess_data(stock_data)
            stock_data.to_csv(data_file)
            print("Data gathering and preprocessing completed successfully.")
        else:
            print("Data gathering failed.")
            return  # Exit the script if data fetching fails
    else:
        print(f"Data file '{data_file}' already exists. Skipping data fetching.")

    # Step 2: Run Backtests and Compare Strategies
    # List of strategies to compare
    strategies = [
        (RSIStrategy, "RSI Strategy"),
        (MovingAverageStrategy, "Moving Average Strategy"),
        (MACDStrategy, "MACD Strategy"),
        (BollingerBandsStrategy, "Bollinger Bands Strategy"),
        (StochasticStrategy, "Stochastic Oscillator Strategy"),
    ]

    # Compare the strategies
    compare_backtests(strategies)

if __name__ == "__main__":
    main()