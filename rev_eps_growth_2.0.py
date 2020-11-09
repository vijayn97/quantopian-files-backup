from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.data import morningstar

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    attach_pipeline(make_pipeline(), 'pipeline')
    schedule_function(open_positions, date_rules.month_start(), time_rules.market_open(minutes=60))
    schedule_function(close_positions, date_rules.month_start(), time_rules.market_open())
    context.max_notional = 2000
    

    
def make_pipeline():
    base_universe = QTradableStocksUS()
    revenue_growth = morningstar.operation_ratios.revenue_growth.latest
    dil_eps_growth = morningstar.earnings_ratios.diluted_eps_growth.latest
    mktcap = morningstar.valuation.market_cap.latest
    
    rev_filter = revenue_growth > 0.2
    eps_filter = dil_eps_growth > 0.2
    mktcap_filter = mktcap < 2000000000

    all_filters = rev_filter & eps_filter & mktcap_filter & base_universe
    
    pipe = Pipeline(
        columns={
            'rev_growth': revenue_growth,
            'dil_eps_growth': dil_eps_growth,
            'mktcap': mktcap
        },
        screen=all_filters
    )
    return pipe


def before_trading_start(context, data):
    context.output = pipeline_output('pipeline')
    context.stocks = context.output.head(20)

def open_positions(context,data):
    today = get_datetime('US/Eastern') 
    if today.month in [1,3,9,12]:
        for stock in context.stocks.index:
            order_target_percent(stock, 0.05)

def close_positions(context,data):
    today = get_datetime('US/Eastern') 
    if today.month in [1,3,9,12]:
        for stock in context.portfolio.positions:
            order_target_percent(stock, 0)


               
               
               
