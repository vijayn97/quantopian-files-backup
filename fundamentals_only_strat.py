from quantopian.pipeline import Pipeline
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline.filters import QTradableStocksUS
from quantopian.pipeline.data import morningstar

def initialize(context):
    attach_pipeline(make_pipeline(), 'pipeline')
    schedule_function(open_positions, date_rules.month_start(), time_rules.market_open(minutes=30))
    schedule_function(close_positions, date_rules.month_start(), time_rules.market_open())
 
def make_pipeline():
    base_universe = QTradableStocksUS()
    #Operating Income / Revenue
    operation_margin = morningstar.operation_ratios.operation_margin.latest
    #EBIT / Revenue
    ebit_margin = morningstar.operation_ratios.ebit_margin.latest
    #(Revenue – Cost of Goods Sold) / Revenue
    gross_margin = morningstar.operation_ratios.gross_margin.latest
    net_margin = morningstar.operation_ratios.net_margin.latest
    mktcap = morningstar.valuation.market_cap.latest

    oper_filter = operation_margin > 0.2
    ebit_filter = ebit_margin > 0.2
    gross_filter = gross_margin > 0.2
    net_filter = net_margin > 0.2
    mktcap_filter = mktcap.top(500)
    
    all_filters = oper_filter & ebit_filter & gross_filter & net_filter & base_universe & mktcap_filter
    
    pipe = Pipeline(
        columns={
            'mktcap' : mktcap,
            'operation_margin' : operation_margin,
            'ebit_margin' : ebit_margin,
            'gross_margin' : gross_margin,
            'net_margin' : net_margin,
        }, screen = all_filters
    )
    return pipe
    
def before_trading_start(context, data):
    context.output = pipeline_output('pipeline')
    context.securities = context.output.head(500)

def open_positions(context,data):
    for stock in context.securities.index:
        order_target_value(stock, context.portfolio.portfolio_value/len(context.securities))
                                 
                                 
def close_positions(context,data):
    for stock in context.portfolio.positions:
        order_target_percent(stock, 0)
