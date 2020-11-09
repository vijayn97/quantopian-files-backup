from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.data import morningstar

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    set_benchmark(sid(21519)) # I can't remember what stock this was supposed to be, but it's likely I just used SPY as the benchmark
    attach_pipeline(make_pipeline_buy(), 'pipeline_buy')
    schedule_function(rebalance, date_rules.month_start(), time_rules.market_open(minutes=60))
    
def make_pipeline_buy():
    base_universe = QTradableStocksUS()
    revenue_growth = morningstar.operation_ratios.revenue_growth.latest
    dil_eps_growth = morningstar.earnings_ratios.diluted_eps_growth.latest
    mktcap = morningstar.valuation.market_cap.latest

    # Picking stocks that show 20% revenue growth and 20% EPS growth
    rev_filter = revenue_growth > 0.20
    eps_filter = dil_eps_growth > 0.20

    all_filters = rev_filter & eps_filter & base_universe
    
    pipe = Pipeline(
        columns={
            'rev_filter' : rev_filter,
            'dil_eps_growth': dil_eps_growth,
            'mktcap' : mktcap
        },
        screen=all_filters
    )
    return pipe
pass


def before_trading_start(context, data):
    context.securities = pipeline_output('pipeline_buy')
    
def rebalance(context,data):
    #print(len(context.securities))
    for stock in context.portfolio.positions:
        if stock not in context.securities.index:
            order_target_percent(stock, 0)
            
    for stock in context.securities.index:
        order_target_value(stock, context.portfolio.portfolio_value/len(context.securities))

def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    pass
