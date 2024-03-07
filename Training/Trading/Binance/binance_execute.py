import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import talib
import numpy as np


class ExecuteOrder:
    def __init__(self, api_key, api_secret,leverage,accountSize,prediction, testnet):
        self.client = Client(api_key=api_key, api_secret=api_secret, testnet=testnet)
        self.accountBalance = 0
        self.leverage = leverage
        self.accountSize = accountSize
        self.prediction = prediction


    def executeOrder(self, symbol,prediction):
            """
                Places a market order on the Binance Futures market with specified parameters.
                
                Parameters:
                - symbol (str): The symbol to trade (e.g., 'BTCUSDT').
                - side (str): The side of the order ('BUY' or 'SELL').
                - leverage (int): The leverage to use for the order.
                - percentage (float): The percentage of the account's quote asset to use for this order.
                
                Returns:
                - dict: The response from the Binance API with the order details. Returns None if the order placement fails.
            """
            try:
                # Set leverage
                self.client.futures_change_leverage(symbol=symbol, leverage=self.leverage)
                
                # Calculate the quantity based on the desired percentage of available balance
                quantity = calculate_quantity(symbol, self.accountSize)

                timestamp = int(time.time() * 1000)    

                # Place order
                order = self.client.futures_create_order(symbol=symbol, side= self.prediction, type=self.client.ORDER_TYPE_MARKET, quantity=quantity, timestamp=timestamp)  # Adjust quantity as needed
                return order
            except BinanceAPIException as e:
                # Connect to a message provider and send a message about the error.
                # send_telegram_message(f"Error placing {side} order: {e.message}")
                return None  
    
    def exitPosition(self, symbol):
        """
            Attempts to close an existing order for a given symbol and side.
            
            Parameters:
            - symbol (str): The symbol for which to close the order (e.g., 'BTCUSDT').
            - side (dict): The order details, particularly containing the 'clientOrderId'.
            
            Returns:
            - bool: True if successful, False otherwise.
        """
        """Close existing order based on the side (BUY/SELL)"""

        if 'clientOrderId' not in side:
                return False

        try:
            self.client.FUTURES_API_VERSION = 'v1'
            closingSide = None
            #open_orders = client.futures_get_all_orders(symbol=symbol)
            order = side       
            #for order in open_orders:
            print(f"Processing Client Order ID: {order['clientOrderId']} at opened position: {order['side']}")
            if order['status'] == self.client.ORDER_STATUS_FILLED:
                print(f"Closing {order['clientOrderId']} order in opposite side...")       
                timestamp = int(time.time() * 1000)
                if order['side'] == self.client.SIDE_BUY:
                    closingSide = self.client.SIDE_SELL
                else:
                    closingSide = self.client.SIDE_BUY
                self.client.futures_create_order(symbol=symbol, side=closingSide, type=self.client.ORDER_TYPE_MARKET, quantity=order['origQty'], timestamp=timestamp)
                send_telegram_message(f"Closed {side} order.")

        except BinanceAPIException as e:
            send_telegram_message(f"Error closing {side} order: {e.message}")