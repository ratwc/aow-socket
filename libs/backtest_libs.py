import pandas as pd
import math
import ta
import copy

decimal_dict = {
    'EUR/USD': 5, 
    'USD/JPY': 3,
    'GBP/USD': 5,
    'USD/CHF': 5,
    'USD/CAD': 5,
    'AUD/USD': 5,
    'NZD/USD': 5,
    'XAU/USD': 3
}

def MA(data, tf, params, symbol): # apply price, type of MA, window(period)

    try:

        # get data for calculate
        apply_price = params['apply_price']
        period = params['period']
        type = params['type']

        # check apply price 
        if apply_price.lower() == 'open': use_data = data['Open'][-period:]
        elif apply_price.lower() == 'close': use_data = data['Close'][-period:]
        elif apply_price.lower() == 'high': use_data = data['High'][-period:]
        elif apply_price.lower() == 'low': use_data = data['Low'][-period:]
        # type of MA
        if type.lower() == "simple": res_ta = ta.trend.SMAIndicator(use_data, period).sma_indicator()
        elif type.lower() == "exponential": res_ta = ta.trend.EMAIndicator(use_data, period).ema_indicator()
        elif type.lower() == "weighted": res_ta = ta.trend.WMAIndicator(use_data, period).wma()
        
        # get signal of the indicator
        ta_value = round(res_ta[-1:].values[0], decimal_dict[symbol])
        tick_value = round(use_data[-1:].values[0], decimal_dict[symbol])
        if tick_value > ta_value: signal = "BUY"
        elif tick_value < ta_value: signal = "SELL"
        else: signal = "NEUTRAL"

        return { "timeframe": tf, "value": ta_value, "signal": signal, "type": "trend"}
    
    except Exception as e :
        print("MA calculation error on > ", e)

def MACD(data, tf, params, symbol): # apply_price, fastperiod, slowperiod, signalperiod

    try: 

        # get data for calculate
        apply_price = params['apply_price']
        fast_period, slow_period, signal_period = params['fastperiod'], params['slowperiod'], params['signalperiod']

        # check apply price 
        if apply_price.lower() == 'open': use_data = data['Open']
        elif apply_price.lower() == 'close': use_data = data['Close']
        elif apply_price.lower() == 'high': use_data = data['High']
        elif apply_price.lower() == 'low': use_data = data['Low']

        res_ta = ta.trend.MACD(use_data, window_fast=fast_period, window_slow=slow_period ,window_sign=signal_period) # signal line is base and macd line will crossover
        macd_line, signal_line = round(res_ta.macd()[-1:].values[0], decimal_dict[symbol]), round(res_ta.macd_signal()[-1:].values[0], decimal_dict[symbol])

        if macd_line > signal_line:
            signal, arrow_type = "BUY", "arrow-up"
        elif macd_line < signal_line:
            signal, arrow_type = "SELL", "arrow-down"
        else:
            signal, arrow_type = "NEUTRAL", "non-arrow"

        return { "timeframe": tf, "arrowtype": arrow_type, "value": macd_line, "signal": signal, "type": "trend"}

    except Exception as e :
        print("MACD calculation error on > ", e)

def PSAR(data, tf, params, symbol): # step, max_step

    try: 

        # get data for calculate
        step, max_step = params['step'], params['max_step']
        high, low, close = data['High'], data['Low'], data['Close']

        res_ta = ta.trend.PSARIndicator(high, low, close, step=float(step), max_step=float(max_step))

        ta_value = round(res_ta.psar()[-1:].values[0], decimal_dict[symbol])
        tick_value = round(data['Close'][-1:].values[0], decimal_dict[symbol])

        if tick_value > ta_value: signal = "BUY"
        elif tick_value < ta_value: signal = "SELL"
        else: signal = "NEUTRAL"

        return { "timeframe": tf, "value": ta_value, "signal": signal, "type": "trend"}
    
    except Exception as e :
        print("PSAR calculation error on > ", e)

def RSI(data, tf, params, symbol): # apply_price, period, overbought, oversold

    try: 
        # get data for calculate
        apply_price, period = params['apply_price'], params['period']
        overbought, oversold = params['overbought'], params['oversold']

        # check apply price 
        if apply_price.lower() == 'open': use_data = data['Open'][-period:]
        elif apply_price.lower() == 'close': use_data = data['Close'][-period:]
        elif apply_price.lower() == 'high': use_data = data['High'][-period:]
        elif apply_price.lower() == 'low': use_data = data['Low'][-period:]

        res_ta  = ta.momentum.RSIIndicator(use_data, window=period).rsi()
        ta_value = round(res_ta[-1:].values[0], 2)

        if ta_value > overbought: signal = "OVERBOUGHT"
        elif ta_value < oversold: signal = "OVERSOLD"
        else: signal = "NEUTRAL"

        return { "timeframe": tf, "value": ta_value, "signal": signal, "type": "momentum"}

    except Exception as e :
        print("RSI calculation error on > ", e)

def CCI(data, tf, params, symbol): # period, overbought, oversold

    try: 
        # get data for calculate
        period = params['period']
        overbought, oversold = params['overbought'], params['oversold']
        high, low, close = data['High'], data['Low'], data['Close']

        res_ta = ta.trend.CCIIndicator(high, low, close, window=int(period), constant=float(0.015))
        ta_value = round(res_ta.cci()[-1:].values[0], 2)  

        if ta_value > overbought: signal = "OVERBOUGHT"
        elif ta_value < oversold: signal = "OVERSOLD"
        else: signal = "NEUTRAL"

        return { "timeframe": tf, "value": ta_value, "signal": signal, "type": "momentum"}

    except Exception as e :
        print("CCI calculation error on > ", e)

def STOCH(data, tf, params, symbol): # period, sma_period, overbought, oversold

    try: 
        # get data for calculate
        period, sma_period = params['period'], params['sma_period']
        overbought, oversold = params['overbought'], params['oversold']
        high, low, close = data['High'], data['Low'], data['Close']

        res_ta = ta.momentum.StochasticOscillator(high, low, close, window=int(period), smooth_window=int(sma_period))   
        ta_value, ta_signal = round(res_ta.stoch()[-1:].values[0], 2), round(res_ta.stoch_signal()[-1:].values[0], 2)

        if ta_signal > overbought: signal = "OVERBOUGHT"
        elif ta_signal < oversold: signal = "OVERSOLD"
        else: signal = "NEUTRAL"

        if ta_signal > ta_value: arrow_type = "arrow-up"
        elif ta_signal < ta_value: arrow_type = "arrow-down"
        else: arrow_type = "non-arrow"

        return { "timeframe": tf, "arrowtype": arrow_type, "value": ta_signal, "signal": signal, "type": "momentum"}

    except Exception as e :
        print("STOCH calculation error on > ", e)

def WPCR(data, tf, params, symbol): # period, overbought, oversold

    try: 
        # get data for calculate
        period = params['period']
        overbought, oversold = params['overbought'], params['oversold']
        high, low, close = data['High'], data['Low'], data['Close']

        res_ta = ta.momentum.WilliamsRIndicator(high, low, close, lbp=int(period))
        ta_value = round(res_ta.williams_r()[-1:].values[0], decimal_dict[symbol])

        if ta_value > overbought: signal = "OVERBOUGHT"
        elif ta_value < oversold: signal = "OVERSOLD"
        else: signal = "NEUTRAL"

        return { "timeframe": tf, "value": ta_value, "signal": signal, "type": "momentum"}

    except Exception as e :
        print("W%R calculation error on > ", e)


## ========= Convert Zone =========

# the comment timeframe feature will update in the future
timeframe = {
    # "1Min": 1,
    "5Min": 5,
    "10Min": 10,
    "15Min": 15,
    "30Min": 30,
    "45Min": 45,
    "1H": 60,
    "2H": 120,
    "3H": 180,
    "4H": 240,
    "8H": 480,
    "12H": 720,
    "1D": 1440,
    # "1W": 10080, # need to have offset because the present start of the week is thuesday
    # "1M": "month"
}

def ohlc_to_ohlc(data, from_tf, to_tf):

    try: 

        if timeframe[from_tf] > timeframe[to_tf]:
            print("to timeframe must be greater than from timeframe")
            return 0

        elif timeframe[from_tf] == timeframe[to_tf]:
            return data

        # copy the data to new variable to prevent data change by reference
        ohlc_data = copy.deepcopy(data)

        # change time from milliseconds to seconds 
        tf_seconds = timeframe[to_tf] * 60

        def format_time(time):
            time = math.floor(time / 1000)
            return time - time % tf_seconds

        ohlc_data.index = ohlc_data.index.map(format_time)

        # find the interval to time
        start_list = [0]
        A = ohlc_data.index
        B = ohlc_data[1:].index
        [start_list.append(idx + 1) for idx in range(len(B)) if A[idx] != B[idx]]
        start_list.append(ohlc_data.index.size)

        new_ohlc = []
        def form_data(idx):

            temp_dict = {}
            tf_data = ohlc_data[start_list[idx]: start_list[idx + 1]]

            # add data to dict
            temp_dict['Datetime'] = tf_data.index.values[-1] * 1000
            temp_dict['Open'] = tf_data['Open'].values[0]
            temp_dict['High'] = max(tf_data['High'].values)
            temp_dict['Low'] = min(tf_data['Low'].values)
            temp_dict['Close'] = tf_data['Close'].values[-1]

            new_ohlc.append(temp_dict)

        list(map(form_data, range(len(start_list[:-1]))))

        return pd.DataFrame(new_ohlc).set_index('Datetime')

    except Exception as e: 

        print("Some Error on convert ohlc: ", e)


def summary(indicators_signal):

    return_summary = {}
    return_summary['all'] = {}
    return_summary['summary'] = {}
    return_summary['all']['SELL'], return_summary['all']['BUY'] = 0, 0

    for indicator in indicators_signal.keys():

        for tf in indicators_signal[indicator]:

            if tf['signal'] in ['BUY', 'OVERSOLD']: return_summary['all']['BUY'] += 1
            elif tf['signal'] in ['SELL', 'OVERBOUGHT']: return_summary['all']['SELL'] += 1
        
    if (return_summary['all']['BUY'] + return_summary['all']['SELL']) != 0:
        return_summary['summary']['BUY'] = return_summary['all']['BUY'] * 100 / (return_summary['all']['BUY'] + return_summary['all']['SELL'])
        return_summary['summary']['SELL'] = return_summary['all']['SELL'] * 100 / (return_summary['all']['BUY'] + return_summary['all']['SELL'])
    else :
        return_summary['summary']['BUY'] = 0
        return_summary['summary']['SELL'] = 0

    return return_summary