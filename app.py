from concurrent.futures import thread
from flask import Flask
from flask_socketio import SocketIO
from threading import Lock
from flask_socketio import send, emit

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
    socketio.emit("tick_data", price)
    get_indicator(df) # call the indicator with detial that send from frontend

# get data from specific symbol
@socketio.on("request_tick")
def tick_data(symbol):
     from data.getdata import sub_tick
     sub_tick(con, symbol, get_tick)

# subscribe all instruments
def sub_all_symbols():
    from data.getdata import get_instruments
    pairs = get_instruments(con)
    # for symbol in pairs : tick_data(symbol)
    tick_data("EUR/USD")

# -----------------------------------------------
# -------------- Get Indicator Data -------------
def get_indicator(df):
    from data.indicator import moving_average
    data = moving_average(df, "1Min", "Close", "Simple", 2)
    socketio.emit("indicator_data", {"value" : round(data.tail(1).values[0], 5)})

@socketio.on("request_indicator")
def indicator_parameters(json):
     print(json)

if __name__ == '__main__':
    global con
    con = price_connect()
    sub_all_symbols() # get all instruments and subscribe
    socketio.run(app, port=8000)