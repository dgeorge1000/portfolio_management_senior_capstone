from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

from pgportfolio.marketdata.coinlist import CoinList
import numpy as np
import pandas as pd
from pgportfolio.tools.data import panel_fillna
from pgportfolio.constants import *
import sqlite3
import os.path
from datetime import datetime
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import time
import sys

import logging

from pandas_datareader import data as pdr
from ta import add_all_ta_features
from ta.utils import dropna
from datetime import datetime


# goal is to return panel of data using Alpha Vantage database, sign up for a free API on the website, students can request for premium key for free!
class AlphaVantageHistoryManager:
    # if offline ,the coin_list could be None
    def __init__(self, coin_number, end, stocks, api_key, api_call_limit, api_interval, generate, volume_average_days=1, volume_forward=0, online=True):
        self.__storage_period = FIVE_MINUTES  # keep this as 300
        self._coin_number = coin_number
        self.__volume_forward = volume_forward
        self.__volume_average_days = volume_average_days
        self.__coins = stocks
        self.__api_key = api_key
        self.__api_call_limit = api_call_limit
        self.__api_interval = api_interval
        self.__generate_new_values = generate
        
        # global variable to hold each month of data since Alpha Vantage only gives intraday data in month slices
        global df_sec 
        df_sec = []
        
    def coins(self):
        return self.__coins
    
    def get_global_data_matrix(self, start, end, features=('close',)):
        """
        :return a numpy ndarray whose axis is [feature, coin, time]
        """
        return self.get_global_dataframe(start, end, features).values

    # returns the securities into a multiIndex dataframe
    def get_global_dataframe(self, start, end, features, stocks, api_key, api_call_limit, api_interval, generate): 
        # if generate == True, the program will get the last 2 years of securities data and push it into an excel
        # if generate == False, the program will read the "./pgportfolio/marketdata/output_alphaVantage.xls" and create the dataframe
        if not generate and os.path.exists("./pgportfolio/marketdata/output_alphaVantage.xls"):
            panel = pd.read_excel('./pgportfolio/marketdata/output_alphaVantage.xls', header=[0,1], index_col=0)
            print(panel)
            return panel
        else:
            ts = TimeSeries(key = api_key, output_format = 'csv')
            # Alpha Vantage only gives out monly intraday data, so will need to do each month and concatenate to get 2 years of data
            two_years = [   "year1month1", "year1month2", "year1month3", "year1month4", "year1month5", "year1month6",
                            "year1month7", "year1month8", "year1month9", "year1month10", "year1month11", "year1month12",
                            "year2month1", "year2month2", "year2month3", "year2month4", "year2month5", "year2month6",
                            "year2month7", "year2month8", "year2month9", "year2month10", "year2month11", "year2month12"]       
            df_sec = []             # list that hold the 24 months of a security before concatenating into 1
            df_complete = []        # list that will hold each final df_sec, will contain all completed securities dataframe
            
            def getData(security, month, total_periods, att):
                # two global variables that will help loop through the function to align the dataframe properly
                global df_sec
                
                # retrieves data from Alpha Vantage
                curr_data = ts.get_intraday_extended(symbol = security, interval = api_interval, slice = month)
                curr_df = pd.DataFrame(list(curr_data[0]))      # convert tuple to a dataframe
                
                # setup of column and index into proper form
                header_row=0
                curr_df.columns = curr_df.iloc[header_row]
                curr_df = curr_df.drop(header_row)
                if(len(curr_df.columns) != 6):                  # this error will occur if minute limit is up 
                    sys.exit("ERROR: Your Alpha Vantage API calls have reached its 1 minute limit, run again at the minute mark. If running at the minute mark still results in this error, you have reached your daily API Limit.")
                    
                curr_df.set_index('time', inplace=True)         # add timestamps

                # remove unwanted labels and fill axis
                curr_df.columns.name = None
                curr_df.index.name = None
                curr_df.bfill(axis ='columns') 
                curr_df.ffill(axis ='columns') 
                curr_df = curr_df[['close', 'high', 'low', 'open', 'volume']]   # reorder columns to correct order
                
                # each value is a string/object, convert to floats
                curr_df['close'] = curr_df['close'].astype(float)
                curr_df['high'] = curr_df['high'].astype(float)
                curr_df['low'] = curr_df['low'].astype(float)
                curr_df['open'] = curr_df['open'].astype(float)
                curr_df['volume'] = curr_df['volume'].astype(float)
                
                df_sec.append(curr_df)          # add the security's month of data to the total security dataframe
                
                # This section will run when the security has completed all the data it needs
                # Will add the database to a list which will hold each individual security's dataframe
                if att % total_periods == 0:
                    df = pd.concat(df_sec, axis=0, join='outer')           # concatenate the list of dataframes into one along the rows
                    df.fillna(method='bfill', inplace=True)
                    df.fillna(method='ffill', inplace=True)
                    df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M:%S")     # make sure timestamps are sorted by converting string to datetime
                    df = df.sort_index(ascending=True)
                    df = add_all_ta_features(df, close="close", high="high", low="low", open="open", volume="volume", fillna='bfill')   # add tech ind
                    df.fillna(method='ffill', inplace=True)
                    df = df[features]                           # include only the indicators wanted by the user
                    print("\n\nINSERTING:", security)
                    print(df)
                    df_complete.append(df)
                    # reset the global variables for the next security
                    df_sec = []
            
            # go through each security and get the full dataframe for 2 years, after concatenate each dataframe into a MultiIndex one
            att = 0
            for security in stocks:
                for month_interval in two_years:
                    if att % api_call_limit == 0 and att != 0:      # will sleep if the api_call_limit for the min is over, will resume at the min mark
                        now = datetime.now()
                        current_time = now.strftime("%S")
                        remaining_time = 60 - int(current_time)
                        print("Will return at the minute mark (in", remaining_time, "s) to reset Alpha Vantage API Limit!")
                        time.sleep(remaining_time + 5) 
                    att = att + 1
                    df = getData(security, month_interval, len(two_years), att)     # calls getData and gets a month of intraday data
                    
            # concatenate the list of dataframes into one Multi Index dataframe and fill data in between
            df = pd.concat(df_complete, axis=1, join='outer')           
            df.fillna(method='bfill', inplace=True)
            df.fillna(method='ffill', inplace=True)

            df.index.name = None            # remove the name index
            index = pd.MultiIndex.from_product([df.index])
            columns = pd.MultiIndex.from_product([stocks, features])
            panel = pd.DataFrame(df.values, index=index, columns=columns, dtype="float64")      # push dataframe into panel

            print(panel)
            panel.to_excel("./pgportfolio/marketdata/output_alphaVantage.xls")           # save dataframe to an excel so we don't have to rerun to generate values 
            return panel


    # select top coin_number of coins by volume from start to end
    def select_coins(self, start, end):
        pass