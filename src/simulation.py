import history

class SimulatedTrade:
    def __init__(self,strategy_id):
        self.strategy_id = strategy_id
        self.history = history.History(strategy_id)
        
    def buy(self, code, quantity, market=True):
        if self.history.isBuyable(code, quantity, market):
            trade_data = self.history.tradeData(True, code, quantity)
            self.history.writeFile(trade_data)
            self.history.updateStatus(trade_data)
        else:
            print("Can't Buy")
            
    def sell(self, code, quantity, market=True):
        if self.history.isSellable(code, quantity, market):
            trade_data = self.history.tradeData(False, code, quantity)
            self.history.writeFile(trade_data)
            self.history.updateStatus(trade_data)
        else:
            print("Can't Sell")
            
    def deposit(self, money=1000000):
        deposit_data = self.history.depositData(money)
        self.history.writeFile(deposit_data)
        self.history.updateStatus(deposit_data)
            
    def show(self):
        print("--------------------------------------------------------")
        print("Recent trade: " + str(self.history.recent_trade_date))
        print("Balance: " + str(self.history.balance))
        print("Stock holding status")
        print(self.history.stock_info)
        print("--------------------------------------------------------")
        
"""
jeonyeok = SimulatedTrade(14)
jeonyeok.show()
jeonyeok.sell("005930",3,False)
jeonyeok.show()
jeonyeok.deposit(1000000)
jeonyeok.show()
jeonyeok.buy("035720",2, False)
jeonyeok.show()
jeonyeok.buy("005930",10,False)
jeonyeok.show()
"""