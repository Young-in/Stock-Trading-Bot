# Libraries for crawling
import requests
from bs4 import BeautifulSoup

import datetime
import util

# Libraries for data processing
import pandas as pd
import numpy as np


def checkStockCode(stock_code):
    """ Check whether the stock code exists
    
    Parameters
    ----------
    stock_code : str
        the stock code (ex. "005930")
    """
    url = f"https://finance.daum.net/quotes/A{stock_code}#home"
    
    html = requests.get(url)
    html.raise_for_status()
    
    return "alert" not in html.text

def getStockPrice(stock_code, period=250):
    """ Return DataFrame of the stock prices.

    Parameters
    ----------
    stock_code : str
        the stock code (ex. "005930")
    period : int, default 250
        the number of stock prices
    """
    if not checkStockCode(stock_code):
        raise ValueError("Nonexistent stock code")
    
    params = {
        'symbol': stock_code,
        'timeframe': 'day',
        'count': period,
        'requestType': 0,
    }
    url = "https://fchart.stock.naver.com/sise.nhn"

    html = requests.get(url, params)
    html.raise_for_status()

    parser = BeautifulSoup(html.text, 'html.parser')
    items = parser.find_all('item')

    prices = pd.DataFrame(
            map(lambda item:
                item.get('data').split('|'),
                items
                ),
            columns=['Date', 'Start', 'High', 'Low', 'End', 'Amount']
        ).astype({
            'Date': 'datetime64',
            'Start': 'int32',
            'High': 'int32',
            'Low': 'int32',
            'End': 'int32',
            'Amount': 'int64',
        }).set_index('Date')

    return prices

def getCurrentStockData(stock_code, timezone="Asia/Seoul"):
    """
    Return current data of requested company
    Parameters
    ----------
    stock_code : str
        the stock code (ex. "005930")
    Return Value
    ----------
    DataFrame
    ex)
    requested_time	                 name    price
    2021-01-30 05:31:34.130440+09:00 삼성전자 82000
    """
    now_local = util.getLocalTime(timezone)
    
    if not checkStockCode(stock_code):
        raise ValueError("Nonexistent stock code")
    url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
    html = requests.get(url)
    html.raise_for_status()

    content = BeautifulSoup(html.content, 'html.parser')
    
    stock_div = content.find("div",{"class":"wrap_company"})
    stock_name = stock_div.find("a").text

    feed = content.find("p",{"class":"no_today"})
    price = int(feed.find("span",{"class":"blind"}).text.replace(",",""))
    
    stock_data = pd.DataFrame([[now_local, stock_name, price]],
                          columns=["requested_time","stock_name","price"]).astype({
                            "stock_name":"object",
                            "price":"int64"})
    
    return stock_data

def getFinancialInfo(stock_code):
    """ Return DataFrame of the financial summary.

    Parameters
    ----------
    stock_code : str
        the stock code (ex. "005930")
    """
    if not checkStockCode(stock_code):
        raise ValueError("Nonexistent stock code")
        
    params = {
        'cmp_cd': stock_code,
        'finGubun': "MAIN",
    }
    url = "http://wisefn.finance.daum.net/v1/company/cF1001.aspx"

    html = requests.get(url, params)
    html.raise_for_status()

    parser = BeautifulSoup(html.text, 'html.parser')
    form = parser.find(id='Form1')
    script = form.contents[-2]

    changeFin, changeFinData, *_ = script.string.split(';')
    changeFin = changeFin.replace('\n', '')
    changeFinData = changeFinData.replace('\n', '')

    change_fin = eval(changeFin.replace("var changeFin = ", "")
                      .replace("<span class='multi-row'>", "")
                      .replace("</span>", ""))

    periods = [
        np.array(['yearly'] * len(change_fin[0])
                 + ['monthly'] * len(change_fin[1])),
        np.concatenate(change_fin, axis=0)
    ]

    change_fin_data = eval(changeFinData.replace('var changeFinData = ', ''))

    change_fin_data_array = np.concatenate(
        list(map(lambda chunk: np.concatenate(chunk, axis=1),
                 change_fin_data)),
        axis=0)

    labels = change_fin_data_array[:, 0]
    data = np.char.replace(change_fin_data_array[:, 1:], ',', '')

    financial = pd.DataFrame(data.T, index=periods, columns=labels)
    financial = financial.apply(pd.to_numeric, axis=1, errors='coerce')

    return financial