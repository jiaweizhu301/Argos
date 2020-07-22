import src.database as db
import json

# Get recommendation from db
def getRecommendation(variance, trend):

    # Get stock info from db
    stocks = db.get_stocks_AI()

    # Set range increments
    varIncr = 1
    trendIncr = 1
    sepStr = "~"

    # Parse stocks for relevant entries
    recommend = []
    for stock in stocks:

        # Exit early if too many
        if len(recommend) > 10:
            recommend = recommend[:7]
            break

        # Extract and check not None
        curVar = stock['variance']
        curTrend = stock['trend']
        if curVar is None or curTrend is None:
            continue
        curTrend *= 10

        # Check if valid variance
        validVar = False
        if variance[0] == '<' and curVar < int(variance[1:]):
            validVar = True
        elif variance[0] == '>' and curVar > int(variance[1:]):
            validVar = True
        elif variance[0] != '<' and variance[0] != '>':
            check = int(variance.split(sepStr)[0])
            validVar = (curVar >= check and curVar < check + varIncr)

        # Check if valid trend
        validTrend = False
        if trend[0] == '<' and curTrend < int(trend[1:]):
            validTrend = True
        elif trend[0] == '>' and curTrend > int(trend[1:]):
            validTrend = True
        elif trend[0] != '>' and trend[0] != '<':
            check = int(trend.split(sepStr)[0])
            validTrend = (curTrend >= check and curTrend < check + trendIncr)

        # Add to list if match
        if validVar and validTrend:
            recommend.append(stock['stock_code'])

    # Return tickers
    return recommend

# Generate JSON of graph
def generateGraph(client, recommend):

    # Get relevant lists
    portfolio = db.get_portfolio(client)
    watchlist = db.get_watchlist(client)
    recommendations = []
    for entry in recommend:
        recommendations.append(db.get_stock_info(entry))

    # Add quantity 0 to watchlist and recommendations
    for entry in watchlist:
        entry['quantity'] = 0
    for entry in recommendations:
        entry['quantity'] = 0

    # Compile full list with no overlaps
    allStocksTicker = []
    allStocks = []
    for entry in portfolio:
        allStocks.append(entry)
        allStocksTicker.append(entry['stock_code'])
        # Add to recommendations if is Sell - always draw that link
        if entry['action'] == 'S':
            recommendations.append(entry)
    for entry in watchlist:
        if entry['stock_code'] not in allStocksTicker:
            allStocks.append(entry)
            allStocksTicker.append(entry['stock_code'])
    for entry in recommendations:
        if entry['stock_code'] not in allStocksTicker:
            allStocks.append(entry)
            allStocksTicker.append(entry['stock_code'])


    # Init JSON and 3 root nodes
    data = {}
    data['nodes'] = []
    data['edges'] = []
    data['nodes'].append({'id': 'Portfolio', 'type': 'root', 'root': True})
    data['nodes'].append({'id': 'Watchlist', 'type': 'root', 'root': True})
    data['nodes'].append({'id': 'Recommendations', 'type': 'root', 'root': True})
    data['edges'].append({'source': 'Portfolio','target': 'Watchlist', 'type': "link"})
    data['edges'].append({'source': 'Watchlist','target': 'Recommendations', 'type': "link"})
    data['edges'].append({'source': 'Recommendations','target': 'Portfolio', 'type': "link"})

    # Add all other nodes
    for entry in allStocks:
        data['nodes'].append({
            'id': entry['stock_code'],
            'type': 'stock',
            'company': entry['company'],
            'industry': entry['industry'],
            'price': entry['price'],
            'variance': "{0:.4f}%".format(entry['variance']),
            'trend': "{0:.4f}%".format(entry['trend']*10),
            'quantity': entry['quantity'],
            'confidence': "{0:.2f}%".format(entry['confidence']*100),
            'action': entry['action'],
            'summary': entry['summary']
        })

    # Add each type of edge
    for entry in portfolio:
        data['edges'].append({
            'source': 'Portfolio',
            'target': entry['stock_code'],
            'type': 'portfolio',
            'quantity': entry['quantity']
        })
    for entry in watchlist:
        data['edges'].append({
            'source': 'Watchlist',
            'target': entry['stock_code'],
            'type': 'watchlist',
            'quantity': entry['quantity'],
        })
    for entry in recommendations:
        data['edges'].append({
            'source': 'Recommendations',
            'target': entry['stock_code'],
            'type': 'recommendations',
            'quantity': "{0:.2f}%".format(entry['confidence']*100)
        })

    return json.dumps(data)

# Store info at end of day
def dailyUpdate():
    db.batch_update_portfolio()
    db.batch_update_stock()
