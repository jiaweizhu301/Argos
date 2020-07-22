import sqlite3
from datetime import datetime


#------------------------------------LOGIN--------------------------------------


# Get hashed password of user
def get_password(username):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command and extract response
    c.execute("SELECT password FROM Users WHERE username = ?;", (username,))
    entry = c.fetchone()
    password = None
    if entry is not None:
        password = entry[0]

    # Disconnect
    conn.commit()
    conn.close()

    return password

# Get salt of user
def get_salt(username):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command and extract response
    c.execute("SELECT salt FROM Users WHERE username = ?;", (username,))
    entry = c.fetchone()
    salt = None
    if entry is not None:
        salt = entry[0]

    # Disconnect
    conn.commit()
    conn.close()

    return salt

# Get type (admin / consultant) of user
def get_type(username):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command and extract response
    c.execute("SELECT type FROM Users WHERE username = ?;", (username,))
    entry = c.fetchone()
    type = None
    if entry is not None:
        type = entry[0]

    # Disconnect
    conn.commit()
    conn.close()

    return type
    
# Get name of given consultant
def get_consultant_name(username):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command and extract response
    c.execute("SELECT given_names, family_name FROM Users WHERE username = ?;", (username,))
    entry = c.fetchone()
    name = "Unknown User"
    if entry is not None:
        name = entry[0] + " " + entry[1]

    # Disconnect
    conn.commit()
    conn.close()

    return name


# ------------------------------------ADMIN-------------------------------------


# Create new user
def create_user(username, given_names, family_name, password, salt, type):

    # Check unique username
    if username_taken(username):
        return

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("INSERT INTO Users(family_name, given_names, username, password, salt, type) VALUES (?, ?, ?, ?, ?, ?);", (family_name, given_names, username, password, salt, type))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Check if given username already taken
def username_taken(username):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command and process response
    c.execute("SELECT COUNT(*) FROM Users WHERE username=?;", (username,))
    resp = (c.fetchone()[0] != 0)

    # Disconnect
    conn.commit()
    conn.close()

    return resp

# Create new client
def create_client(title, given_names, family_name, principal):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Calc client_id
    c.execute("SELECT COALESCE(MAX(client_id) + 1, 0) FROM Client")
    client_id = c.fetchone()[0]

    # Execute command
    c.execute("INSERT INTO Client(title, client_id, given_names, family_name, principal) VALUES (?, ?, ?, ?, ?);", (title, client_id, given_names, family_name, principal))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Delete existing user
def delete_user(username):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("DELETE FROM Users WHERE username = ?", (username,))
    c.execute("DELETE FROM Manages WHERE username = ?", (username,))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Delete existing client
def delete_client(client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("DELETE FROM Client WHERE client_id = ?;", (client_id,))
    c.execute("DELETE FROM Manages WHERE client_id = ?;", (client_id,))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Grant access of consultant to client
def grant_access(username, client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Check not already present
    c.execute("SELECT COUNT(*) FROM Manages WHERE username = ? AND client_id = ?", (username, client_id))
    if c.fetchone()[0] > 0:
        return

    # Execute command
    c.execute("INSERT INTO Manages(username,client_id) VALUES(?, ?);", (username, client_id))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Revoke access of consultant to client
def revoke_access(username, client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("DELETE FROM Manages WHERE client_id = ? AND username = ?;", (client_id, username))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Update stock quantity for clients portfolio
def update_stock(client_id, stock_code, quantity):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Check if already present
    c.execute("SELECT COUNT(*) FROM Holdings WHERE client_id = ? AND stock_code = ?;", (client_id, stock_code))
    notPresent = (c.fetchone()[0] == 0)

    # Execute relevant command
    if notPresent and quantity == 0:
        pass
    elif notPresent:
        c.execute("INSERT INTO Holdings VALUES(?,?,?);", (client_id, stock_code, quantity))
    elif quantity == 0:
        c.execute("DELETE FROM Holdings WHERE client_id = ? AND stock_code = ?;", (client_id, stock_code))
    else:
        c.execute("UPDATE Holdings SET quantity = ? WHERE client_id = ? AND stock_code = ?;", (quantity, client_id, stock_code))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Get list of all consultants
def get_all_consultants():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT username, given_names, family_name FROM Users WHERE type = 'C' ORDER BY username;")
    entries = c.fetchall()

    # Extract response
    consultants = [{
        'username': row[0],
        'given_names': row[1],
        'family_name': row[2]
    } for row in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return consultants

# Get list of all clients
def get_all_clients():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT client_id, title, given_names, family_name FROM Client ORDER BY client_id;")
    entries = c.fetchall()

    # Extract response
    clients = [{
        'client_id': row[0],
        'title': row[1],
        'given_names': row[2],
        'family_name': row[3]
    } for row in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return clients

# Get list of all users
def get_all_users():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT username FROM Users ORDER BY username;")
    entries = c.fetchall()

    # Extract response
    users = [ x[0] for x in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return users

# Set new password for given client
def change_password(username, new_hashed_pw, new_salt):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("UPDATE Users SET password = ?, salt = ? WHERE username = ?;", (new_hashed_pw, new_salt, username))

    # Disconnect
    conn.commit()
    conn.close()

    return

# ---------------------------------CONSULTANT-----------------------------------
# *********************************CLIENT TAB***********************************

# Get clients for given consultant
def get_my_clients(username):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT C.client_id, C.title, C.given_names, C.family_name FROM Client C JOIN Manages M ON (C.client_id = M.client_id) WHERE username = ? ORDER BY C.client_id", (username,))
    entries = c.fetchall()

    # Extract response
    clients = [{
        'client_id': row[0],
        'title': row[1],
        'given_names': row[2],
        'family_name': row[3]
    } for row in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return clients

# Get info for given client
def get_client_info(client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT title, given_names, family_name, principal FROM Client WHERE client_id = ?;", (client_id,))
    row = c.fetchone()

    # Extract response
    client = None
    if row is not None:
        client = {
            'title': row[0],
            'given_names': row[1],
            'family_name': row[2],
            'principal': row[3]
        }

     # Disconnect
    conn.commit()
    conn.close()

    return client
    
# Get info for given client
def get_top_stocks(client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    
    # Get relevant dates
    c.execute("SELECT MAX(stock_time) FROM StockPrice")
    date = c.fetchone()[0]
    c.execute("SELECT MAX(stock_time) FROM StockPrice WHERE stock_time != ?", (date,))
    prev_date = c.fetchone()[0]
    
    # Get global top
    c.execute("SELECT (P1.price / P2.price) - 1 AS change, P1.stock_code FROM StockPrice P1 JOIN StockPrice P2 ON (P1.stock_code = P2.stock_code) WHERE P1.price NOT NULL AND P1.stock_time = ? AND P2.stock_time = ? ORDER BY ABS(change) DESC LIMIT 3", (date, prev_date))
    rows = c.fetchall()
    top_market = []
    for cur in rows:
        top_market.append(cur[1] + ": {0:.3f}%".format(cur[0]))
        
    # Get held top
    c.execute("SELECT * FROM (SELECT (P1.price / P2.price) - 1 AS change, P1.stock_code FROM StockPrice P1 JOIN StockPrice P2 ON (P1.stock_code = P2.stock_code) WHERE P1.price NOT NULL AND P1.stock_time = ? AND P2.stock_time = ? ORDER BY ABS(change) DESC) NATURAL JOIN (SELECT stock_code FROM Holdings WHERE client_id = ?) LIMIT 3", (date, prev_date, client_id))
    rows = c.fetchall()
    top_held = []
    for cur in rows:
        top_held.append(cur[1] + ": {0:.3f}%".format(cur[0]))
    while len(top_held) < 3:
        top_held.append("-")    
    
    # Disconnect
    conn.commit()
    conn.close()

    return top_held, top_market

# Get portfolio value for given client
def get_portfolio_value(client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT SUM(H.quantity * S.price) FROM Holdings H JOIN Stock S ON (H.stock_code = S.stock_code) WHERE H.client_id = ?;", (client_id,))
    responce = c.fetchone()
    value = 0
    if responce is not None:
        value = responce[0]

     # Disconnect
    conn.commit()
    conn.close()

    return value

# Get portfolio value for given client
def get_portfolio_change(client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get current val of portfolio
    c.execute("SELECT SUM(H.quantity * S.price) FROM Holdings H JOIN Stock S ON (H.stock_code = S.stock_code) WHERE H.client_id = ?;", (client_id,))
    responce = c.fetchone()
    current_val = 0
    if responce is not None:
        current_val = responce[0]

    # Get previous value of portfolio
    c.execute("SELECT value FROM PortfolioValue WHERE (client_id = ? AND portfolio_time = (SELECT MAX(portfolio_time) FROM PortfolioValue WHERE client_id = ?))", (client_id, client_id))
    responce = c.fetchone()
    old_val = 0
    if responce is not None:
        old_val = responce[0]

    value = 0
    if current_val != 0 and old_val != 0:
        value = (current_val / old_val) - 1
    value *= 100

     # Disconnect
    conn.commit()
    conn.close()

    return value

# Get notes for given client
def get_client_notes(client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get old notes
    c.execute("SELECT note_time, notes FROM ClientNotes WHERE client_id = ? AND note_time != DATE('now', 'localtime') ORDER BY note_time DESC", (client_id,))
    entries = c.fetchall()
    notes = {}
    notes['saved'] = [{
        'note_time': datetime.strptime(row[0], '%Y-%m-%d').strftime('%d/%m/%y'),
        'notes': row[1]
    } for row in entries]

    # Get current note 
    c.execute("SELECT notes FROM ClientNotes WHERE client_id = ? AND note_time = DATE('now', 'localtime')", (client_id,))
    val = c.fetchone()
    current_note = "" 
    if val is not None:
        current_note = val[0]
    notes['current'] = current_note

     # Disconnect
    conn.commit()
    conn.close()

    return notes

# Add not for given client
def update_note(client_id, note):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Check if already note for today 
    c.execute("SELECT COUNT(*) FROM ClientNotes WHERE client_id = ? AND note_time = DATE('now', 'localtime')", (client_id,))
    exists = (c.fetchone()[0] != 0)

    if exists:
        c.execute("UPDATE ClientNotes SET notes = ? WHERE client_id = ? AND note_time = DATE('now', 'localtime')", (note, client_id))
    else:
        c.execute("INSERT INTO ClientNotes VALUES(DATE('now', 'localtime'),?,?)", (client_id, note))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Get portfolio value grouping by industry
def portfolio_by_industry(client_id):
    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT industry, SUM(H.quantity * S.price) as value FROM Holdings H JOIN Stock S ON (H.stock_code = S.stock_code) WHERE H.client_id = ? GROUP BY industry;", (client_id,))
    entries = c.fetchall()

    # Extract response
    total = 0
    for row in entries:
        total += row[1]

    # get industries and portions for those industries
    industries = [row[0] for row in entries]
    portion = [(row[1] / total) * 100  for row in entries]

    # declare list that used to contain all stocks entries
    entriesWhole = []

    # for each industry, add stocks for the industry onto the list
    for industry in industries:
        c.execute("SELECT S.stock_code, H.quantity * S.price as value FROM Holdings H JOIN Stock S ON (H.stock_code = S.stock_code) WHERE H.client_id = ? AND S.industry = ?;", (client_id,industry))
        entries = c.fetchall()
        entriesWhole.append(entries)
    
    #find the total for all stocks values
    stocksTotal = 0
    for entry in entriesWhole:
        for row in entry:
            stocksTotal += row[1]

    #all the stocks code and portions
    stocks = []
    stocksPortions = []

    #find the stocks portions and added stocks code onto the list
    for entry in entriesWhole:
        for row in entry:
            stocks.append(row[0])
            stocksPortions.append((row[1] / total) * 100)
    
    data = {'industries': industries, 'portion': portion, 'stocks' : stocks, 'stocksPortions' : stocksPortions}

     # Disconnect
    conn.commit()
    conn.close()

    return data

# *********************************STOCK TAB************************************

# Get list of all stocks
def get_all_stocks():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT stock_code FROM Stock WHERE price NOT NULL ORDER BY stock_code;")
    entries = c.fetchall()

    # Extract response
    stocks = [ x[0] for x in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return stocks

# Get portfolio of given client
def get_portfolio(client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT S.stock_code, H.quantity, S.company, S.industry, S.price, S.pricetime, S.variance, S.trend, S.confidence, S.action, S.summary FROM Stock S JOIN Holdings H ON (S.stock_code = H.stock_code) WHERE client_id = ?", (client_id,))
    entries = c.fetchall()

    # Extract response
    holdings = [{
        'stock_code': row[0],
        'quantity': row[1],
        'company': row[2],
        'industry': row[3],
        'price': row[4],
        'pricetime': row[5],
        'variance': row[6],
        'trend': row[7],
        'confidence': row[8],
        'action': row[9],
        'summary': row[10]
    } for row in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return holdings

# Get info for given stock
def get_stock_info(stock_code):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT stock_code, company, industry, price, pricetime, variance, trend, confidence, action, summary FROM Stock WHERE stock_code = ?", (stock_code,))
    row = c.fetchone()

    # Extract response
    stock = None
    if row is not None:
        stock = {
            'stock_code': row[0],
            'company': row[1],
            'industry': row[2],
            'price': row[3],
            'pricetime': row[4],
            'variance': row[5],
            'trend': row[6],
            'confidence': row[7],
            'action': row[8],
            'summary': row[9]
        }

    # Disconnect
    conn.commit()
    conn.close()

    return stock
    
# Get current price of given stock
def get_stock_price(stock):
    
    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT price FROM Stock WHERE stock_code = ?", (stock,))
    row = c.fetchone()

    # Extract response
    price = 0
    if row is not None:
        price = row[0]

    # Disconnect
    conn.commit()
    conn.close()

    return price

# Get watchlist of given client
def get_watchlist(client_id):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT S.stock_code, S.company, S.industry, S.price, S.pricetime, S.variance, S.trend, S.confidence, S.action, S.summary FROM Stock S JOIN Watchlist W ON (S.stock_code = W.stock_code) WHERE client_id = ?", (client_id,))
    entries = c.fetchall()

    # Extract response
    watchlist = [{
        'stock_code': row[0],
        'company': row[1],
        'industry': row[2],
        'price': row[3],
        'pricetime': row[4],
        'variance': row[5],
        'trend': row[6],
        'confidence': row[7],
        'action': row[8],
        'summary': row[9]     
    } for row in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return watchlist

# Check if stock in client's watchlist
def in_watch_list(client, stock):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Run query
    c.execute("SELECT COUNT(*) FROM WatchList WHERE client_id = ? AND stock_code = ?", (client, stock))
    inWatchList = (c.fetchone()[0] != 0)

    # Disconnect
    conn.commit()
    conn.close()

    return inWatchList
    
# Check if stock in client's holdings
def in_holdings(client, stock):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Run query
    c.execute("SELECT quantity FROM Holdings WHERE client_id = ? AND stock_code = ?", (client, stock))
    quantity = 0
    resp = c.fetchone()
    if resp is not None:
        quantity = resp[0]

    # Disconnect
    conn.commit()
    conn.close()

    return quantity

# Add new stock to given clients watchlist
def toggle_in_watchlist(client_id, stock_code):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Check if currently in watchlist
    c.execute("SELECT COUNT(*) FROM WatchList WHERE client_id = ? AND stock_code = ?", (client_id, stock_code))
    inWatchlist = (c.fetchone()[0] != 0)

    # Toggle
    if inWatchlist: 
        c.execute("DELETE FROM Watchlist WHERE client_id = ? AND stock_code = ?;", (client_id, stock_code))
    else:
        c.execute("INSERT INTO Watchlist VALUES(?,?);", (client_id, stock_code))

    # Disconnect
    conn.commit()
    conn.close()

    return not inWatchlist

# Get price history for stock
def get_price_history(stock_code):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT stock_time, price FROM StockPrice WHERE stock_code = ?", (stock_code,))
    entries = c.fetchall()

    # Extract response
    times = [row[0] for row in entries]
    prices = [row[1] for row in entries]

    data = {} 
    data['times'] = times
    data['prices'] = prices

    # Disconnect
    conn.commit()
    conn.close()

    return data


# -------------------------------API & AI STUFF---------------------------------


# Get the stock that has longest time since last update
def get_oldest_stock():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command and extract response
    c.execute("SELECT stock_code FROM Stock ORDER BY pricetime ASC LIMIT 1;")
    entry = c.fetchone()
    stock_code = entry[0]

    # Disconnect
    conn.commit()
    conn.close()

    return stock_code

# Store stock info
def store_stock_info(code, variance, trend, price, pricetime, confidence, action, summary):

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("UPDATE Stock SET variance = ?, trend = ?, price = ?, pricetime = ?, confidence = ?, action = ?, summary = ? WHERE stock_code = ?;", (variance, trend, price, pricetime, confidence, action, summary, code))

    # Disconnect
    conn.commit()
    conn.close()

    return

# Get info of all stocks for AI
def get_stocks_AI():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT stock_code, variance, trend FROM Stock WHERE action = 'B' ORDER BY price DESC;")
    entries = c.fetchall()

    # Extract response
    stocks = [{
        'stock_code': row[0],
        'variance': row[1],
        'trend': row[2]
    } for row in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return stocks

# ------------------------------- DAILY UPDATE---------------------------------

# Get price of all stocks
def get_stock_prices():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT stock_code, price FROM Stock")
    entries = c.fetchall()

    # Extract response
    stocks = [{
        'stock_code': row[0],
        'price': row[1]
    } for row in entries]

    # Disconnect
    conn.commit()
    conn.close()

    return stocks

# Store portfolio value of all users
def batch_update_portfolio():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Update for each client
    for client in get_all_clients():

        client_id = client['client_id']

        # Get value of portfolio
        c.execute("SELECT SUM(H.quantity * S.price) FROM Holdings H JOIN Stock S ON (H.stock_code = S.stock_code) WHERE H.client_id = ?;", (client_id,))
        responce = c.fetchone()
        value = 0
        if responce is not None:
            value = responce[0]

        # Store
        c.execute("INSERT INTO PortfolioValue(portfolio_time, client_id, value) VALUES(DATE('now', 'localtime'), ?, ?);", (client_id, value))

    # Disconnect
    conn.commit()
    conn.close()

# Store price of all stocks
def batch_update_stock():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Update for each client
    for stock in get_stock_prices():

        # Get info
        stock_code = stock['stock_code']
        price = stock['price']

        # If already have 15 delete one
        c.execute("SELECT COUNT(*) FROM StockPrice WHERE stock_code = ?", (stock_code,))
        full = (c.fetchone()[0] >= 15)
        if full:
            c.execute("DELETE FROM StockPrice WHERE stock_code = ? AND stock_time IN (SELECT stock_time FROM StockPrice WHERE stock_code = ? ORDER BY stock_time ASC LIMIT 1);", (stock_code, stock_code))


        # Store current price
        c.execute("INSERT INTO StockPrice(stock_time, stock_code, price) VALUES(DATE('now', 'localtime'), ?,?);", (stock_code, price))

    # Disconnect
    conn.commit()
    conn.close()


# --------------------------------CSV DOWNLOAD----------------------------------


# Get stock data as csv string
def get_stock_csv():

    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute command
    c.execute("SELECT * FROM Stock WHERE price IS NOT NULL ORDER BY stock_code;")
    entries = c.fetchall()

    # Headers
    data = "Ticker,Industry,Company,Variance,Trend,Price,Last Update,Confidence,Action\n"

    # Add stock data but not suggestions
    for row in entries: 
        for i in range(len(row) - 1 ):
            data += '\"' + str(row[i]) + '\",'
        data += '\n'

    # Disconnect
    conn.commit()
    conn.close()

    return data


# -------------------------------- TRANSACTION ---------------------------------

# Update principal for given client
def get_principal(client):
    
    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute
    c.execute("SELECT principal FROM Client WHERE client_id = ?", (client,))
    val = c.fetchone()[0]

    # Disconnect
    conn.commit()
    conn.close()
    
    return val

# Update principal for given client
def set_principal(client, principal):
    
    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute
    c.execute("UPDATE Client SET principal = ? WHERE client_id = ?", (principal, client))

    # Disconnect
    conn.commit()
    conn.close()
    
# Add transaction
def add_transaction(client, action, stock, quantity, price, note):
    
    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute
    c.execute("INSERT INTO Transactions VALUES(?,?,?,?,?,?,DATETIME('now', 'localtime'));", (client, action, stock, quantity, price, note))

    # Disconnect
    conn.commit()
    conn.close()
    
# Get all transactons for given user
def get_transactions(client):
    
    # Connect
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Execute
    c.execute("SELECT * FROM Transactions WHERE client_id = ? ORDER BY transac_time DESC;", (client,))
    entries = c.fetchall()
    
    # Extract response
    transactions = []
    for row in entries:
        c.execute("SELECT price FROM Stock WHERE stock_code = ?", (row[2],))
        cur_price = c.fetchone()[0]
        action = "Bought"
        if row[1] == 'S':
            action = "Sold"
        transactions.append({
            'action': action,
            'stock': row[2],
            'time': datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S').strftime('%H:%M %d/%m/%y'),
            'price': "${0:.2f}".format(row[4]),
            'current_price': "${0:.2f}".format(cur_price),
            'price_change': "{0:.3f}%".format(((cur_price / row[4]) - 1) * 100),
            'quantity': row[3],
            'cost': "${0:.2f}".format(row[3] * row[4]),
            'note': row[5]
        })
    
    # Disconnect
    conn.commit()
    conn.close()
    
    return transactions
