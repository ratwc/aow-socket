# using library socketio_4.6.1 and engineio_3.9.0
import fxcmpy

def connect():
    # define access api token
    access_token = "427c34263cffb2f79c1406d7f5ab5e12bf625946"

    # connect to fxcm server
    con = fxcmpy.fxcmpy(access_token=access_token, log_level='error', server='demo', log_file='log.txt')

    # return connection
    if con.is_connected():
        print("Connect Successful!")
        return con
    else :
        print("Connect Fail!")
        return False