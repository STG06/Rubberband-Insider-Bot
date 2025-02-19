import requests
from bs4 import BeautifulSoup
import yfinance as yh
from datetime import datetime,timedelta
from alpaca.data.timeframe import TimeFrame
import time 
import schedule
import csv
import google.generativeai as genai
import streamlit as st
import pandas as pd

def initialize():
    #Streamlit setup
    """st.header("**Rubberband Insider Algo**")
    st.divider()"""

    #Webscrapping Setup
    data_roma_url = "https://www.dataroma.com/m/home.php"
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    homePageResponse = requests.get(data_roma_url,headers=headers)
    stocks = {}

    currentDate = int(str(datetime.now().date()).split("-")[2])
    weekBeforeDate = currentDate - 7

    #Gemeni AI Setup
    genai.configure(api_key="AIzaSyDoRkJARx--SsCKRhjRsAIdy-ddPIucXTg")
    model = genai.GenerativeModel("gemini-1.5-flash")
   
   

    #Getting insider Stocks 
    if homePageResponse.status_code == 200:
       soup = BeautifulSoup(homePageResponse.text, "html.parser")
       prettySoup = soup.prettify()
       div_ins = soup.find("div", id="ins")
       if div_ins:
           table = div_ins.find("table")
           tbody = table.find("tbody")
           if tbody:
               rows = tbody.findAll("tr")
               for row in rows:
                   cells = row.find_all("td")

                   stockData = cells[1].get_text(strip=True).split("-")
                   stock = stockData[0].strip()

                   if cells[0].get_text(strip=True) == "Today":
                       if stock not in stocks:
                           stocks[stock] = ["Today",1]
                       else:
                           stocks[stock][1] += 1
                   else:

                       date = cells[0].get_text(strip=True)
                       day = int(cells[0].get_text(strip=True).split()[0])

                       if(day > weekBeforeDate and day <= currentDate):
                           if stock not in stocks:
                               stocks[stock] = [date,1]
                           else:
                               stocks[stock][1] += 1
    else:
        print("Error with html")

    #Getting Data about Insider Stocks 
    for stock in stocks.keys():
        data = {}
        ticker = yh.Ticker(stock)
        info = ticker.info
        data["Sector"] = info.get("sector")
        data["Industry"] = info.get("industry")
        data["Market Cap"] = info.get("marketCap")
        data["Current Price"] = info.get("currentPrice")
        data["Dividend Rate"] = info.get("dividendRate")
        data["Dividend Yield"] = info.get("dividendYield")
        data["Trailing PE"] = info.get("trailingPE")
        data["Forward PE"] = info.get("forwardPE")
        data["Beta"] = info.get("beta")
        data["Profit Margins"] = info.get("profitMargins")
        data["Total Revenue"] = info.get("totalRevenue")
        data["Earngins Growth"] = info.get("earningsGrowth")
        data["Revenue Growth"] = info.get("revenueGrowth")
        stocks[stock].append(data)
        time.sleep(2);
        

    #Getting Recent News about each Stock
    for stock in stocks.keys():
        news = getStockNews(stock, "f5f88558259b4fab8b25a5139a6f1c49")
        stocks[stock].append(news)

    #Displaying all insider stocks using streamlit 
    """st.subheader("**Insider Stocks this week**")
    data_rows = []
    news_rows = []

    for stock, values in stocks.items():
         date = values[0] # Extract date from set
         count = values[1]          # Extract count
         details = values[2]        # Extract detailed data
         news = values[3]           # Extract recent news

        

         data_rows.append({
            "Stock": stock,
            "Date": date,
            "Count": count,
            **details
            })

         for key, value in news.items():
             news_rows.append({
                "Stock": stock,
                "Article": key,
                "News": value,
                })

    df = pd.DataFrame(data_rows)
    df_news = pd.DataFrame(news_rows)

    st.dataframe(df)
    st.divider()
    
    st.subheader("**Recent News About the Stocks**")
    st.dataframe(df_news)
    st.divider()"""

    #Asking Google Gemini for which stocks to purchase
    prompt = f"""
    Here is data for multiple stocks in a structured format. Each stock includes metrics like sector, industry, market cap, current price, dividend rate, PE ratios, growth rates, and recent news about the company. 
    Analyze the data and choose the top 5 stocks to purchase based on the following criteria:
    1. **Growth Potential**:
       - Earnings Growth: Must have an earnings growth rate of 10%+.
       - Revenue Growth: Must have a revenue growth rate of 10%+.
    2. **Valuation**:
       - Trailing P/E: Must be below the industry average.
       - Forward P/E: Should be below 25.
       - Dividend Yield: Preferably above 3%.
    3. **Risk and Stability**:
       - Beta: Preferably between 0.5 and 1.2.
       - Profit Margins: Should be above 10%.
       - Debt-to-Equity: Preferably below 0.5.
    4. **Market Conditions**:
       - Sector: Look for growth sectors like Technology, Healthcare, and Consumer Discretionary.
       - Market Cap: Preferably Mid-cap to Large-cap stocks.
    5. **Dividends**: Stability and a consistent history of increasing dividends are a plus.

    Stocks:
    {stocks}

    For each of the top 5 stocks you select, explain why it was chosen based on the metrics provided. Only list the stocks with high yield potential dont bother with anything else"""
   
    
    detailedResponse = model.generate_content(prompt)
    stockResponse = model.generate_content(f"Just list the top 5 stocks from this content and seperate them with spaces. If there are no stocks then just leave it blank {detailedResponse.text}")
    
    #Displaying top 5 stock picks using streamlit
    """st.subheader("**Top 5 stock picks according to AI**")
    st.write(detailedResponse.text)"""

    #Putting stocks into a csv file for Quant Connect
    stockStr = stockResponse.text.strip()
    stockList = stockStr.split()
    with open("InsiderStocks.csv", mode="w",newline="") as file:
        writer = csv.writer(file)
        for stock in stockList:
            writer.writerow([stock])

    for stock in stockList[:]:
        if not stock.isupper():
            stockList.remove(stock)

    return stockList

def getStockNews(stock, api_key):
    news = {}
    url = "https://newsapi.org/v2/everything"
    
    # Parameters for the request
    params = {
        "q": stock,          
        "sortBy": "publishedAt",  
        "language": "en",         
        "apiKey": api_key         
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            news[1] = "This stock has no recent news"
        for i, article in enumerate(articles[:5], start =1):
            news[i] = (
                f"Title: {article['title']}\n"
                f"Source: {article['source']['name']}\n"
                f"Published At: {article['publishedAt']}\n"
                f"URL: {article['url']}\n"
            )
    else:
        news[1]= "Error retrieving news data"

    return news


if __name__ == "__main__":
    initialize()
