# indicators.py

import pandas as pd
import numpy as np

def SMA(values, n):
    """
    Simple Moving Average of `values`, `n` periods.
    """
    return pd.Series(values).rolling(n).mean().values

def RSI(array, period):
    """
    Calculate the Relative Strength Index (RSI).
    """
    delta = np.diff(array)
    gain = np.maximum(delta, 0)
    loss = -np.minimum(delta, 0)
    gain = np.insert(gain, 0, 0)
    loss = np.insert(loss, 0, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.values

def StochasticOscillator(high_prices, low_prices, close_prices, n=14):
    """
    Calculate the Stochastic Oscillator (%K and %D lines).
    """
    lowest_low = pd.Series(low_prices).rolling(window=n).min()
    highest_high = pd.Series(high_prices).rolling(window=n).max()
    percent_k = 100 * (close_prices - lowest_low) / (highest_high - lowest_low)
    percent_d = percent_k.rolling(window=3).mean()
    return percent_k.values, percent_d.values

def BollingerBands(close_prices, n=20, n_std=2):
    """
    Calculate Bollinger Bands.
    """
    middle_band = pd.Series(close_prices).rolling(window=n).mean()
    std_dev = pd.Series(close_prices).rolling(window=n).std()
    upper_band = middle_band + n_std * std_dev
    lower_band = middle_band - n_std * std_dev
    return upper_band.values, middle_band.values, lower_band.values

def MACD(close_prices, n_fast=12, n_slow=26):
    """
    Calculate the MACD line.
    """
    ema_fast = pd.Series(close_prices).ewm(span=n_fast, adjust=False).mean()
    ema_slow = pd.Series(close_prices).ewm(span=n_slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    return macd_line.values

def SignalLine(macd_line, n_signal=9):
    """
    Calculate the Signal line.
    """
    signal_line = pd.Series(macd_line).ewm(span=n_signal, adjust=False).mean()
    return signal_line.values