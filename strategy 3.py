import backtrader as bt
import backtrader.feeds as btfeeds
import numpy as np
from scipy import stats

class Pearson (bt.Indicator):
    """Calculates moving pearson correlation coefficient"""
    lines = ('pearson',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        self.lines.pearson[0] = (np.corrcoef(self.datas[0].get(size=self.p.period), self.datas[1].get(size=self.p.period)))[0][1]

class Theil (bt.Indicator):
    """Calculates moving theil index"""
    lines = ('theil',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self): #0/1
        self.lines.theil[0] = (stats.theilslopes(self.datas[0].get(size=self.p.period), self.datas[1].get(size=self.p.period)))[0]


class CorrelationStrategy(bt.Strategy):
    params = (('period', 15),
              ('th_theil_d', 30),
              ('th_theil_u', 59),
              ('th_pear', 50),
              ('sl_per', -1),
              ('tp_per', 12),
              ('money_k', 100))

    def buyf_sells(self):
        """Creates buy order for 1 stock and sell order for 2 stock"""
        total_pos = self.params.money_k * (self.broker.getcash())

        a = self.dataclose_f[0]
        b = self.dataclose_s[0]

        """Money are equally splitted between 2 trades for equal impact"""
        size_first = total_pos / (2 * a)
        size_second = total_pos / (2 * b)

        """The same amount of money is spent executing buy order as there're gained from sell"""
        self.sell(self.datas[1], size=size_second)
        self.buy(self.datas[0], size=size_first)

    def buys_sellf(self):
        """Creates buy order for 2 stock and sell order for 1 stock"""
        total_pos = self.params.money_k * (self.broker.getcash())

        a = self.dataclose_f[0]
        b = self.dataclose_s[0]

        """Money are equally splitted between 2 trades for equal impact"""
        size_first = total_pos / (2 * a)
        size_second = total_pos / (2 * b)

        """The same amount of money is spent executing buy order as there're gained from sell"""
        self.sell(self.datas[0], size=size_first)
        self.buy(self.datas[1], size=size_second)


    def __init__(self):
        """Calculates all the indexes and datas"""
        self.dataclose_f = self.datas[0].close
        self.dataclose_s = self.datas[1].close
        self.Pearson = Pearson(self.datas[0], self.datas[1], period=self.params.period)
        self.Theil = Theil(self.datas[0], self.datas[1], period=self.params.period)

    def next(self):
        """If there are no positions at the moment, new can be opened"""
        if not self.position:
            """Position created when theil decreases and crosses th_theil_d/100 and pearson is low enough"""
            if (self.Theil[-1] > self.params.th_theil_d/100) and (self.Theil[0] < self.params.th_theil_d/100) and (self.Pearson[0] < self.params.th_pear/100):
                self.buyf_sells()

            """Position created when theil increases and crosses th_theil_u/100 and pearson is low enough"""
            if (self.Theil[-1] < self.params.th_theil_u/100) and (self.Theil[0] > self.params.th_theil_u/100) and (self.Pearson[0] < self.params.th_pear/100):
                self.buys_sellf()

        else:
            """Calculating pnl of 2 opened positions together"""
            p1 = self.getposition(data=self.datas[0])
            p2 = self.getposition(data=self.datas[1])
            prof = (p1.adjbase - p1.price) * p1.size + (p2.adjbase - p2.price) * p2.size
            pnl = prof / self.broker.getcash()

            """Closing deals if profit or loss is big enough"""
            if (pnl < self.params.sl_per/100) or (pnl > self.params.tp_per/100):
                if (p1.size > 0) and (p2.size < 0):
                    """Closing order depends on which trade is buy and which is sell"""
                    self.close(self.datas[0])
                    self.close(self.datas[1])
                else:
                    self.close(self.datas[1])
                    self.close(self.datas[0])

            """Closing all trades at the last day"""
            if (str(self.datas[0].datetime.date(0)) == "2020-02-13") and self.position:
                self.close(self.datas[0])
                self.close(self.datas[1])

    def stop(self):
        print("Profit:", str(int((self.broker.getvalue() - 10000 - 15000) // 1000)) + "k")  # pro account costs 15k for 10 years
        print("Average annual percent:", round((((self.broker.getvalue())/10000)**(1/9)), 3) * 100 - 100)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    strats = cerebro.addstrategy(CorrelationStrategy)

    data_f = btfeeds.GenericCSVData(dataname='NOC_10.csv', openinterest=-1, dtformat="%Y-%m-%d", tmformat=-1)
    data_s = btfeeds.GenericCSVData(dataname='LMT_10.csv', openinterest=-1, dtformat="%Y-%m-%d", tmformat=-1)

    cerebro.adddata(data_f)
    cerebro.adddata(data_s)

    """Can't execute deals bigger then market volume of that day"""
    filler = bt.broker.fillers.FixedSize()
    cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc=80))

    cerebro.broker.setcash(10000)
    cerebro.broker.setcommission(commission=0.0005, interest=0.0269)
    # commission from interactive broker pro (129$/month) = 15k for 10years of testing

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

    thestrats = cerebro.run()

    print('Sharpe index:', round(thestrats[0].analyzers.sharpe.get_analysis().popitem()[1], 3))
    cerebro.plot()
