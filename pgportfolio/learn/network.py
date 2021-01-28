#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import tensorflow as tf
import tflearn


class NeuralNetWork:
    def __init__(self, feature_number, rows, columns, layers, device):
        tf_config = tf.ConfigProto()
        self.session = tf.Session(config=tf_config)
        if device == "cpu":
            tf_config.gpu_options.per_process_gpu_memory_fraction = 0
        else:
            #tf.config.experimental.set_memory_growth(tf.config.experimental.list_physical_devices("GPU")[0], True)
            tf_config.gpu_options.per_process_gpu_memory_fraction = 0.2
        self.input_num = tf.placeholder(tf.int32, shape=[])
        self.input_tensor = tf.placeholder(tf.float32, shape=[None, feature_number, rows, columns])
        self.previous_w = tf.placeholder(tf.float32, shape=[None, rows])
        self._rows = rows
        self._columns = columns

        self.layers_dict = {}
        self.layer_count = 0

        self.output = self._build_network(layers)

    def _build_network(self, layers):
        pass


class CNN(NeuralNetWork):
    # input_shape (features, rows, columns)
    def __init__(self, feature_number, rows, columns, layers, device):
        NeuralNetWork.__init__(self, feature_number, rows, columns, layers, device)

    def add_layer_to_dict(self, layer_type, tensor, weights=True):

        self.layers_dict[layer_type + '_' + str(self.layer_count) + '_activation'] = tensor
        self.layer_count += 1

    # grenrate the operation, the forward computaion
    def _build_network(self, layers):
        network = tf.transpose(self.input_tensor, [0, 2, 3, 1])
        # [batch, assets, window, features]
        network = network / network[:, :, -1, 0, None, None]
        for layer_number, layer in enumerate(layers):
            if layer["type"] == "DenseLayer":
                network = tflearn.layers.core.fully_connected(network,
                                                              int(layer["neuron_number"]),
                                                              layer["activation_function"],
                                                              regularizer=layer["regularizer"],
                                                              weight_decay=layer["weight_decay"] )
                self.add_layer_to_dict(layer["type"], network)
            elif layer["type"] == "Activation":
                network = tflearn.activation(network, activation=layer["activation_type"])
            elif layer["type"] == "DropOut":
                network = tflearn.layers.core.dropout(network, layer["keep_probability"])
            elif layer["type"] == "EIIE_Dense":
                width = network.get_shape()[2]
                network = tflearn.layers.conv_2d(network, int(layer["filter_number"]),
                                                 [1, width],
                                                 [1, 1],
                                                 "valid",
                                                 layer["activation_function"],
                                                 regularizer=layer["regularizer"],
                                                 weight_decay=layer["weight_decay"])
                self.add_layer_to_dict(layer["type"], network)
            elif layer["type"] == "ConvLayer":
                network = tflearn.layers.conv_2d(network, int(layer["filter_number"]),
                                                 allint(layer["filter_shape"]),
                                                 allint(layer["strides"]),
                                                 layer["padding"],
                                                 layer["activation_function"],
                                                 regularizer=layer["regularizer"],
                                                 weight_decay=layer["weight_decay"])
            elif layer["type"] == "DilatedConvLayer":
                network = tflearn.layers.conv.atrous_conv_2d(network, int(layer["filter_number"]),
                                                 allint(layer["filter_shape"]),
                                                 int(layer["rate"]),
                                                 layer["padding"],
                                                 layer["activation_function"],
                                                 regularizer=layer["regularizer"],
                                                 weight_decay=layer["weight_decay"])
                self.add_layer_to_dict(layer["type"], network)
            elif layer["type"] == "MaxPooling":
                network = tflearn.layers.conv.max_pool_2d(network, layer["strides"])
            elif layer["type"] == "AveragePooling":
                network = tflearn.layers.conv.avg_pool_2d(network, layer["strides"])
            elif layer["type"] == "LocalResponseNormalization":
                network = tflearn.layers.normalization.local_response_normalization(network)
            elif layer["type"] == "BatchNormalization":
                network = tflearn.layers.normalization.batch_normalization(network)
            elif layer["type"] == "ResidualTCN":
                #From "Probabilistic Forecasting with Temporal Convolutional Neural Network"
                #Originally used for retail sales prediction
                start = network
                network = tflearn.layers.conv.atrous_conv_2d(network, int(layer["filter_number"]),
                                                 allint(layer["filter_shape"]),
                                                 int(layer["rate"]),
                                                 "same",
                                                 layer["activation_function"],
                                                 regularizer=layer["regularizer"],
                                                 weight_decay=layer["weight_decay"])
                network = tflearn.layers.core.dropout(network, layer["keep_probability"])
                network = tflearn.layers.normalization.batch_normalization(network)  
                network = tflearn.activation(network, activation="ReLU")
                network = tflearn.layers.conv.atrous_conv_2d(network, int(layer["filter_number"]),
                                                 allint(layer["filter_shape"]),
                                                 int(layer["rate"]),
                                                 "same",
                                                 layer["activation_function"],
                                                 regularizer=layer["regularizer"],
                                                 weight_decay=layer["weight_decay"])
                network = tflearn.layers.core.dropout(network, layer["keep_probability"])
                network = tflearn.layers.normalization.batch_normalization(network) 
                network = network + start
            elif layer["type"] == "EIIE_Output":
                width = network.get_shape()[2]
                network = tflearn.layers.conv_2d(network, 1, [1, width], padding="valid",
                                                 regularizer=layer["regularizer"],
                                                 weight_decay=layer["weight_decay"])
                self.add_layer_to_dict(layer["type"], network)
                network = network[:, :, 0, 0]
                btc_bias = tf.ones((self.input_num, 1))
                self.add_layer_to_dict(layer["type"], network)
                network = tf.concat([btc_bias, network], 1)
                network = tflearn.layers.core.activation(network, activation="softmax")
                #network = (network)*2
                self.add_layer_to_dict(layer["type"], network, weights=False)
            elif layer["type"] == "EIIE_ShortSell":
                width = network.get_shape()[2]
                network = tflearn.layers.conv_2d(network, 1, [1, width], padding="valid",
                                                 regularizer=layer["regularizer"],
                                                 weight_decay=layer["weight_decay"])
                self.add_layer_to_dict(layer["type"], network)
                network = network[:, :, 0, 0]
                btc_bias = tf.ones((self.input_num, 1))
                self.add_layer_to_dict(layer["type"], network)
                network = tf.concat([btc_bias, network], 1)
                network = -tflearn.layers.core.activation(network, activation="softmax")
                """
                network = network[:, 0]
                print(network.shape)
                network = tf.concat([network, tf.concat([tf.zeros(1), tf.ones(1)], axis=0)], axis=1)
                print(network.shape)
                """
                #print(network.shape)
                #network[1] = tf.constant([0.0, -1.0, 0.0])
                #network = network#*tf.concat(tf.zeros(1), tf.ones(1), tf.zeros(1))
                #network = (network-.5)
                #netsum = tf.math.reduce_sum(tf.math.abs(network))
                #network = network/netsum
                self.add_layer_to_dict(layer["type"], network, weights=False)
                
            elif layer["type"] == "Output_WithW":
                network = tflearn.flatten(network)
                network = tf.concat([network,self.previous_w], axis=1)
                network = tflearn.fully_connected(network, self._rows+1,
                                                  activation="softmax",
                                                  regularizer=layer["regularizer"],
                                                  weight_decay=layer["weight_decay"])
            elif layer["type"] == "CNN_LSTM":
                network = tf.transpose(network, [0, 2, 3, 1])
                resultlist = []
                reuse = False
                for i in range(self._rows):
                    if i > 0:
                        reuse = True
                    result = tflearn.layers.simple_rnn(network[:, :, :, i],
                                                     int(layer["neuron_number"]),
                                                     dropout=0,
                                                     scope="lstm"+str(layer_number),
                                                     reuse=reuse)
                    resultlist.append(result)
                network = tf.stack(resultlist)
                network = tf.transpose(network, [1, 0, 2])
                network = tf.reshape(network, [-1, self._rows, 1, int(layer["neuron_number"])])                    
                    
            elif layer["type"] == "TCCBlock":
                start = network 
                """tflearn.layers.conv_2d(network, int(layer["filter_number"]), 
                                                             [1,1],
                                                             padding="same",
                                                             activation="ReLU",
                                                             weight_decay=0.0)"""
                network = tflearn.layers.conv.atrous_conv_2d(network, 
                                                             int(layer["filter_number"]), 
                                                             [1,3], 
                                                             int(layer["dilation_rate"]), 
                                                             padding="same",
                                                             activation="ReLU",
                                                             regularizer=layer["regularizer"],
                                                             weight_decay=0)
                network = tflearn.layers.normalization.local_response_normalization(network)
                network = tflearn.activation(network, activation="ReLU")
                network = tflearn.layers.dropout(network, layer["keep_prob"])
                network = tflearn.layers.conv.atrous_conv_2d(network, 
                                                             int(layer["filter_number"]),
                                                             [1,3], 
                                                             int(layer["dilation_rate"]), 
                                                             padding="same",
                                                             activation="ReLU",
                                                             regularizer=layer["regularizer"],
                                                             weight_decay=0)
                network = tflearn.layers.normalization.local_response_normalization(network)
                network = tflearn.activation(network, activation="ReLU")
                network = tflearn.layers.dropout(network, layer["keep_prob"])
                network = tflearn.layers.conv.conv_2d(network, 
                                                          int(layer["filter_number"]), 
                                                          [self._rows, 1], 
                                                          padding="same",
                                                          activation="ReLU",
                                                          regularizer=layer["regularizer"],
                                                          weight_decay=0)
                network = tflearn.activation(network, activation="ReLU")
                network = tflearn.layers.dropout(network, layer["keep_prob"])
                
                network = tf.concat([network, start], axis=3)
                network = tflearn.layers.conv_2d(network, int(layer["filter_number"]), 
                                                             [1,1],
                                                             padding="same",
                                                             activation="ReLU",
                                                             weight_decay=0)
                #network = tflearn.activation(network+start, activation="ReLU")
                self.add_layer_to_dict(layer["type"], network)
                
            elif layer["type"] == "EIIE_Output_WithW":
                width = network.get_shape()[2]
                height = network.get_shape()[1]
                features = network.get_shape()[3]
                network = tf.reshape(network, [self.input_num, int(height), 1, int(width*features)])
                w = tf.reshape(self.previous_w, [-1, int(height), 1, 1])
                network = tf.concat([network, w], axis=3)
                network = tflearn.layers.conv_2d(network, 1, [1, 1], padding="valid",
                                                 regularizer=layer["regularizer"],
                                                 weight_decay=layer["weight_decay"])
                self.add_layer_to_dict(layer["type"], network)
                network = network[:, :, 0, 0]
                #btc_bias = tf.zeros((self.input_num, 1))
                btc_bias = tf.get_variable("btc_bias", [1, 1], dtype=tf.float32,
                                       initializer=tf.zeros_initializer)
                # self.add_layer_to_dict(layer["type"], network, weights=False)
                btc_bias = tf.tile(btc_bias, [self.input_num, 1])
                network = tf.concat([btc_bias, network], 1)
                self.voting = network
                self.add_layer_to_dict('voting', network, weights=False)
                network = tflearn.layers.core.activation(network, activation="softmax")
                self.add_layer_to_dict('softmax_layer', network, weights=False)

            elif layer["type"] == "EIIE_LSTM" or\
                            layer["type"] == "EIIE_RNN":
                network = tf.transpose(network, [0, 2, 3, 1])
                resultlist = []
                reuse = False
                for i in range(self._rows):
                    if i > 0:
                        reuse = True
                    if layer["type"] == "EIIE_LSTM":
                        result = tflearn.layers.lstm(network[:, :, :, i],
                                                     int(layer["neuron_number"]),
                                                     dropout=layer["dropouts"],
                                                     scope="lstm"+str(layer_number),
                                                     reuse=reuse)
                    else:
                        result = tflearn.layers.simple_rnn(network[:, :, :, i],
                                                           int(layer["neuron_number"]),
                                                           dropout=layer["dropouts"],
                                                           scope="rnn"+str(layer_number),
                                                           reuse=reuse)
                    resultlist.append(result)
                network = tf.stack(resultlist)
                network = tf.transpose(network, [1, 0, 2])
                network = tf.reshape(network, [-1, self._rows, 1, int(layer["neuron_number"])])
            else:
                raise ValueError("the layer {} not supported.".format(layer["type"]))
        return network


def allint(l):
    return [int(i) for i in l]

