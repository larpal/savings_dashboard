import pandas as pd
import pandas_datareader as pdr

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
