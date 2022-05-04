from flask import Flask
from flask_socketio import SocketIO, send, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aow-senior'
socketio = SocketIO(app, cors_allowed_origins="*")

# get connection from fxcm server
def price_connect():
    from libs.connect import connect_with_api, connect_with_library
    return connect_with_library()

# ----------- Manage Realtime Tick Data -----------

# function callback data when new tick data occur.
def get_tick(price, df):
    from data.tick import manage_ohlc
    tick = manage_ohlc(df['Bid'], price['Symbol'], con, "realtime") # manage tick to get all data
    socketio.emit("tick_data", json.dumps(tick))
    
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
    from data.initial import initial_ohlc
    all_pairs = get_instruments(con)
    for symbol in all_pairs:
        # initial data if running on close market day
        initial_ohlc(symbol, con)
        # real subscribe data to get realtime
        tick_data(symbol)

# main function
if __name__ == '__main__':
    global con
    con = price_connect() # connect to fxcm server variable
    import send # module to mange the data to send to client
    sub_symbols() # sub all symbol fot get realtime data

    socketio.run(app, port=8000, host='0.0.0.0')
    

