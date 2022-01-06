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
        self.purchases_cum = self.get_cum_purchases()
    @st.cache
    def get_stock_data(self, price_type='Close') -> pd.DataFrame:
        """ get stock price data from yahoo finance
        """
        return pdr.get_data_yahoo(self.ticker)[[price_type]]\
                .rename(columns={price_type:self.ticker})

    def get_cum_purchases(self):
        """ get cumulative purchase history
        """

        self.purchases_cum = self.purchases.copy()
        self.purchases_cum[["Einstandswert","Stückzahl"]] = \
                self.purchases_cum[["Einstandswert","Stückzahl"]].cumsum()


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
