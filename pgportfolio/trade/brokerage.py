# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 04:54:19 2021

@author: Noah
"""

from binance.client import Client
import numpy as np
import os

class Brokerage:
    
    def __init__(self, coins, period):
        self._coins = coins
        self._period = period
    
    def rebalance(self):
        pass
    
    def getlastX(self):
        pass
    
    
class Binance(Brokerage):
    
    def __init__(self, coins, period):
        super().__init__(coins, period)
        self._coins = self.__fixcoins(self._coins)
        
        api_key = os.environ.get('binance_key')
        api_secret = os.environ.get('binance_secret_key')

        self.client = Client(api_key, api_secret)
        
        print(self.__translateperiod(self._period))
        
    def __translateperiod(self, period):
        if period == 300:
            return Client.KLINE_INTERVAL_5MINUTE
        elif period == 900:
            return Client.KLINE_INTERVAL_15MINUTE
        elif period == 1800:
            return Client.KLINE_INTERVAL_30MINUTE
        elif period == 7200:
            return Client.KLINE_INTERVAL_2HOUR
        elif period == 14400:
            return Client.KLINE_INTERVAL_4HOUR
        elif period == 86400:
            return Client.KLINE_INTERVAL_1DAY
        else:
            raise ValueError('peroid has to be 5min, 15min, 30min, 2hr, 4hr, or a day')
        
    def __fixcoins(self, coins):
        newcoins = []
        for c in coins:
            if "reversed_" in c:
                c = c.replace("reversed_", "")
                c =  c + "BTC"
                newcoins.append(c)
            else:
                c = "BTC" + c
                newcoins.append(c)
        return newcoins
    
    def getlastX():
        pass
        

Binance(["reversed_USDC", "ETH"], 1800)