import quantopian.algorithm as algo
import math
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS


def initialize(context):
    context.spy = sid(8554)
    # Rebalance every day, 1 hour after market open.
    schedule_function(
        SPY_sma,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )

def SPY_sma(context, data):
    sma_50 = data.history(context.spy, "price", 50, "1d").mean()
    sma_200 = data.history(context.spy, 'price', 200, '1d').mean()

    if sma_50 > sma_200:
        order_target_percent(context.spy, 1)
              
        
    elif sma_200 > sma_50:
        order_target_percent(context.spy, 0)
        
        
        
        
