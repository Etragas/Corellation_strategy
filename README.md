# Correlation strategy bot
This is a stock bot that looks at prices of 2 stocks and decides when to buy and sell each of them.
This strategy is based on  idea, that some stocks tend to maintain their correlation.  So betting against fluctuations of their correlaltion can generate profit.

## Math
To estimate correlation I've used running Theil and Pearson correlation coeffisients between prices of 2 stocks.
Theil(Y, X) estemates average ratio dY/dX. Order in which arguments are passed is important (Theil(Y, X) ≠ 1 / Theil(X, Y)) https://en.wikipedia.org/wiki/Theil%E2%80%93Sen_estimator \
Pearson estemates how strong correlation is. Ranges from -1 to 1, where 1 is exact positive correlation and -1 is exact negative. Doesn't depend on order of arguments https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

## Stocks
I've chose daily prices of stocks of Northrop Grumman Corporation (NYSE:NOC) and Lockheed Martin (NYSE:LMT). They are top 3 and 1 suppliers of US army forces.
I didn't pick Boeng (#2 supplier) because it has big unrelated part of busines, whereas those two specialise on production for military.

## Used soft
Yahoo finance - data source\
Python 3.8.2 \
python libraries:
- scipy - Theil correlation
- numpy - Pearson correlation
- backtrader - backtasting and trading framework

## Opening trades
Let Theil coefficient = dPriceOf1/dPriceOf2

1 stock is bought and 2 is sold when:
1. Pearson coefficient is low enough
2. Theil coefficien crosses the lower bound

2 stock is bought and 1 is sold when:
1. Pearson coefficient is low enough
2. Theil coefficien crosses the upper bound

Money for a whole trade is devided equally and each part is spent on buying/selling each stock, so balance of account stays unchanged.
Also it makes both stocks equally affect the outcome despite differences in price.
 


Buying 
###### Opening trades

###### Closig trades
bb

## Results
cc

## Concerns
ddd
