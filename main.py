from flask import *
import sqlite3
app = Flask(__name__)
database = sqlite3.connect("users.db")
app.secret_key = '123'

cursor = database.cursor()

if not cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='members'").fetchone():
    cursor.execute("CREATE TABLE members(username, password, first_name, last_name, email, age)")
    database.commit()
else:
    pass

get_requests_count = 0
post_requests_count = 0

def valid_username(username):
    with sqlite3.connect("users.db") as database:
        cursor = database.cursor()
        if cursor.execute("SELECT count(*) FROM members WHERE username=?", (username,)).fetchone()[0] > 1:
            return False
        else: return True

def valid_email(email):
    if "@" not in email:
        return False
    else: return True

def create_accounts(username, password, first_name, last_name, email, age):
    with sqlite3.connect("users.db") as database:
        cursor = database.cursor()
        cursor.execute("INSERT INTO members VALUES(?, ?, ?, ?, ?, ?)", (username, password, first_name, last_name, email, age))
        database.commit()

def valid_login(username, password):
    if username == "admin":
        if password == "pass":
            return True
        else: return False
    else: return False


def valid_user_login(username, password):
    with sqlite3.connect("users.db") as database:
        cursor = database.cursor()
        if cursor.execute("SELECT count(*) FROM members WHERE username=?", (username,)).fetchone()[0] > 0:
            query_pass = cursor.execute("SELECT password FROM members WHERE username=?", (username,)).fetchone()[0]
            if query_pass == password:
                return True
            else: return False
        else: return False
    # return True


@app.route("/")
def redir_to_home():
    global get_requests_count
    global post_requests_count
    get_requests_count += 1
    return redirect("/home.html")

@app.route("/login.html", methods=['POST', 'GET'])
def login():
    global get_requests_count
    global post_requests_count
    error = None
    if request.method == 'GET':
        get_requests_count += 1
        if request.cookies.get('login_auth') == "true":
            flash("Already logged in!")
            return redirect('/home.html')
        else:
            return render_template("login.html")
    if request.method == 'POST':
        post_requests_count += 1
        if valid_user_login(request.form['username'],
                       request.form['password']):
            flash("Logged in!")
            redirection = make_response(redirect("/home.html"))
            redirection.set_cookie("login_auth", value="true")
            return redirection
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

@app.route("/create-account.html", methods=['POST', 'GET'])
def create_account():
    global get_requests_count
    global post_requests_count
    error = None
    if request.method == 'GET':
        get_requests_count += 1
        return render_template("create-account.html")
    if request.method == 'POST':
        post_requests_count += 1
        if valid_username(request.form['username']):
            if valid_email(request.form['email']):
                create_accounts(username=request.form['username'], password=request.form['password'], email=request.form['email'], age=request.form['age'], first_name=request.form['first_name'], last_name=request.form['last_name'])
                redirection = make_response(redirect("/login.html"))
                flash("Account sucessfully created!")
                return redirection
            elif not valid_email(request.form['email']):
                error = 'Invalid email, please enter a valid email address.'
        elif not valid_username(request.form['username']):
            error = 'Username taken or blacklisted, please choose another.'
    return render_template('create-account.html', error=error)

@app.route("/home.html")
def home():
    global get_requests_count
    global post_requests_count
    get_requests_count += 1
    return render_template("home.html")

@app.route("/download.html")
def downloads():
    global get_requests_count
    global post_requests_count
    get_requests_count += 1
    return render_template("download.html")

@app.route("/about.html")
def about():
    global get_requests_count
    global post_requests_count
    get_requests_count += 1
    return render_template("about.html")

@app.route("/devdashboard")
def developer_dashboard():
    global get_requests_count
    global post_requests_count
    get_requests_count += 1
    if request.cookies.get('auth') == "true":
        return f"<p>get requests since last reboot: {get_requests_count}</p><br><p>post requests since last reboot: {post_requests_count}</p>"
    else:
        return "<p>Not authenticated, please login.</p>"

@app.route("/devlogin", methods=['POST', 'GET'])
def dev_logins():
    global get_requests_count
    global post_requests_count
    error = None
    if request.method == 'GET':
        get_requests_count += 1
        if request.cookies.get('auth') == "true":
            return redirect('/devdashboard')
        else:
            return render_template("devlogin.html")
    if request.method == 'POST':
        post_requests_count += 1
        if valid_login(request.form['username'],
                       request.form['password']):
            redirection = make_response(redirect("/devdashboard"))
            redirection.set_cookie("auth", value="true")
            return redirection
        else:
            error = 'Invalid username/password'
    return render_template('devlogin.html', error=error)

