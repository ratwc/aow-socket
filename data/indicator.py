# get all technical indicator
import ta

def moving_average(tick, tf, apply, type, period): # tick data, timeframe, apply price, type of MA, window(period)
    # resample to ohlc
    use_tick = tick['Ask'].resample(tf).ohlc() 
    # check apply price 
    if apply.lower() == 'open': use_tick = use_tick['open']
    elif apply.lower() == 'close': use_tick = use_tick['close']
    elif apply.lower() == 'high': use_tick = use_tick['high']
    elif apply.lower() == 'low': use_tick = use_tick['low']
    # type of MA
    if type.lower() == "simple": return ta.trend.SMAIndicator(use_tick, period).sma_indicator()
    elif type.lower() == "exponential": return ta.trend.EMAIndicator(use_tick, period).ema_indicator()
    elif type.lower() == "weighted": return ta.trend.WMAIndicator(use_tick, period).wma()
