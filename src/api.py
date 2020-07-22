import urllib.request
import json
from datetime import datetime

from src.ai import processData
import src.database as db

# Store price points
class PricePoint:
    def __init__(self, timestamp, price):
        self.timestamp = timestamp
        self.price = price

# Store result of price query
class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.prices = []

    def addPrice(self, timestamp, price):
        price = PricePoint(timestamp, price) 
        self.prices.append(price)


# Get info for a given stock
def stockInfo(ticker):

    # Query parameters
    # Interval options: 1, 5, 15, 30, 60
    # OutputSize options: compact (100), full (1080-360)
    interval = "5" 
    outputSize = "compact"
    apiKey = "I08MFJ1XE83EC64R"

    # Get json data
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"\
        "&symbol=" + ticker + ".AX&interval=" + interval + "min"\
        "&outputsize=" + outputSize + "&apikey=" + apiKey
    raw = urllib.request.urlopen(url)
    data = json.loads(raw.read().decode())

    # Stock not supported - update time and set price to be number of times skipped
    if 'Error Message' in data:
        db.store_stock_info(ticker, None, None, None, datetime.today(), None, None, None)
        return None

    # Get keys for data extraction
    dataKey = "Time Series (" + interval + "min)" 
    priceKey = "4. close"

    # Exceeded API Rate-limit
    if dataKey not in data:
        return None

    # Extract data
    stock = Stock(ticker)
    for timestamp in data[dataKey]:
        time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        price = data[dataKey][timestamp][priceKey]
        stock.addPrice(time, price)

    # Return
    return stock
    
# Update oldest stocks info
def updateStock():
    
    # Get oldest stock
    ticker = db.get_oldest_stock()

    # Get pricepoints from API and call AI
    data = stockInfo(ticker)
    if data is not None:
        processData(data)
