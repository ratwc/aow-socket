import datetime as dt
import json
from bson.objectid import ObjectId
from libs.db_connect import mongo_connect
import pandas as pd
from libs.backtest_libs import *

MAX_LAST_CANDLES = 100
DB = mongo_connect() # mongodb connect 

"""
    page_id (string)
    start_date (milliseconds in timestamp)
    end_date (milliseconds in timestamp)
    per_buy (int 0 - 100)
    per_sell (int 0 - 100)
"""

def backtest_calculation(page_id, start_date, end_date, per_buy, per_sell, con, socketio): # count is for counting the progress 

    socketio.emit("backtest", json.dumps({"status": "success", "message": "Backtest start", "status_code": 0}) )

    # --- CALL HISTRORICAL DATA ---

    try: 

        start_date = start_date - start_date % 86400

        page = DB['page'].find_one( {"_id": ObjectId(page_id)} )

        symbol = page['currency_pair']
        lastest_time = math.floor(dt.datetime.now().timestamp())

        for tf in page['timeframe']:

            tf_time = MAX_LAST_CANDLES * timeframe[tf] * 60
            before_time = start_date - tf_time
            before_time = before_time - before_time % 86400
            lastest_time = min(lastest_time, before_time)

        data_range = list(range(lastest_time, end_date, 2592000))
        data_range.append(end_date)

        hist_df = pd.DataFrame()
        for idx in range(len(data_range) - 1):
            # get start date and end date
            start = dt.datetime.utcfromtimestamp(data_range[idx])
            end = dt.datetime.utcfromtimestamp(data_range[idx + 1])

            # get historical data
            hist_data = con.get_candles(symbol, period="m5", start=start, end=end)[['bidopen','bidclose','bidhigh','bidlow']]

            # merge data to dataframe
            hist_df = pd.concat([hist_df, hist_data])
            hist_df = hist_df[~hist_df.index.duplicated(keep='last')]

        hist_df.rename(columns = {'bidopen':'Open', 'bidhigh':'High', 'bidlow': 'Low', 'bidclose': 'Close'}, inplace = True)
        start_index = list(map(lambda t: math.floor(t) >= start_date, (hist_df.index.view(int) / 10 ** 9))).count(False) + 1

        hist_df['Datetime'] = hist_df.index
        hist_df = hist_df.reset_index(drop=True)
        ohlc_data = json.loads(hist_df.to_json(orient='records'))
        ohlc_df = pd.DataFrame(ohlc_data).set_index('Datetime')

        # print("Success when get histrorical data")
        socketio.emit("backtest", json.dumps({"status": "success", "message": "Get histrorical data success", "status_code": 1}) )
    
    except Exception as e:
        print("Fail when get histrorical data > ", e)
        return {"status": "fail", "message": "Get histrorical data fail!", "status_code": -1}

    # --- CALL BACKTEST LOGS ---
    
    try:

        indicators = list(DB['indicator'].find( { "page_id": ObjectId(page_id) } ))

        all_ohlc_data = {}
        for tf in page['timeframe']:
            all_ohlc_data[tf] = ohlc_to_ohlc(ohlc_df, "5Min", tf)

        timeframs = page['timeframe']

        # calculate progress
        n_tasks = len(range(start_index, len(ohlc_data)))

        def calculate_data(idx, count, progress):

            indicators_signal = {}
            time = ohlc_data[idx-1:idx][0]['Datetime'] # current time step
            # calculate each indicator
            for indicator in indicators:
                try:
                    # get variable of each indicator
                    model, params, temp_signals = indicator['indicator_model'], indicator['parameters'], []

                    # signal in each indicator 
                    for tf in timeframs:
                
                        tf_df = all_ohlc_data[tf][all_ohlc_data[tf].index <= time][-MAX_LAST_CANDLES:]

                        diff_time = ohlc_df[(ohlc_df.index <= time) & (ohlc_df.index >= tf_df[-1:].index[0])]

                        diff_converted = ohlc_to_ohlc(diff_time, "5Min", tf)
                        tf_df[-1:] = diff_converted[:1]

                        # space to add more indicator model calculation
                        # ------- THREND -------
                        if model == "MA": temp_signals.append(MA(tf_df, tf, params, symbol))
                        elif model == "MACD": temp_signals.append(MACD(tf_df, tf, params, symbol))
                        elif model == "PSAR": temp_signals.append(PSAR(tf_df, tf, params, symbol))
                        # # ------- MOMENTUM -------
                        elif model == "RSI": temp_signals.append(RSI(tf_df, tf, params, symbol))
                        elif model == "CCI": temp_signals.append(CCI(tf_df, tf, params, symbol))
                        elif model == "STOCH": temp_signals.append(STOCH(tf_df, tf, params, symbol))
                        elif model == "W%R": temp_signals.append(WPCR(tf_df, tf, params, symbol))

                    # save signal to dict
                    indicators_signal[indicator['indicator_id']] = temp_signals

                except:
                    print("Can not calculate some indicator because invalid model or parameters missing!")

            result = summary(indicators_signal)['summary']
            result.update(ohlc_data[idx-1:idx][0])

            count += 1
            curr_progress = math.floor(count * 100 / n_tasks)

            if curr_progress != progress:
                socketio.emit("backtest", json.dumps({"status": "success", "message": "Calculating backtest", "progress": curr_progress, "status_code": 2}) )

            return result, count, curr_progress

        count = 0
        progress = -1
        backtest_log = []
        for idx in range(start_index, len(ohlc_data)):
            result, count, progress = calculate_data(idx, count, progress)
            backtest_log.append(result)

        # print("Success when backtesting")
        socketio.emit("backtest", json.dumps({"status": "success", "message": "Calculate backtest success", "status_code": 3}) )
    
    except Exception as e:
        print("Fail when backtesting > ", e)
        return {"status": "fail", "message": "Calculate backtest fail!", "status_code": -1}

    # --- CALL BACKTEST ANALYTICS RESULT ---

    try: 

        backtest_result = []
        order = None
        for backtest in backtest_log:
            # intial state 
            if order == None and (backtest['BUY'] >= per_buy or backtest['SELL'] >= per_sell):
                start_datetime = backtest['Datetime']
                start_price = backtest['Close']
                high_price = backtest['High']
                low_price = backtest['Low']
                if backtest['BUY'] >= per_buy : order = "BUY"
                else: order = "SELL"

            # after first order start
            elif backtest['BUY'] >= per_buy and order == "SELL":
                backtest_result.append( { 
                    "Order": "SELL", 
                    "Datetime": start_datetime, 
                    "Price": start_price,
                    "MFE": low_price ,"MAE": high_price, 
                    "Volatility": round((backtest['Close'] - start_price) * 10 ** (decimal_dict[symbol] - 1), 2)
                } )
                # open new position 
                order = "BUY"
                start_datetime = backtest['Datetime']
                start_price = backtest['Close']
                high_price = backtest['High']
                low_price = backtest['Low']

            elif backtest['SELL'] >= per_sell and order == "BUY":
                backtest_result.append( { 
                    "Order": "BUY", 
                    "Datetime": start_datetime, 
                    "Price": start_price,
                    "MFE": high_price ,"MAE": low_price, 
                    "Volatility": round((backtest['Close'] - start_price) * 10 ** (decimal_dict[symbol] - 1), 2)
                } )
                # open new position 
                order = "SELL"
                start_datetime = backtest['Datetime']
                start_price = backtest['Close']
                start_price = backtest['Close']
                high_price = backtest['High']
                low_price = backtest['Low']

            if order == "BUY" or order == "SELL":
                high_price = max(backtest['High'], high_price)
                low_price = min(backtest['Low'], low_price)

        # print("Success when analyze data")
        socketio.emit("backtest", json.dumps({"status": "success", "message": "Analyze backtest success", "status_code": 4}) )

    except Exception as e:
        print("Fail when analyze data > ", e)
        return {"status": "fail", "message": "Analyze backtest fail!", "status_code": -1}

    return {"status": "success", "message": "Backtest success", "result": backtest_result, "symbol": symbol, "status_code": 5} 


