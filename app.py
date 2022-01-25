import streamlit as st
import pandas as pd
import pandas_datareader as pdr
from src.stock import BuyHistory, Stock, StockPortfolio

SOURCE_FILE = "investments.csv"

st.write("Savings Dashboard")

st.write("Class BuyHistory")
invests = BuyHistory(SOURCE_FILE)
invests.buys
df = invests.buys
st.write("""---""")
# cumulative buying history
df_cum = df.copy()
for stock in df_cum["Aktienticker"].unique():
    df_cum.loc[df_cum["Aktienticker"]==stock,["Einstandswert","Stückzahl"]] = \
    df_cum.loc[df_cum["Aktienticker"]==stock,["Einstandswert","Stückzahl"]].cumsum()
invests.holdings

st.write("""---""")

vwrl = Stock("VWRL.AS", "Vanguard FTSE All World", df)
st.write("Class prices\n",vwrl.prices,vwrl.holdings)
st.line_chart(vwrl.valuations)

st.write("""StockPortfolio""")
st.write("""---""")
portfolio = StockPortfolio(invests.buys)
st.write(portfolio.stocks.keys())
st.write("""---""")

@st.cache
def get_stock_data(stocks:list=['NVDA']) -> pd.DataFrame:
    """ get stock price data from yahoo finance
    """
    new_data = {}
    err = []
    for stock in stocks:
        try:
            new_data[stock] = pdr.get_data_yahoo(stock)[['Close']].rename(columns={'Close':stock})
        # new_data[stock]
        except:
            err.append(stock)    
    return pd.concat(new_data.values(), axis=1), err

df_test, err = get_stock_data(df['Aktienticker'].unique())
st.write(f'No data found for tickers {err}')
st.write(df['Aktienticker'].unique())
df_test
st.line_chart(df_test)

### compute current worth
df_stocks_cum = df_test.copy()
# add column Einstandswert and cumulate stock valuations
df_stocks_cum["Einstandswert"] = 0
df_stocks_cum.loc[df_stocks_cum.index<df_cum.index[0],"VWRL.AS"] = 0
df_stocks_cum.loc[df_stocks_cum.index>=df_cum.index[-1],"VWRL.AS"] = df_stocks_cum.loc[df_stocks_cum.index>=df_cum.index[-1],"VWRL.AS"]*df_cum.iloc[-1]["Stückzahl"]
df_stocks_cum.loc[df_stocks_cum.index>=df_cum.index[-1],"Einstandswert"] = df_cum.iloc[-1]["Einstandswert"]

# aggregate einstandswert
for t1,t2 in zip(df_cum.index[:-1], df_cum.index[1:]):
    df_stocks_cum.loc[(t1<=df_stocks_cum.index) & (df_stocks_cum.index<t2),"VWRL.AS"] = \
    df_stocks_cum.loc[(t1<=df_stocks_cum.index) & (df_stocks_cum.index<t2),"VWRL.AS"] *df_cum.loc[t1]["Stückzahl"]

    df_stocks_cum.loc[(t1<=df_stocks_cum.index) & (df_stocks_cum.index<t2),"Einstandswert"] = df_cum.loc[t1]["Einstandswert"]

st.write(df_stocks_cum)
st.line_chart(df_stocks_cum)

df_stocks_cum["Gewinn"] = 100*(df_stocks_cum["VWRL.AS"]/df_stocks_cum["Einstandswert"]-1)
st.line_chart(df_stocks_cum[["Gewinn"]])

# field to add new stocks to current list
new_buy = st.checkbox("Neuer Kauf")
if new_buy:
    date = st.date_input("Kaufdatum")
    ticker = st.text_input("Aktienticker")
    buy_value = st.number_input("Einstandswert")
    amount = st.number_input("Stückzahl")
    add_buy = st.button("Hinzufügen")
    if add_buy:
        df = df.reset_index().append({"Datum":date,
                        "Aktienticker":ticker,
                        "Einstandswert":buy_value,
                        "Stückzahl":amount},
                        ignore_index=True)
        df.to_csv(SOURCE_FILE, index=None)
        new_buy = False
    
