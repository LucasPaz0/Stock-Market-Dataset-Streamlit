import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import altair as alt

# buscar informações da empresa
@st.cache_data
def fetch_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        if 'longName' not in info:
            return None
        return info
    except Exception:
        return None

# buscar os dados financeiros trimestrais
@st.cache_data
def fetch_quarterly_financials(symbol):
    try:
        stock = yf.Ticker(symbol)
        financials = stock.quarterly_financials.T
        if financials.empty:
            return None
        return financials
    except Exception:
        return None

# buscar os dados financeiros anuais
@st.cache_data
def fetch_annual_financials(symbol):
    try:
        stock = yf.Ticker(symbol)
        financials = stock.financials.T
        if financials.empty:
            return None
        return financials
    except Exception:
        return None

# buscar o histórico semanal da ação
@st.cache_data
def fetch_weekly_price_history(symbol):
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period='1y', interval='1wk')
        if history.empty:
            return None
        return history
    except Exception:
        return None

st.title('📈 Stock Dashboard')

symbol = st.text_input('Enter a stock symbol', 'AAPL').upper()

# verifica se o símbolo é válido
information = fetch_stock_info(symbol)

if information is None:
    st.error("⚠️ Invalid stock symbol! Please enter a valid one.")
else:
    st.header('🏢 Company Information')
    st.subheader(f'📌 Name: {information["longName"]}')
    st.subheader(f'💰 Market Cap: ${information["marketCap"]:,}')
    st.subheader(f'🏭 Sector: {information["sector"]}')

    price_history = fetch_weekly_price_history(symbol)

    if price_history is None:
        st.error("⚠️ No price data available for this symbol.")
    else:
        st.header('📊 Stock Price Chart')

        price_history = price_history.rename_axis('Date').reset_index()
        candle_stick_chart = go.Figure(data=[go.Candlestick(
            x=price_history['Date'],
            open=price_history['Open'],
            low=price_history['Low'],
            high=price_history['High'],
            close=price_history['Close']
        )])

        candle_stick_chart.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(candle_stick_chart, use_container_width=True)

    # busca os dados financeiros
    quarterly_financials = fetch_quarterly_financials(symbol)
    annual_financials = fetch_annual_financials(symbol)

    if quarterly_financials is None or annual_financials is None:
        st.error("⚠️ No financial data available for this symbol.")
    else:
        st.header('📑 Financials')

        selection = st.radio('Select period:', ['Quarterly', 'Annual'])

        if selection == 'Quarterly':
            quarterly_financials = quarterly_financials.rename_axis('Quarter').reset_index()
            quarterly_financials['Quarter'] = quarterly_financials['Quarter'].astype(str)

            revenue_chart = alt.Chart(quarterly_financials).mark_bar(color='red').encode(
                x='Quarter:O',
                y='Total Revenue'
            )
            net_income_chart = alt.Chart(quarterly_financials).mark_bar(color='cyan').encode(
                x='Quarter:O',
                y='Net Income'
            )

            st.altair_chart(revenue_chart, use_container_width=True)
            st.altair_chart(net_income_chart, use_container_width=True)

        if selection == 'Annual':
            annual_financials = annual_financials.rename_axis('Year').reset_index()
            annual_financials['Year'] = annual_financials['Year'].astype(str).apply(lambda year: year.split('-')[0])

            revenue_chart = alt.Chart(annual_financials).mark_bar(color='red').encode(
                x='Year:O',
                y='Total Revenue'
            )
            net_income_chart = alt.Chart(annual_financials).mark_bar(color='cyan').encode(
                x='Year:O',
                y='Net Income'
            )

            st.altair_chart(revenue_chart, use_container_width=True)
            st.altair_chart(net_income_chart, use_container_width=True)
