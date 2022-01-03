import streamlit as st
import pandas as pd
import pandas_datareader as pdr

SOURCE_FILE = "investments.csv"

st.write("Savings Dashboard")

try:
    df = pd.read_csv(SOURCE_FILE).sort_values(by="Datum").set_index("Datum")
except:
    df = pd.DataFrame(columns=["Datum", "Aktienticker",
                               "Einstandswert", "Stückzahl"])

df
df_cum = df.copy()
for stock in df_cum["Aktienticker"].unique():
    df_cum.loc[df_cum["Aktienticker"]==stock,["Einstandswert","Stückzahl"]] = \
    df_cum.loc[df_cum["Aktienticker"]==stock,["Einstandswert","Stückzahl"]].cumsum()
st.write(df_cum)

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

# compute current worth
df_stocks_cum = df_test.copy()
for t1,t2 in zip(df_cum.index[:-1], df_cum.index[1:]):
    st.write(t1,t2)
    st.write(df_stocks_cum[(t1<=df_stocks_cum.index) & (df_stocks_cum.index<t2)]["VWRL.AS"])# *= \
    #df_cum[t1]["Stückzahl"]

# field to add new stocks to current list
new_buy = st.checkbox("Neuer Kauf")
if new_buy:
    date = st.date_input("Kaufdatum")
    ticker = st.text_input("Aktienticker")
    buy_value = st.number_input("Einstandswert")
    amount = st.number_input("Stückzahl")
    add_buy = st.button("Hinzufügen")
    if add_buy:
        df = df.append({"Datum":date,
                        "Aktienticker":ticker,
                        "Einstandswert":buy_value,
                        "Stückzahl":amount},
                        ignore_index=True)
        df.to_csv(SOURCE_FILE, index=None)
        new_buy = False
    
