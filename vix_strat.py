import quantopian.algorithm as algo
from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.data.quandl import cboe_vix

def make_pipeline():
    my_pipe = Pipeline()
    my_pipe.add(cboe_vix.vix_close.latest, 'vix_close')
    
    return pipe

def initialize(context):
    schedule_function(
        rebalance,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )
    
    attach_pipeline(make_pipeline(), "pipeline")
    
    schedule_function(record_vars, date_rules.every_day(),
        time_rules.market_close())
    
def before_trading_start(context, data):
    context.output = pipeline_output('pipeline')     
    context.vix = context.output["VixOpen"].iloc[0]

def rebalance(context, data):
    if (cboe_vix.vix_close.latest > 20):
        order_target_percent(sid(8554), 1)
    else:
        order_target_percent(sid(8554), -1)
    pass

def record_vars(context, data):
    print((cboe_vix.vix_close.latest))
    leverage=context.account.leverage  
    exposure=context.account.net_leverage  
    record(leverage=leverage, exposure=exposure)
    pass

def handle_data(context, data):
    """
    Called every minute.
    """
    pass
