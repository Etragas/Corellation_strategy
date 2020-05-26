import backtrader as bt
import backtrader.feeds as btfeeds
import numpy as np
from scipy import stats


class Pearson (bt.Indicator):
    # Calculates moving pearson correlation coefficient
    lines = ('pearson',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        self.lines.pearson[0] = (np.corrcoef(self.datas[0].get(size=self.p.period), self.datas[1].get(size=self.p.period)))[0][1]


class Deviation (bt.Indicator):
    # Calculates moving standard deviation
    lines = ('std',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self):
        self.lines.std[0] = np.std(self.datas[0].get(size=self.p.period))


class Theil (bt.Indicator):
    # Calculates moving theil index
    lines = ('theil',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self): #0/1
        self.lines.theil[0] = (stats.theilslopes(self.datas[0].get(size=self.p.period), self.datas[1].get(size=self.p.period)))[0]


class Average (bt.Indicator):
    # Calculates simple moving average
    lines = ('average',)
    params = (('period', 20),)

    def __init__(self):
        self.addminperiod(self.params.period)

    def next(self): #0/1
        self.lines.average[0] = np.mean(self.datas[0].get(size=self.p.period))

class CorrelationStrategy(bt.Strategy):
    # List of all parameters
    # They are all integers for easier testing
    params = (('period', 15),
            ('bol_k_up', 20),
            ('bol_k_down', 20),
            ('bol_k_close', 6),
            ('th_pear_d', 49),
            ('th_pear_u', 50),
            ('sl_per', -6),
            ('tp_per', 6),
            ('money_k', 40),
            ('period_close', 75),
            ('prolong', 2.3),)

    def buyf_sells(self):
        # Creates buy order for 1st stock and sell order for 2nd stock
        total_pos = self.params.money_k * (self.broker.getcash())

        a = self.dataclose_f[0]
        b = self.dataclose_s[0]

        # Money are equally splitted between 2 trades for equal impact
        size_first = total_pos / (2 * a)
        size_second = total_pos / (2 * b)

        # The same amount of money is spent executing buy order as there's gained from sell
        self.sell(self.datas[1], size=size_second)
        self.buy(self.datas[0], size=size_first)

    def buys_sellf(self):
        # Creates buy order for 2 stock and sell order for 1 stock
        total_pos = self.params.money_k * (self.broker.getcash())

        a = self.dataclose_f[0]
        b = self.dataclose_s[0]

        # Money are equally splitted between 2 trades for equal impact
        size_first = total_pos / (2 * a)
        size_second = total_pos / (2 * b)

        # The same amount of money is spent executing buy order as there's gained from sell
        self.sell(self.datas[0], size=size_first)
        self.buy(self.datas[1], size=size_second)


    def __init__(self):
        # Calculates all the indexes and datas
        self.dataclose_f = self.datas[0].close
        self.dataclose_s = self.datas[1].close
        self.Pearson = Pearson(self.datas[0], self.datas[1], period=self.params.period)
        self.Theil = Theil(self.datas[0], self.datas[1], period=self.params.period)
        self.aver_Theil = Average(self.Theil, period=self.params.period_close)
        # Period for standard deviation is longer to be less volatile (like envelope indicator)
        self.std_Theil = Deviation(self.Theil, period=round(self.params.period_close*self.params.prolong))

    def next(self):
        # If there are no positions at the moment, new can be opened
        if not self.position:
            # Position created when theil decreases and crosses boundary and pearson is low enough
            # Boundaries are calculated similarly to bollinger bands
            # They depend on average and standard deviation of previous data
            std_range = self.std_Theil
            u_boundary = self.aver_Theil + std_range * self.params.bol_k_up / 100
            d_boundary = self.aver_Theil - std_range * self.params.bol_k_down / 100

            if (self.Theil[-1] > d_boundary) and (self.Theil[0] < d_boundary) and (self.Pearson[0] < self.params.th_pear_d / 100):
                self.buyf_sells()

            if (self.Theil[-1] < u_boundary) and (self.Theil[0] > u_boundary) and (self.Pearson[0] < self.params.th_pear_u /100):
                self.buys_sellf()

        # Logic for closing existing positions
        else:
            # Calculating "pnl" of 2 opened positions together#
            p1 = self.getposition(data=self.datas[0])
            p2 = self.getposition(data=self.datas[1])
            prof = (p1.adjbase - p1.price) * p1.size + (p2.adjbase - p2.price) * p2.size
            pnl = prof / self.broker.getcash()

            # Closing deals if profit or loss is big enough or Theil is out of boundaries
            # Closing order depends on which stock is bought and which is sold

            std_range_c = self.std_Theil
            u_boundary_c_g = self.aver_Theil + std_range_c * (self.params.bol_k_up + self.params.bol_k_close) / 100
            d_boundary_c_g = self.aver_Theil - std_range_c * (self.params.bol_k_down - self.params.bol_k_close) / 100
            u_boundary_c_b = self.aver_Theil + std_range_c * (self.params.bol_k_up - self.params.bol_k_close) / 100
            d_boundary_c_b = self.aver_Theil - std_range_c * (self.params.bol_k_down + self.params.bol_k_close) / 100

            # Closed because of Theil boundaries
            if ((p1.size > 0) and (p2.size < 0)) and ((self.Theil > d_boundary_c_g) or (self.Theil < d_boundary_c_b)):
                self.close(self.datas[0])
                self.close(self.datas[1])
                return
            elif (p1.size < 0) and (p2.size > 0) and ((self.Theil < u_boundary_c_g) or (self.Theil > u_boundary_c_b)):
                self.close(self.datas[1])
                self.close(self.datas[0])
                return

            # Closed when pnl is out of boundaries
            if (pnl < self.params.sl_per/100) or (pnl > self.params.tp_per/100):
                if (p1.size > 0) and (p2.size < 0):
                    self.close(self.datas[0])
                    self.close(self.datas[1])
                    return
                else:
                    self.close(self.datas[1])
                    self.close(self.datas[0])
                    return

            # Closing all trades at the last day
            if (str(self.datas[0].datetime.date(0)) == "2020-02-13"):
                if (p1.size > 0) and (p2.size < 0):
                    self.close(self.datas[0])
                    self.close(self.datas[1])
                    return
                else:
                    self.close(self.datas[1])
                    self.close(self.datas[0])
                    return

    def stop(self):
        print(self.broker.getvalue() - 10000,
              self.params.bol_k_up,
              self.params.bol_k_down,
              self.params.bol_k_close_g,
              self.params.bol_k_close_b,
              self.params.sl_per,
              self.params.tp_per,
              self.params.period_close,
              self.params.prolong)

if __name__ == '__main__':
    # If more cpus used, memory error eventually occurs (for my core i7)
    cerebro = bt.Cerebro(maxcpus = 4,stdstats=False)

    # Arrays with possible values can be assigned for each parameter
    strats = cerebro.optstrategy(
        CorrelationStrategy,
        period = 15,
        bol_k_up = 20,
        bol_k_down = 25,
        bol_k_close = range(1, 30, 5),
        th_pear = 49,
        sl_per = range(-22, -1, 5),
        tp_per = range(1, 22, 5),
        money_k = 10,
        period_close = 75,
        prolong = 2.3)

    # Order of stocks should be the same in both files
    data_f = btfeeds.GenericCSVData(dataname='NOC_10.csv', openinterest=-1, dtformat="%Y-%m-%d", tmformat=-1)
    data_s = btfeeds.GenericCSVData(dataname='LMT_10.csv', openinterest=-1, dtformat="%Y-%m-%d", tmformat=-1)

    cerebro.adddata(data_f)
    cerebro.adddata(data_s)

    cerebro.broker.setcash(10000)
    # Sample commission from interactive broker pro
    cerebro.broker.setcommission(commission=0.0005, interest=0.0269)

    # Can't execute deals with volume bigger then 1% of market volume during that day
    filler = bt.broker.fillers.FixedSize()
    cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc=1))


    thestrats = cerebro.run()
    thestrat = thestrats[0]

# using 4 cpus 1 test takes  ~0.9 sec
