import quantopian.algorithm as algo
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS


def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    # Rebalance every day, 1 hour after market open.
    algo.schedule_function(
        rebalance,
        algo.date_rules.month_start(),
        algo.time_rules.market_open()
    )

def rebalance(context, data):
    today = get_datetime('US/Eastern')
    if today.month in [1, 3, 9, 12]:
        dollar_index = data.history(symbol('UUP'), 'price', 90, '1d')
        spy_sma_50 = data.history(symbol('SPY'), 'price', 50, '1d').mean()
        spy_sma_200 = data.history(symbol('SPY'), 'price', 200, '1d').mean()
        iwm_sma_50 = data.history(symbol('IWM'), 'price', 50, '1d').mean()
        iwm_sma_200 = data.history(symbol('IWM'), 'price', 200, '1d').mean()
        # If dollar today is stronger than dollar 3 months ago, buy IWM. Else buy SPY.
        if (dollar_index[-1] > dollar_index[0]):
            order_target_percent(symbol('IWM'), 1)
            order_target_percent(symbol('SPY'), 0)
            print(context.portfolio.positions)
        else:
            order_target_percent(symbol('SPY'), 1)
            order_target_percent(symbol('IWM'), 0)
            print(context.portfolio.positions)

def handle_data(context, data):
    """
    Called every minute.
    """
    pass
