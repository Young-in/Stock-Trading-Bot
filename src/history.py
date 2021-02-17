import pandas as pd
import numpy as np
import crawler

import util
import exception
import datetime
import pytz
import os
import re


def loadFeeData(path="../data/fee/"):
    """
    Return recent trade fee data of NH
    Return value is dataframe with column
    (min max expression)
    
    Parameters
    ----------
    path = str
        path of directory contains fee data
    """
    if util.isFileExist(path):
        file_list = os.listdir(path)
        if len(file_list) > 0:
            file_name = max(file_list)
            fee_data = pd.read_csv(path+file_name)
        else:
            raise FileNotFoundError("No Fee Data File : " + path)
    else:
        raise FileNotFoundError("Directory not Found : " + path)
    return fee_data
        
def netPrice(trade_type, price, tax=0.003):
    """
    Return net price.
    Net is amount of tax and fee.
    
    Parameters
    ----------
    trade_type = bool
        There are two types of trade. Buying and selling. Buying stock is "True" and selling stock is "False"
    price = int
        price
    tax = float
        Trade tax. It is usaually 0.3%
    """
    fee_data = loadFeeData()
    net = 0
    
    min_df = fee_data[fee_data["min"] <= price]
    max_df = fee_data[fee_data["max"] > price]
    inner_row = pd.concat([min_df,max_df],axis=1,join="inner").T.drop_duplicates()
    fee_expression = inner_row.loc["expression",inner_row.columns[0]]
    net += int(eval(str(price)+fee_expression))
    if not trade_type:
        net += int(price * tax)
    return net


def checkMarketOpened(now, area="Asia/Seoul"):
    """
    Return true if market is open, flase otherwise
    It only works well for korea market 
    
    Parameters
    ----------
    now = local datetime from util.getLocalTime() 
    """
    day_list = ['mon',"tue","wed","thu","fri","sat","sun"]
    day = day_list[now.weekday()]
    
    date = datetime.datetime.today().date()
    open_time = datetime.datetime.combine(date,datetime.datetime(2021,1,1,9,0).time(),
                                         tzinfo=pytz.timezone("Asia/Seoul"))
    close_time = datetime.datetime.combine(date,datetime.datetime(2021,1,1,15,30).time(),
                                         tzinfo=pytz.timezone("Asia/Seoul"))
    
    return True if (now > open_time and now < close_time) and day not in ["sat","sun"] else False


class History:
    """
    'History' class helps trading stocks and history file I/O.
    
    The word 'data' is only used for dataframe with format like below.
    ------------------------------------------------------------
        date code   name price quantity amount net balance
    0    ~    ~       ~    ~      ~       ~     ~     ~
    ------------------------------------------------------------
    For every func that uses data, It checks if data has right format because history should be maintained     accurately.
    
    Trade histories are saved in file named "../data/history/purchase_history_xx.csv". xx is strategy id.
    The file doesn't have information about columns of dataframe. 
    Columns are assigned through func 'readFile'.
    
    Let me explain about one line in __init__.
    ------------------------------------------------------------
    self.stock_info, self.recent_trade_date, self.balance = self.getTradeStatus()
    ------------------------------------------------------------
    Reading history file for every trade or save all histories in memory are inefficient.
    History class saves informations for trade in above three variances.
    The variance 'stock_info' is a dataframe with format like below.
    ------------------------------------------------------------
             name     quantity     amount
    code
     ~        ~            ~        ~
     -        -            -        -
     ~        ~            ~        ~
    ------------------------------------------------------------
    stock code is the index of dataframe stock_info.
    """
    def __init__(self, strategy_id, dir_path="../data/history/"):
        self.dir_path = dir_path
        self.strategy_id = strategy_id
        self.file_name = dir_path + "purchase_history_" + str(self.strategy_id) + ".csv"
        self.__columns = ["date","code","name","price","quantity","amount","net","balance"]
        self.__dtypes = ["object","object","int64","int64","int64","int64","int64"]
        self.__ = open(self.file_name,"a").close()
        self.balance = 0
        self.stock_info, self.recent_trade_date, self.balance = self.getTradeStatus()
    
    
    def readFile(self):
        """
        Read purchase history file and return contents of it.
        """
        if util.isFileExist(self.file_name):
            try:
                history = pd.read_csv(self.file_name,
                    dtype={"code":"object","name":"object"},
                    names=self.__columns).astype({"code":"category","name":"category"})
                history["date"]=pd.to_datetime(history["date"],errors="raise")
            except pd.errors.EmptyDataError:
                raise pd.errors.EmptyDataError("No Data to Read : " + self.file_name)
        else:
            raise FileNotFoundError("No History File : " + self.file_name)
        
        return history
    
    
    def writeFile(self, data):
        """
        Write data to history file.
        """
        if not util.isFileExist(self.file_name):
            raise FilenotFoundError("No History File : " + self.file_name)
            
        if not self.checkData(data):
            raise exception.WrongInputError(data) 
        
        data.to_csv(self.file_name,mode='a',header=False,index=False)
        
    
    def checkData(self,data):
        """
        Return true if data has right format else false.
        """
        error_count = 0
        index = data.index[0]
        code = data.loc[index,"code"]
        is_column_same = True
        comp = pd.DataFrame([[util.getLocalTime(),"000000","0",0,0,0,0,0]],
                    columns=self.__columns).astype(dict(zip(self.__columns[self.__columns.index("code"):],self.__dtypes)))
        
        if not data.loc[index,"date"] >= self.recent_trade_date:
            raise exception.TimeError(data.loc[index,"date"])
            
        if not (data.columns == comp.columns).all():
            error_count += 1
            is_column_same = False
            
        if data.loc[index,"code":"amount"].isnull().all() and is_column_same: #입금 데이터
            if not data.dtypes.date == comp.dtypes.date or not data.dtypes.balance == comp.dtypes.balance:
                error_count += 1
                
        elif not (data.dtypes == comp.dtypes).all() and is_column_same:
            error_count += 1
            
        elif is_column_same:
            if not re.compile("\d{6}").match(code) and not len(code) == 6:
                error_count += 1
            if not data.loc[index,"price"] * abs(data.loc[index,"quantity"]) == data.loc[index,"amount"]:
                error_count += 1
        
        return False if error_count > 0 else True
        
        
    def getTradeStatus(self, seed_money = 1000000):
        """
        Return informations for trade.
        This func is special(?) because it is used in instructor.
        Parameters
        ----------
        seed_money = int
            Starting balance if history file doesn't have any contents.
        """
        history = self.readFile()
        if history.shape[0] > 0:
            stock_info = history.groupby(["code","name"])[["quantity","amount"]].sum()
            stock_info = stock_info.reset_index().set_index("code")
            stock_info = stock_info[stock_info["quantity"]>0]
            recent = history.loc[history["date"].idxmax()]
            recent_balance = recent["balance"]
            recent_date = recent["date"]
        else:
            if not util.isFileExist(self.file_name):
                raise FilenotFoundError("No History File : " + self.file_name)
            self.depositData(seed_money).to_csv(self.file_name,mode='a',header=False,index=False)

            stock_info = pd.DataFrame(columns=["code","name","quantity","amount"])
            stock_info.set_index("code")
            recent_balance = seed_money
            recent_date = util.getLocalTime()
            stock_info.astype({
            "name":"object",
            "quantity":"int64",
            "amount":"int64"
            })
        return stock_info, recent_date, recent_balance
    
        
    def tradeData(self, trade_type, code, quantity, code_len=6):
        """
        Return data for trade.
        Parameters
        ----------
        trade_type = bool
            true -> buying, false -> selling
        code = str
            Stock code
        quantity = int
            Quantity of stocks to trade
        code_len = int
            Length of stock code
        """
        try:
            if not re.compile("\d{6}").match(code) and len(code) != code_len:
                raise exception.WrongInputError(code)
        except TypeError:
            raise TypeError("Wrong Input : " + code)
            
        quantity = int(quantity) if trade_type else -int(quantity)
        
        if quantity == 0:
            raise exception.WrongInputError(quantity)
            
        if not crawler.checkStockCode(code):
            raise ValueError("Nonexistent stock code")
            
        current = crawler.getCurrentStockData(code).loc[0]
        
        if current["requested_time"] < self.recent_trade_date:
            raise exception.TimeError(current["requested_time"])
        
        amount = quantity * current['price']
        net = netPrice(trade_type, abs(amount))
        balance = self.balance - amount - net
        
        data = [current["requested_time"], code, current["stock_name"],
                   current["price"], quantity, abs(amount), net, balance]
        
        trade_data = pd.DataFrame([data],columns=self.__columns).astype(dict(zip(self.__columns[self.__columns.index("code"):],self.__dtypes)))
        return trade_data
    
    
    def depositData(self, money):
        """
        Return data for deposit
        Only date and balance have value. Others are Na
        Parameters
        ----------
        money = int
            Money to deposit
        """
        money = int(money)
        if money <= 0:
            raise exception.WrongInputError(money)
        
        now_local = util.getLocalTime()
        balance = self.balance + money
        
        data = [now_local] + [np.nan]*6 + [balance]
        deposit_data = pd.DataFrame([data],columns=self.__columns)
        
        return deposit_data
    
    
    def isBuyable(self, data):
        """
        Return true if user can buy stock else false
        """
        error_count = 0
        index = data.index[0]
        #if not checkMarketOpened(data.loc[index,"date"]):
        #    error_count += 1
        if not self.checkData(data):
            error_count += 1
        else:
            if not data.loc[index,"date"] >= self.recent_trade_date:
                raise exception.TimeError(data.loc[index,"date"])
            
            if not data.loc[index,"balance"] >= 0:
                error_count += 1
        
        return False if error_count > 0 else True
    
    
    def isSellale(self, data):
        """
        Return true if user can sell stock else false
        """
        error_count = 0
        index = data.index[0]
        #if not checkMarketOpened(data.loc[index,"date"]): #check if market is opened
        #    error_count += 1
        if not self.checkData(data):
            error_count += 1
        else:
            if not data.loc[index,"date"] >= self.recent_trade_date:
                raise exception.TimeError(data.loc[index,"date"])
                
            if data.loc[index,"code"] not in self.stock_info.index:
                error_count += 1
            else:
                if not self.stock_info.loc[data.loc[index,"code"],"quantity"] + data.loc[index,"quantity"] >= 0: #ambiguous issue
                    error_count += 1
                
            
        return False if error_count > 0 else True
    
    
    def __updateStatus(self, data):
        """
        Update informations for trade.
        This func is private becuase it changes value of class variances.
        """
        if not len(data.index) == 1:
            raise exception.WrongInputError(data)
            
        if not self.checkData(data):
            raise exception.WrongInputError(data) 
        
        index = data.index[0]
        code = data.loc[index,"code"]
        
        if code in self.stock_info.index:
            new_quantity = self.stock_info.loc[code,"quantity"]+data.loc[index,"quantity"]
            self.stock_info.loc[code,"quantity"] = new_quantity
            data_amount = data.loc[index,"amount"] if data.loc[index,"quantity"] > 0 else -data.loc[index,"amount"]
            new_amount = self.stock_info.loc[code,"amount"]+data_amount
            self.stock_info.loc[code,"amount"] = new_amount
        else:
            new_info = data.loc[index,["name","quantity","amount"]]
            new_row = pd.DataFrame([new_info],
                                   index=[data.loc[index,"code"]],
                                   columns=["name","quantity","amount"])
            self.stock_info = pd.concat([self.stock_info,new_row])
    
        self.balance = data.loc[index,"balance"]
        self.recent_trade_date = data.loc[index,"date"] 
        
    
    def updateStatus(self, data):
        self.__updateStatus(data)
        
"""    
h = History(78)
print("=============================")
print(h.stock_info)
print(h.balance)
print(h.recent_trade_date)
"""
'''
b = h.tradeData(True,"005930",4)
print(b)
print(h.isBuyable(b))
h.writeFile(b)
h.updateStatus(b)
print(h.stock_info)
print(h.balance)
print(h.recent_trade_date)
s = h.tradeData(False,"005930",3)
print(h.isSellale(s))
h.writeFile(s)
h.updateStatus(s)
print(h.stock_info)
print(h.balance)
print(h.recent_trade_date)
b1 = h.tradeData(True,"009830",6)
h.writeFile(b1)
h.updateStatus(b1)
print(h.stock_info)
print(h.balance)
print(h.recent_trade_date)
'''