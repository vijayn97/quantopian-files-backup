from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data import morningstar

# Called once at start of algorithm
def initialize(context):
    schedule_function(rebalance, date_rules.month_start(), time_rules.market_open())
    attach_pipeline(make_pipeline(), 'my_pipeline')
    
def make_pipeline():
    prof_grade = morningstar.asset_classification.profitability_grade.latest
    growth_grade = morningstar.asset_classification.growth_grade.latest
    mktcap = morningstar.valuation.market_cap.latest
    
    prof_filter = prof_grade.startswith('A')
    gg_filter = growth_grade.startswith('A')
    mktcap_filter = (10000000000 < mktcap < 200000000000)
    
    all_filters = prof_filter & gg_filter & mktcap_filter
    return Pipeline(columns={'prof_grade':prof_grade, 'growth_grade': growth_grade, 'mktcap':mktcap}, screen = all_filters)

# Called everyday before market open
def before_trading_start(context, data):
    context.raw_pipe_output = pipeline_output('my_pipeline')
    context.stocks = context.raw_pipe_output.head(10)
    # Assigning equal weight to each stock
    context.pct_per_stock = 1.0/len(context.stocks)
    
def rebalance(context, data):
    for stock in context.stocks.index:
        sma_25 = data.history(stock, 'price', 25, '1d').mean()
        sma_50 = data.history(stock, 'price', 50, '1d').mean()
        # Close position if we own stock and the MACD is negative
        if sma_25 < sma_50:
            order_target_percent(stock,0)
        # Enter position if we don't own the stock and MACD is positive
        elif sma_25 > sma_50:
            order_target_percent(stock, context.pct_per_stock)
            
    for stock in context.portfolio.positions:
        if ((stock not in context.stocks.index) & (sma_25 < sma_50)):
            order_target_percent(stock, 0)
