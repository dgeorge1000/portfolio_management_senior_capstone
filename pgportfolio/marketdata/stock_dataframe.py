import numpy as np
from pandas_datareader import data as pdr
from datetime import date
import yfinance as yf
yf.pdr_override()
import pandas as pd

# hierarchical indices and columns
# input start and end time for stock data
start_date= "2019-01-01"
end_date="2019-04-30"



ticker_list = []            # Tickers list that will stock names from "most_active_stocks.txt"
df_list = []                # list of all dataframes for stocks

            
with open('most_active_stocks.txt','r') as file:                
    for line in file:                   # reading each line                  
        for word in line.split():       # reading each word                     
             ticker_list.append(word)    # store stock name into ticker list   
                    
               
def getData(ticker):
    data = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
    df = pd.DataFrame(data, columns = ['Close','High','Low'])
    df_list.append(df)                  # puts dataframe into the list
                    
for tik in ticker_list:
    df = getData(tik)
                    
df = pd.concat(df_list, axis=1, join='inner')           # contains all dataframes
stocks = ticker_list
         
df.index.name = None            # remove the name index
index = pd.MultiIndex.from_product([df.index])
columns = pd.MultiIndex.from_product([ticker_list, ['close', 'high', 'low']])

# create the DataFrame
panel = pd.DataFrame(df.values, index=index, columns=columns, dtype="float64")
print(panel)
 # panel = panel_fillna(panel, "both")



'''
start = 1498881600
end = 1561953600
period = 1800
time_index = pd.to_datetime(list[range(start, end+1, period)],unit='s')
print(time_index)
'''