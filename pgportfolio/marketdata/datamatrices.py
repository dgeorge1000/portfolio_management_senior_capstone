from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import pgportfolio.marketdata.globaldatamatrix as gdm
import pgportfolio.marketdata.stockglobaldatamatrix as sgdm
import pgportfolio.marketdata.alphaVantage_globaldatamatrix as avgdm
import numpy as np
import pandas as pd
import logging
import json
from pgportfolio.tools.configprocess import parse_time
from pgportfolio.tools.configprocess import preprocess_config
from pgportfolio.tools.configprocess import fill_dates_alphaVantage
from pgportfolio.tools.data import get_volume_forward
import pgportfolio.marketdata.replaybuffer as rb

MIN_NUM_PERIOD = 3


class DataMatrices:
    def __init__(self, start, end, period, market, feature_number, features_list, batch_size=50, volume_average_days=30, buffer_bias_ratio=0,
                 coin_filter=1, window_size=50, test_portion=0.15,
                 portion_reversed=False, online=False, is_permed=False):
        """
        :param start: Unix time
        :param end: Unix time
        :param access_period: the data access period of the input matrix.
        :param trade_period: the trading period of the agent.
        :param global_period: the data access period of the global price matrix.
                              if it is not equal to the access period, there will be inserted observations
        :param coin_filter: number of coins that would be selected
        :param window_size: periods of input data
        :param train_portion: portion of training set
        :param is_permed: if False, the sample inside a mini-batch is in order
        :param validation_portion: portion of cross-validation set
        :param test_portion: portion of test set
        :param portion_reversed: if False, the order to sets are [train, validation, test]
        else the order is [test, validation, train]
        """
        
        # access json file and retrieve any relevant information the user wants to include
        with open("./pgportfolio/net_config.json") as file:
            config = json.load(file)
        config = preprocess_config(config)
        market = config["input"]["market_type"]
        start = int(start)
        self.__end = int(end)
        # assert window_size >= MIN_NUM_PERIOD
        self.__coin_no = coin_filter
        self.__features = features_list
        self.feature_number = feature_number
        volume_forward = get_volume_forward(self.__end-start, test_portion, portion_reversed)
        if market == "poloniex":
            self.__history_manager = gdm.HistoryManager(coin_number=coin_filter, end=self.__end,
                                                    volume_average_days=volume_average_days,
                                                    volume_forward=volume_forward, online=online)
            self.__global_data = self.__history_manager.get_global_dataframe(start,
                                                                         self.__end,
                                                                         period=period,
                                                                         features=features_list)
        elif market == "yahoo":
            with open("./pgportfolio/net_config.json") as file:
                config = json.load(file)
            config = preprocess_config(config)
            stock_data = config["input"]["stocks"]
            self.__history_manager = sgdm.StockHistoryManager(coin_number=coin_filter, end=self.__end, stocks=stock_data,
                                                    volume_average_days=volume_average_days,
                                                    volume_forward=volume_forward, online=online)

            self.__global_data = self.__history_manager.get_global_dataframe(start,
                                                                         self.__end,
                                                                         features_list,
                                                                         stock_data)
        elif market == "alphaVantage":
            with open("./pgportfolio/net_config.json") as file:
                config = json.load(file)
            config = preprocess_config(config)
            stock_data = config["input"]["stocks"]                  # contains user defined securities  
            api_key = config["input"]["api_key"]                    # user Alpha Vantage API Key
            api_call_limit = config["input"]["api_call_limit"]      # user Alpha Vantage call limit
            api_interval = config["input"]["api_interval"]          # time interval for the data
            # initiatize stock history manager class
            self.__history_manager = avgdm.AlphaVantageHistoryManager(coin_number=coin_filter, end=self.__end, online=online, stocks=stock_data,
                                                    api_key=api_key, api_call_limit=api_call_limit, api_interval=api_interval,
                                                    volume_average_days=volume_average_days,
                                                    volume_forward=volume_forward)
            # return a dataframe of all securities data and corresponding tech. ind.
            self.__global_data = self.__history_manager.get_global_dataframe(start,
                                                                         self.__end,
                                                                         online,
                                                                         features_list,
                                                                         stock_data,
                                                                         api_key,
                                                                         api_call_limit,
                                                                         api_interval)
            # fill_dates_alphaVantage()
        else:
            raise ValueError("market {} is not valid".format(market))
                    #Go from [coins*features, index] to [features, coins, index]

        self.raw = self.__global_data.values.reshape(
            len(self.__global_data.index),
            len(self.__global_data.columns.levels[0]),
            len(self.__global_data.columns.levels[1]),
            )    
        self.raw = self.raw.transpose(2,1,0)
        self.__period_length = period
        # portfolio vector memory, [time, assets]
        self.__PVM = pd.DataFrame(index=self.__global_data.index, #time index
                                  columns=self.__global_data.columns.levels[0]) #first level is coin names
        self.__PVM = self.__PVM.fillna(1.0 / self.__coin_no)

        print(self.__PVM)
        self._window_size = window_size
        self._num_periods = len(self.__global_data.index)
        self.__divide_data(test_portion, portion_reversed)

        self._portion_reversed = portion_reversed
        self.__is_permed = is_permed

        self.__batch_size = batch_size
        self.__delta = 0  # the count of global increased
        end_index = self._train_ind[-1]
        self.__replay_buffer = rb.ReplayBuffer(start_index=self._train_ind[0],
                                               end_index=end_index,
                                               sample_bias=buffer_bias_ratio,
                                               batch_size=self.__batch_size,
                                               coin_number=self.__coin_no,
                                               is_permed=self.__is_permed)

        logging.info("the number of training examples is %s"
                     ", of test examples is %s" % (self._num_train_samples, self._num_test_samples))
        logging.debug("the training set is from %s to %s" % (min(self._train_ind), max(self._train_ind)))
        logging.debug("the test set is from %s to %s" % (min(self._test_ind), max(self._test_ind)))

    @property
    def global_weights(self):
        return self.__PVM

    @staticmethod
    def create_from_config(config):
        """main method to create the DataMatrices in this project
        @:param config: config dictionary
        @:return: a DataMatrices object
        """
        config = config.copy()
        input_config = config["input"]
        print(input_config["feature_number"])
        print(input_config["features_list"])
        train_config = config["training"]
        start = parse_time(input_config["start_date"])
        end = parse_time(input_config["end_date"])
        return DataMatrices(start=start,
                            end=end,
                            market=config["input"]["market_type"],
                            feature_number=input_config["feature_number"],
                            features_list=input_config["features_list"],
                            window_size=input_config["window_size"],
                            online=input_config["online"],
                            period=input_config["global_period"],
                            coin_filter=input_config["coin_number"],
                            is_permed=input_config["is_permed"],
                            buffer_bias_ratio=train_config["buffer_biased"],
                            batch_size=train_config["batch_size"],
                            volume_average_days=input_config["volume_average_days"],
                            test_portion=input_config["test_portion"],
                            portion_reversed=input_config["portion_reversed"],
                            )

    @property
    def global_matrix(self):
        return self.__global_data

    @property
    def coin_list(self):
        return self.__history_manager.coins

    @property
    def num_train_samples(self):
        return self._num_train_samples

    @property
    def test_indices(self):
        return self._test_ind[:-(self._window_size+1):]

    @property
    def num_test_samples(self):
        return self._num_test_samples

    def append_experience(self, online_w=None):
        """
        :param online_w: (number of assets + 1, ) numpy array
        Let it be None if in the backtest case.
        """
        self.__delta += 1
        self._train_ind.append(self._train_ind[-1]+1)
        appended_index = self._train_ind[-1]
        self.__replay_buffer.append_experience(appended_index)

    def get_test_set(self):
        return self.__pack_samples(self.test_indices)

    def get_training_set(self):
        return self.__pack_samples(self._train_ind[:-self._window_size])

    def next_batch(self):
        """
        @:return: the next batch of training sample. The sample is a dictionary
        with key "X"(input data); "y"(future relative price); "last_w" a numpy array
        with shape [batch_size, assets]; "w" a list of numpy arrays list length is
        batch_size
        """
        batch = self.__pack_samples([exp.state_index for exp in self.__replay_buffer.next_experience_batch()])
        return batch

    def __pack_samples(self, indexs):

        
        indexs = np.array(indexs)
        last_w = self.__PVM.values[indexs-1, :]
        def setw(w):
            self.__PVM.iloc[indexs, :] = w
        M = [self.get_submatrix(self.raw ,index) for index in indexs]
        M = np.array(M)
        X = M[ :,: , :, :-1]
        y = M[ :, :, :, -1] / M[:, 0 , None, : , -2]

        return {"X": X, "y": y, "last_w": last_w, "setw": setw}

    # volume in y is the volume in next access period
    def get_submatrix(self, raw, ind):
        return raw[:,:,ind:ind+self._window_size+1]

    def __divide_data(self, test_portion, portion_reversed):
        train_portion = 1 - test_portion
        s = float(train_portion + test_portion)
        if portion_reversed:
            portions = np.array([test_portion]) / s
            portion_split = (portions * self._num_periods).astype(int)
            indices = np.arange(self._num_periods)
            self._test_ind, self._train_ind = np.split(indices, portion_split)
        else:
            portions = np.array([train_portion]) / s
            portion_split = (portions * self._num_periods).astype(int)
            indices = np.arange(self._num_periods)
            self._train_ind, self._test_ind = np.split(indices, portion_split)

        self._train_ind = self._train_ind[:-(self._window_size + 1)]
        # NOTE(zhengyao): change the logic here in order to fit both
        # reversed and normal version
        self._train_ind = list(self._train_ind)
        self._num_train_samples = len(self._train_ind)
        self._num_test_samples = len(self.test_indices)
