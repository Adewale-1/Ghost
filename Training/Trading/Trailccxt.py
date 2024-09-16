import ccxt

import pandas as pd
import numpy as np

from datetime import datetime

exchange = ccxt.binance()
bars = exchange.fetch_ohlcv("BTCUSDT", timeframe="4H", limit=30)

print(bars)
