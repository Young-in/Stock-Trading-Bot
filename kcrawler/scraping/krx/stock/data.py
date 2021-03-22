from kcrawler.scraping.krx.krxio import KrxIo
import pandas as pd

class ListedAll(KrxIo):
    """
    상장된 모든 종목 검색
    """
    @property
    def bld(self):
        return "dbms/comm/finder/finder_stkisu"
    
    def fetch(self, mktsel: str="ALL", searchText: str = "") -> pd.DataFrame:
        """ [12003] 개별종목 시세 추이
        Parameters
        ---------------------------
        mktsel : str -> 조회 시장(STK, KSQ, ALL)
        searchText : str -> 검색할 종목, 공백은 ALL
        """
        data = self.read(mktsel=mktsel, searchText=searchText, typeNo=0)
        return pd.DataFrame(data['block1'])
    
class DelistedAll(KrxIo):
    """
    상장폐지된 모든 종목 검색
    """
    @property
    def bld(self):
        return "dbms/comm/finder/finder_listdelisu"
    
    def fetch(self, mktsel: str="ALL", searchText: str = "") -> pd.DataFrame:
        """[20037] 상장폐지종목 현황
        Parameters
        ---------------------------
        Same with ListedAll
        """
        data = self.read(mktsel=mktsel, searchText=searchText, typeNo=0)
        return pd.DataFrame(data['block1'])
    
class StockPriceDay(KrxIo):
    """
    개별종목시세 기간 검색
    """
    @property
    def bld(self):
        
class StockPriceAll(KrxIo):
    """
    전종목시세 날짜별 검색
    """
    @property
    def bld(self):
        return "dbms/MDC/STAT/standard/MDCSTAT01501"
    
    def fetch(self, trdDd: str, mktId: str="ALL", share: str="1", money: str="1") -> pd.DataFrame:
        """[12001] 전종목 시세
        Parameters
        ---------------------------
        mktId : str -> 조회 시장(STK, KSQ, ALL)
        trdDd : str -> 검색할 날짜
        share : str -> 주 단위(1->1주,2->1000주,3->1000000주)
        money : str -> 금액 단위(1->천원,2->백만원,3->십억원)
        """
        data = self.read(mktId=mktId,trdDd=trdDd,share=share,money=money,csvxls_isNo="false")
        return pd.DataFrame(data['OutBlock_1'])