# get data from fxcm server

# function to subscribe data.
def sub_tick(con, symbol, get_tick): # connect, symbol

    try:
        # unsubscribe symbol 
        con.unsubscribe_market_data(symbol)

        # subscribe symbol
        con.subscribe_market_data(symbol, (get_tick, ))
    except:
        
        # to prevent symbol error
        print("Can't subscribe ", symbol," symbol with some error from server of invalid symbol")
    

def unsub_all(con):
    # unsubscribe all symbol
    for sub_symbol in con.get_subscribed_symbols() :
        con.unsubscribe_market_data(sub_symbol)

# get instruments pair only 
def get_instruments(con):

    # # get all instruments
    # instruments = con.get_instruments()

    # # get forex pair only
    # pairs = [symbol for symbol in instruments if "/" in symbol]

    # fix_pairs = ['EUR', 'JPY', 'USD', 'CHF', 'CAD', 'GBP', 'AUD', 'NZD', 'XAU', 'XAG']

    # return list(set.intersection(set([pair for fix in fix_pairs for pair in pairs if fix in pair.split("/")[0]]) \
    #              , set([pair for fix in fix_pairs for pair in pairs if fix in pair.split("/")[1]])))

    return ['EUR/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF' ,'USD/CAD' ,'AUD/USD', 'NZD/USD', 'XAU/USD']



    
