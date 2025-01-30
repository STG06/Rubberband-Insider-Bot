from sched import scheduler
import sched
from datetime import datetime, timedelta
from alpaca.data.timeframe import TimeFrame
import time 
import schedule
import csv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
import alpaca_trade_api as tradeapi
from alpaca.data.requests import StockLatestQuoteRequest
from Initialize import initialize

# Alpaca API setup
alpaca_api_key = "KEY"  # Add key here
alpaca_secret = "KEY"  # Add key here
alpaca_baseurl = "https://paper-api.alpaca.markets"

alpaca = TradingClient(
    alpaca_api_key, 
    alpaca_secret, 
    paper=True
)

client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret)
live_client = tradeapi.REST(alpaca_api_key, alpaca_secret, alpaca_baseurl)

# Current Portfolio stock data
stocks = {}

with open("Portfolio.csv", mode="r") as file:
    if file:
        lines = file.readlines()
        for line in lines:
            if line:
                aList = line.split(",")
                stocks[aList[0]] = (float(aList[1]), float(aList[2]))

def buyStocks(symbol, amount):
    try:
        quote = live_client.get_latest_trade(symbol)
        current_price = quote.price

        shares = amount / current_price

        market_order_data = MarketOrderRequest(
            symbol=symbol,
            notional=amount, 
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )

        # Submit the order
        alpaca.submit_order(order_data=market_order_data)
        print(f"Market order placed to buy approximately ${amount} worth of {symbol} at ${current_price:.2f} per share.")
    except:
        print("No stocks meet the criteria to buy")

def main():
    stockList = initialize()

    # Using Alpaca to buy/sell
    if isMarketOpen():
        for stock in stockList:
            positions = alpaca.get_all_positions()
            currentStocks = [position.symbol for position in positions]
            if stock not in currentStocks and len(positions) < 5:
                buyStocks(stock, 300)
                rubber_band_strategy(stock) 
    else:
        print("Market is closed")

def isMarketOpen():
    clock = alpaca.get_clock()
    return clock.is_open

def executeStrategy():
    if isMarketOpen():
        symbols_to_remove = []
        for symbol, (lower_band, upper_band) in stocks.items():
            last_trade = live_client.get_latest_trade(symbol)
            currentPrice = last_trade.price
            
            if currentPrice > upper_band or currentPrice < lower_band:
                try:
                    position = alpaca.get_open_position(symbol)
                    qtyToSell = float(position.qty)

                    live_client.submit_order(symbol=symbol, qty=qtyToSell, side="sell", type="market", time_in_force="day")
                    print(f"Sold all {qtyToSell} shares of {symbol} at {currentPrice}")

                    symbols_to_remove.append(symbol)
                    remove_row("Portfolio.csv", symbol)
                    initialize()
                except Exception as e:
                    print(f"Error while placing sell order or no position to sell: {e}")

        for symbol in symbols_to_remove:
            stocks.pop(symbol)
    else:
        print("Market is currently closed")

if __name__ == "__main__":
    main()

# Continuously checking the market every minute
schedule.every(1).minutes.do(executeStrategy)

while True:
    schedule.run_pending()
    time.sleep(1)
