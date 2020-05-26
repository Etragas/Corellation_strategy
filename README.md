# This's a trading bot
This stock bot tracks prices of 2 assets and autamaticly makes trading decisions.
That strategy is based on idea that some stocks tend to maintain their correlation for example close competitors or assest price and corresponding industry player. Betting against fluctuations of their correlaltion can generate profit.

## Math
Running Theil and Pearson correlation coefficients between prices of 2 stocks are used to estimate correlation. Let X, Y be time series of 2 asset prices and w - lenght of the time frame. Theil(X, Y, w) estimates average ratio dY/dX over last w days. Please note: order in which arguments are passed is important (Theil(Y, X) ≠ 1 / Theil(X, Y)) https://en.wikipedia.org/wiki/Theil%E2%80%93Sen_estimator \
Pearson coefficio estimates correlation strength. It ranges from -1 to 1, where 1 is exact positive correlation and -1 is exact negative. Unlike Theil coefficient, Pearson coefficient is invariant to parameter order. https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

## Stocks
For argoritm demonstration one can choose a pair of close competitors whose stock prices correlate. Results below are based on historical daily prices of Northrop Grumman Corporation (NYSE:NOC) and Lockheed Martin (NYSE:LMT) stock. They are top 3 and 1 suppliers of US army forces.
Boeng (#2 supplier) wasn't picked because it has big unrelated part of busines, whereas other two specialise on production for military.

## Software tools
data source: Yahoo finance\
Python 3.8.2 \
python libraries:
- scipy - Theil correlation
- numpy - Pearson correlation
- backtrader - backtasting and trading framework

## Opening trades
Let Theil coefficient = dPriceOf1/dPriceOf2

Pearson coefficent detects instances of weak correlation.

One stock is bought and other is sold when:
1. Pearson coefficient is low enough
2. Theil coefficien crosses the upper (buy - asset 2, sell - asset 1) or lower bound (buy - asset 1, sell - asset 2)

##### Blue line on the chart is Theil coef, yellow - Pearsons calculated for 2 sample sets of data. When Theil coefficient changes, Pearsons coef decreases
![](chart_ex_corr.png)

Boundaries are calculated as average +- running standart deviation * parameter. This is an exact formula for Bollinger bands, though in in algorithm period for running standard deviation is twice as big as for an average. It makes smoother lines and more predictable results.

Money for a whole trade is devided equally and each part is spent on buying/selling each stock, so balance of account stays unchanged.
Also it makes both stocks equally affect the outcome despite differences in price.
 


## Closing Trades

Trades close when:
1. Profit or loss are bigger then thresholds.
2. Theil coefficient crosses upper or lower boundaries.
3. It's the last day of used testing data

Boundaries are calculated as explained above.

## Results

Strategy results in 218% for 9 years of test (annualised 9%) and Sharpe coeffiscient ((average year profit percentage - zero risk profit percentage) / std deviation of portfolio) 0.38 which is considered very bad. On the graph below green and red triangles represent executed buy/sell orders. Red line on the top graph is value of account.

![](chart_1.png)

## Concerns
There aren't many trades - only 17. Also most of them are performed in sequences of 5-6 whithin 3-6 months. So most of the time there are no trades executed. It results in risk that exceeds normal by ~3 times.








