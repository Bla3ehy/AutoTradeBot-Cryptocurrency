from finlab_crypto.online import TradingMethod, TradingPortfolio, render_html
from finlab_crypto.strategy import Strategy
from finlab_crypto.indicators import trends
import finlab_crypto
import configparser
import Notice
from Notice import lineNotifyMessage, openFile



def main():
    
    configParser = configparser.ConfigParser()
    configParser.read(r'App.config')
    key = configParser.get('AppConfig', 'key')
    secret = configParser.get('AppConfig','secret')
    token = configParser.get('AppConfig','token')
    Asset = configParser.get('AppConfig','asset')
    
    # Filter: trends = {
    #     'sma': sma,
    #     'wma': wma,
    #     'lowpass': lowpass,
    #     'hullma': hullma,
    #     'zlma': zlma,
    #     'alma': alma,
    #     'detrend': detrend,
    #     'linear_reg': linear_reg
    # }

    @Strategy(name="hullma", n1=110, n2=260)
    def trend_strategy(ohlcv):
        name = trend_strategy.name
        n1 = trend_strategy.n1
        n2 = trend_strategy.n2

        filtered1 = trends[name](ohlcv.close, n1)
        filtered2 = trends[name](ohlcv.close, n2)

        entries = (filtered1 > filtered2) & (filtered1.shift() < filtered2.shift())
        exit = (filtered1 < filtered2) & (filtered1.shift() > filtered2.shift())

        figures = {
            'overlaps': {
                'trend1': filtered1,
                'trend2': filtered2,
            }
        }
        return entries, exit, figures



    # altcoin strategy
    # --------------------
    # 'ADABUSD', 'ETHBUSD', 'BTCBUSD', 'BNBBUSD'
    # trend_strategy(ohlcv, variables={'name': 'sma', 'n1', 30, 'n2': 130}, freq='4h')
    # {'ETHUSDT': 0.5, 'ADABUSD': 0.1,'default':0.2}

    tm1 = TradingMethod(
        symbols=['ADABUSD', 'ETHBUSD', 'BTCBUSD', 'BNBBUSD'],
        freq='4h',
        # lookback:backtest data length
        lookback=1500, #K棒數
        strategy=trend_strategy,
        variables=dict(
            name='sma',
            n1=110,
            n2=260,
        ),
        filters={},
        # how to set weight_btc?Please see teacher additional materials.
        weight_btc=0.02,
        name='altcoin-trend-hullma'
    )

    # btc strategy
    # --------------------
    # 'BTCUSDT'
    # trend_strategy(ohlcv, variables={'name': 'hullma', 'n1', 70, 'n2': 108}, freq='4h')

    # tm2 = TradingMethod(
    #     symbols=['BUSDUSDT'],
    #     freq='4h',
    #     lookback=1000,
    #     strategy=trend_strategy,
    #     variables=dict(
    #         name='hullma',
    #         n1=70,
    #         n2=108,
    #     ),
    #     filters={},
    #     weight_btc=1,  #想要投資的資產，以比特幣做單位
    #     name='btc-trend-hullma'
    # )

    # mode = 'LIMIT'
    # mode = 'MARKET'
    # mode = 'TEST'

    def rebalance_position():
        tp = TradingPortfolio(key, secret)
        tp.register(tm1)
        order_length = 0
        success_length = 0
        # tp.register(tm2)

        # get all price data
        #full_ohlcvs = tp.get_full_ohlcvs()

        tp = TradingPortfolio(key, secret)
        tp.register(tm1)
        # tp.register(tm2)
        tp.register_margin('USDT', int(Asset)) #想要投資的資產

        ohlcvs = tp.get_ohlcvs()
        
        signals = tp.get_latest_signals(ohlcvs)
        position, position_btc, new_orders = tp.calculate_position_size(signals)
        
        mode="TEST"
        order_results = tp.execute_orders(new_orders, mode=mode)
        order_length = len(new_orders.index)

        print(order_results)
        
        if mode == "TEST":
            html = render_html(signals,position,position_btc,new_orders,order_results)
            with open("profolio.html",mode="w",encoding="utf-8") as file:
                file.writelines(html)
            confirm = openFile()
            print(confirm)
            if confirm == True:
                mode="MARKE"
                order_results = tp.execute_orders(new_orders, mode=mode)
                success_length = len(order_results[['result']] == 'success')

            print(order_length)
            print(success_length)
            
            if (order_length == success_length):
                lineNotifyMessage(token,'Success')
            else:
                lineNotifyMessage(token,'Fail')

    rebalance_position()



if __name__ == "__main__":
    main()
