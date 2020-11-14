from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from pgportfolio.marketdata.coinlist import CoinList
import numpy as np
import pandas as pd
from pgportfolio.tools.data import panel_fillna
from pgportfolio.constants import *
import sqlite3
from datetime import datetime
import logging

from pandas_datareader import data as pdr
from datetime import date
#import yfinance as yf
#yf.pdr_override()



class StockHistoryManager:
    # if offline ,the coin_list could be None
    # NOTE: return of the sqlite results is a list of tuples, each tuple is a row
    def __init__(self, coin_number, end, volume_average_days=1, volume_forward=0, online=True):
        self.__storage_period = FIVE_MINUTES  # keep this as 300
        self._coin_number = coin_number
        self.__volume_forward = volume_forward
        self.__volume_average_days = volume_average_days
        self.__coins = []
        with open('most_active_stocks.txt','r') as file:                
            for line in file:                   # reading each line                  
                for word in line.split():       # reading each word        
                    self.__coins.append(word)

    # 
    def coins(self):
        return self.__coins
    
    def get_global_data_matrix(self, start, end, features=('close',)):
        """
        :return a numpy ndarray whose axis is [feature, coin, time]
        """
        return self.get_global_dataframe(start, end, features).values

    # returns the stocks into a multiIndex dataframe
    # NOTE need to change start and end to timestamp, and period is 1 day as of now
    def get_global_dataframe(self, start, end, features): 
        #Sample start and end
        start_date= "2014-01-01"
        end_date="2020-07-01"
        
        ticker_list = []            # Tickers list that will stock names from "most_active_stocks.txt"
        df_list = []                # list of all dataframes for stocks

        features = [feature.capitalize() for feature in features]
        with open('most_active_stocks.txt','r') as file:                
            for line in file:                   # reading each line                  
                for word in line.split():       # reading each word        
                    ticker_list.append(word)    # store stock name into ticker list   
                    
               
        def getData(ticker):
            startdt = datetime.fromtimestamp(start)
            enddt = datetime.fromtimestamp(end)
            print("getting stock data from: " + ticker)
            data = pdr.DataReader(ticker,start=start_date, end=end_date, data_source='yahoo')
            df = pd.DataFrame(data, columns = features)
            df_list.append(df)                  # puts dataframe into the list
                    
                    
        for tik in ticker_list:
            df = getData(tik)
                    
        df = pd.concat(df_list, axis=1, join='inner')           # contains all dataframes
        stocks = ticker_list
         
        df.index.name = None            # remove the name index
        index = pd.MultiIndex.from_product([df.index])
        columns = pd.MultiIndex.from_product([ticker_list, features])

        # create the DataFrame
        panel = pd.DataFrame(df.values, index=index, columns=columns, dtype="float64")
        
        panel = panel_fillna(panel, "both")
        return panel

    # select top coin_number of coins by volume from start to end
    def select_coins(self, start, end):
        pass