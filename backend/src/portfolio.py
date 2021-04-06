########################
#   Portfolio Module   #
########################

import time
from flask import Blueprint, request
from json import dumps
from database import create_DB_connection
from token_util import get_id_from_token
from helpers import TimeSeries, AlphaVantageAPI
from datetime import datetime
from stock import retrieve_stock_price_at_date
from iexfinance.stocks import Stock
import pandas as pd

PORTFOLIO_ROUTES = Blueprint('portfolio', __name__)


###################################
# Please leave all functions here #
###################################


# Create portfolio object in the database
def create_portfolio(user_id, portfolio_name):
    # Check name is within the max length
    if len(portfolio_name) >= 30:
        return {'status': 400, 'message': 'Portfolio name must be less than 30 characters.'}

    conn = create_DB_connection()
    cur = conn.cursor()
    # check that (portfolio_name, user_id) is unique
    sql_query = "SELECT * FROM Portfolios WHERE portfolio_name=%s AND user_id=%s"
    cur.execute(sql_query, (portfolio_name, user_id))
    query_results = cur.fetchall()
    if not query_results:
        # If the user has no portfolios called portfolio_name, create a portfolio with that name.
        sql_query = "INSERT INTO Portfolios (portfolio_name, user_id) VALUES (%s, %s)"
        cur.execute(sql_query, (portfolio_name, user_id))
        conn.commit()
        response = {
            'status': 200,
            'message': 'Portfolio called \'' + portfolio_name + '\' has been created.'
        }
    else:
        response = {
            'status': 400,
            'message': 'Already a portfolio named \'' + portfolio_name + '\'.'
        }
    # Close connection and return response
    conn.close()
    return response


# Edit portfolio (e.g. change name of portfolio) in database
# Note: does not check whether old_portfolio_name actually exists. If it does exist, it changes its name to newportfolio_name. Otherwise does noting.
def edit_portfolio(user_id, old_portfolio_name, new_portfolio_name):
    # Check new name is within the max length
    if len(new_portfolio_name) >= 30:
        return {'status': 400, 'message': 'Portfolio name must be less than 30 characters.'}

    conn = create_DB_connection()
    cur = conn.cursor()
    # check that (new_portfolio_name, user_id) is unique in portfolio table
    sql_query = "SELECT * FROM Portfolios WHERE portfolio_name=%s AND user_id=%s"
    cur.execute(sql_query, (new_portfolio_name, user_id))
    query_results = cur.fetchall()
    if not query_results:
        # update portfolio table
        sql_query = "UPDATE Portfolios SET portfolio_name=%s WHERE portfolio_name=%s AND user_id=%s"
        cur.execute(sql_query, (new_portfolio_name, old_portfolio_name, user_id))
        # update holdings table
        sql_query = "UPDATE Holdings SET portfolio_name=%s WHERE portfolio_name=%s AND user_id=%s"
        cur.execute(sql_query, (new_portfolio_name, old_portfolio_name, user_id))
        response ={
            'status': 200,
            'message' : '\'' + old_portfolio_name + "\' has been changed to \'" + new_portfolio_name + "\'."
        }
        # TODO: update notes table
    else:
        response = {
            'status' : 400,
            'message' : 'Already a portfolio named' + new_portfolio_name + '.'
        }
    # Commit changes, close connection and return response to user
    conn.commit()
    conn.close()
    return response


# Delete portfolio object from the database
# Note: this function does not check whether user_id or portfolio exists. It just deletes them if they exist
def delete_portfolio(user_id, portfolio_name):
    conn = create_DB_connection()
    cur = conn.cursor()
    # Delete from portfolio table
    sql_query = "DELETE FROM Portfolios WHERE portfolio_name=%s AND user_id=%s"
    cur.execute(sql_query, (portfolio_name, user_id))
    # Delete from holdings table
    sql_query = "DELETE FROM Holdings WHERE portfolio_name=%s AND user_id=%s"
    cur.execute(sql_query, (portfolio_name, user_id))
    # Commit changes, close connection and return response to user
    conn.commit()
    conn.close()
    return {'status' : 200, 'message' : "Portfolio named \'" + portfolio_name + "\' has been deleted."}


############# Investment helper functions #################
def total_stock_change(stock_ticker, purchase_price):
    # Get investment current price
    quick_data = TimeSeries().get_quick_quote(stock_ticker)
    current_price = float(quick_data['Global Quote']['05. price'])
    return (current_price - purchase_price)*100 / purchase_price


# Add investments to portfolio object in database
# Note: this assumes portfolio_name and all the other inputs are of the correct size and data type
def add_investment(user_id, portfolio_name, num_shares, timestamp, stock_ticker):
    # Validate date
    purchase_date = datetime.fromtimestamp(timestamp)
    if purchase_date > datetime.now():
        return {
            'status': 400,
            'error': 'Invalid purchase date, date must be in the past/present'
        }
    conn = create_DB_connection()
    cur = conn.cursor()
    purchase_price = retrieve_stock_price_at_date(stock_ticker, purchase_date)
    # Execute query and close connections
    sql_query = "INSERT INTO Holdings (user_id, portfolio_name, purchase_price, num_shares, purchase_date, stock_ticker) VALUES (%s, %s, %s, %s, %s, %s)"
    cur.execute(sql_query, (user_id, portfolio_name, purchase_price, num_shares, purchase_date.strftime('%Y-%m-%d %H:%M:%S'), stock_ticker))
    conn.commit()
    conn.close()
    return {'status' : 200, 'message' : "Investment in " + stock_ticker + " has been added to portfolio named \'" + portfolio_name + "\'."}


# Delete investments from portfolio object in database
def delete_investment(investment_id):
    conn = create_DB_connection()
    cur = conn.cursor()
    # Delete from holdings table
    sql_query = "delete from Holdings where investment_id=%s"
    cur.execute(sql_query, (investment_id, ))
    conn.commit()
    conn.close()
    return {'status' : 200, 'message' : "Investment removed successfully."}


# Get an individual investment's total performance
# Note: this assumes investment_id is correct.
def get_investment_tc(investment_id):
    conn = create_DB_connection()
    cur = conn.cursor()
    # Get investment purchase price
    sql_query = "SELECT purchase_price, stock_ticker FROM Holdings WHERE investment_id=%s"
    cur.execute(sql_query, (investment_id, ))
    query_results = cur.fetchall()
    purchase_price = float(query_results[0][0])
    stock_ticker = query_results[0][1]
    # Compute total change
    total_change = total_stock_change(stock_ticker, purchase_price)
    conn.close()
    return {
        'status' : 200,
        'data' : {
            'id': investment_id,
            'total_change': total_change
        }
    }

# Get the 'trendiness' of each invested stock symbol
def get_trending_investments(num):
    conn = create_DB_connection()
    cur = conn.cursor()
    sql_query = "SELECT stock_ticker, count(distinct user_id) AS user_count FROM Holdings GROUP BY stock_ticker ORDER BY user_count DESC limit %s"
    cur.execute(sql_query, (num, ))
    query_results = cur.fetchall()
    data = []
    for tupl in query_results:
        data.append({
            'stock': tupl[0],
            'count': tupl[1]
        })
    conn.close()
    return {'status': 200, 'data': data}


############ Additional functions ##############
def get_portfolios(user_id):
    conn = create_DB_connection()
    cur = conn.cursor()
    sql_query = "SELECT portfolio_name FROM Portfolios WHERE user_id=%s"
    cur.execute(sql_query, (user_id, ))
    query_results = cur.fetchall()
    data = []
    for tupl in query_results:
        data.append(tupl[0])
    conn.close()
    return {'status' : 200, 'data' : data}


def get_investments(user_id, portfolio_name):
    conn = create_DB_connection()
    cur = conn.cursor()
    sql_query = "SELECT * FROM Holdings WHERE user_id=%s AND portfolio_name=%s"
    cur.execute(sql_query, (user_id, portfolio_name))
    query_results = cur.fetchall()
    data = []
    for row in query_results:
        new_investment = {
            'investment_id': row[0],
            'purchase_price': str(row[3]),
            'num_shares': row[4],
            'purchase_date': row[5].strftime("%Y-%m-%d"),
            'total_change': total_stock_change(row[6], float(row[3])),
            'stock_ticker': row[6]
        }
        data.append(new_investment)

    conn.close()
    return {'status' : 200, 'data' : data}


def get_portfolio_performance(user_id, portfolio_name):
    conn = create_DB_connection()
    cur = conn.cursor()
    sql_query = "SELECT * FROM Holdings WHERE user_id=%s AND portfolio_name=%s"
    try:
        cur.execute(sql_query, (user_id, portfolio_name))
    except:
        return {'status' : 400, 'error' : 'Something went wrong while searching Holdings table for user_id = \'' + str(user_id) + '\' and portfolio_name = \'' + str(portfolio_name) + '\'.'}
    query_results = cur.fetchall()
    if not query_results:
        return {'status' : 400, 'error' : 'There are no investments in a portfolio called \'' + portfolio_name + '\'.'}
    conn.close()
    
    # Fill the data dictionary with investments and collect the stock tickers for a batch API call
    data = {'investments' : []}
    stocks = []
    for row in query_results:
        stock_ticker = row[6]
        if stock_ticker not in stocks:
            stocks.append(stock_ticker)

        new_investment = {
            'investment_id': row[0],
            'purchase_price': str(row[3]),
            'num_shares': row[4],
            'purchase_date': row[5].strftime("%Y-%m-%d"),
            'stock_ticker': stock_ticker
        }
        data['investments'].append(new_investment)

    # Fetch stock prices
    batch = Stock(stocks)
    batch = batch.get_quote()
    total_value_change = 0
    total_invested_capital = 0
    for investment in data['investments']:
        value_change = batch.latestPrice[investment['stock_ticker']] - float(investment['purchase_price'])
        investment['total_change'] = (value_change * 100) / float(investment['purchase_price'])
        total_value_change += value_change
        total_invested_capital += float(investment['purchase_price'])

    data['portfolio_change'] = (total_value_change * 100) / total_invested_capital
    response = {
        'status' : 200, 
        'message' : 'Successfully calculated the performance of portfolio \'' + portfolio_name + '\', as well as its individual investments.', 
        'data' : data}
    return response


################################
# Please leave all routes here #
################################

# Get the list of portfolios owned by a user
@PORTFOLIO_ROUTES.route('/user/portfolio', methods=['GET'])
def get_user_portfolios_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    return dumps(get_portfolios(user_id))


# Get the list of investments of a portfolio owned by a user
@PORTFOLIO_ROUTES.route('/user/investment', methods=['GET'])
def get_user_portfolio_investments_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    portfolio_name = request.args.get('portfolio')
    return dumps(get_investments(user_id, portfolio_name))


# Create a new portfolio
@PORTFOLIO_ROUTES.route('/portfolio', methods=['POST'])
def create_user_portfolio_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    portfolio_name = request.args.get('name')
    response = create_portfolio(user_id, portfolio_name)
    return dumps(response)


# Modify an existing portfolio
@PORTFOLIO_ROUTES.route('/portfolio', methods=['PUT'])
def edit_user_portfolio_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    old_portfolio_name = request.args.get('name')
    data = request.get_json()
    new_portfolio_name = data['name']
    response = edit_portfolio(user_id, old_portfolio_name, new_portfolio_name)
    return dumps(response)


# Delete an existing portfolio
@PORTFOLIO_ROUTES.route('/portfolio', methods=['DELETE'])
def delete_user_portfolio_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    portfolio_name = request.args.get('name')
    response = delete_portfolio(user_id, portfolio_name)
    return dumps(response)


# Get total change of an existing investment
@PORTFOLIO_ROUTES.route('/investment/total-change', methods=['GET'])
def get_investment_total_change_wrapper():
    investment_id = request.args.get('id')
    return dumps(get_investment_tc(investment_id))


# Get trending investments
@PORTFOLIO_ROUTES.route('/investment/trending', methods=['GET'])
def get_investment_trending_wrapper():
    num = request.args.get('n')
    response = get_trending_investments(num)
    return dumps(response)

# Create a new investment
# Expects payload:
'''
    num_shares: number
    stock_ticker: string
    purchase_date: number (in UNIX timestamp format, i.e. seconds since 1970)
'''
@PORTFOLIO_ROUTES.route('/investment', methods=['POST'])
def add_investment_user_portfolio_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    data = request.get_json()
    portfolio_name = request.args.get('portfolio')
    num_shares = data['num_shares']
    stock_ticker = data['stock_ticker']
    purchase_date = int(data['purchase_date'])
    response = add_investment(user_id, portfolio_name, num_shares, purchase_date, stock_ticker)
    return dumps(response)


# Delete an existing investment
@PORTFOLIO_ROUTES.route('/investment', methods=['DELETE'])
def delete_investment_user_portfolio_wrapper():
    investment_id = request.args.get('id')
    return dumps(delete_investment(investment_id))


# Get the performance of a portfolio and its individual investments.
@PORTFOLIO_ROUTES.route('/user/portfolio/performance', methods=['GET'])
def get_portfolio_performance_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    portfolio_name = request.args.get('name')
    response = get_portfolio_performance(user_id, portfolio_name)
    return dumps(response)


############ Tests #############
# create_portfolio('4', 'Austin\'s portfolio')
# create_portfolio('4', 'Austi')
# edit_portfolio('4', 'Austin\'s portfolio', 'Bob\'s portfolio')
# delete_portfolio('4', 'Bob\'s portfolio')
# delete_portfolio('4', 'Austi')
# add_investment('7', 'Sally\'s portfolio', '50', 1611061200, 'BHP')
# get_investment("2380756e-863c-11eb-af93-0a4e2d6dea13")
# get_trending_investments('10')

# print(total_stock_change("IBM", 100))
# print(total_stock_change("BHP", 100))
# print(total_stock_change("LIN", 100))
# print(total_stock_change("JPM", 100))
# print(total_stock_change("MA", 100))


# stock = "IBM"
# batch = Stock([stock])
# batch = batch.get_quote()
# print(batch.latestPrice[stock])
# batch = pd.DataFrame(batch)
# print(batch.loc[stock, "latestPrice"])
# for key, value in batch.items():
#     print(key, " : ", value)

#create_portfolio("02708412-912d-11eb-a6dc-0a4e2d6dea13", "Portfolio Performance test")
# add TSLA, IBM
#add_investment("02708412-912d-11eb-a6dc-0a4e2d6dea13", "Portfolio Performance test", 1, time.time(), "IBM")
#add_investment("02708412-912d-11eb-a6dc-0a4e2d6dea13", "Portfolio Performance test", 1, time.time(), "ORCL")
#dd_investment("02708412-912d-11eb-a6dc-0a4e2d6dea13", "Portfolio Performance test", 1, time.time(), "IBM")
# test 
print(get_portfolio_performance("02708412-912d-11eb-a6dc-0a4e2d6dea13", "Portfolio Performance test"))
