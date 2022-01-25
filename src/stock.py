import pandas as pd
import pandas_datareader as pdr
import streamlit as st

class Stock:

    def __init__(self,
            ticker:str,
            name:str,
            purchases:pd.DataFrame,
            ):
        self.ticker = ticker
        self.name = name
        self.prices = self.get_stock_data()
        self.purchases = purchases[purchases["Aktienticker"]==ticker]
        self.holdings = self.get_holdings()
        self.valuations = self.get_valuations()

    @st.cache
    def get_stock_data(self, price_type='Close') -> pd.DataFrame:
        """ get stock price data from yahoo finance
        """
        return pdr.get_data_yahoo(self.ticker)[[price_type]]\
                .rename(columns={price_type:self.ticker})

    def get_holdings(self) -> pd.DataFrame:
        """ get cumulative purchase history
        """
        df = self.purchases.copy().sort_index()
        df[["Einstandswert","Stückzahl"]] = \
                df[["Einstandswert","Stückzahl"]].cumsum()
        return df

    def get_valuations(self) -> pd.DataFrame:
        #initialize
        df = self.prices.copy()
        df["Einstandswert"] = 0
        df.loc[df.index<self.holdings.index[0],self.ticker] = 0
        df.loc[df.index>=self.holdings.index[-1],self.ticker] = \
                df.loc[df.index>=self.holdings.index[-1],:] \
                *self.holdings.iloc[-1]["Stückzahl"]
        df.loc[df.index>=self.holdings.index[-1],"Einstandswert"] = \
                self.holdings.iloc[-1]["Einstandswert"]
        # aggregate einstandswert
        for t1,t2 in zip(self.holdings.index[:-1], self.holdings.index[1:]):
            df.loc[(t1<=df.index) & (df.index<t2),self.ticker] = \
                df.loc[(t1<=df.index) & (df.index<t2),self.ticker] \
                *self.holdings.loc[t1]["Stückzahl"]
            df.loc[(t1<=df.index) & (df.index<t2),"Einstandswert"] = \
                self.holdings.loc[t1]["Einstandswert"] 
        return df

class StockPortfolio:
    """Portfolio consisting of multiple stocks."""
    def __init__(self, buys: pd.DataFrame):
        self.stocks = self.initialize_stocks(buys)

    @st.cache
    def initialize_stocks(self, buys: pd.DataFrame) -> pd.DataFrame:
        stocks = {}
        for ticker in buys["Aktienticker"].unique():
            stocks[ticker] = Stock(ticker, ticker, buys)
        return stocks

class BuyHistory:

    def __init__(self, source_file:str):
        self.buys = self.load_data(source_file)
        self.holdings = self.compute_holdings()

    @st.cache
    def load_data(self, source_file:str):
        try:
            df = pd.read_csv(source_file).sort_values(by="Datum").set_index("Datum")
        except:
            df = pd.DataFrame(
                    columns=["Datum", "Aktienticker",
                             "Einstandswert", "Stückzahl"])
        return df

    def compute_holdings(self):
        df = self.buys.copy()
        for stock in df["Aktienticker"].unique():
            df.loc[df["Aktienticker"]==stock,
                          ["Einstandswert","Stückzahl"]] = \
            df.loc[df["Aktienticker"]==stock,
                          ["Einstandswert","Stückzahl"]].cumsum()
        return df
