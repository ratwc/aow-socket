from socket import socket
from flask import Flask, request
from flask_socketio import SocketIO, send, emit
import json
# import socket and connect from app.py
try:
    from __main__ import socketio, con, app
except ImportError:
    from app import socketio, con, app

from data.tick import symbols_data, default_name, default_tf

# ----------- Send OHLC Data -----------
def get_ohlc(symbol, tf):
    try: 
        ohlc_data = ohlc_to_ohlc(symbols_data[symbol][default_name], default_tf, tf)
        ohlc_data['Datetime'] = ohlc_data.index
        ohlc_data = ohlc_data.reset_index(drop=True)
        ohlc_data_json = ohlc_data.to_json(orient='records')
        return ohlc_data_json
    except: 
        print("Symbol data not available!")

from libs.convert import ohlc_to_ohlc
@socketio.on("request_ohlc_data")
def send_ohlc(params):
    symbol, tf = params['symbol'], params['timeframe']
    socketio.emit("ohlc_data", get_ohlc(symbol, tf))

@socketio.on("request_current_ohlc")
def send_current(params):
    symbol, tf = params['symbol'], params['timeframe']
    socketio.emit("current_ohlc", json.loads(get_ohlc(symbol, tf))[-1:][0])


# ---------- Send Indicator Signal ----------
    
from data.indicator import *
@socketio.on("request_indicators")
def send_indicators(indicators_config):
    indicators, symbol, timeframes  = indicators_config['indicators'], indicators_config['symbol'], indicators_config['timeframes']
    return_indicators = {}
    # calculate each indicator
    for indicator in indicators:
        # get variable of each indicator
        model = indicator['indicator_model']
        params = indicator['parameters']
        # signal in each indicator 
        temp_signals = []
        for tf in timeframes:
            # space to add more indicator model calculation
            if model == "MA": temp_signals.append(MA(symbol, tf, params))


        # save signal to dict
        return_indicators[indicator['indicator_id']] = temp_signals

    print(return_indicators)
    socketio.emit("indicators", return_indicators)

# ----------- Send NEWS data -------------
from data.news import *
@socketio.on("request_forex_news")
def send_forex_news():
    socketio.emit("forex_news", get_forex_news())

# @app.route('/get_economic_calendar', methods=['GET'])
@socketio.on("get_economic_calendar")
def send_economic_calendar(symbol):
    socketio.emit("economic_calendar", get_economic_calendar(symbol['symbol']))

# ----------- Send Instruments -----------
@socketio.on("request_instruments")
def instruments():
    from data.getdata import get_instruments
    all_pairs = json.dumps(get_instruments(con))
    socketio.emit("instruments", all_pairs)

# ------------ Initial Price ------------
from data.initial import initial_price
@socketio.on("request_initial_price")
def send_initial_price(symbol):
    tick = initial_price(symbol, con)
    if bool(tick) :
        socketio.emit("tick_data", tick)
