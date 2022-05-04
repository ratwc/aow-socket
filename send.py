from curses.ascii import RS
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
    socketio.emit("ohlc_data", json.dumps(get_ohlc(symbol, tf)))

@socketio.on("request_current_ohlc")
def send_current(params):
    symbol, tf = params['symbol'], params['timeframe']
    socketio.emit("current_ohlc", json.dumps(json.loads(get_ohlc(symbol, tf))[-1:][0]))


# ---------- Send Indicator Signal ----------
    
from data.indicator import *
from data.summary import summary
@socketio.on("request_indicators")
def send_indicators(indicators_config):
    indicators, symbol, timeframes  = indicators_config['indicators'], indicators_config['symbol'], indicators_config['timeframes']
    indicators_signal = {}
    # calculate each indicator
    has_error = False
    for indicator in indicators:
        try:
            # get variable of each indicator
            model = indicator['indicator_model']
            params = indicator['parameters']
            # signal in each indicator 
            temp_signals = []
            for tf in timeframes:
                # space to add more indicator model calculation
                if model == "MA": temp_signals.append(MA(symbol, tf, params))
                if model == "MACD": temp_signals.append(MACD(symbol, tf, params))
                if model == "RSI": temp_signals.append(RSI(symbol, tf, params))


            # save signal to dict
            indicators_signal[indicator['indicator_id']] = temp_signals
            if 0 in temp_signals:
                has_error = True
        except:
            print("Can not calculate some indicator because invalid model or parameters missing!")

    if has_error :
        socketio.emit("indicators", json.dumps("ERROR"))
    else :
        return_indicators = {"indicators_signal": indicators_signal, "summary": summary(indicators_signal)}
        socketio.emit("indicators", json.dumps(return_indicators))

# ----------- Send NEWS data -------------
from data.news import *
@socketio.on("request_forex_news")
def send_forex_news():
    socketio.emit("forex_news", json.dumps(get_forex_news()))

# @app.route('/get_economic_calendar', methods=['GET'])
@socketio.on("get_economic_calendar")
def send_economic_calendar(symbol):
    socketio.emit("economic_calendar", (get_economic_calendar(symbol['symbol'])))

# ----------- Send Instruments -----------
@socketio.on("request_instruments")
def instruments():
    from data.getdata import get_instruments
    all_pairs = json.dumps(get_instruments(con))
    socketio.emit("instruments", json.dumps(all_pairs))

# ------------ Initial Price ------------
from data.initial import initial_price
@socketio.on("request_initial_price")
def send_initial_price(symbol):
    tick = initial_price(symbol, con)
    if bool(tick) :
        socketio.emit("tick_data", json.dumps(tick))
