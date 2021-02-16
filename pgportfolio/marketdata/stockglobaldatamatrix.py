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
from ta import add_all_ta_features
from ta.utils import dropna
#import yfinance as yf
#yf.pdr_override()



class StockHistoryManager:
    # if offline ,the coin_list could be None
    # NOTE: return of the sqlite results is a list of tuples, each tuple is a row
    def __init__(self, coin_number, end, stocks, volume_average_days=1, volume_forward=0, online=True):
        self.__storage_period = FIVE_MINUTES  # keep this as 300
        self._coin_number = coin_number
        self.__volume_forward = volume_forward
        self.__volume_average_days = volume_average_days
        self.__coins = stocks
        
    def coins(self):
        return self.__coins
    
    def get_global_data_matrix(self, start, end, features=('close',)):
        """
        :return a numpy ndarray whose axis is [feature, coin, time]
        """
        return self.get_global_dataframe(start, end, features).values

    # returns the securities and tech ind into a multiIndex dataframe
    def get_global_dataframe(self, start, end, features, stocks): 
        #Sample start and end
        df_list = []                # list of all dataframes for stocks

        # features = [feature.capitalize() for feature in features]
        
        def getData(ticker):
            startdt = datetime.fromtimestamp(start)         # convert timestamp to date and time
            enddt = datetime.fromtimestamp(end)
            print("getting stock data from: " + ticker)
            data = pdr.DataReader(ticker,start=startdt, end=enddt, data_source='yahoo')     # get the security data from yfinance
            df = pd.DataFrame(data, columns = ['Close','High','Low','Open','Volume'])       # construct dataframe with security data
            df = add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna='bfill')  # add all tech ind, with back fill for NaN values
            df.fillna(method='ffill', inplace=True)         # forward fill NaN if necessary
            df.columns = df.columns.str.lower()             # lowercase columns for proper input
            df = df[features]                               # crop the dataframe to include only features the user wants
            df_list.append(df)                  # puts dataframe into the list
                                             
        for tik in stocks:          # calls each security to be added to the dataframe
            df = getData(tik)
                        
        df = pd.concat(df_list, axis=1, join='outer')           # concatenate the list of dataframes into one Multi Index dataframe
        df.fillna(method='bfill', inplace=True)
        df.fillna(method='ffill', inplace=True)
             
        df.index.name = None            # remove the name index
        index = pd.MultiIndex.from_product([df.index])
        columns = pd.MultiIndex.from_product([stocks, features])

        # contains the final dataframe in proper format for the neural netwoek
        panel = pd.DataFrame(df.values, index=index, columns=columns, dtype="float64")
        print(panel)
        return panel

    # select top coin_number of coins by volume from start to end
    def select_coins(self, start, end):
        pass
