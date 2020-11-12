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
import yfinance as yf
yf.pdr_override()



class StockHistoryManager:
    # if offline ,the coin_list could be None
    # NOTE: return of the sqlite results is a list of tuples, each tuple is a row
    def __init__(self, coin_number, end, volume_average_days=1, volume_forward=0, online=True):
        self.__storage_period = FIVE_MINUTES  # keep this as 300
        self._coin_number = coin_number
        self.__volume_forward = volume_forward
        self.__volume_average_days = volume_average_days
        self.__coins = None

    # 
    def get_global_data_matrix(self, start, end, period=300, features=('close',)):
        """
        :return a numpy ndarray whose axis is [feature, coin, time]
        """
        return self.get_global_dataframe(start, end, period, features).values

    # returns the stocks into a multiIndex dataframe
    # NOTE need to change start and end to timestamp, and period is 1 day as of now
    def get_global_dataframe(start, end, period, features): 
        '''Sample start and end
        start_date= "2019-01-01"
        end_date="2019-04-30"
        '''
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
        
        # panel = panel_fillna(panel, "both")

    # select top coin_number of coins by volume from start to end
    def select_coins(self, start, end):
        if not self._online:
            logging.info("select coins offline from %s to %s" % (datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M'),
                                                                    datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M')))
            connection = sqlite3.connect(DATABASE_DIR)
            try:
                cursor=connection.cursor()
                cursor.execute('SELECT coin,SUM(volume) AS total_volume FROM History WHERE'
                               ' date>=? and date<=? GROUP BY coin'
                               ' ORDER BY total_volume DESC LIMIT ?;',
                               (int(start), int(end), self._coin_number))
                coins_tuples = cursor.fetchall()

                if len(coins_tuples)!=self._coin_number:
                    logging.error("the sqlite error happend")
            finally:
                connection.commit()
                connection.close()
            coins = []
            for tuple in coins_tuples:
                coins.append(tuple[0])
        else:
            coins = list(self._coin_list.topNVolume(n=self._coin_number).index)
        logging.debug("Selected coins are: "+str(coins))
        return coins
