# TradingView Screener & Dashboard

A modern, mobile-friendly Streamlit web app for advanced stock screening, analytics, and dashboards—focused on Indian and global markets (NSE/BSE and worldwide). Effortlessly scan for high-momentum stocks above multiple EMAs, visualize price bands, analyze company financials, and export results—all with an intuitive, responsive UI. **Supports cross-asset, cross-exchange, and global scanning using TradingView's data universe.**

---

## 📚 Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [App Pages Overview](#app-pages-overview)
4. [Screenshots](#screenshots)
5. [Installation & Quickstart](#installation--quickstart)
6. [Usage Guide](#usage-guide)
7. [Performance Optimization & Caching](#performance-optimization--caching)
8. [Configuration & Customization](#configuration--customization)
9. [Technical Architecture](#technical-architecture)
10. [Developer Guide](#developer-guide)
11. [FAQ & Troubleshooting](#faq--troubleshooting)
12. [Contributing](#contributing)
13. [License](#license)
14. [Contact](#contact)

---

## 🏁 Project Overview
A robust, extensible platform for:
- **Active traders & investors** seeking momentum stocks using technical filters.
- **Analysts** needing interactive dashboards for Indian and global equities, indices, forex, crypto, and more.
- **Developers** who want a modular, customizable analytics toolkit.

**Key Value Propositions:**
- **Global Reach:** Scan all instruments—equities, indices, forex, crypto, ETFs, and more—across all major exchanges and borders using TradingView's global data.
- **No vendor lock-in:** 100% open source, no API keys required for core features.
- **Modular:** Add new dashboards, screens, or data sources with minimal effort.
- **Modern UI:** Mobile-first, responsive, and highly interactive.

---

## 🚀 Features

### Cross-Asset & Global Scanning
- **All Instruments Supported:**
  - Scan equities, indices, commodities, forex, cryptocurrencies, ETFs, and more.
  - Cross-exchange: NSE, BSE, NYSE, NASDAQ, LSE, crypto exchanges, and many others.
  - Cross-border: Effortlessly scan global markets and compare instruments worldwide.

### Stock Scanners
- **Multi-EMA Scanner:**
  - Find stocks and other instruments trading above 50, 150, and 200-day EMAs.
  - Advanced filters: exchange, volume, price, market cap, sector, asset class, and more.
  - Copy tickers by sector/industry, export CSV, and view key metrics.
- **Custom EMA Scanner:**
  - Define custom EMA periods and thresholds for personalized scans on any instrument.

### Dashboards & Analytics
- **Price Bands Dashboard:**
  - Visualize stocks and instruments by price bands with interactive charts and metrics.
  - Export band data and see last update times.
- **Company Financials:**
  - Deep-dive into financials, ratios, and performance for any listed company.
- **Results Calendar:**
  - View, filter, and export scan results by date or criteria.
- **Stock News:**
  - Fetch latest news for any stock (supports global tickers).
  - Manual refresh and auto-update.

### UI/UX & Interactivity
- Modern, mobile-friendly layout with cards, tabs, and responsive tables.
- Export buttons, copy-to-clipboard, and interactive widgets.
- Customizable themes via CSS.

### Extensibility
- Add new dashboards, custom logic, or styling with ease.
- Modular directory structure for easy feature addition.

---

## 🗂️ App Pages Overview

| Page | Icon | Description |
|------|------|-------------|
| **Advanced Scanner** | 🚦 | Powerful multi-asset scanner with advanced technical & fundamental filters for stocks, indices, forex, crypto, and more. |
| **Stock News** | 📰 | Latest stock news dashboard. Fetches and displays headlines from external sources for market awareness. |
| **Custom EMA Scanner** | 🧮 | Define your own EMA periods/thresholds for personalized scans on any instrument. Now also displays live news for each scanned symbol directly in the results. |
| **Industry Visualization** | 🏭 | Visualize sector and industry data with interactive charts to spot trends and leaders. |
| **Price Bands** | 💹 | Visualize stocks by price bands, export data, and see last update times. |
| **Results Calendar** | 🗓️ | Track upcoming company results and board meetings, filter and export by date. |
| **Company Financials** | 💼 | Deep-dive into company financials, ratios, and key metrics for listed stocks. |
| **Global Financials** | 🌎 | View and compare global company financials and ratios. |
| **Performance Scanner** | 🏆 | Analyze stock performance across custom metrics and timeframes. |
| **News Search Engine** | 🔎 | Search and filter news across global and Indian stocks. |
| **NSE Volume Gainers** | 🚧 | Identify NSE stocks with significant volume spikes for potential trading setups. |
| **NSE 200EMA Uptrend** | 📈 | Scan NSE stocks above their 200-day EMA to find long-term uptrends. |

---

## 🖼️ Screenshots
_Add screenshots or GIFs here to showcase the UI and features._

---

## ⚡ Installation & Quickstart

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/globallivescanning.github.io.git
   cd globallivescanning.github.io
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app locally:**
   ```bash
   streamlit run streamlit_app.py
   ```

#### Troubleshooting
- If you encounter `ModuleNotFoundError`, ensure you're in the correct directory and using the right Python environment.
- For Playwright errors, run `playwright install` after installing requirements.

---

## 📝 Usage Guide

- Use the sidebar to navigate between dashboards and scanners.
- Configure filters and parameters for each scan.
- Export results as CSV or copy tickers as needed.
- Use **Results Calendar** to review results by date.
- The app is fully responsive—use in landscape mode on mobile for best experience.

---

## ⚙️ Configuration & Customization

### Editing Scan Logic
- Main scanner logic: `pages/02_📈_Custom_Scanner.py`
- Add new dashboards: Create Python scripts in `pages/`

### Styling
- Modify CSS in each page or shared `style.css` for colors, layout, and branding.

### Data Sources
- **TradingView Screener:** Cross-asset, global scanning with SQL-like queries.
- **Google Sheets:** News/dashboard data as CSV via pandas.
- **GNews:** Latest news for any stock (supports global tickers).
- **VaderSentiment:** Sentiment analysis of news headlines.
- **Pytz:** Timezone conversions for accurate date/time.

### Caching
- Uses Streamlit’s `@st.cache_data` for fast reloads and reduced API calls.

---

## 🏗️ Technical Architecture

```
+-------------------+
|  User Interface   |
|  (Streamlit App)  |
+-------------------+
          |
          v
+---------------------------+
|      App Logic (Python)   |
| - Scanner modules         |
| - Data processing         |
| - Visualization           |
+---------------------------+
          |
          v
+-------------------------------+
|   Data Sources & APIs         |
| - TradingView Screener (NSE,  |
|   global, crypto, forex, etc) |
| - Google Sheets (news, etc.)  |
| - GNews (latest news)        |
| - VaderSentiment (sentiment) |
| - Pytz (timezone conversions) |
+-------------------------------+
```

- **Directory Structure:**
  - `streamlit_app.py` – Main entry point.
  - `pages/` – Modular app pages: Advanced Scanner, Custom EMA, Price Bands, Financials, News, etc.
  - `requirements.txt` – All Python dependencies.
  - `style.css` – Custom CSS for UI/UX.

- **Main Dependencies:**
  - `streamlit`, `tradingview-screener`, `pandas`, `numpy`, `plotly`, `openpyxl`, `beautifulsoup4`, `playwright`, `flask`, `werkzeug`, `requests`, `scikit-learn`, `tqdm`, `gnews`, `vaderSentiment`, `pytz`, `tabulate`

- **Security:**
  - No secrets or API keys required for public data sources.
  - All data fetches are wrapped in `try/except` with user-friendly error messages.

---

## 👩‍💻 Developer Guide

### Coding Standards
- Follow PEP8 for Python code.
- Use descriptive variable/function names.
- Add docstrings to all public functions.

### Linting & Testing
- Lint: `ruff .`
- Test: `pytest`
- Type-check: `pyright`

### Adding Features
- New dashboards: Add scripts to `pages/` and update navigation if needed.
- New data sources: Integrate in a modular way (see `utils.py` for helpers).

### Branching & PRs
- Use feature branches for new features.
- Open PRs with clear descriptions and reference related issues.

---

## ❓ FAQ & Troubleshooting

**Q: Can I scan instruments outside India?**
A: Yes! The app supports global, cross-asset, cross-exchange scanning for all instrument types—equities, forex, crypto, indices, and more.

**Q: Why do I get a ModuleNotFoundError?**
A: Ensure you have installed all dependencies with `pip install -r requirements.txt` and are using the correct Python environment.

**Q: Data not updating?**
A: Try clearing Streamlit cache or restarting the app. Check your internet connection.

**Q: Playwright errors?**
A: Run `playwright install` after installing requirements.

**Q: How to add a new scan or dashboard?**
A: Create a new script in `pages/`, following the structure of existing modules.

---

## 🤝 Contributing

Pull requests, issues, and feature suggestions are welcome! Please open an issue to discuss your ideas or submit a PR. See [Developer Guide](#developer-guide) for more.

---

## 📄 License

MIT License. See [LICENSE](./LICENSE) for details.

---

## 📬 Contact

For questions, suggestions, or help, open an issue or contact [your-email@example.com].

---

**Happy Scanning!**
