import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time
import talib
import numpy as np

# Constants
FEE = 0.001  # 0.1%

# Binance API keys Test Net
ENABLE_TESTNET = True # False for Main Net
API_KEY = ''
API_SECRET = ''

# Telegram settings
ENABLE_TELEGRAM = False
TELEGRAM_API = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'

client = Client(api_key=API_KEY, api_secret=API_SECRET, testnet=ENABLE_TESTNET)

def send_telegram_message(message):
    if ENABLE_TELEGRAM:
        url = f"https://api.telegram.org/bot{TELEGRAM_API}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
        requests.get(url)
    
    # console output
    print(f"{message}")

def get_historical_data(symbol, interval):
    """
    Fetches historical price data for a specified symbol and interval using the Binance Futures API.
    
    Parameters:
    - symbol (str): The symbol for which to get historical data (e.g., 'BTCUSDT').
    - interval (str): The interval for the klines/candlesticks data (e.g., '1d' for one day).
    
    Returns:
    - list of float: A list of closing prices for each kline/candlestick.
    """
    klines = client.futures_klines(symbol=symbol, interval=interval)
    # this gets the close price for each kline
    close_prices = [float(entry[4]) for entry in klines]
    return close_prices

def get_latest_price(symbol):
    """
    Retrieves the latest price for a given symbol using the Binance Futures API.
    
    Parameters:
    - symbol (str): The symbol for which to get the latest price (e.g., 'BTCUSDT').
    
    Returns:
    - float: The latest price of the symbol.
    """
    ticker = client.futures_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

def adjust_precision(value, precision):
    """
    Adjusts the precision of a given numeric value to the specified number of decimal places.
    
    Parameters:
    - value (float): The numeric value to adjust.
    - precision (int): The number of decimal places to round to.
    
    Returns:
    - str: The value formatted as a string with the specified precision.
    """
    format_string = "{:0.0" + str(precision) + "f}"
    return format_string.format(value)

def get_balance(asset):
    """
    Retrieves the wallet balance for a specific asset using the Binance Futures API.
    
    Parameters:
    - asset (str): The asset for which to get the wallet balance (e.g., 'USDT').
    
    Returns:
    - float: The wallet balance of the specified asset. Returns 0.0 if the asset is not found.
    """
    account_info = client.futures_account()
    for asset_balance in account_info['assets']:
        if asset_balance['asset'] == asset:
            return float(asset_balance['walletBalance'])
    return 0.0

def calculate_quantity(symbol, percentage):
    """
    Calculates the quantity to trade for a given symbol based on the percentage of the quote asset balance.
    
    Parameters:
    - symbol (str): The trading symbol (e.g., 'BTCUSDT').
    - percentage (float): The percentage of the quote asset balance to use for the trade.
    
    Returns:
    - str: The calculated quantity to trade, adjusted to the correct precision.
    """
    # Fetch account information
    account_info = client.futures_account()
    exchange_info = client.get_exchange_info()

    pair_info = next((item for item in exchange_info['symbols'] if item['symbol'] == symbol), None)

    if pair_info:
        # Extracting precision for quantity (lot size)
        lot_size_filter = next(filter for filter in pair_info['filters'] if filter['filterType'] == 'LOT_SIZE')
        quantity_precision = len(str(lot_size_filter['stepSize']).rstrip('0').split('.')[1]) if '.' in str(lot_size_filter['stepSize']) else 0

        # Extracting precision for price
        price_filter = next(filter for filter in pair_info['filters'] if filter['filterType'] == 'PRICE_FILTER')
        price_precision = len(str(price_filter['tickSize']).rstrip('0').split('.')[1]) if '.' in str(price_filter['tickSize']) else 0

        #print(f"Quantity Precision for {symbol}: {quantity_precision} decimal places")
        #print(f"Price Precision for {symbol}: {price_precision} decimal places")
    else:
        print(f"Information for {symbol} not found")
    
    # Extract the balance for the quote asset (e.g., USDT for BTCUSDT)
    quote_asset = 'USDT'  # Assuming all trading pairs are in the format ASSETUSDT
    quote_balance = 0.0
    for asset_balance in account_info['assets']:
        if asset_balance['asset'] == quote_asset:
            quote_balance = float(asset_balance['walletBalance'])
            break
    
    # Calculate the desired quantity
    desired_quantity = (percentage / 100) * quote_balance
    
    # Fetch the latest price for the symbol to convert the desired quantity to the base asset quantity
    latest_price = get_latest_price(symbol)
    base_asset_quantity = desired_quantity / latest_price
    
    qty = adjust_precision(base_asset_quantity, price_precision)

    print(f"{quote_asset} {quote_balance} {desired_quantity} {qty}")

    return qty

def place_order(symbol, side, leverage, percentage):
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
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        
        # Calculate the quantity based on the desired percentage of available balance
        quantity = calculate_quantity(symbol, percentage)

        timestamp = int(time.time() * 1000)    

        # Place order
        order = client.futures_create_order(symbol=symbol, side=side, type=client.ORDER_TYPE_MARKET, quantity=quantity, timestamp=timestamp)  # Adjust quantity as needed
        return order
    except BinanceAPIException as e:
        send_telegram_message(f"Error placing {side} order: {e.message}")
        return None

def close_order(symbol, side):
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
        client.FUTURES_API_VERSION = 'v1'
        closingSide = None
        #open_orders = client.futures_get_all_orders(symbol=symbol)
        order = side       
        #for order in open_orders:
        print(f"Processing Client Order ID: {order['clientOrderId']} at opened position: {order['side']}")
        if order['status'] == client.ORDER_STATUS_FILLED:
            print(f"Closing {order['clientOrderId']} order in opposite side...")       
            timestamp = int(time.time() * 1000)
            if order['side'] == client.SIDE_BUY:
                closingSide = client.SIDE_SELL
            else:
                closingSide = client.SIDE_BUY
            client.futures_create_order(symbol=symbol, side=closingSide, type=client.ORDER_TYPE_MARKET, quantity=order['origQty'], timestamp=timestamp)
            send_telegram_message(f"Closed {side} order.")

    except BinanceAPIException as e:
        send_telegram_message(f"Error closing {side} order: {e.message}")

def main(symbol, short_ema_period, long_ema_period, interval, leverage, percentage):
    """
    Main trading logic that uses exponential moving averages (EMA) to make trading decisions.
    
    Parameters:
    - symbol (str): The trading symbol (e.g., 'BTCUSDT').
    - short_ema_period (int): The period for the short EMA.
    - long_ema_period (int): The period for the long EMA.
    - interval (str): The interval for fetching historical data.
    - leverage (int): The leverage to use for trading.
   ).
    
    Returns:
    - list: A list of closing prices for each kline/candlestick.
    """
    last_action = {}
    balance = 0.0
    earning = 0.0
    last_action['side'] = None
    #client.FUTURES_API_VERSION = 'v2'
    while True:
        try:
            balance = get_balance('USDT')
            close_prices = get_historical_data(symbol, interval)
            short_ema = talib.EMA(np.array(close_prices), timeperiod=short_ema_period)[-1]
            long_ema = talib.EMA(np.array(close_prices), timeperiod=long_ema_period)[-1]
            latest_price = get_latest_price(symbol)
            #close_order(symbol, 'SELL')
            
            if short_ema > long_ema and last_action['side'] != client.SIDE_BUY:
                close_order(symbol, last_action)
                earning += (get_balance('USDT') - balance)
                order = place_order(symbol, client.SIDE_BUY, leverage, percentage)
                if order and order['status'] == Client.ORDER_STATUS_NEW:
                    last_action = order
                    send_telegram_message(f"Placed BUY order at {latest_price}. Qty: {percentage}, Short EMA: {short_ema}, Long EMA: {long_ema}")

            elif short_ema < long_ema and last_action['side'] != client.SIDE_SELL:
                close_order(symbol, last_action)
                earning += (get_balance('USDT') - balance)
                order = place_order(symbol, client.SIDE_SELL, leverage, percentage)
                if order and order['status'] == Client.ORDER_STATUS_NEW:
                    last_action = order
                    send_telegram_message(f"Placed SELL order at {latest_price}. Qty: {percentage}, Short EMA: {short_ema}, Long EMA: {long_ema}")

            send_telegram_message(f"Balance: ${balance} Earning: ${earning} Running: ${latest_price}. Qty: {percentage}, Short EMA: ${short_ema}, Long EMA: ${long_ema}")
            time.sleep(60*2)  # Wait for 1 minute before the next iteration

        except requests.exceptions.Timeout:
            send_telegram_message("Timeout error when communicating with Binance's API. Retrying...")
            continue

if __name__ == "__main__":
    
    import sys
    symbol = sys.argv[1]
    short_ema_period = int(sys.argv[2])
    long_ema_period = int(sys.argv[3])
    interval = sys.argv[4]
    leverage = int(sys.argv[5])
    percentage = float(sys.argv[6])

    main(symbol, short_ema_period, long_ema_period, interval, leverage, percentage)
