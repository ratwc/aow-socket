# get all technical indicator
from libs.convert import ohlc_to_ohlc
import ta
from data.tick import symbols_data, default_name, default_tf

def MA(symbol, tf, params): # tick data, timeframe, apply price, type of MA, window(period)

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
        ta_value = round(res_ta[-1:].values[0], 5)
        tick_value = round(use_data[-1:].values[0], 5)
        if tick_value > ta_value: signal = "BUY"
        elif tick_value < ta_value: signal = "SELL"
        else: signal = "NEUTRAL"

        return { "timeframe": tf, "value": ta_value, "signal": signal, "datetime": symbols_data[symbol]['last_seconds']}
    
    except :
        print("Some Error on MA indicator calculation")