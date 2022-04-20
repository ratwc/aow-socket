from concurrent.futures import thread
from socket import socket
from flask import Flask
from flask_socketio import SocketIO
from threading import Lock
from flask_socketio import send, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aow-senior'
socketio = SocketIO(app, cors_allowed_origins="*")

# get connection from fxcm server
def price_connect():
    from data.connect import connect
    return connect()

# ----------- Get Realtime Tick Data -----------

# function callback data when new tick data occur.
def get_tick(price, df):
    from data.tick import manage_tick
    tick, ohlc_m1 = manage_tick(df['Bid'], price['Symbol'], con) # manage tick to get all data
    socketio.emit("ohlc_data", {"Symbol": price['Symbol'], "OHLC": ohlc_m1}) # send ohlc 1 minutes data
    socketio.emit("tick_data", {"Symbol": price['Symbol'], "OHLC": tick}) # send tick data 
    
# get data from specific symbol
@socketio.on("request_tick")
def tick_data(symbol):
    from data.getdata import sub_tick
    sub_tick(con, symbol, get_tick)

# un-subscribe all symbol
@socketio.on("remove_all_symbols")
def unsub_symbol():
    from data.getdata import unsub_all
    unsub_all(con)

# ----------- Get Instruments -----------

@socketio.on("request_instruments")
def instruments():
    from data.getdata import get_instruments
    all_pairs = json.dumps(get_instruments(con))
    socketio.emit("instruments", all_pairs)


# -------------- Get NEWS Data --------------

if __name__ == '__main__':
    global con # global variable with connect to fxcm server
    con = price_connect()
    socketio.run(app, port=8000)