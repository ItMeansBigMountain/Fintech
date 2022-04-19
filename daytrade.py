import robin_stocks as r
import pandas as pd
import matplotlib.pyplot as plt

# AUTH
username = ""
password = ""
r.login(username,password)

#retrieve stocks data
my_stocks = r.build_holdings()

#build data frame
df = pd.DataFrame(my_stocks)
df = df.T
df['ticker'] = df.index
df = df.reset_index(drop=True)
cols = df.columns.drop(['id','type','name','pe_ratio','ticker'])
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

#make 2 tables, buy and sell | (below $25 and percent change of half a percent)
df_buy = df[(df['average_buy_price'] <= 25.000) & (df['quantity'] == 1.000000) & (df['percent_change'] <= -.50)]
df_sell = df[(df['quantity'] == 5.000000) & (df['percent_change'] >= .50)]

tkr_buy_list  = df_buy['ticker'].tolist()
tkr_sell_list = df_sell['ticker'].tolist()

print(tkr_buy_list)
print(tkr_sell_list)


#sell execution
if len(tkr_sell_list) > 0:
    for i in tkr_sell_list:
        print(i)
        print(r.orders.order_sell_market(i,4,timeInForce= 'gfd'))
else:
    print('Nothing to sell right now!')

#buy execution
if len(tkr_buy_list) > 0:
    for i in tkr_buy_list:
        test = r.orders.order_buy_market(i,4,timeInForce= 'gfd')
        # DEBUG
        print(i)
        print(test)
        print(type(test))
else:
    print('Nothing to buy right now!')
