from flask import Flask
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aow-senior'
socketio = SocketIO(app, cors_allowed_origins="*")

con = None # connect to fxcm server variable

# get connection from fxcm server
def price_connect():
    from libs.connect import connect
    return connect()

# ----------- Manage Realtime Tick Data -----------

# function callback data when new tick data occur.
def get_tick(price, df):
    from data.tick import manage_ohlc
    tick = manage_ohlc(df['Bid'], price['Symbol'], con) # manage tick to get all data
    socketio.emit("tick_data", tick)
    
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

# subcribe all instruments
@socketio.on("sub_all_symbols")
def sub_symbols():
    from data.getdata import get_instruments
    all_pairs = get_instruments(con)
    for symbol in all_pairs:
        tick_data(symbol)

import send # module to mange the data to send to client

# main function
if __name__ == '__main__':
    con = price_connect()
    # tick_data("EUR/USD")
    sub_symbols()
    socketio.run(app, port=8000)
    

