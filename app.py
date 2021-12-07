import streamlit as st
import pandas as pd

SOURCE_FILE = "investments.csv"

st.write("Savings Dashboard")

try:
    df = pd.read_csv(SOURCE_FILE)
except:
    df = pd.DataFrame(columns=["Datum", "Aktienticker",
                               "Einstandswert", "Stückzahl"])

df

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
    
