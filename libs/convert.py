# library to convert everything in my project 
import copy
import math
import pandas as pd
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
            return pd.DataFrame(data).set_index('Datetime')

        # copy the data to new variable to prevent data change by reference
        ohlc_data = copy.deepcopy(data)
        # sort with accending time 
        ohlc_data = sorted(ohlc_data, key=lambda d: d['Datetime'], reverse=False) 
        # change time from milliseconds to seconds 
        for d in ohlc_data: d['Datetime'] = math.floor(d['Datetime'] / 1000)

        tf_seconds = timeframe[to_tf] * 60

        for d in ohlc_data: d['Datetime'] = d['Datetime'] - d['Datetime'] % tf_seconds

        # find the interval to time
        start_list = [0]
        [start_list.append(idx + 1) for idx in range(len(ohlc_data[:-1])) if ohlc_data[idx]['Datetime'] != ohlc_data[idx + 1]['Datetime']]
        start_list.append(len(ohlc_data))

        new_ohlc = []
        def form_data(idx):

            temp_dict = {}
            tf_data = ohlc_data[start_list[idx]: start_list[idx + 1]]

            # add data to dict
            temp_dict['Datetime'] = tf_data[0]['Datetime'] * 1000
            temp_dict['Open'] = tf_data[0]['Open']
            temp_dict['High'] = max(tf_data, key=lambda d:d['High'])['High']
            temp_dict['Low'] = min(tf_data, key=lambda d:d['Low'])['Low']
            temp_dict['Close'] = tf_data[len(tf_data) - 1]['Close']

            new_ohlc.append(temp_dict)

        list(map(form_data, range(len(start_list[:-1]))))

        return pd.DataFrame(new_ohlc).set_index('Datetime')

    except: 

        print("Some Error on convert ohlc")
