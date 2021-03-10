This file will describe the net_config options.

{
  "layers":[
    {"filter_shape": [1, 2], "filter_number": 3, "type": "ConvLayer"},
    {"filter_number":10, "type": "EIIE_Dense", "regularizer": "L2", "weight_decay": 5e-9},
    {"type": "EIIE_Output_WithW","regularizer": "L2", "weight_decay": 5e-8}
  ],
  "training":{
    "steps":2000000,
    "learning_rate":0.000001,
    "batch_size":5,
    "buffer_biased":5e-5,
    "snap_shot":false,
    "fast_train":true,
    "training_method":"Adam",
    "loss_function":"riskfactor"
  },
  "input":{
    "window_size":5,
    "global_period":1800,
    "test_portion":0.08,
    "online":true,
    "market_type":"alphaVantage",
    "generate_new_values":false,
    "api_key":" ",
    "api_call_limit": 200,
    "api_interval": "30min",
    "start_date":"2019/03/20",
    "end_date":"2020/03/08",
    "volume_average_days":30,
    "stocks": ["TQQQ", "TMF", "AGQ"],
    "coin_number":3, 
    "features_list": ["close", "high", "low", "open", "volume", "trend_macd"],
    "feature_number":6
  },
  "trading":{
    "trading_consumption":0.0025,
    "rolling_training_steps":50,
    "learning_rate":0.00028,
    "buffer_biased":5e-5
  }
}

********************************************************************************************************************************************************************************
For "input":
  "stocks": enter the tickers you want
  "coin_number": enter the number of tickers you put into "stocks"
  "features_list": enter the features you like
    5 Price Indexes:            "close", "high", "low", "open", "volume"
    83 Tech. Ind. Features:     "volume_adi", "volume_obv", "volume_cmf", "volume_fi", "volume_mfi", "volume_em", "volume_sma_em", "volume_vpt", "volume_nvi", "volume_vwap", "volatility_atr", "volatility_bbm", "volatility_bbh", "volatility_bbl", "volatility_bbw", "volatility_bbp", "volatility_bbhi", "volatility_bbli", "volatility_kcc", "volatility_kch", "volatility_kcl", "volatility_kcw", "volatility_kcp", "volatility_kchi", "volatility_kcli", "volatility_dcl", "volatility_dch", "volatility_dcm", "volatility_dcw", "volatility_dcp", "volatility_ui", "trend_macd", "trend_macd_signal", "trend_macd_diff", "trend_sma_fast", "trend_sma_slow", "trend_ema_fast", "trend_ema_slow", "trend_adx", "trend_adx_pos", "trend_adx_neg", "trend_vortex_ind_pos", "trend_vortex_ind_neg", "trend_vortex_ind_diff", "trend_trix", "trend_mass_index", "trend_cci", "trend_dpo", "trend_kst", "trend_kst_sig", "trend_kst_diff", "trend_ichimoku_conv", "trend_ichimoku_base", "trend_ichimoku_a", "trend_ichimoku_b", "trend_visual_ichimoku_a", "trend_visual_ichimoku_b", "trend_aroon_up", "trend_aroon_down", "trend_aroon_ind", "trend_psar_up", "trend_psar_down", "trend_psar_up_indicator", "trend_psar_down_indicator", "trend_stc", "momentum_rsi", "momentum_stoch_rsi", "momentum_stoch_rsi_k", "momentum_stoch_rsi_d", "momentum_tsi", "momentum_uo", "momentum_stoch", "momentum_stoch_signal", "momentum_wr", "momentum_ao", "momentum_kama", "momentum_roc", "momentum_ppo", "momentum_ppo_signal", "momentum_ppo_hist", "others_dr", "others_dlr", "others_cr"
        
        Volume Indicators:      "volume_adi", "volume_obv", "volume_cmf", "volume_fi", "volume_mfi", "volume_em", "volume_sma_em", "volume_vpt", "volume_nvi", "volume_vwap"
        Volatility Indicators:  "volatility_atr", "volatility_bbm", "volatility_bbh", "volatility_bbl", "volatility_bbw", "volatility_bbp", "volatility_bbhi", "volatility_bbli", "volatility_kcc", "volatility_kch", "volatility_kcl", "volatility_kcw", "volatility_kcp", "volatility_kchi", "volatility_kcli", "volatility_dcl", "volatility_dch", "volatility_dcm", "volatility_dcw", "volatility_dcp", "volatility_ui"
        Trend Indicators:       "trend_macd", "trend_macd_signal", "trend_macd_diff", "trend_sma_fast", "trend_sma_slow", "trend_ema_fast", "trend_ema_slow", "trend_adx", "trend_adx_pos", "trend_adx_neg", "trend_vortex_ind_pos", "trend_vortex_ind_neg", "trend_vortex_ind_diff", "trend_trix", "trend_mass_index", "trend_cci", "trend_dpo", "trend_kst", "trend_kst_sig", "trend_kst_diff", "trend_ichimoku_conv", "trend_ichimoku_base", "trend_ichimoku_a", "trend_ichimoku_b", "trend_visual_ichimoku_a", "trend_visual_ichimoku_b", "trend_aroon_up", "trend_aroon_down", "trend_aroon_ind", "trend_psar_up", "trend_psar_down", "trend_psar_up_indicator", "trend_psar_down_indicator", "trend_stc"
        Momentum Indicators:    "momentum_rsi", "momentum_stoch_rsi", "momentum_stoch_rsi_k", "momentum_stoch_rsi_d", "momentum_tsi", "momentum_uo", "momentum_stoch", "momentum_stoch_signal", "momentum_wr", "momentum_ao", "momentum_kama", "momentum_roc", "momentum_ppo", "momentum_ppo_signal", "momentum_ppo_hist"
	      Others:                 "others_dr", "others_dlr", "others_cr"

  Tech Ind Library GitHub: https://github.com/bukosabino/ta
  
 	"api_key": input your API Key in a string. Free keys are available at https://www.alphavantage.co/support/#api-key
	"api_call_limit": input your API Key call limit. Free keys as of 1/2021 are capped at 5 calls per min
	"api_interval": interval of time to get intraday data ("1min", "5min", "15min", "30min", "60min")
	"generate_new_values": if market==alphaVantage, the 1st generation_new_values=true will create a .xls of last 2 years of data. After that sheet is created, if 
				generate_new_values = false, it will look for the .xls sheet so it doesn't have to take time to generate new values. It is important to note
				generate_new_values = true will get you fully current data while false will run on the last data you generated
  
********************************************************************************************************************************************************************************

TEST RESULTS: bull market

volume_adi: no movement but good
volume_cmv: no movement but good
volume_fi: some movement and bad
volume_mfi: worse
volume_em: worse
volume_sma_em: much worse
volume_vpt: some movement but good
volume_nvi: no movement but good
volume_vwap: worse
volatility_atr: zeros in some column, results are perfectly at 1
volatility_bbm: worse
volatility_bbh: better!!  1.589440 BTC
volatility_bbl: better!!  1.516414 BTC
volatility_bbw: worse (slightly)
volatility_bbp: stays at 1
volatility_bbhi: worse (slightly)
volatility_bbli: stays at 1
volatility_kcc: worse (slightly)
volatility_kch: worse
volatility_kcl: better!  1.306781 BTC
volailitity_kcw: worse (slightly)
volatility_kcp: stays at 1
volatility_kchi: stays at 1
volatility_kcli: stays at 1
volatility_dcl: worse
volatility_dch: better!! 1.389588 BTC
volatility_dcm: worse (slightly)





