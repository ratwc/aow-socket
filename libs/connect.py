# using library socketio_4.6.1 and engineio_3.9.0
import fxcmpy

def connect():
    # define access api token
    access_token = "d808da394895605e414394e79c1a3c9ffafad862"

    # connect to fxcm server
    con = fxcmpy.fxcmpy(access_token=access_token, log_level='error', server='demo', log_file='log.txt')

    # return connection
    if con.is_connected():
        print("Connect Successful!")
        return con
    else :
        print("Connect Fail!")
        return False