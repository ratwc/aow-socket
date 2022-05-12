from socket import socket
from flask import Flask, request
from flask_socketio import SocketIO, send, emit
import json
# import socket and connect from app.py
try:
    from __main__ import socketio, con, app, NpEncoder
except ImportError:
    from app import socketio, con, app, NpEncoder

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
    socketio.emit("ohlc_data", json.dumps(get_ohlc(symbol, tf), cls=NpEncoder))

@socketio.on("request_current_ohlc")
def send_current(params):
    symbol, tf = params['symbol'], params['timeframe']
    socketio.emit("current_ohlc", json.dumps(json.loads(get_ohlc(symbol, tf))[-1:][0], cls=NpEncoder))


# ---------- Send Indicator Signal ----------
    
from data.indicator import *
from data.summary import summary
@socketio.on("request_indicators")
def send_indicators(indicators_config):
    try:
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
                    # ------- THREND -------
                    if model == "MA": temp_signals.append(MA(symbol, tf, params))
                    elif model == "MACD": temp_signals.append(MACD(symbol, tf, params))
                    elif model == "PSAR": temp_signals.append(PSAR(symbol, tf, params))
                    # ------- MOMENTUM -------
                    elif model == "RSI": temp_signals.append(RSI(symbol, tf, params))
                    elif model == "CCI": temp_signals.append(CCI(symbol, tf, params))
                    elif model == "STOCH": temp_signals.append(STOCH(symbol, tf, params))
                    elif model == "W%R": temp_signals.append(WPCR(symbol, tf, params))

                # save signal to dict
                indicators_signal[indicator['indicator_id']] = temp_signals
                if 0 in temp_signals:
                    has_error = True
            except:
                print("Can not calculate some indicator because invalid model or parameters missing!")

        if has_error :
            socketio.emit("indicators", json.dumps("ERROR", cls=NpEncoder))
        else :
            return_indicators = {"indicators_signal": indicators_signal, "summary": summary(indicators_signal)}
            socketio.emit("indicators", json.dumps(return_indicators, cls=NpEncoder))
    except Exception as e:
        print("Indicator signals calculation error, with error code: ", e)
        socketio.emit("indicators", json.dumps("ERROR", cls=NpEncoder))

@socketio.on("request_onetime_indicators")
def send_onetime_indicators(indicators_config):
    try:
        indicators, symbol = indicators_config['indicators'], indicators_config['symbol']
        indicators_signal = {}
        # calculate each indicator
        for indicator in indicators:
            # get variable of each indicator
            model = indicator['indicator_model']
            params = indicator['parameters']
            # signal in each indicator 
            if model == "CURMETER": indicators_signal[indicator['indicator_id']] = Strength()
            if model == "VOLMETER": indicators_signal[indicator['indicator_id']] = Volatility(symbol, params)
            if model == "PRICEDIS": indicators_signal[indicator['indicator_id']] = Distribution(symbol, params)

        socketio.emit("onetime_indicators", json.dumps(indicators_signal, cls=NpEncoder))

    except Exception as e:
        print("Indicator signals calculation error, with error code: ", e)
        socketio.emit("indicators", json.dumps("ERROR", cls=NpEncoder))


# ----------- Send NEWS data -------------
from data.news import *
@socketio.on("request_forex_news")
def send_forex_news():
    socketio.emit("forex_news", json.dumps(get_forex_news(), cls=NpEncoder))

# @app.route('/get_economic_calendar', methods=['GET'])
@socketio.on("get_economic_calendar")
def send_economic_calendar(symbol):
    socketio.emit("economic_calendar", json.dumps(get_economic_calendar(symbol['symbol'])))

# ----------- Send Instruments -----------
@socketio.on("request_instruments")
def instruments():
    from data.getdata import get_instruments
    all_pairs = json.dumps(get_instruments(con))
    socketio.emit("instruments", json.dumps(all_pairs, cls=NpEncoder))

# ------------ Initial Price ------------
from data.initial import initial_price
@socketio.on("request_initial_price")
def send_initial_price(symbol):
    tick = initial_price(symbol, con)
    if bool(tick) :
        socketio.emit("tick_data", json.dumps(tick, cls=NpEncoder))

# ------------ Market Status ------------
@socketio.on("request_market_status")
def send_market_status():
    from data.getdata import market_status
    socketio.emit("market_status", market_status())


# ============= Backtest Module ===============

from data.backtest import backtest_calculation
@socketio.on("request_backtest")
def send_backtest(configs):
    page_id, from_date, to_date, per_buy, per_sell = configs['page_id'], configs['from_date'], configs['to_date'], configs['per_buy'], configs['per_sell']
    backtest_result = backtest_calculation(page_id, from_date, to_date, per_buy, per_sell, con, socketio)
    socketio.emit("backtest",  json.dumps(backtest_result, cls=NpEncoder))
