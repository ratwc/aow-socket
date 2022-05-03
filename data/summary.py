

def summary(indicators_signal):

    return_summary = {}
    return_summary['timeframe'] = {}
    return_summary['all'] = {}
    return_summary['all']['SELL'], return_summary['all']['BUY'] = 0, 0
    for indicator in indicators_signal.keys():

        for tf in indicators_signal[indicator]:

            if tf['timeframe'] not in return_summary['timeframe']:
                return_summary['timeframe'][tf['timeframe']] = {}
                # initial trend 
                return_summary['trend'] = {}
                return_summary['timeframe'][tf['timeframe']]['trend'] = {}
                return_summary['timeframe'][tf['timeframe']]['trend']['BUY'], return_summary['trend']['BUY'] = 0, 0
                return_summary['timeframe'][tf['timeframe']]['trend']['SELL'], return_summary['trend']['SELL'] = 0, 0
                return_summary['timeframe'][tf['timeframe']]['trend']['NEUTRAL'], return_summary['trend']['NEUTRAL'] = 0, 0
                # initial momentum
                return_summary['momentum'] = {}
                return_summary['timeframe'][tf['timeframe']]['momentum'] = {}
                return_summary['timeframe'][tf['timeframe']]['momentum']['OVERBOUGHT'], return_summary['momentum']['OVERBOUGHT'] = 0, 0
                return_summary['timeframe'][tf['timeframe']]['momentum']['OVERSOLD'], return_summary['momentum']['OVERSOLD'] = 0, 0
                return_summary['timeframe'][tf['timeframe']]['momentum']['NEUTRAL'], return_summary['momentum']['NEUTRAL'] = 0, 0

            if tf['type'] == 'trend':
                return_summary['timeframe'][tf['timeframe']]['trend'][tf['signal']] += 1
                return_summary['trend'][tf['signal']] += 1
            elif tf['type'] == 'momentum':
                return_summary['timeframe'][tf['timeframe']]['momentum'][tf['signal']] += 1
                return_summary['momentum'][tf['signal']] += 1

            if tf['signal'] in ['BUY', 'OVERSOLD']: return_summary['all']['BUY'] += 1
            elif tf['signal'] in ['SELL', 'OVERBOUGHT']: return_summary['all']['SELL'] += 1
            
    return_summary['summary'] = {}
    if (return_summary['all']['BUY'] + return_summary['all']['SELL']) != 0:
        return_summary['summary']['BUY'] = return_summary['all']['BUY'] * 100 / (return_summary['all']['BUY'] + return_summary['all']['SELL'])
        return_summary['summary']['SELL'] = return_summary['all']['SELL'] * 100 / (return_summary['all']['BUY'] + return_summary['all']['SELL'])
    else :
        return_summary['summary']['BUY'] = 0
        return_summary['summary']['SELL'] = 0

    return return_summary








    



