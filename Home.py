import streamlit as st

st.set_page_config(
    page_title="Trading Analysis Tools",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Trading Analysis Tools")

st.markdown("""
Welcome to the Trading Analysis Tools! This application provides various tools for stock market analysis:

### Available Tools:
1. **TradingView Stock News** - Get real-time news updates for stocks
2. **ChartInk Stock Analysis** - Technical analysis and charts from ChartInk
3. More tools coming soon...

### How to Use:
1. Select a tool from the sidebar on the left
2. Enter the stock symbol you want to analyze
3. View the analysis results and insights

### Note:
This application is for research purposes only. Please be aware of the risks involved in trading.
""")

# Add any additional widgets or features for the home page here

st.sidebar.success("Select a tool from above.") 