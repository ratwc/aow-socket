import math
from data.tick import manage_ohlc

def initial_ohlc(symbol, con):

    manage_ohlc(None, symbol, con, "initial")


def initial_price(symbol, con):

    try: 
        if con != None:
            lastest_close = con.get_candles(symbol, period='H1', number=1)
            lastest_datetime = math.floor(lastest_close['bidclose'].index.view(int) / 10 ** 6)
            lastest_price = lastest_close['bidclose'].values[0]

            return {"Symbol": symbol, "Tick": lastest_price, "Datetime": lastest_datetime, "Lastest": lastest_price}
    
    except Exception as e :

        print("Initial price error on symbol: ", symbol, " with error: ", e)
