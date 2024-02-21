import robin_stocks.robinhood as r
import pandas as pd
import matplotlib.pyplot as plt
import pprint
import math
import time
from getpass import getpass
import time
import json
import configparser

#sometimes mass buying gives time out throttle errors. Try to add a time.sleep(2) per buy




def main():
    print("\n\n\n\nWelcome to the robin hood portfolio app!\n")
    print("Please log into your RobinHood account")
    # add username and password inputs later by calling a new function

    r = login()

    print("Please wait while we gather your stocks...")
    my_stocks = r.build_holdings(with_dividends=True)

    pprint.pprint(my_stocks)

    my_account = r.build_user_profile()
    # phoenix = r.load_phoenix_account()
    

    print("\n\n")
    pprint.pprint(my_account)
    print('\n')
    print("1 - Top preformors")
    print("2 - Profit / Exspense ratio sort")
    print("3 - Crypto")
    print("4 - Rating for all my stocks")
    print("5 - Dividend Prospective")
    print("6 - Dividend Payment History")
    print("7 - Write all stock data into text file")
    print("8 - Industry Charts")
    print("9 - Sector Charts")
    print("10 -Overall Price $ Movment Chart")
    print("11 -Daily $ Movement Chart")
    print("12 -Get Earnings")
    print("13 -Get News")
    print("14 -Get Instrumentals")
    print("15 -Daily Percentage Movement Chart")
    print("16 -Total Percentage Movement Chart")


    print("\n")

    # print("watchlist - Watchlist Interface")
    print("rebuy: CAUTION: REBUY STOCKS USING $$$")
    print("help - Details of each command\n")
    print('reset  or  refresh   -- Refreshes stock data')
    
    option = input("Please choose an option: ")

    if option == "1":
        sortEquity(my_stocks)

    elif option == "2":
        peRATIOsort(my_stocks)

    elif option == "3":
        cryptoView(r)

    elif option == "4":
        getRatings(my_stocks , r)

    elif option == "5":
        Dividend_Sort(my_stocks)

    elif option == "6":
        dividends(r)

    elif option == "7":
        writeData(my_stocks)

    elif option == "8":
        industrySort(r , my_stocks)

    elif option == "9":
        SectorSort(r , my_stocks)

    elif option == "10":
        ReturnChart(r , my_stocks)

    elif option == "11":
        DailyMovement(r , my_stocks)

    elif option == "12":
        GetEarnings(r , my_stocks)

    elif option == "13":
        GetNews( r , my_stocks)

    elif option == "14":
        instrumentalBeatswtf( r , my_stocks)

    elif option == "15":
        DailyMovementPercent( r , my_stocks)

    elif option == "16":
        ReturnChartPercentage( r , my_stocks)



    elif option == "omg":
        nuke(  my_stocks ,   r )

    elif option == "rebuy":
        rebuy(my_stocks , r )

    elif option == "help":
        app_help()

    # elif option == "watchlist":
    #     watchlist(r)

    elif option == "end" or option == "":
        endprogram = True

    elif option == "reset" or option == "refresh" :
        main()
    
    else:
        print("\nERROR: Invalid option, please try again.\n")

def login():
    global username , password
    
    # CREDENTIALS
    config = configparser.ConfigParser()
    config.read("secrets.ini")
    username = config["CREDENTIALS"]["username"]
    password = config["CREDENTIALS"]["password"]

    # auto login
    r.login(username,password)
    print("Login successful\n")
    return r

def sortEquity(my_stocks):

    payout = []

    for key, value in my_stocks.items():

        if (float(value.get("quantity")) - round(float(value.get("quantity"))) ) != 0:
            average_buy_price = float(value.get("average_buy_price")) * float(value.get("quantity"))
            price = float(value.get("price"))* float(value.get("quantity"))

        else:
            average_buy_price = float(value.get("average_buy_price"))
            price = float(value.get("price"))

        payout_price = float(price) - float(average_buy_price)
        payout.append(  (key,'{0:.2f}'.format(payout_price) ) )

    payout = Sort_Tuple(payout)
    
    with open("sort_equity.json", "a") as f:
        json.dump(payout, f)

    with open("my-stocks.json", "a") as f:
        json.dump(my_stocks, f)

    pprint.pprint(payout)

def peRATIOsort(my_stocks):
    
    payout = []

    for key, value in my_stocks.items():
        pe_ratio = value.get("pe_ratio")
        if pe_ratio == None:
            pe_ratio = 0.00
        payout.append(  (key, pe_ratio ) )


    payout = Sort_Tuple(payout)

    with open("peRATIOsort.json", "a") as f:
        json.dump(payout, f)

    pprint.pprint(payout)

def Dividend_Sort(my_stocks):
    
    dividends = []

    for key, value in my_stocks.items():
        total_dividend = value.get("dividend_rate")
        # total_dividend = value.get("total_dividend")
        if total_dividend == None:
            total_dividend = 0.00
        dividends.append(  (key, total_dividend ) )


    dividends = Sort_Tuple(dividends)

    with open("div-sort.json", "a") as f:
        json.dump(payout, f)

    pprint.pprint(dividends)

def cryptoView(r):
    crypto = r.crypto.get_crypto_positions()

    owned_coins = []

    for dictionary in crypto:

        symbol = dictionary["currency"]["code"]
        name = dictionary["currency"]["name"]
        quantity = dictionary["quantity_available"]
        cost = dictionary["cost_bases"][0]["direct_cost_basis"]
        quote = r.crypto.get_crypto_quote(symbol, info = "ask_price")

        quote = float(quote) * float(quantity)

        if float(quantity) == 0 :
            continue
        else:

            print()

            print( name , symbol)
            print( "Quantity: ", quantity)
            print( "Profit: " , float(quote) - float(cost))


            print()
    
    with open("div-sort.json", "a") as f:
        json.dump(dictionary, f)

def getRatings(my_stocks, r):

    #building rating_data
    rating_data = []
    strings = []
    for key, value in my_stocks.items():
        stock_data = r.stocks.get_ratings(key,info = "summary")

        if type(stock_data) is str:
            rating_data.append((key , 0))
            strings.append(stock_data)

        elif stock_data.get("ratings") == []:
            rating_data.append((key , 0))
        else:
            rating_data.append([key , stock_data])


    # building buy_rating_arr
    buy_rating_arr = []
    for ticker , dictionary in rating_data:
        if dictionary == 0 :
            continue
        else:
            buy_rating = int(dictionary["num_buy_ratings"]) / (int(dictionary["num_buy_ratings"]) + int(dictionary["num_hold_ratings"]) + int(dictionary["num_sell_ratings"]))
            buy_rating_arr.append((ticker, buy_rating))

    # SORT
    buy_rating_arr = Sort_Tuple(buy_rating_arr)
    pprint.pprint(buy_rating_arr)
    pprint.pprint(strings)












    #DEBUG comment out
    # rating_data = []
    # for key, value in my_stocks.items():
    #     stock_data = r.stocks.get_ratings( key , info = "summary")
    #     print(key)
    #     print(type(stock_data))
    #     print()

def app_help():
    print('\n')
    print("1: Top preformors - Sorted list of all stock profits")
    print("2: Profit / Exspense ratio sort - Sorted ratios of all stocks' money in vs money out")
    print("3: Crypto - Crypto information pertaining to your account")
    print("4: Rating for all my stocks - Analyst buy rating percentage sorted2")
    print("5: Dividend Prospective - Displays how much each stock gives in dividends\n")
    print("6: Dividend Payment History - Stock Dividend History\n")

    # print("watchlist: Account Watchlist Interface")
    print("rebuy: CAUTION: REBUYS ALL STOCKS AT LEAST ONCE")
    print("reset / restart: Refreshing app data")

def dividends(r):
    dividends = r.account.get_dividends(info=None)
    dividends = reversed(dividends)

    paid = []
    pending = []

    for x in dividends:
        amount = x["amount"]
        payable_date = x['payable_date']
        state = x['state']

        print()
        print(amount)
        print(payable_date)
        print(state)
        # print(x['id'])
        print()

        if state == "paid":
            paid.append(float(amount))
        elif state == "pending":
            pending.append(float(amount))
        else:
            pass

    paid_div_total = sum(paid)
    pending_div_total = sum(pending)

    print("You have earned: " + str( paid_div_total ) )
    print("You will earn: " + str( pending_div_total ) + " by " + payable_date  )

        #you can add ticker using that ID

def rebuy(my_stocks , r ):
    print("CAUTION: YOU NEED MONEY TO DO THIS FUNCTION")
    print("CAUTION: AT LEAST ONE DOLLAR IN EACH STOCK")
    print("CAUTION: THIS FUNCTION WILL REBUY ALL YOUR STOCKS AT LEAST ONCE...\n")
    

    all_stocks = []
    for key, value in my_stocks.items():
        # value.get("price")
        all_stocks.append(key)
    
    at_least = len(all_stocks)

    print(all_stocks)
    print("You must spend at least: $" + str( at_least )  )
    print()
    
    proceed = False
    option = input('Please type "Proceed" in order to continue: ')

    if option == 'Proceed':
        proceed = True
    else:
        print(' Resetting Application...\n')
        main()

    if proceed == True:

        money_valid = False

        while money_valid == False:
            how_much = input("please specify total amount you want to spend into re-investing towards your portfollio [NUMBERS ONLY ,decimal is okay...]: ")

            if float(how_much) >= at_least:
                money_valid = True
            else:
                print("ERROR: total investment cost must be more than: ", str(at_least) )

        how_much = float(how_much)
        reinvest_in_each = (how_much / at_least)

        reinvest_in_each = "{:.2f}".format(reinvest_in_each)
        reinvest_in_each = float(reinvest_in_each)

        print("You will invest: $" + str(reinvest_in_each)  )

        for key, value in my_stocks.items():
            # value.get("price")
            price = float(value.get("price"))
            difference = price - float(reinvest_in_each)
            percentage = float(difference) / price
            percentage = 1 - percentage
            percentage -= .000001
            quantity = "{:.6f}".format(percentage)
            print(quantity)

            buy = r.orders.order_buy_fractional_by_price(key, reinvest_in_each, timeInForce='gfd')
            print(buy)
            time.sleep(20)

def nuke( my_stocks , r):

    with open('STOCKS.txt', 'a', encoding='utf-8') as f:

        for key, value in my_stocks.items():
            # value.get("price")
            quantity = value.get("quantity")

            f.write(key)
            f.write('\n')
            f.write(quantity)
            f.write('\n')
            f.write('\n')

            print(key)
            print(float(quantity) - .0005)
            print()

            sell = r.orders.order( key , quantity , "market", "immediate", "sell",  timeInForce='gfd')
            print(sell)
            print()
            time.sleep(2)

def writeData(my_stocks):
    with open('All_Data.txt', 'a', encoding='utf-8') as f:

        for key, value in my_stocks.items():
            amount_paid_to_date = value.get("amount_paid_to_date")
            average_buy_price = value.get("average_buy_price")
            dividend_rate = value.get("dividend_rate")
            equity_change = value.get("equity_change")
            stock_id = value.get("id")
            name = value.get("name")
            pe_ratio = value.get("pe_ratio")
            percent_change = value.get("percent_change")
            percentage = value.get("percentage")
            price = value.get("price")
            quantity = value.get("quantity")
            total_dividend = value.get("total_dividend")
            stock_type = value.get("type")



            # WRITING DATA INTO FILE
            f.write(key)
            f.write('\n')


            if amount_paid_to_date == None:
                f.write("Dividend amount paid to date: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("Dividend amount paid to date: ")
                f.write(amount_paid_to_date)
                f.write('\n')


            if average_buy_price == None:
                f.write("average_buy_price: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("average_buy_price: ")
                f.write(average_buy_price)
                f.write('\n')


            if dividend_rate == None:
                f.write("dividend_rate: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("dividend_rate: ")
                f.write(dividend_rate)
                f.write('\n')


            if equity_change == None:
                f.write("equity_change: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("equity_change: ")
                f.write(equity_change)
                f.write('\n')


            if stock_id == None:
                f.write("stock_id: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("stock_id: ")
                f.write(stock_id)
                f.write('\n')


            if name == None:
                f.write("name: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("name: ")
                f.write(name)
                f.write('\n')


            if pe_ratio == None:
                f.write("pe_ratio: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("pe_ratio: ")
                f.write(pe_ratio)
                f.write('\n')


            if percent_change == None:
                f.write("percent_change: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("percent_change: ")
                f.write(percent_change)
                f.write('\n')


            if percentage == None:
                f.write("percentage: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("percentage: ")
                f.write(percentage)
                f.write('\n')


            if price == None:
                f.write("price: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("price: ")
                f.write(price)
                f.write('\n')


            if quantity == None:
                f.write("quantity: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("quantity: ")
                f.write(quantity)
                f.write('\n')


            if total_dividend == None:
                f.write("total_dividend: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("total_dividend: ")
                f.write(total_dividend)
                f.write('\n')


            if stock_type == None:
                f.write("stock_type: ")
                f.write(" N/A")
                f.write('\n')
            else:
                f.write("stock_type: ")
                f.write(stock_type)
                f.write('\n')

            f.write('\n')

def industrySort(r , my_stocks):
    industries = []
    equity_values = []

    for key , value in my_stocks.items():
        equity = value.get("equity")

        fundamental = r.stocks.get_fundamentals(key)
        industries.append(fundamental[0]["industry"])
        equity_values.append(equity)

        print(key)
        print(equity)
        print(fundamental[0]["industry"])
        print()

    labels = tuple(set(industries))
    sizes = []
    equity_sizes = []
    for x in range(len(labels)):
        count = 0
        equity_count = 0
        for y in range(len(industries)):
            if labels[x] == industries[y]:
                equity_count += float(equity_values[y])
                count+= 1 
        sizes.append(count)
        equity_sizes.append(equity_count)

    #graphing
    bar_chart(list(labels), equity_sizes, "Industries" , "Equity in Industries" , "Industries Equity", "green")
    piechart(labels , equity_sizes)

    bar_chart(list(labels), sizes, "Industries" , "Amount Of Stocks" , "Industry Count", "blue")
    piechart(labels , sizes)

def SectorSort(r , my_stocks):
    sectors = []
    equity_values = []

    for key , value in my_stocks.items():
        equity = value.get("equity")

        fundamental = r.stocks.get_fundamentals(key)
        sectors.append(   (fundamental[0]["sector"]   )    )
        equity_values.append(equity)

        print(key)
        print(equity)
        print(fundamental[0]["sector"])
        print()

    labels = tuple(set(sectors))
    sizes = []
    equity_sizes = []
    for x in range(len(labels)):
        count = 0
        equity_count = 0
        for y in range(len(sectors)):
            if labels[x] == sectors[y]:
                equity_count += float(equity_values[y])
                count+= 1 
        sizes.append(count)
        equity_sizes.append(equity_count)

    #graphing
    bar_chart(list(labels), equity_sizes, "Sectors" , "Equity in Sector" , "Sector Equity", "green")
    piechart(labels , equity_sizes)
    
    bar_chart(list(labels), sizes, "Sectors" , "Amount Of Stocks in Each Sector" , "Sector Count", "blue")
    piechart(labels , sizes)

def ReturnChart(r , my_stocks):
    xPOS = []
    yPOS = []

    xNEG = []
    yNEG = []

    for key , value in my_stocks.items():
        average_buy_price = value['average_buy_price']
        current = value['price']


        returns =float(current) - float(average_buy_price)

        if returns > 0 :
            xPOS.append(key)
            yPOS.append( returns )
        else:
            xNEG.append(key)
            yNEG.append( returns )

        #debug
        print(key)
        print(average_buy_price)
        print(current)
        print()

    bar_chart(xPOS , yPOS , 'Tickers' , 'Growth' , 'Movment' , 'green')
    bar_chart(xNEG , yNEG , 'Tickers' , 'Loss' , 'Movment' , 'red')

def ReturnChartPercentage(r , my_stocks):
    xPOS = []
    yPOS = []

    xNEG = []
    yNEG = []

    for key , value in my_stocks.items():
        average_buy_price = value['average_buy_price']
        current = value['price']


        returns =float(current) / float(average_buy_price)
        returns -= 1

        if returns > 0 :
            xPOS.append(key)
            yPOS.append( returns )
        else:
            xNEG.append(key)
            yNEG.append( returns )

        #debug
        print(key)
        print(average_buy_price)
        print(current)
        print()

    bar_chart(xPOS , yPOS , 'Tickers' , 'Growth' , 'Movment' , 'green')
    bar_chart(xNEG , yNEG , 'Tickers' , 'Loss' , 'Movment' , 'red')

def DailyMovement(r , my_stocks):
    xPOS = []
    yPOS = []

    xNEG = []
    yNEG = []

    for key , value in my_stocks.items():
        if key =='BRK.A':
            continue
        price = value['price']
        historical =  r.stocks.get_stock_quote_by_symbol(key, info=None)
        close_price = historical['previous_close']


        returns =float(price) - float(close_price)

        if returns > 0 :
            xPOS.append(key)
            yPOS.append( returns )
        else:
            xNEG.append(key)
            yNEG.append( returns )

        #debug
        print(key)
        print(price)
        print(close_price)
        print()




    bar_chart(xPOS , yPOS , 'Tickers' , 'Growth' , 'Movment' , 'green')
    bar_chart(xNEG , yNEG , 'Tickers' , 'Loss' , 'Movment' , 'red')

def DailyMovementPercent(r , my_stocks):
    xPOS = []
    yPOS = []

    xNEG = []
    yNEG = []

    for key , value in my_stocks.items():
        price = value['price']
        historical =  r.stocks.get_stock_quote_by_symbol(key, info=None)
        close_price = historical['previous_close']


        returns = float(price) / float(close_price)
        returns -= 1

        if returns > 0 :
            xPOS.append(key)
            yPOS.append( returns )
        else:
            xNEG.append(key)
            yNEG.append( returns )

        #debug
        print(key)
        print(price)
        print(close_price)
        print()




    bar_chart(xPOS , yPOS , 'Tickers' , 'Growth' , 'Movment' , 'green')
    bar_chart(xNEG , yNEG , 'Tickers' , 'Loss' , 'Movment' , 'red')

def GetEarnings(r , my_stocks):
    for key , value in my_stocks.items():
        earnings = r.stocks.get_earnings(key, info=None)
        print(key)
        pprint.pprint(earnings)
        print()

def GetNews(r , my_stocks):
    for key , value in my_stocks.items():
        news = r.stocks.get_news(key, info=None)
        print(key)
        pprint.pprint(news)
        print()

def instrumentalBeatswtf(r , my_stocks):
    for key , value in my_stocks.items():
        instrument = r.stocks.get_instruments_by_symbols(key, info=None)
        
        print(key)
        pprint.pprint(instrument)
        print()

#functional... functions?
def bar_chart(x , y , X_label , Y_label, Title , color_input):

    plt.style.use('ggplot')

    # x = []
    # y = []

    x_pos = [i for i, _ in enumerate(x)]
    plt.bar(x_pos, y, color= color_input ) #STR ex: "green"
    plt.xlabel(X_label)
    plt.ylabel(Y_label)
    plt.title(Title)
    plt.xticks(x_pos, x)

    # plt.tick_params(axis='x', which='major', labelsize=3)

    plt.xticks(rotation=90)

    plt.show()
def piechart(labels , sizes):
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()
def Sort_Tuple(tup):
    lst = len(tup)
    for i in range(0, lst):
        for j in range(0, lst-i-1):
            if (float(tup[j][1]) > float(tup[j + 1][1])):
                temp = tup[j]
                tup[j]= tup[j + 1]
                tup[j + 1]= temp
    return tup



# calling functions here!
main()
