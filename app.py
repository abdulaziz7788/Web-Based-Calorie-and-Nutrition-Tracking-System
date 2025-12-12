from flask import Flask,request,session,redirect,url_for,render_template,flash
import hashlib
import mysql.connector
from datetime import timedelta
from models.user import User
from database import cursor, db
from flask_mail import Mail,Message
from mail_service import MailService
import random

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = "5MS2"
app.permanent_session_lifetime = timedelta(days=5)

mail_service = MailService(app)


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
        if user == "not_verified":
            flash("⚠️ Please verify your email first!", "warning")
            return redirect(url_for('login'))

        if user:
            session['user'] = user[1]
            return redirect(url_for('home'))
        else:
            flash("❌ Email or password is wrong!", "danger")
            return redirect(url_for('login'))

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


            if success:
                email = session['email']
                token = mail_service.generate_token(email)
                verify_link = url_for('verify_email', token=token, _external=True)

                body=f"""
                Welcome to CaloriFlow!

                Please verify your email by clicking the link below:

                {verify_link}
                """

                mail_service.send_email(
                subject="Verify Your Email",
                recipients=[email],
                body=body
                )

                session.clear()
                flash(" Registration successful! Check your email to verify your account.", "success")
                return redirect(url_for('login'))
            else:
                flash("❌ Email already exists!", "danger")
                return redirect(url_for('register', step="3"))


        return render_template("step3.html")

@app.route('/verify/<token>')
def verify_email(token):
    email = mail_service.confirm_token(token)

    if not email:
        return "Invalid or expired token ❌"

    sql = "UPDATE user SET is_verified = 1 WHERE email = %s"
    cursor.execute(sql, (email,))
    db.commit()

    return "<p>Your email has been verified successfully! <p>"

@app.route('/send_reset_code', methods=['POST'])
def send_reset_code():
    email = request.form['email']

    sql = "SELECT user_id FROM user WHERE email=%s"
    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    if not user:
        flash("❌ No account found with this email.", "danger")
        return redirect(url_for('getmail'))

    import random
    code = str(random.randint(100000, 999999))

    session['reset_email'] = email
    session['reset_code'] = code

    mail_service.send_email(
        subject="Your Password Reset Code",
        recipients=[email],
        body=f"Your password reset code is: {code}"
    )

    flash("📩 A verification code has been sent to your email.", "info")
    return redirect(url_for('verify_reset_code'))

@app.route('/verify_reset_code', methods=['GET', 'POST'])
def verify_reset_code():
    if request.method == 'GET':
        return render_template('verify_reset_code.html')

    entered_code = request.form['code']

    if entered_code == session.get('reset_code'):
        session['reset_verified'] = True
        return redirect(url_for('new_password'))

    flash("❌ Incorrect code. Try again.", "danger")
    return redirect(url_for('verify_reset_code'))

@app.route('/new_password', methods=['GET', 'POST'])
def new_password():
    if not session.get('reset_verified'):
        return redirect(url_for('forgot_password'))

    if request.method == 'GET':
        return render_template('new_password.html')

    password = request.form['password']
    confirm = request.form['confirm_password']

    if password != confirm:
        flash("❌ Passwords do not match.", "danger")
        return redirect(url_for('new_password'))

    hashed = hashlib.sha256(password.encode()).hexdigest()
    email = session['reset_email']

    sql = "UPDATE user SET password_hash=%s WHERE email=%s"
    cursor.execute(sql, (hashed, email))
    db.commit()

    session.pop('reset_email', None)
    session.pop('reset_code', None)
    session.pop('reset_verified', None)

    flash("✅ Your password has been updated! You can now log in.", "success")
    return redirect(url_for('login'))


@app.route('/getmail')
def getmail():
    return render_template('getmail.html')

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