from pandas_datareader import data as pdr
from datetime import date
import yfinance as yf
yf.pdr_override()
import pandas as pd

# input start and end time for stock data
start_date= "2019-01-01"
end_date="2019-04-30"

# Tickers list that will stock names from "most_active_stocks.txt"
ticker_list = []

with open('most_active_stocks.txt','r') as file: 
    # reading each line     
    for line in file: 
        # reading each word         
        for word in line.split(): 
            # store stock name into ticker list     
            ticker_list.append(word) 
    
today = date.today()
            

files=[]
def getData(ticker):
    data = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
    dataname= ticker+'_'+str(today)
    files.append(dataname)
    SaveData(data, dataname)

# Create a data folder in your current dir.
def SaveData(df, info):
    df.to_csv('./data/'+info+'.csv')

#This loop will iterate over ticker list, will pass one ticker to get data, and save that data as file.
for tik in ticker_list:
    getData(tik)
for i in range(0,len(ticker_list)):
    df1= pd.read_csv('./data/'+ str(files[i])+'.csv')
