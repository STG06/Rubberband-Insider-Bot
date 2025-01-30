import requests
from bs4 import BeautifulSoup
import yfinance as yh
from datetime import datetime, timedelta
from alpaca.data.timeframe import TimeFrame
import time 
import schedule
import csv
import google.generativeai as genai
import streamlit as st
import pandas as pd

def initialize():
    # Webscraping Setup
    data_roma_url = "https://www.dataroma.com/m/home.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    homePageResponse = requests.get(data_roma_url, headers=headers)
    stocks = {}

    currentDate = int(str(datetime.now().date()).split("-")[2])
    weekBeforeDate = currentDate - 7

    # Google Gemini AI Setup
    genai.configure(api_key="KEY")  # Add key here
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Getting insider Stocks 
    if homePageResponse.status_code == 200:
        soup = BeautifulSoup(homePageResponse.text, "html.parser")
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
                    date = cells[0].get_text(strip=True)
                    day = int(date.split()[0])
                    if date == "Today":
                        stocks[stock] = ["Today", 1]
                    elif weekBeforeDate < day <= currentDate:
                        stocks.setdefault(stock, [date, 0])[1] += 1
    else:
        print("Error with HTML response")

    # Getting Data about Insider Stocks 
    for stock in stocks.keys():
        ticker = yh.Ticker(stock)
        info = ticker.info
        stocks[stock].append({
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Market Cap": info.get("marketCap"),
            "Current Price": info.get("currentPrice"),
            "Dividend Rate": info.get("dividendRate"),
            "Dividend Yield": info.get("dividendYield"),
            "Trailing PE": info.get("trailingPE"),
            "Forward PE": info.get("forwardPE"),
            "Beta": info.get("beta"),
            "Profit Margins": info.get("profitMargins"),
            "Total Revenue": info.get("totalRevenue"),
            "Earnings Growth": info.get("earningsGrowth"),
            "Revenue Growth": info.get("revenueGrowth")
        })

    # Getting Recent News about each Stock
    for stock in stocks.keys():
        news = getStockNews(stock, "KEY")  # Add key here
        stocks[stock].append(news)

    # Writing stocks into CSV file
    with open("InsiderStocks.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        for stock in stocks.keys():
            writer.writerow([stock])

    return list(stocks.keys())

def getStockNews(stock, api_key):
    news = {}
    url = "https://newsapi.org/v2/everything"
    params = {"q": stock, "sortBy": "publishedAt", "language": "en", "apiKey": api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        for i, article in enumerate(articles[:5], start=1):
            news[i] = f"Title: {article['title']}\nSource: {article['source']['name']}\nPublished At: {article['publishedAt']}\nURL: {article['url']}"
    else:
        news[1] = "Error retrieving news data"
    return news

if __name__ == "__main__":
    initialize()
