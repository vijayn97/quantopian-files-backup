from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.data import morningstar
from quantopian.pipeline.factors import (AverageDollarVolume, ExponentialWeightedMovingAverage, SimpleMovingAverage)

def initialize(context):
    attach_pipeline(make_pipeline_buy(), 'pipeline_buy')
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open(minutes=30))
    schedule_function(my_record_vars, date_rules.every_day(),
        time_rules.market_close())
pass

def make_pipeline_buy():
    base_universe = QTradableStocksUS()
    mktcap = morningstar.valuation.market_cap.latest

    mktcap_filter = mktcap > 10000000000
    all_filters = mktcap_filter & base_universe
    
    pipe = Pipeline(
        columns={
            'mktcap_filter' : mktcap_filter,
        },
        screen=all_filters
    )
    return pipe
pass

def before_trading_start(context, data):
    context.securities = pipeline_output('pipeline_buy')
pass
    
def rebalance(context,data):
    for stock in context.securities.index:
        sma_5 = data.history(stock, 'price', bar_count=5, frequency='1d').mean()
        sma_10 = data.history(stock, 'price', bar_count=10, frequency='1d').mean()
        if (sma_5 > sma_10):
            order_target_value(stock, context.portfolio.portfolio_value/len(context.securities))
        else:
            order_target_value(stock, -(context.portfolio.portfolio_value*0.05)/len(context.securities))
pass
      
def my_record_vars(context, data):
    leverage=context.account.leverage  
    exposure=context.account.net_leverage  
    record(leverage=leverage, exposure=exposure)  

    longs = 0  
    shorts = 0
    for position in context.portfolio.positions.itervalues():  
        if position.amount > 0:  
            longs += 1  
        if position.amount < 0:  
            shorts += 1  
    record(long_count=longs, short_count=shorts)  
