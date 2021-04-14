#######################
#   Screener Module   #
#######################
import time
from flask import Blueprint, request
from json import dumps, loads
from database import create_DB_connection
from token_util import get_id_from_token
from datetime import datetime
import psycopg2
from stock import retrieve_stock_price_at_date
from iexfinance.stocks import Stock
import pandas as pd
from psycopg2.extras import RealDictCursor
import psycopg2.extras

from flask import Blueprint

SCREENER_ROUTES = Blueprint('screener', __name__)


###################################
# Please leave all functions here #
###################################

def screener_save(screener_name, user_id, parameters):

    if len(screener_name) > 30:
        rtrn = {
            'status' : 400,
            'error' : 'Screener name cannot be more than 30 characters. Try a new name.'
        }
        return rtrn

    conn = create_DB_connection()
    cur = conn.cursor()
    sql_query = "INSERT INTO screeners (screener_name, user_id, parameters) VALUES (%s, %s, %s)"
    try:
        cur.execute(sql_query, (screener_name, user_id, str(parameters)))
        rtrn = {
            'status' : 200,
            'message' : 'Parameters saved under the name \'' + screener_name + '\'.'
        }
    except psycopg2.errors.UniqueViolation:
        rtrn = {
            'status' : 400,
            'error' : 'There is already a screener called \'' + screener_name + '\'. Try another name.'
        }
    except:
        rtrn = {
            'status' : 400,
            'error' : 'Something went wrong while inserting.'
        }
    conn.commit()
    conn.close()
    return rtrn


def screener_load_all(user_id):
    conn = create_DB_connection()
    cur = conn.cursor()
    sql_query = "SELECT screener_name, parameters FROM screeners where user_id=%s"
    try:
        cur.execute(sql_query, (user_id, ))
        response = cur.fetchall()
        if not response:
            rtrn = {
                'status' : 400,
                'error' : 'User with user_id \'' + str(user_id) + '\' does not have any screeners.'
            }
        else:
            data =[]
            for row in response:
                new_screener = {
                    'name' : row[0],
                    'params' : eval(row[1])
                }
                data.append(new_screener)

            rtrn = {
                'status' : 200,
                'message' : 'Screener load successful.',
                'data' : data
            }
    except:
        rtrn = {
            'status' : 400,
            'error' : 'Something went wrong while fetching parameters.'
        }
    conn.close()
    return rtrn


def screener_delete(screener_name, user_id):
    conn = create_DB_connection()
    cur = conn.cursor()
    sql_query = "DELETE FROM screeners WHERE screener_name=%s AND user_id=%s"
    cur.execute(sql_query, (screener_name, user_id))
    conn.commit()
    conn.close()
    return {'status' : 200, 'message' : "Screen called \'" + screener_name + "\' have been removed."}


# Not being used?
def screener_edit_parameters(screener_name, user_id, parameters):
    conn = create_DB_connection()
    cur = conn.cursor()
    sql_query = "UPDATE screeners SET parameters=%s WHERE screener_name=%s AND user_id=%s"
    try:
        cur.execute(sql_query, (str(parameters), screener_name, user_id))
        rtrn = {
            'status' : 200,
            'message' :  'Screen called \'' + screener_name + '\' has been updated.'
        }
    except:
        rtrn = {
            'status' : 400,
            'error' : 'Something went wrong when updating screeners.'
        }
    conn.commit()
    conn.close()
    return rtrn

def screen_stocks(parameters):
    if not isinstance(parameters, dict):
        rtrn = {
            'status' : 400,
            'error' : 'Parameters must be a dictionary.'
        }

    conn = create_DB_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    overviews_query = "SELECT stock_ticker FROM securities_overviews WHERE "
    values = []
    for key, item in parameters['securities_overviews'].items():
        if key in ["region", "sector", "industry"]:
            continue
        new_param = ""
        if isinstance(item, str) or isinstance(item, (int, float)):
            new_param = "{key}=%s".format(key=key)
            values.append(item)
        else:
            min = item[0]
            max = item[1]
            if (min != None and max != None):
                new_param = "{key} > %s AND {key} < %s".format(key=key)
                values.append(min)
                values.append(max)
            elif (min == None):
                new_param = "{key} < %s".format(key=key)
                values.append(max)
            else:
                new_param = "{key} > %s".format(key=key)
                values.append(min)
        overviews_query += new_param
        overviews_query += " AND "
    overviews_query = overviews_query[:-5]
    values = tuple(values)
    cur.execute(overviews_query, values)

    rtrn = cur.fetchall()
    if not rtrn:
        data = {
            "status" : 400,
            "error" : "There are no stocks which fit those parameters."
            }
    else:
        stocks = []
        for s in rtrn:
            stocks.append(s['stock_ticker'])
        batch = Stock(stocks)
        batch = batch.get_quote()
        data = {
            "status" : 200,
            "message" : "Screen successfull.",
            "data" : []
        }
        for s in stocks:
            new_stock = {
                'stock ticker' : s,
                'price' : batch.latestPrice[s],
                'price change' : batch.change[s],
                'price change percentage' : batch.changePercent[s],
                'volume' : batch.volume[s],
                'market capitalization' : batch.marketCap[s],
                'PE ratio' : batch.peRatio[s]
            }
            data['data'].append(new_stock)

    conn.close()
    return data


################################
# Please leave all routes here #
################################

@SCREENER_ROUTES.route('/screener/save', methods=['POST'])
def screener_save_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    screener_name = request.args.get('name')
    data = request.get_json()
    result = screener_save(screener_name, user_id, data['parameters'])
    return dumps(result)


@SCREENER_ROUTES.route('/screener/load', methods=['GET'])
def screener_load_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    result = screener_load_all(user_id)
    return dumps(result)


@SCREENER_ROUTES.route('/screener', methods=['DELETE'])
def screener_delete_wrapper():
    token = request.headers.get('Authorization')
    user_id = get_id_from_token(token)
    screener_name = request.args.get('name')
    result = screener_delete(screener_name, user_id)
    return dumps(result)

@SCREENER_ROUTES.route('/screener', methods=['GET'])
def screen_stocks_wrapper():
    import pdb; pdb.set_trace()
    # data = request.get_json()
    # parameters = data['parameters']
    region = request.args.getlist("region")
    market_cap = request.args.get("market_cap")
    yearly_low = float(request.args.get("yearly_low"))
    yearly_high = request.args.get("yearly_high")
    eps = request.args.getlist("eps")[0:2]
    beta = request.args.getlist("beta")[0:2]
    payout_ratio = request.args.getlist("payout_ratio")[0:2]


    eps[0] = float(eps[0]) if eps[0] else None
    eps[1] = float(eps[1]) if eps[1] else None
    beta[0] = float(beta[0]) if beta[0] else None
    beta[1] = float(beta[1]) if beta[1] else None
    payout_ratio[0] = float(payout_ratio[0]) if payout_ratio[0] else None
    payout_ratio[1] = float(payout_ratio[1]) if payout_ratio[1] else None

    sector = request.args.getlist("sector")
    industry = request.args.getlist("Industry")
    parameters = {
        "securities_overviews": {
            "region": region,
            "market_cap": market_cap,
            "yearly_low": yearly_low,
            "yearly_high": yearly_high,
            "eps": eps,
            "beta": beta,
            "payout_ratio": payout_ratio,
            "sector": sector,
            "industry": industry,
        }
    }
    return dumps(screen_stocks(parameters))



if __name__ == "__main__":
    test = {
        'securities_overviews' : {
            # 'sector': ["Technology", "Consumer Cyclical"],
            'eps' : (4, None),
            'beta' : (1, 3),
            'payout_ratio' : (None, 0.3)

        }
    }
    # import pdb; pdb.set_trace()
    print(screen_stocks(test))
