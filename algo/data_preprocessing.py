# data_preprocessing.py

import requests
import pandas as pd
import os

# Load your API key from an environment variable
API_KEY = 'Q9RVxM49GO6ZeIpyZSr4CXBZpnnZyWOk'  # Ensure this environment variable is set
BASE_URL = 'https://api.polygon.io/v2/aggs/ticker/'

def get_historical_data(ticker, multiplier, timespan, start_date, end_date):
    """
    Fetches historical data from Polygon.io and returns it as a pandas DataFrame.
    Handles pagination to retrieve all available data.
    """
    url = f'{BASE_URL}{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}'
    params = {
        'apiKey': API_KEY
    }
    all_results = []

    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            json_response = response.json()
            results = json_response.get('results', [])
            if results:
                all_results.extend(results)
            else:
                print("No results in the response.")
                break

            next_url = json_response.get('next_url')
            if next_url:
                # Use the next_url for the next request
                url = next_url
                params = {
                    'apiKey': API_KEY
                }
            else:
                # No more pages to fetch
                break
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            break

    if all_results:
        df = pd.DataFrame(all_results)
        df['date'] = pd.to_datetime(df['t'], unit='ms')  # Convert timestamp to datetime
        return df
    else:
        print("No data returned for the given parameters.")
        return None

def preprocess_data(df):
    """
    Preprocesses the data for backtesting, renames columns, and sets the index.
    """
    df.rename(columns={
        'o': 'Open',
        'h': 'High',
        'l': 'Low',
        'c': 'Close',
        'v': 'Volume'
    }, inplace=True)
    df.set_index('date', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.sort_index(inplace=True)
    return df

# Example of how to gather and preprocess data
if __name__ == "__main__":
    ticker = 'AAPL'  # Example ticker symbol
    multiplier = 1
    timespan = 'hour'  # Fetch hourly data
    start_date = '2023-09-01'  # Adjust as needed
    end_date = '2023-10-01'    # Adjust as needed

    stock_data = get_historical_data(ticker, multiplier, timespan, start_date, end_date)
    if stock_data is not None:
        stock_data = preprocess_data(stock_data)
        stock_data.to_csv('preprocessed_stock_data.csv')  # Save the preprocessed data to a CSV file
        print("Data gathering and preprocessing completed successfully.")
    else:
        print("Data gathering failed.")