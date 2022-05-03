from libs.db_connect import mongo_connect
import math
import datetime as dt
import pandas as pd
import json
from libs.convert import ohlc_to_ohlc

DB = mongo_connect() # mongodb connect 
SAVE_DATA = False # state to disable and enable save data to DB

save_seconds = 3600 # define the every time for save data to db
symbols_data = dict()
default_tf = "5Min"
default_name = "ohlc_m5"

def convert_ohlc(tick, tf="5Min"):
    
    ohlc_m5 = tick.resample(tf).ohlc()
    ohlc_m5.rename(columns = {'open':'Open', 'high':'High', 'low': 'Low', 'close': 'Close'}, inplace = True)

    return ohlc_m5

def get_ohlc(symbol, con): # function for initial data of each symbol

    db_data = DB['history'].find_one({ "Symbol": symbol })
    db_df = pd.DataFrame(json.loads(db_data['OHLC_M5']))
    db_df.index = db_df['Datetime']
    db_df = db_df.drop("Datetime", axis=1)

    # get missing data 
    db_last_date = math.floor(db_df[-1:].index[0] / 1000)
    db_last_date = db_last_date - db_last_date % 86400
    start = dt.datetime.utcfromtimestamp(db_last_date)
    current_date = math.floor(dt.datetime.now(dt.timezone.utc).timestamp())
    current_date = (current_date - current_date % 86400) + 86400
    end = dt.datetime.utcfromtimestamp(current_date)

    get_data = con.get_candles(symbol, period='m5', start=start, end=end)[['bidopen','bidclose','bidhigh','bidlow']]
    get_data.rename(columns = {'bidopen':'Open', 'bidhigh':'High', 'bidlow': 'Low', 'bidclose': 'Close'}, inplace = True)

    get_data.index = list(map(lambda time: math.floor(time / 10 ** 6), get_data.index.view(int)))

    # merge 2 dataframe 
    ohlc_m5 = pd.concat([db_df, get_data])
    ohlc_m5 = ohlc_m5[~ohlc_m5.index.duplicated(keep='last')]

    # store data in global variable
    global symbols_data
    ohlc_m5['Datetime'] = ohlc_m5.index
    ohlc_m5 = ohlc_m5.reset_index(drop=True)
    ohlc_m5_json = json.loads(ohlc_m5.to_json(orient='records'))
    symbols_data[symbol]['ohlc_m5'] = ohlc_m5_json

    print("Initial ", symbol, " seccess")

def manage_ohlc(tick, symbol, con, status):

     # check symbol is a new symbol to get ohlc or not
    global symbols_data, save_seconds
    if symbol not in symbols_data:
        symbols_data[symbol] = dict()
        symbols_data[symbol]['first_finished'] = False # check get first data has finished
        symbols_data[symbol]['ohlc_m5'] = None # initial ohlc 5 minute data of each symbol
        symbols_data[symbol]['save_time'] = 0 # recent save time
        symbols_data[symbol]['midnight_time'] = 0 # initial midnight time

    # check first initial data has finished
    if symbols_data[symbol]['first_finished'] == False:
        symbols_data[symbol]['first_finished'] = True
        get_ohlc(symbol, con)
    
    # manage tick data on OHLC 5 minutes
    recent_ohlc_m5 = symbols_data[symbol]['ohlc_m5']
    if recent_ohlc_m5 != None and status != "initial":

        # get checking time to handle if new save time occur
        last_seconds = math.floor(int(tick[-1:].index.values[0]) / (10 ** 9))
        save_time = last_seconds - last_seconds % save_seconds  
        what_day = last_seconds - last_seconds % 86400

        # convert tick to 1 minutes timeframe
        ohlc_m5 = convert_ohlc(tick)
        ohlc_m5['Datetime'] = ohlc_m5.index
        ohlc_m5 = ohlc_m5.reset_index(drop=True)

        last_steam = json.loads(ohlc_m5[-1:].to_json(orient='records'))[0] # tick steaming 
        last_recent = recent_ohlc_m5[len(recent_ohlc_m5) - 1] # lastest data store

        # update the lastest tick to global variable data 
        if last_steam['Datetime'] == last_recent['Datetime'] :
            recent_ohlc_m5[len(recent_ohlc_m5) - 1]['High'] = max(last_recent['High'], last_steam['High'])
            recent_ohlc_m5[len(recent_ohlc_m5) - 1]['Low'] = min(last_recent['Low'], last_steam['Low'])
            recent_ohlc_m5[len(recent_ohlc_m5) - 1]['Close'] = last_steam['Close']
        else :
            recent_ohlc_m5.append(last_steam.copy())

        symbols_data[symbol]['ohlc_m5'] = recent_ohlc_m5

        # set last steam tick to current time
        symbols_data[symbol]['last_seconds'] = last_seconds * 1000

        # save data to DB
        if SAVE_DATA and symbols_data[symbol]['save_time'] != save_time:

             # update save time
            symbols_data[symbol]['save_time'] = save_time

            save_data(symbol, recent_ohlc_m5, last_seconds)

        if symbols_data[symbol]['midnight_time'] != what_day:

            symbols_data[symbol]['midnight_time'] = what_day

            ohlc_1D = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, "1D")

            symbols_data[symbol]['lastest_close'] = ohlc_1D['Close'][-2:-1].values[0]

        if 'lastest_close' not in symbols_data[symbol]: # to fix bug on initial data not complete yet

            symbols_data[symbol]['lastest_close'] = last_steam['Close']

        return {"Symbol": symbol, "Tick": last_steam['Close'], "Datetime": symbols_data[symbol]['last_seconds'], "Lastest": symbols_data[symbol]['lastest_close']}
    

def save_data(symbol, data, last_seconds):

    try :
        # drop last save data in db
        del_res = DB['history'].delete_many({"Symbol": symbol})

        if del_res.acknowledged == True:
                    
            DB['history'].insert_one({"Symbol": symbol, "OHLC_M5":  json.dumps(data)})
            print(symbol, " was saved at timestamp > ", last_seconds * 1000)

    except: 
        # some error on save to db
        print("Can't update data of ", symbol ," to database")