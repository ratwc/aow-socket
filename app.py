from concurrent.futures import thread
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
    df['Timestamp'] = df.index
    df['Symbol'] = price['Symbol']
    tick_df = df[['Timestamp', 'Symbol', 'Bid']]
    tick_json = tick_df.to_json(orient='records')
    socketio.emit("tick_data", tick_json)
    
# get data from specific symbol
@socketio.on("request_tick")
def tick_data(symbol):
    from data.getdata import sub_tick
    sub_tick(con, symbol, get_tick)

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