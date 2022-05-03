from libs.fxcm_libs import fxcm_rest_api_token as fxcm_rest_api
import fxcmpy

api_token = "d808da394895605e414394e79c1a3c9ffafad862"
server = "demo"

def connect_with_api():

    trader = fxcm_rest_api.Trader(api_token, server) 
    trader.login()

    return trader

def connect_with_library():

    # connect to fxcm server
    con = fxcmpy.fxcmpy(access_token=api_token, log_level='error', server='demo', log_file='log.txt')

    # return connection
    if con.is_connected():
        print("Connect Successful!")
        return con