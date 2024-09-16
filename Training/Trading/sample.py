

import pandas
import pandas_ta as ta


data = pd.read_csv(
    "/Users/adewaleadenle/Software Development/GitHub Projects/Ghost/Training/Trading/CurrencyData/preprocessed_data2.csv"
)


data["EMA"] = ta.ema(df.Close, length = 200)
emasignal = [0] * len(data)

backcandles = 10

for row in range(backcandles , len(data)):
    uptrend = 1
    downtred = 1
    for i in range(row - backcandles , row + 1):
        if data.High[i] >= data.EMA[i]:
            
            downtred = 0
        else data.Low[i] <= data.EMA[i]:
            uptrend = 0
    if uptrend == 1 and downtrend == 1:
        emasignal[row] = 3
    elif uptrend == 1:
        emasignal[row] = 1
    elif downtrend == 1:
        emasignal[row] = -1
        
data['EMASignal'] = emasignal


VSignal = [0] * len(data)
volumeBackCandles = 1

for row in range(volumeBackCandles + 1, len(data)):
    VSignal[row] = 1
    
    for i in range (row - volumeBackCandles, row):
        if data.Volume[row] < data.Volume[i] and data.Volume[row-1] < data.Volume[row-2]:
            volumeBackCandles[row] = 0
    
data['VSignal'] = VSignal


PriceSignal = [0]*len(data)
pbackcandles = 4
for row in range(pbackcandles, len(data)):
    PriceSignal[row] = 1
    for i in range(row-pbackcandles, row):
        if data.EMASignal[row] == -1: #downtrende
            if data.Open[row] <= data.Close[row]: #downcandle row
                PriceSignal[row]=0
            elif data.Open[i] > data.Close[i]: #downcandle i we are looking for 4 upcandles
                PriceSignal[row]=0
        if data.EMASignal[row] == 1: #uptrend
            if data.Open[row]>=data.Close[row]: #upcandle row
                PriceSignal[row]=0
            elif data.Open[i] < data.Close[i]: #upcandle i we are looking for 4 dowcandles
                PriceSignal[row]=0
        else:
            PriceSignal[row] = 0

data['PriceSignal']=PriceSignal


TotSignal = [0] * len(data)
for row in range(0, len(data)):
    if data.EMASignal[row]== -1 and data.VSignal[row]==1 and data.PriceSignal[row]==1:
        TotSignal[row]= -1
    if df.EMASignal[row]==1 and df.VSignal[row]==1 and df.PriceSignal[row]==1:
        TotSignal[row]= 1

data['TotSignal']=TotSignal