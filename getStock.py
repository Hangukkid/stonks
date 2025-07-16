import yfinance as yf
from time import sleep
from datetime import datetime, timedelta
import gspread

# from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials
from requests_ratelimiter import LimiterSession, RequestRate, Limiter, Duration
from constants import *

def waitUntilNextTime():
    currTime = datetime.now()
    if (currTime.hour <= 8):
        sleep((9 - currTime.hour) * 60 * 60)
        return
    elif (currTime.hour >= 16):
        sleep((9 + 23 - currTime.hour) * 60 * 60)
    newMinute = 10 - (currTime.minute % 10)
    
    sleep(newMinute * 60)

def get_google_sheets_client():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    # Authorize the client
    return gspread.authorize(creds)

def findTickerValue(ticker):
    print(ticker)
    # history_rate = RequestRate(1, Duration.SECOND)
    # limiter = Limiter(history_rate)
    # session = LimiterSession(limiter=limiter)
    # session.headers['User-agent'] = 'tickerpicker/1.0'
    tickerStats = yf.Ticker(ticker)#, session=session)
    # print(tickerStats.info)
    price = None
    if (tickerStats.info.get("currentPrice") != None):
        return tickerStats.info["currentPrice"] 
    elif (tickerStats.info.get("bid") != None and tickerStats.info.get("ask") != None):
        return (tickerStats.info["bid"] + tickerStats.info["ask"])/2
    
    return None


while True:
    try:
        sheets = get_google_sheets_client()
        spreadsheet = sheets.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.sheet1  # Open the first sheet

        tickers = worksheet.row_values(1)
        for i in range(1, len(tickers)):
            ticker = tickers[i]
            price = None
            if (len(ticker) == 0 or ticker == "Total" or ticker == "Unused"):
                continue
            while (price == None):
                price = findTickerValue(ticker)
                sleep(1)
            worksheet.update_cell(3, i + 1, price)
        # print(yf.Ticker("CAD=X").info.get("previousClose"))
        worksheet.update_cell(100, 1, yf.Ticker("CAD=X").info.get("previousClose"))
        worksheet.update_cell(1, 1, datetime.now().strftime("%I:%M%p @ %Y-%m-%d"))
        print("Updated at " + datetime.now().strftime("%I:%M%p @ %Y-%m-%d"))
    except:
        print("unknown error")
    waitUntilNextTime()

#python3 -m pip install yfinance --upgrade --no-cache-dir