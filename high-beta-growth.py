from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.factors import (
    AverageDollarVolume, RollingLinearRegressionOfReturns,
)
from quantopian.pipeline.data import morningstar

def initialize(context):
    context.beta_threshold = 1
    # Arguments to pass to linear regression factor.
    context.returns_length = 7
    context.regression_length = 100
    context.target_asset = symbol('SPY')
     
    schedule_function(
        func=rebalance, 
        date_rule=date_rules.month_start(days_offset=0), 
        time_rule=time_rules.market_open(hours=0,minutes=30), 
    )
    
    attach_pipeline(my_pipeline(context), 'my_pipeline')
         
def my_pipeline(context):
    pipe = Pipeline()

    revenue_growth = morningstar.operation_ratios.revenue_growth.latest
    dil_eps_growth = morningstar.earnings_ratios.diluted_eps_growth.latest
    net_income_growth = morningstar.operation_ratios.net_income_growth.latest
    operation_income_growth = morningstar.operation_ratios.operation_income_growth.latest
    
    #Filters
    # Only consider the top 10% of stocks ranked by dollar volume.
    dollar_volume = AverageDollarVolume(window_length=1)
    high_dollar_volume = dollar_volume.percentile_between(90, 100)
    #Traditional growth stocks metrics: >25% growth in all related factors
    rev_filter = revenue_growth > 0.20
    eps_filter = dil_eps_growth > 0.20
    income_filter = net_income_growth > 0.20
    opin_filter = operation_income_growth > 0.20
    
    # Create a regression factor with SPY.
    regression = RollingLinearRegressionOfReturns(
        target=context.target_asset,
        returns_length=context.returns_length,
        regression_length=context.regression_length,
        mask=high_dollar_volume,
    )
    alpha = regression.alpha
    beta = regression.beta
    correlation = regression.r_value
    low_beta = (beta < context.beta_threshold) & \
               (beta > -context.beta_threshold)
    high_beta = ~low_beta
    
    pipe.add(alpha, 'alpha')
    pipe.add(beta, 'beta')
    pipe.add(correlation, 'correlation')
    pipe.add(low_beta, 'low_beta')
    pipe.add(high_beta, 'high_beta')
    pipe.set_screen(rev_filter & eps_filter & income_filter & opin_filter & high_dollar_volume)
    
    return pipe
    pass
 
def before_trading_start(context, data):
    context.output = output = pipeline_output('my_pipeline')
    context.stocks = stocks = output[output['high_beta']].index
    context.stock_weights = assign_weights(stocks)
    pass
    
def assign_weights(stocks):
    # Equally weight all securities.
    num_stocks = len(stocks)
    if num_stocks == 0: 
        return 0
    else:
        equal_weight = 1.0 / num_stocks
        weights = [equal_weight] * num_stocks
        return weights
    pass
 
def rebalance(context, data):
    print(len(context.stocks))
    sells = set(context.portfolio.positions) - set(context.stocks)
    for asset in sells:
        if data.can_trade(asset):
            order_target(asset, 0)
    if context.stock_weights != 0:
        buys = zip(context.stocks, context.stock_weights)
        for asset, weight in buys:
            if data.can_trade(asset):
                order_target_percent(asset, weight)
    pass
           
