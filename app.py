from flask import Flask,request,session,redirect,url_for,render_template
import mysql.connector
from datetime import timedelta
from models.user import User
from database import cursor, db

app = Flask(__name__)
app.secret_key = "5MS2"
app.permanent_session_lifetime = timedelta(days=5)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    if request.method == "POST":
        user = User.login(
            request.form['email'],
            request.form['password']
        )
        if user:
            session.permanent = True
            session['user'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    step = request.args.get("step", "1")

    if step == "1":
        if request.method == "POST":
            session['first-name'] = request.form['first-name']
            session['last-name'] = request.form['last-name']
            session['gender'] = request.form['gender']
            session['dob'] = request.form['dob']
            return redirect(url_for("register", step="2"))

        return render_template("step1.html")

    elif step == "2":
        if request.method == "POST":
            session['height'] = request.form['height']
            session['weight'] = request.form['weight']
            session['activity-level'] = request.form['activity-level']
            return redirect(url_for("register", step="3"))

        return render_template("step2.html")

    elif step == "3":
        if request.method == "POST":
            session['email'] = request.form['email']
            session['password'] = request.form['password']

            success = User.register(
                email=session['email'],
                password=session['password'],
                first_name=session['first-name'],
                last_name=session['last-name'],
                gender=session['gender'].upper(),
                dob=session['dob'],
                weight=float(session['weight']),
                height=float(session['height']),
                activity=session['activity-level']
            )

            session.clear()

            if success:
                return redirect(url_for('login'))
            else:
                return "❌ Email already exists!"

        return render_template("step3.html")

@app.route("/dashboard",methods=["POST","GET"])
def dashboard():
    if 'user' in session:
        userID = session['user']
        user = User.get_user_by_id(userID)

        if user:
            return f"<h1>Welcome {user.first_name} <h1>" #HTML code not finished yet
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)