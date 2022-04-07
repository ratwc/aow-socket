# get data from fxcm server

# function to subscribe data.
def sub_tick(con, symbol, get_tick): # connect, symbol
    # unsubscribe symbol 
    con.unsubscribe_market_data(symbol)

    # subscribe symbol
    con.subscribe_market_data(symbol, (get_tick, ))

# get instruments pair only 
def get_instruments(con):
    # get all instruments
    instruments = con.get_instruments()
    # get pair only
    return [symbol for symbol in instruments if "/" in symbol]



    
