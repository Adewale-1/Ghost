import json
import websocket
import pandas as pd


assets = ["BTCUSDT"]

assets = [asset.lower() + "@kline_1h" for asset in assets]

assets = "/".join(assets)


def on_message(ws, message):
    message = json.loads(message)
    print(message)


socket = "wss://stream.binance.com:9443/stream?streams=" + assets


ws = websocket.WebSocketApp(socket, on_message=on_message)

ws.run_forever()

