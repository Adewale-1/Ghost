# import pandas as pd
# import pandas_ta as ta
# import numpy as np

# def enrich_data(data, ema_length=200, back_candles=10, volume_back_candles=1, price_back_candles=4):
#     """
#     Enrich the existing data with trend and volume indicators.

#     :param data: Pandas DataFrame with historical data
#     :param ema_length: Length of EMA for trend detection
#     :param back_candles: Number of candles to look back for EMA signal
#     :param volume_back_candles: Number of candles to look back for volume signal
#     :param price_back_candles: Number of candles to look back for price signal
#     :return: Enriched Pandas DataFrame
#     """
#     # Ensure the index is datetime
#     data.index = pd.to_datetime(data.index)

#     # Calculate EMA
#     data["EMA"] = ta.ema(data.Close, length=ema_length)

#     # EMA Signal
#     data['EMASignal'] = calculate_ema_signal(data, back_candles)

#     # Volume Signal
#     data['VSignal'] = calculate_volume_signal(data, volume_back_candles)

#     # Price Signal
#     data['PriceSignal'] = calculate_price_signal(data, price_back_candles)

#     # Total Signal
#     data['TotSignal'] = calculate_total_signal(data)

#     return data

# def calculate_ema_signal(data, back_candles):
#     emasignal = [0] * len(data)
#     for row in range(back_candles, len(data)):
#         uptrend = downtrend = 1
#         for i in range(row - back_candles, row + 1):
#             if data.High.iloc[i] >= data.EMA.iloc[i]:
#                 downtrend = 0
#             if data.Low.iloc[i] <= data.EMA.iloc[i]:
#                 uptrend = 0
#         if uptrend == 1 and downtrend == 1:
#             emasignal[row] = 3
#         elif uptrend == 1:
#             emasignal[row] = 1
#         elif downtrend == 1:
#             emasignal[row] = -1
#     return emasignal

# def calculate_volume_signal(data, volume_back_candles):
#     vsignal = [0] * len(data)
#     for row in range(volume_back_candles + 1, len(data)):
#         vsignal[row] = 1
#         for i in range(row - volume_back_candles, row):
#             if data.Volume.iloc[row] < data.Volume.iloc[i] and data.Volume.iloc[row-1] < data.Volume.iloc[row-2]:
#                 vsignal[row] = 0
#     return vsignal

# def calculate_price_signal(data, price_back_candles):
#     pricesignal = [0] * len(data)
#     for row in range(price_back_candles, len(data)):
#         pricesignal[row] = 1
#         for i in range(row - price_back_candles, row):
#             if data.EMASignal.iloc[row] == -1:  # downtrend
#                 if data.Open.iloc[row] <= data.Close.iloc[row]:  # downcandle row
#                     pricesignal[row] = 0
#                 elif data.Open.iloc[i] > data.Close.iloc[i]:  # downcandle i we are looking for 4 upcandles
#                     pricesignal[row] = 0
#             if data.EMASignal.iloc[row] == 1:  # uptrend
#                 if data.Open.iloc[row] >= data.Close.iloc[row]:  # upcandle row
#                     pricesignal[row] = 0
#                 elif data.Open.iloc[i] < data.Close.iloc[i]:  # upcandle i we are looking for 4 dowcandles
#                     pricesignal[row] = 0
#             else:
#                 pricesignal[row] = 0
#     return pricesignal

# def calculate_total_signal(data):
#     totsignal = [0] * len(data)
#     for row in range(len(data)):
#         if data.EMASignal.iloc[row] == -1 and data.VSignal.iloc[row] == 1 and data.PriceSignal.iloc[row] == 1:
#             totsignal[row] = -1
#         if data.EMASignal.iloc[row] == 1 and data.VSignal.iloc[row] == 1 and data.PriceSignal.iloc[row] == 1:
#             totsignal[row] = 1
#     return totsignal

# # Example usage:
# # Assuming you have your data in a DataFrame called 'df'
# # enriched_df = enrich_data(df)
# # enriched_df.to_csv('enriched_data.csv')
# df = pd.read_csv(
#     "/Users/adewaleadenle/Software Development/GitHub Projects/Ghost/Training/Trading/CurrencyData/preprocessed_data2.csv",
#     index_col="Datetime",
#     parse_dates=True,
# )

# # Enrich the data
# enriched_df = enrich_data(df)

# # Save the enriched data if needed
# enriched_df.to_csv("enriched_data.csv")

import pandas as pd
import pandas_ta as ta
import numpy as np


def calculate_enhanced_signals(data):
    # Calculate EMA
    data["EMA"] = ta.ema(data.Close, length=200)

    # Calculate EMA Signal
    backcandles = 10
    emasignal = np.zeros(len(data))

    for row in range(backcandles, len(data)):
        uptrend = 1
        downtrend = 1
        for i in range(row - backcandles, row + 1):
            if data.High.iloc[i] >= data.EMA.iloc[i]:
                downtrend = 0
            elif data.Low.iloc[i] <= data.EMA.iloc[i]:
                uptrend = 0
        if uptrend == 1 and downtrend == 1:
            emasignal[row] = 3
        elif uptrend == 1:
            emasignal[row] = 1
        elif downtrend == 1:
            emasignal[row] = -1

    data["EMASignal"] = emasignal

    # Calculate Volume Signal
    volumeBackCandles = 1
    VSignal = np.ones(len(data))

    for row in range(volumeBackCandles + 1, len(data)):
        for i in range(row - volumeBackCandles, row):
            if (
                data.Volume.iloc[row] < data.Volume.iloc[i]
                and data.Volume.iloc[row - 1] < data.Volume.iloc[row - 2]
            ):
                VSignal[row] = 0

    data["VSignal"] = VSignal

    # Calculate Price Signal
    pbackcandles = 4
    PriceSignal = np.zeros(len(data))

    for row in range(pbackcandles, len(data)):
        PriceSignal[row] = 1
        for i in range(row - pbackcandles, row):
            if data.EMASignal.iloc[row] == -1:  # downtrend
                if data.Open.iloc[row] <= data.Close.iloc[row]:  # downcandle row
                    PriceSignal[row] = 0
                elif (
                    data.Open.iloc[i] > data.Close.iloc[i]
                ):  # downcandle i we are looking for 4 upcandles
                    PriceSignal[row] = 0
            elif data.EMASignal.iloc[row] == 1:  # uptrend
                if data.Open.iloc[row] >= data.Close.iloc[row]:  # upcandle row
                    PriceSignal[row] = 0
                elif (
                    data.Open.iloc[i] < data.Close.iloc[i]
                ):  # upcandle i we are looking for 4 dowcandles
                    PriceSignal[row] = 0
            else:
                PriceSignal[row] = 0

    data["PriceSignal"] = PriceSignal

    # Calculate Total Signal
    TotSignal = np.zeros(len(data))
    for row in range(0, len(data)):
        if (
            data.EMASignal.iloc[row] == -1
            and data.VSignal.iloc[row] == 1
            and data.PriceSignal.iloc[row] == 1
        ):
            TotSignal[row] = -1
        elif (
            data.EMASignal.iloc[row] == 1
            and data.VSignal.iloc[row] == 1
            and data.PriceSignal.iloc[row] == 1
        ):
            TotSignal[row] = 1

    data["TotSignal"] = TotSignal

    return data
