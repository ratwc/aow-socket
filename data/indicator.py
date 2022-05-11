# get all technical indicator
from libs.convert import ohlc_to_ohlc
import warnings
import ta
from data.tick import symbols_data, default_name, default_tf
import requests as r
from bs4 import BeautifulSoup as bs
import datetime as dt
import math
import re

warnings.filterwarnings("ignore") # disable any warnings

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

## ------------------ TREND INDICATORS ------------------

def MA(symbol, tf, params): # apply price, type of MA, window(period)

    try:
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0

        # get data for calculate
        apply_price = params['apply_price']
        period = params['period']
        type = params['type']

        # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)

        # check apply price 
        if apply_price.lower() == 'open': use_data = ohlc_data['Open'][-period:]
        elif apply_price.lower() == 'close': use_data = ohlc_data['Close'][-period:]
        elif apply_price.lower() == 'high': use_data = ohlc_data['High'][-period:]
        elif apply_price.lower() == 'low': use_data = ohlc_data['Low'][-period:]
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

        # check if market close
        if 'last_seconds' in symbols_data[symbol]:
            last_seconds = symbols_data[symbol]['last_seconds']
        else : last_seconds = use_data[-1:].index.values[0]

        return { "timeframe": tf, "value": ta_value, "signal": signal, "datetime": last_seconds, "type": "trend"}
    
    except Exception as e :
        print("MA calculation error on > ", e)


def MACD(symbol, tf, params): # apply_price, fastperiod, slowperiod, signalperiod

    try: 
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0

        # get data for calculate
        apply_price = params['apply_price']
        fast_period, slow_period, signal_period = params['fastperiod'], params['slowperiod'], params['signalperiod']

        # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)

        # check apply price 
        if apply_price.lower() == 'open': use_data = ohlc_data['Open']
        elif apply_price.lower() == 'close': use_data = ohlc_data['Close']
        elif apply_price.lower() == 'high': use_data = ohlc_data['High']
        elif apply_price.lower() == 'low': use_data = ohlc_data['Low']

        res_ta = ta.trend.MACD(use_data, window_fast=fast_period, window_slow=slow_period ,window_sign=signal_period) # signal line is base and macd line will crossover
        macd_line, signal_line = round(res_ta.macd()[-1:].values[0], decimal_dict[symbol]), round(res_ta.macd_signal()[-1:].values[0], decimal_dict[symbol])

        if macd_line > signal_line:
            signal, arrow_type = "BUY", "arrow-up"
        elif macd_line < signal_line:
            signal, arrow_type = "SELL", "arrow-down"
        else:
            signal, arrow_type = "NEUTRAL", "non-arrow"

        # check if market close
        if 'last_seconds' in symbols_data[symbol]:
            last_seconds = symbols_data[symbol]['last_seconds']
        else : last_seconds = use_data[-1:].index.values[0]

        return { "timeframe": tf, "arrowtype": arrow_type, "value": macd_line, "signal": signal, "datetime": last_seconds, "type": "trend"}

    except Exception as e :
        print("MACD calculation error on > ", e)


def PSAR(symbol, tf, params): # step, max_step

    try: 
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0

        # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)

        # get data for calculate
        step, max_step = params['step'], params['max_step']
        high, low, close = ohlc_data['High'], ohlc_data['Low'], ohlc_data['Close']

        res_ta = ta.trend.PSARIndicator(high, low, close, step=float(step), max_step=float(max_step))

        ta_value = round(res_ta.psar()[-1:].values[0], decimal_dict[symbol])
        tick_value = round(ohlc_data['Close'][-1:].values[0], decimal_dict[symbol])

        if tick_value > ta_value: signal = "BUY"
        elif tick_value < ta_value: signal = "SELL"
        else: signal = "NEUTRAL"

        # check if market close
        if 'last_seconds' in symbols_data[symbol]:
            last_seconds = symbols_data[symbol]['last_seconds']
        else : last_seconds = ohlc_data[-1:].index.values[0]

        return { "timeframe": tf, "value": ta_value, "signal": signal, "datetime": last_seconds, "type": "trend"}
    
    except Exception as e :
        print("PSAR calculation error on > ", e)


## ------------------ MOMENTUM INDICATORS ------------------


def RSI(symbol, tf, params): # apply_price, period, overbought, oversold

    try: 
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0
    
        # get data for calculate
        apply_price, period = params['apply_price'], params['period']
        overbought, oversold = params['overbought'], params['oversold']

         # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)

        # check apply price 
        if apply_price.lower() == 'open': use_data = ohlc_data['Open'][-period:]
        elif apply_price.lower() == 'close': use_data = ohlc_data['Close'][-period:]
        elif apply_price.lower() == 'high': use_data = ohlc_data['High'][-period:]
        elif apply_price.lower() == 'low': use_data = ohlc_data['Low'][-period:]

        res_ta  = ta.momentum.RSIIndicator(use_data, window=period).rsi()
        ta_value = round(res_ta[-1:].values[0], 2)

        if ta_value > overbought: signal = "OVERBOUGHT"
        elif ta_value < oversold: signal = "OVERSOLD"
        else: signal = "NEUTRAL"

        # check if market close
        if 'last_seconds' in symbols_data[symbol]:
            last_seconds = symbols_data[symbol]['last_seconds']
        else : last_seconds = use_data[-1:].index.values[0]

        return { "timeframe": tf, "value": ta_value, "signal": signal, "datetime": last_seconds, "type": "momentum"}

    except Exception as e :
        print("RSI calculation error on > ", e)


def CCI(symbol, tf, params): # period, overbought, oversold

    try: 
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0

        # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)

        # get data for calculate
        period = params['period']
        overbought, oversold = params['overbought'], params['oversold']
        high, low, close = ohlc_data['High'], ohlc_data['Low'], ohlc_data['Close']

        res_ta = ta.trend.CCIIndicator(high, low, close, window=int(period), constant=float(0.015))
        ta_value = round(res_ta.cci()[-1:].values[0], 2)  

        if ta_value > overbought: signal = "OVERBOUGHT"
        elif ta_value < oversold: signal = "OVERSOLD"
        else: signal = "NEUTRAL"

        # check if market close
        if 'last_seconds' in symbols_data[symbol]:
            last_seconds = symbols_data[symbol]['last_seconds']
        else : last_seconds = ohlc_data[-1:].index.values[0]

        return { "timeframe": tf, "value": ta_value, "signal": signal, "datetime": last_seconds, "type": "momentum"}

    except Exception as e :
        print("CCI calculation error on > ", e)


def STOCH(symbol, tf, params): # period, sma_period, overbought, oversold

    try: 
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0

        # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)

        # get data for calculate
        period, sma_period = params['period'], params['sma_period']
        overbought, oversold = params['overbought'], params['oversold']
        high, low, close = ohlc_data['High'], ohlc_data['Low'], ohlc_data['Close']

        res_ta = ta.momentum.StochasticOscillator(high, low, close, window=int(period), smooth_window=int(sma_period))   
        ta_value, ta_signal = round(res_ta.stoch()[-1:].values[0], 2), round(res_ta.stoch_signal()[-1:].values[0], 2)

        if ta_signal > overbought: signal = "OVERBOUGHT"
        elif ta_signal < oversold: signal = "OVERSOLD"
        else: signal = "NEUTRAL"

        if ta_signal > ta_value: arrow_type = "arrow-up"
        elif ta_signal < ta_value: arrow_type = "arrow-down"
        else: arrow_type = "non-arrow"

        # check if market close
        if 'last_seconds' in symbols_data[symbol]:
            last_seconds = symbols_data[symbol]['last_seconds']
        else : last_seconds = ohlc_data[-1:].index.values[0]

        return { "timeframe": tf, "arrowtype": arrow_type, "value": ta_signal, "signal": signal, "datetime": last_seconds, "type": "momentum"}

    except Exception as e :
        print("STOCH calculation error on > ", e)


def WPCR(symbol, tf, params): # period, overbought, oversold

    try: 
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0

        # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)

        # get data for calculate
        period = params['period']
        overbought, oversold = params['overbought'], params['oversold']
        high, low, close = ohlc_data['High'], ohlc_data['Low'], ohlc_data['Close']

        res_ta = ta.momentum.WilliamsRIndicator(high, low, close, lbp=int(period))
        ta_value = round(res_ta.williams_r()[-1:].values[0], decimal_dict[symbol])

        if ta_value > overbought: signal = "OVERBOUGHT"
        elif ta_value < oversold: signal = "OVERSOLD"
        else: signal = "NEUTRAL"

        # check if market close
        if 'last_seconds' in symbols_data[symbol]:
            last_seconds = symbols_data[symbol]['last_seconds']
        else : last_seconds = ohlc_data[-1:].index.values[0]

        return { "timeframe": tf, "value": ta_value, "signal": signal, "datetime": last_seconds, "type": "momentum"}

    except Exception as e :
        print("W%R calculation error on > ", e)


## ------------------ OTHER INDICATORS ------------------

def Strength():

    try:
        def multiple_replacer(*key_values):
            replace_dict = dict(key_values)
            replacement_function = lambda match: replace_dict[match.group(0)]
            pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
            return lambda string: pattern.sub(replacement_function, string)
                
        def multiple_replace(string, *key_values):
            return multiple_replacer(*key_values)(string)


        #get the site and parse the html
        x = r.get("http://www.livecharts.co.uk/currency-strength.php").text

        cur = bs(x, "html5lib")

        #Find all Currency by id
        pairs = [c for c in cur.find_all(id="map-innercontainer-symbol")]

        #To be excluded
        y = str('style="background-image:none"')

        #Finding the current level we need to loop through all levels
        levels = [
            'map-innercontainer-strong3',
            'map-innercontainer-strong2',
            'map-innercontainer-strong1',
            'map-innercontainer-weak1',
            'map-innercontainer-weak2',
            'map-innercontainer-weak3',
        ]

        lv = [l for l in cur.find_all(id=levels)]

        mine = lv

        replacements = (u"div", u""),(u'id="map-innercontainer-',u""),(u"<",""),(u'style="background-image:none"',u""),(u'">',""),(u"/",u""),(u"",u""),(u">",u""),(u'"',u"")

        strength_dict = dict()
        for i in range(10):
            pair_strength = multiple_replace(str(mine[(i)*6:(i+1)*6]), *replacements)
            pair_strength = [st.strip() for st in pair_strength.replace(u'\xa0', u' ').replace('[', '').replace(']', '').split(",")]
            # get strength number 
            num_strength = 7 - len([lowest for lowest in pair_strength if lowest == "weak3"])

            strength_dict[pairs[i].text[:3]] = num_strength

        return strength_dict

    except Exception as e :
        print("Strength calculation error on > ", e)

def Volatility(symbol, params): # time_interval

    MAX_RANGE = 24

    try: 
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0

        # get data for calculate
        time_interval = params['time_interval']

        # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, time_interval)

        # get volatility
        d = ohlc_data[-(MAX_RANGE+1):]['Close']
        d_pips = abs((d - d.shift(1))[-MAX_RANGE:] * 10 ** (decimal_dict[symbol] - 1))

        # def format(time):
        #     return dt.datetime.utcfromtimestamp(math.floor(time / 1000)).strftime("%H:%M")

        # d_pips.index = d_pips.index.map(format)

        X = d_pips.index.values.tolist()
        Y = list(map(lambda v: round(v, 1), d_pips.tolist()))

        return { "X": X, "Y": Y } 

    except Exception as e :
        print("Volatility calculation error on > ", e)


def Distribution(symbol, params):

    INTERVAL = 200

    try: 
        if symbol not in symbols_data or symbols_data[symbol][default_name] == None: return 0

        # get data for calculate
        tf, period = params['timeframe'], params['period']

        # get data and convert to specific timeframe
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)

        # get distribution
        dis_data = ((ohlc_data['Close'] * 10 ** 5).apply(math.floor) - (ohlc_data['Close'] * 10 ** 5).apply(math.floor) % INTERVAL + math.floor(INTERVAL / 2)).value_counts().sort_index()

        X = dis_data.tolist()
        Y = list(map(lambda p: p / 10 ** decimal_dict[symbol], dis_data.index.tolist()))
        X.reverse()
        Y.reverse()

        return { "X": X, "Y": Y } 

    except Exception as e :
        print("Distribution calculation error on > ", e)

    











    
