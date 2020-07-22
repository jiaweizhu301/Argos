# Library includes
from flask import Flask, render_template, request, redirect, session, Response
from flask_session import Session
import json
import sys
import random

# Update scheduler includes
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Local file includes
from src.security import *
from src.api import updateStock
from src.query import *
import src.database as db

# Initialise app
app = Flask(__name__)
sess = Session()

# Login page
@app.route("/", methods=['GET', 'POST'])
def login():

    # Get request - view page
    if request.method == "GET":
        session.clear()
        return render_template("login.html", username="", error_msg="")

    # Else POST request - check login
    # Get parameters
    user = request.form["user"]
    pswd = request.form["pswd"]

    # Check valid and type
    admin = isAdmin(user)
    valid = correctPassword(user, pswd)

    # Invalid - error msg
    if not valid:
        msg = "Invalid username and password combination"
        return render_template("login.html", username=user, error_msg=msg)

    # Valid - redirect appropriately
    session['user'] = user
    if admin:
        return redirect("/admin")
    else:
        return redirect("/home")

# --------------------------------------------------------

# Admin page
@app.route("/admin")
def admin():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Get required lists
    users = db.get_all_users()
    users.remove(session["user"])
    stocks = db.get_all_stocks()
    consultants = [ x['username'] for x in db.get_all_consultants() ]
    clients = [{'id':x['client_id'],
        'name':x['title']+' '+x['given_names']+' '+x['family_name']+\
        ' - '+str(x['client_id'])
        } for x in db.get_all_clients()]

    # Set info msg if username already taken
    userTaken = ""
    if "info" in session:
        userTaken = "Username \"" + session["info"] + "\" is already taken"
        session.pop("info")

    # Return admin page
    return render_template("admin.html",users=users, stocks=stocks, consultants=consultants, clients=clients, userTaken=userTaken)

# Admin security check
@app.route("/admin_sec_check", methods=['POST'])
def admin_sec_check():
    if "user" not in session or not isAdmin(session["user"]):
        return "SECURITY BREACH"
    return "Valid"

# Create new user endpoint
@app.route("/create_user", methods=['POST'])
def create_user():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Extract fields
    user = request.form["user"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    pswd = request.form["pswd"]
    type = request.form["type"]

    # Check username taken
    if db.username_taken(user):
        session["info"] = user
        return redirect("/admin")

    # Secure password
    salt = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    pswd = hashPass(pswd, salt)

    # Add user to db
    db.create_user(user, fname, lname, pswd, salt, type)

    return redirect("/admin")

# Delete user endpoint
@app.route("/del_user", methods=['POST'])
def del_user():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Extract fields and remove from db
    user = request.form["user"]
    db.delete_user(user)

    return redirect("/admin")

# Change user password
@app.route("/change_pswd", methods=['POST'])
def change_pswd():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Extract id and remove from db
    user = request.form["user"]
    pswd = request.form["pswd"]
    print(user, pswd)

    # Secure password
    salt = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    print(salt)
    pswd = hashPass(pswd, salt)
    print(pswd)

    # Update password
    db.change_password(user, pswd, salt)

    return redirect("/admin")

# Create client endpoint
@app.route("/create_client", methods=['POST'])
def create_client():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Extract fields and remove from db
    title = request.form["title"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    principal = int(request.form["principal"])

    # Add client to db
    db.create_client(title, fname, lname, principal)

    return redirect("/admin")

# Delete client endpoint
@app.route("/del_client", methods=['POST'])
def del_client():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Extract id and remove from db
    client_id = request.form["client"]
    db.delete_client(client_id)

    return redirect("/admin")

# Grant access for consultant to manage client
@app.route("/grant_access", methods=['POST'])
def grant_access():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Extract id and add to db
    client_id = request.form["client"]
    consultant = request.form["consult"]
    db.grant_access(consultant, client_id)

    return redirect("/admin")

# Revoke access for consultant to manage client
@app.route("/revoke_access", methods=['POST'])
def revoke_access():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Extract ids and remove from db
    client_id = request.form["client"]
    consultant = request.form["consult"]
    db.revoke_access(consultant, client_id)

    return redirect("/admin")

# Update stock quantity for given client
@app.route("/set_quantity", methods=['POST'])
def set_quantity():

    # Security check
    if "user" not in session or not isAdmin(session["user"]):
        return redirect("/")

    # Extract id and remove from db
    stock = request.form["stock"]
    client = request.form["client"]
    quantity = int(request.form["quantity"])
    db.update_stock(client, stock, quantity)

    return redirect("/admin")

# --------------------------------------------------------

# Home page
@app.route("/home")
def home():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return redirect("/")

    # Get required lists from db
    stocks = db.get_all_stocks()
    clients = [{'id':x['client_id'],
        'name':x['title']+' '+x['given_names']+' '+x['family_name']+\
        ' - '+str(x['client_id'])
        } for x in db.get_my_clients(session["user"])]
    consoltant_name = db.get_consultant_name(session["user"])

    # Return home page
    return render_template("home.html", stock_list=stocks, client_list=clients, name=consoltant_name)

# Graph Endpoint
@app.route("/graph", methods=['POST'])
def graph_endpoint():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract params
    client = request.form["client"]
    variance = request.form["var"]
    trend = request.form["trend"]

    # Update session
    if variance == "-" and trend == "-":
        variance = session["variance"]
        trend = session["trend"]
    else:
        session["variance"] = variance
        session["trend"] = trend

    # Get JSON of graph for given client and return
    recommend = getRecommendation(variance, trend)
    graph = generateGraph(client, recommend)
    data = {"variance": variance, "trend": trend, "data": graph}
    return json.dumps(data)

# Get stock info
@app.route("/stock_info", methods=['POST'])
def stock_endpoint():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract param
    stock = request.form["stock"]
    client = request.form["client"]

    # Get data
    data = db.get_stock_info(stock)
    if data['variance'] is not None:
        data['variance'] = "{0:.4f}%".format(data['variance'])
        data['trend'] = "{0:.4f}%".format(data['trend']*10)
    else:
        data['variance'] = "N/A"
        data['trend'] = "N/A"
        data['price'] = "0.00"
    data['confidence'] = "{0:.2f}%".format(data['confidence']*100)
    data['inWatchlist'] = db.in_watch_list(client, stock)
    quantity = db.in_holdings(client, stock)
    if quantity == 0:
        data['owned'] = "Unowned"
    else:
        data['owned'] = "Owned - " + str(quantity)

    # Return
    return json.dumps(data)
    
    
# Get price of given stock
@app.route("/stock_price", methods=['POST'])
def stock_price():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract param and return price
    stock = request.form["stock"]
    return str(db.get_stock_price(stock))

# Toggle stock in watchlist
@app.route("/watchlist", methods=['POST'])
def watchlist_endpoint():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract param and toggle
    stock = request.form["stock"]
    client = request.form["client"]
    status = db.toggle_in_watchlist(client, stock)

    # Return current status
    if status:
        return "t"
    return "f"

# Get notes for client
@app.route("/notes", methods=['POST'])
def get_notes():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract param and toggle
    client = request.form["client"]
    data = db.get_client_notes(client)

    return json.dumps(data)

# Save today's note
@app.route("/save_note", methods=['POST'])
def save_note():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract param and toggle
    client = request.form["client"]
    note = request.form["note"]
    status = db.update_note(client, note)

    return "SUCCESS"

# Get client info
@app.route("/client_info", methods=['POST'])
def client_info():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract client ID and get info
    client = request.form["client"]
    data = db.get_client_info(client)
    data['principal'] = "{0:.2f}".format(data['principal'])
    data['portfolio_value'] =  "{0:.2f}".format(db.get_portfolio_value(client))
    data['portfolio_change'] = "{0:.3f}%".format(db.get_portfolio_change(client))

    # Get most volative personal + market stocks
    personal, market = db.get_top_stocks(client)
    data['top_personal'] = personal
    data['top_market'] = market

    return json.dumps(data)

# Get data for historical stock price graph
@app.route("/price_hist", methods=['POST'])
def price_history():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract stock and return data
    stock = request.form["stock"]
    data = db.get_price_history(stock)
    return json.dumps(data)

# Get spread of portfolio across different industries
@app.route("/industry_spread", methods=['POST'])
def industry_spread():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract stock and return data
    client = request.form["client"]
    data = db.portfolio_by_industry(client)
    return json.dumps(data)

# Return distribution of recommendations for heatmap
@app.route("/ai_dist", methods=['POST'])
def ai_distribution():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Setup axis vals
    trends = ['<-4', '-4~-3', '-3~-2', '-2~-1', '-1~0',
        '0~1', '1~2', '2~3', '3~4', '>4']
    variances = ['0~1', '1~2', '2~3', '3~4', '4~5',
        '5~6', '6~7', '7~8', '8~9', '9~10', '>10']

    # Calc freq of each pairing
    freq = [ [0] * len(trends) for _ in range(len(variances)) ]
    vals = db.get_stocks_AI()
    for stock in vals:

        # Check valid
        if stock['trend'] is None or stock['variance'] is None:
            continue

        # Trend Index
        trendIndex = int(stock['trend'] * 10)
        if trendIndex < -4:
            trendIndex = 0
        elif trendIndex <0 or (trendIndex == 0 and stock['trend'] < 0):
            trendIndex += 4
        else:
            trendIndex += 5
        if trendIndex > 9:
            trendIndex = 9

        # Variance Index
        varIndex = int(stock['variance'])
        if varIndex > 10:
            varIndex = 10

        freq[varIndex][trendIndex] += 1

    # Compile data and return
    data = {'trends': trends, 'variances': variances, 'data': freq}
    return json.dumps(data)

# Download csv file of stock data
@app.route("/stockData")
def stockData():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return redirect("/")

    # Create csv and return
    csv = db.get_stock_csv()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=stockData.csv"})

# Add new transaction
@app.route("/new_transac", methods=['POST'])
def new_transac():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract info
    client = request.form["client"]
    action = request.form["action"]
    stock = request.form["stock"]
    quantity = float(request.form["quantity"])
    price = float(request.form["price"])
    note = request.form["note"]

    # Get current holding for stock
    portf = db.get_portfolio(client)
    holding = None
    for entry in portf:
        if entry['stock_code'] == stock:
            holding = entry
            break

    # Get new quantity
    new_quant = 0
    if action == 'B':
        new_quant = quantity
        if holding is not None:
            new_quant += holding['quantity']
    else:
        if holding is None:
            return json.dumps({'status': 'FAILURE', 'msg': 'Cannot sell - client does not own ' + stock})
        new_quant = holding['quantity'] - quantity
        if new_quant < 0:
            return json.dumps({'status': 'FAILURE', 'msg': "Cannot sell - client only owns {0:.4f}".format(holding['quantity'])})

    # Check have funds and change accordingly
    funds = db.get_principal(client)
    val = float(str(round(quantity * price, 2)))
    if action == 'B' and funds < val:
        return json.dumps({'status': 'FAILURE', 'msg': "Cannot buy - insufficiemt funds by ${0:.2f}".format(val - funds)})
    if action == 'B':
        funds -= val
        db.set_principal(client, funds)
    else:
        funds += val
        db.set_principal(client, funds)

    # Update holdings and log transaction
    db.update_stock(client, stock, new_quant)
    db.add_transaction(client, action, stock, quantity, price, note)

    # Return success
    return json.dumps({'status': "SUCCESS", 'new_princ': "{0:.2f}".format(funds)})

# Update principal
@app.route("/update_principal", methods=['POST'])
def update_principal():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Extract param
    client = request.form["client"]
    action = request.form["action"]
    quantity = float(request.form["quantity"])

    # Update principal
    funds = db.get_principal(client)
    if action == 'D':
        funds += quantity
        db.set_principal(client, funds)
    else:
        funds -= quantity
        db.set_principal(client, funds)

    # Return new
    return "{0:.2f}".format(funds)

# Get all transactions
@app.route("/get_transac", methods=['POST'])
def get_transac():

    # Security check
    if "user" not in session or not isConsultant(session["user"]):
        return "SECURITY BREACH"

    # Return data
    client = request.form["client"]
    data = db.get_transactions(client)
    return json.dumps(data)

# --------------------------------------------------------

# Main
if __name__ == '__main__':

    # Init session
    app.secret_key = '5\xcfx\x92w\x8eW\xb9\xf7\x05\xc8E0Eb\x9b\xfd\x19\x90\xc1\xa9\xcd\xd2vA\xf4\xd8\x17(`\x92q'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)

    # Start app
    if len(sys.argv) > 1 and sys.argv[1] == "server":

        # Setup creation + destruction of scheduler
        scheduler = BackgroundScheduler()
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

        # Job: Update stock info
        scheduler.add_job(
            func=updateStock,
            trigger=IntervalTrigger(seconds=15),
            id='update_stock',
            name='Update oldest stock price',
            replace_existing=True,
            max_instances=2
        )

        # Job: Store end of day data
        scheduler.add_job(
            func=dailyUpdate,
            trigger='cron',
            hour='23',
            minute='55',
            id='daily_update',
            name='Store end of day info'
        )

        # Add SSL certificate
        context = ('host.crt', 'host.key')
        app.run(host="0.0.0.0", port=443, ssl_context=context)

    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        import src.testAll
    else:
        app.run()
