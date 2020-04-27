import backtrader as bt
import backtrader.feeds as btfeeds
import numpy as np
from scipy import stats

class Pearson (bt.Indicator):
    lines = ('pearson',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        self.lines.pearson[0] = (np.corrcoef(self.datas[0].get(size=self.p.period), self.datas[1].get(size=self.p.period)))[0][1]

class Theil (bt.Indicator):
    lines = ('theil',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self): #0/1
        self.lines.theil[0] = (stats.theilslopes(self.datas[0].get(size=self.p.period), self.datas[1].get(size=self.p.period)))[0]

class STP (bt.Indicator):
    lines = ('stp',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):  # 0/1
        self.lines.stp[0] = (stats.theilslopes(self.datas[0].get(size=self.p.period), self.datas[1].get(size=self.p.period)))[0] * ((np.corrcoef(self.datas[0].get(size=self.p.period), self.datas[1].get(size=self.p.period)))[0][1] ** 5)


class CorrelationStrategy(bt.Strategy):
    params = (('period',  15), ('th_theil_d', 30), ('th_theil_u', 70), ('th_pear', 50), ('sl_per', -1), ('tp_per', 12), ('sl_k', 85)) # k= tp/sl

    def buyf_sells(self):
        total_pos = 40*(self.broker.getcash())

        a = self.dataclose_f[0]
        b = self.dataclose_s[0]

        size_first = total_pos / (2*a)
        size_second = total_pos / (2*b)


        self.sell(self.datas[1], size = size_second)
        self.buy(self.datas[0], size = size_first)

    def buys_sellf(self):
        total_pos = 40*(self.broker.getcash())

        a = self.dataclose_f[0]
        b = self.dataclose_s[0]

        size_first = total_pos / (2*a)
        size_second = total_pos / (2*b)


        self.sell(self.datas[0], size = size_first)
        self.buy(self.datas[1], size = size_second)


    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose_f = self.datas[0].close
        self.dataclose_s = self.datas[1].close
        self.Pearson = Pearson(self.datas[0], self.datas[1], period=self.params.period)
        self.Theil = Theil(self.datas[0], self.datas[1], period=self.params.period)

    def next(self):
        if not self.position:
            if (self.Theil[-1] > self.params.th_theil_d/100) and (self.Theil[0] < self.params.th_theil_d/100) and (self.Pearson[0] < self.params.th_pear/100):
                self.buyf_sells()
                #print("1")

            if (self.Theil[-1] < self.params.th_theil_u/100) and (self.Theil[0] > self.params.th_theil_u/100) and (self.Pearson[0] < self.params.th_pear/100):
                self.buys_sellf()
                #print("2")
        else:
            p1 = self.getposition(data=self.datas[0])
            p2 = self.getposition(data=self.datas[1])
            prof = (p1.adjbase - p1.price) * p1.size + (p2.adjbase - p2.price) * p2.size
            pnl = prof / self.broker.getcash()

            if (pnl < self.params.sl_per/100) or (pnl > self.params.tp_per/100):
                #print("sltp", round(pnl, 3), prof)
                if (p1.size > 0) and (p2.size < 0):
                    self.close(self.datas[0])
                    self.close(self.datas[1])
                else:
                    self.close(self.datas[1])
                    self.close(self.datas[0])


            if (str(self.datas[0].datetime.date(0)) == "2020-02-13") and self.position:
                self.close(self.datas[0])
                self.close(self.datas[1])

    def stop(self):
        print("Profit:", str(int((self.broker.getvalue() - 500000) // 1000)) + "k", self.params.th_theil_u)
        #print("Percent:", ((self.broker.getvalue())/500000)**(1/9))
        #print(self.params.period, self.params.threshold, self.params.stoploss, self.params.takeprofit_k, "Profit:",(self.broker.getvalue() - 500000))


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    strats = cerebro.optstrategy(
        CorrelationStrategy,
        th_theil_u = range(50, 100, 1))

    data_f = btfeeds.GenericCSVData(dataname='NOC_10.csv', openinterest=-1, dtformat="%Y-%m-%d", tmformat=-1)
    data_s = btfeeds.GenericCSVData(dataname='LMT_10.csv', openinterest=-1, dtformat="%Y-%m-%d", tmformat=-1)

    cerebro.adddata(data_f)
    cerebro.adddata(data_s)

    cerebro.broker.setcash(500000)
    cerebro.broker.setcommission(commission=0.0005, interest=0.0269)

    thestrats = cerebro.run()
    thestrat = thestrats[0]