# Rubberband Insider Bot

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Required dependencies (install via `pip`):
  ```sh
  pip install requests beautifulsoup4 yfinance alpaca-trade-api pandas schedule streamlit google-generativeai
  ```

### API Key Configuration
This program requires API keys for several services. Replace the placeholder keys with your own.

1. **Google Gemini AI API Key**:
   - Sign up at [Google AI](https://ai.google.com/)
   - Get an API key
   - Replace in `initialize()`:
     ```python
     genai.configure(api_key="YOUR_GEMINI_API_KEY")
     ```

2. **Alpaca Trading API Key**:
   - Create an account at [Alpaca](https://alpaca.markets/)
   - Get API keys
   - Replace in `main.py`:
     ```python
     alpaca_api_key = "YOUR_ALPACA_API_KEY"
     alpaca_secret = "YOUR_ALPACA_SECRET_KEY"
     ```

3. **News API Key** (optional for stock news):
   - Sign up at [NewsAPI](https://newsapi.org/)
   - Get an API key
   - Replace in `getStockNews()`:
     ```python
     news = getStockNews(stock, "YOUR_NEWSAPI_KEY")
     ```

---

## How It Works

### 1. **Stock Selection & Data Collection**
- The bot scrapes insider transaction data from **Dataroma** to find stocks with significant insider activity in the past week.
- It retrieves financial data from **Yahoo Finance** (market cap, PE ratio, growth metrics, etc.).
- It collects recent news articles for each stock using **NewsAPI**.
- All insider stocks are stored in `InsiderStocks.csv`.

### 2. **AI-Based Analysis**
- The bot uses **Google Gemini AI** to evaluate and rank the top five stocks based on earnings growth, valuation, risk, and dividends.
- AI selects the best stocks for trading and outputs recommendations.

### 3. **Trading Execution**
- Using **Alpaca API**, the bot automatically buys the top-selected stocks (if they are not already in the portfolio).
- It invests a default of **$300 per stock**, but this amount can be changed easily in `main.py` by modifying the following line:
  ```python
  buyStocks(stock, 300)  # Change 300 to your desired investment amount per stock
  ```
- The portfolio of active stocks is stored in `Portfolio.csv`.

### 4. **Rubberband Trading Strategy**
- For each stock, the bot:
  - Calculates a **7-day mean price**.
  - Computes the **ATR (Average True Range)**.
  - Sets **upper and lower price bands** using ATR.
- If a stock’s price **exceeds the upper band**, it sells the stock.
- If a stock’s price **drops below the lower band**, it sells the stock.
- If a stock is sold, a new stock is selected from the AI’s recommendations to maintain a full portfolio.

### 5. **Continuous Monitoring**
- The bot runs **every minute** to check stock prices and execute trades if conditions are met.
- Uses `schedule` and `time.sleep(1)` to ensure the strategy runs consistently.

---

## Running the Bot
Run the script:
```sh
python main.py
```
Let it run during **market hours**, and it will automatically handle stock selection, execution, and monitoring.

---

## Paper Trading vs. Real Trading
This bot currently runs in **paper trading mode**, meaning all trades are simulated and do not involve real money. 

If you want to switch to real trading:
1. **Change the Alpaca API Base URL** in `main.py`:
   ```python
   alpaca_baseurl = "https://paper-api.alpaca.markets"
   ```
   to:
   ```python
   alpaca_baseurl = "https://api.alpaca.markets"
   ```

2. **Ensure you have real trading permissions** on your Alpaca account.
3. **Fund your account** with actual money before executing live trades.

Be cautious when switching to real trading, as the bot will execute actual buy and sell orders based on its algorithm.

