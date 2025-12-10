from flask import Flask,request,session,redirect,url_for,render_template,flash
import hashlib
import mysql.connector
from datetime import timedelta
from models.user import User
from database import cursor, db

app = Flask(__name__)
app.secret_key = "5MS2"
app.permanent_session_lifetime = timedelta(days=5)

@app.route('/')
def start():
    if 'user' in session:
        return redirect(url_for('home'))
    else:
        return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    if request.method == "POST":
        user = User.login(
            request.form['email'],
            request.form['password']
        )
        if user:
            session.permanent = True
            session['user'] = user[0]
            return redirect(url_for('home'))
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

@app.route("/home",methods=["POST","GET"])
def home():
    if 'user' in session:
        userID = session['user']
        user = User.get_user_by_id(userID)

        if user:
            return render_template('home.html',first_name = user.first_name,kcal = user.get_recommended_calories())
    else:
        return redirect(url_for('login'))

@app.route('/progress',methods=["POST","GET"])
def progress():
    if 'user' in session:
        userID = session['user']
        user = User.get_user_by_id(userID)

        if user:
            return render_template('progress.html')
    else:
        return redirect(url_for('login'))

@app.route('/settings',methods=["POST","GET"])
def settings():
    if 'user' in session:
        userID = session['user']
        user = User.get_user_by_id(userID)

        if request.method == "POST":
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            email = request.form.get("email")
            dob = request.form.get("dob")
            gender = request.form.get("gender")
            height = request.form.get("height")
            weight = request.form.get("weight")
            activity = request.form.get("activity")

            sql = '''
                UPDATE user
                SET first_name=%s,last_name=%s,email=%s,date_of_birth=%s,gender=%s,height=%s,current_weight=%s,activity_level=%s
                WHERE user_id=%s
                '''
            cursor.execute(sql,(first_name,last_name,email,dob,gender,height,weight,activity,userID))
            db.commit()

            user = User.get_user_by_id(userID)

            return render_template('settings.html',
                                    first_name = user.first_name,
                                    last_name = user.last_name,
                                    email = user.email,
                                    dob=user.dob,
                                    gender=user.gender,
                                    height = user.height,
                                    weight=user.weight,
                                    activity = user.activity)
        elif user:
            return render_template('settings.html',
                                    first_name = user.first_name,
                                    last_name = user.last_name,
                                    email = user.email,
                                    dob=user.dob,
                                    gender=user.gender,
                                    height = user.height,
                                    weight=user.weight,
                                    activity = user.activity)
    else:
        return redirect(url_for('start'))

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('start'))

    userID = session['user']
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_new_password = request.form['confirm_new_password']

    if new_password != confirm_new_password:
        flash("New passwords do not match", "danger")
        return redirect(url_for('settings'))

    user = User.get_user_by_id(userID)

    if not user.check_password(current_password):
        flash("Current password is incorrect", "danger")
        return redirect(url_for('settings'))
    
    hashed = hashlib.sha256(new_password.encode()).hexdigest()
    sql = "UPDATE user SET password_hash=%s WHERE user_id=%s"
    cursor.execute(sql, (hashed, userID))
    db.commit()

    flash("Password updated successfully!", "success")
    return redirect(url_for('settings'))


@app.route('/logout',methods=["POST","GET"])
def logout():
    if 'user' in session:
        session.clear()
        return redirect(url_for('start'))


if __name__ == "__main__":
    app.run(debug=True)