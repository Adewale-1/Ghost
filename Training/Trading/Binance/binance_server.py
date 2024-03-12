import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import talib
import numpy as np


class ConnectToBinance:

    def __init__(self, api_key, api_secret,leverage,accountSize,prediction, testnet):
        self.client = Client(api_key=api_key, api_secret=api_secret, testnet=testnet)
        self.accountBalance
        self.leverage = leverage
        self.accountSize = accountSize
        self.prediction = prediction
        
    def getHistoricalData(self, symbol, interval):
        """
            Fetches historical price data for a specified symbol and interval using the Binance Futures API.
            
            Parameters:
            - symbol (str): The symbol for which to get historical data (e.g., 'BTCUSDT').
            - interval (str): The interval for the klines/candlesticks data (e.g., '1d' for one day).
            
            Returns:
            - data : The OHLCV data for the specified symbol and interval.
        """
        data = self.client.futures_klines(symbol=symbol, interval=interval)
        
        return data
    
    def getLatestPrice(self, symbol):
        """
            Fetches the latest price for a specified symbol using the Binance Futures API.
            
            Parameters:
            - symbol (str): The symbol for which to get the latest price (e.g., 'BTCUSDT').
            
            Returns:
            - price : The latest price for the specified symbol.
        """
        price = self.client.futures_ticker(symbol=symbol)
        
        return float(price['lastPrice'])
    
    def getAccountBalance(self, asset):
        """
            Retrieves the wallet balance for a specific asset using the Binance Futures API.
            
            Parameters:
            - asset (str): The asset for which to get the wallet balance (e.g., 'USDT').
            
            Returns:
            - float: The wallet balance of the specified asset. Returns 0.0 if the asset is not found.
        """
        account_info = self.client.futures_account()
        for asset_balance in account_info['assets']:
            if asset_balance['asset'] == asset:
                return float(asset_balance['walletBalance'])
        return 0.0

    