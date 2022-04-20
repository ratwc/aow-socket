from data.db_connect import mongo_connect
import math
import json
import datetime as dt

db = mongo_connect()

def convert_ohlc(tick, tf="1Min"):
    
    ohlc_m1 = tick.resample(tf).ohlc()
    ohlc_m1.rename(columns = {'open':'Open', 'high':'High', 'low': 'Low', 'close': 'Close'}, inplace = True)

    return ohlc_m1

save_seconds = 300 # define the every time for save data to db
symbols_data = dict() # dict for save the data of each symbol (save time and last ohlc 1m)

def manage_tick(tick, symbol, con):
    
    # check if key of symbol exist or not then create a new one
    global symbols_data
    if symbol not in symbols_data:
        symbols_data[symbol] = dict()
        symbols_data[symbol]['old_save_time'] = 0
        symbols_data[symbol]['last_ohlc_m1'] = []
    # get symbol data
    old_save_time = symbols_data[symbol]['old_save_time']
    last_ohlc_m1 = symbols_data[symbol]['last_ohlc_m1']
    
    # get checking time to handle if new save time occur
    last_seconds = math.floor(int(tick[-1:].index.values[0]) / (10 ** 9))
    save_time = last_seconds - last_seconds % save_seconds
    
    # convert current tick to 1 minute ohlc 
    ohlc_m1 = convert_ohlc(tick)
    ohlc_m1['Datetime'] = ohlc_m1.index
    ohlc_m1 = ohlc_m1.reset_index(drop=True)
    
    # handle data every save_secondes minutes
    if old_save_time != save_time:
    
        # check if last_ohlc_m1 is empty then call the historical data to fill it
        if len(last_ohlc_m1) == 0:
            db_symbol = db['history'].find_one({"Symbol": symbol}) # get 1 minute ohlc from db
            
            if db_symbol != None:
                db_ohlc_m1 = json.loads(db_symbol['OHLC_m1'])
                
                # fill the missing time
                last_db_time = math.floor(db_ohlc_m1[len(db_ohlc_m1) - 1]['Datetime'] / 1000)
                
                curr_time = last_seconds - last_seconds % 60 
                
                # *** it have a limit to call hitorical data
                miss_start = dt.datetime.utcfromtimestamp((last_db_time - last_db_time % 86400))
                miss_end = dt.datetime.utcfromtimestamp((curr_time - curr_time % 86400) + 86400)
                missing_data_df = con.get_candles(symbol, period='m1', \
                                               start=miss_start, end=miss_end)[['bidopen','bidclose','bidhigh','bidlow']]
                missing_data_df.rename(columns = {'bidopen':'Open', 'bidhigh':'High', \
                                                  'bidlow': 'Low', 'bidclose': 'Close'}, \
                                       inplace = True)
                
                missing_data_df['Datetime'] = missing_data_df.index
                missing_data_df = missing_data_df.reset_index(drop=True)
                
                last_ohlc_m1 = json.loads(missing_data_df.to_json(orient='records'))
            
            else :
                last_ohlc_m1 = json.loads(ohlc_m1.to_json(orient='records'))
                
        # drop last save data in db
        db['history'].delete_many({"Symbol": symbol})
        db['history'].insert_one({"Symbol": symbol, "OHLC_m1":  json.dumps(last_ohlc_m1)})
        
        # set new save time
        old_save_time = save_time 
        
    # to update last price every tick
    last_steam = json.loads(ohlc_m1[-1:].to_json(orient='records'))[0] # tick steaming 
    last_recent = last_ohlc_m1[len(last_ohlc_m1) - 1] # lastest data store

    if last_steam['Datetime'] == last_recent['Datetime'] :
        last_ohlc_m1[len(last_ohlc_m1) - 1]['High'] = max(last_recent['High'], last_steam['High'])
        last_ohlc_m1[len(last_ohlc_m1) - 1]['Low'] = min(last_recent['Low'], last_steam['Low'])
        last_ohlc_m1[len(last_ohlc_m1) - 1]['Close'] = last_steam['Close']
    else :
        last_ohlc_m1.append(last_steam.copy())

    # transfrom return data with last value that a seconds
    last_steam['Datetime'] = last_seconds * 1000
    
    # save data to symbol data
    symbols_data[symbol]['old_save_time'] = old_save_time
    symbols_data[symbol]['last_ohlc_m1'] = last_ohlc_m1
    
    return last_steam, last_ohlc_m1

