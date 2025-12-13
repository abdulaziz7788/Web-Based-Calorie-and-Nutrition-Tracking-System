from flask import Flask,request,session,redirect,url_for,render_template,flash,jsonify,Blueprint
import hashlib
import mysql.connector
from datetime import timedelta,datetime,date
from models.user import User
from models.activity import Activity
from models.workout import Workout
from models.meals import Meal
from models.Food import Food
from models.mealfood import MealFood
from models.WaterIntake import WaterIntake
from models.goal import Goal
from models.sleep import Sleep
from models.progress import Progress
from database import cursor, db
from flask_mail import Mail,Message
from mail_service import MailService
import random
import re

app = Flask(__name__)
app.config.from_object('config')
app.secret_key = "5MS2"
app.permanent_session_lifetime = timedelta(days=5)

# Security improvements
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

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
        user = User.login(request.form['email'], request.form['password'])

        if user == "not_verified":
            flash("⚠️ Please verify your email first!", "warning")
            return redirect(url_for('login'))

        if user:
            session['user'] = user.user_id
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
            # FIX: Convert gender to uppercase
            session['gender'] = request.form['gender'].upper()
            
            # Validate date of birth
            dob = request.form['dob']
            try:
                dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
                today = datetime.now().date()
                age = (today - dob_date).days // 365
                
                if dob_date >= today:
                    flash("❌ Date of birth cannot be in the future!", "danger")
                    return redirect(url_for("register", step="1"))
                
                if age < 13:
                    flash("❌ You must be at least 13 years old to register!", "danger")
                    return redirect(url_for("register", step="1"))
                    
            except ValueError:
                flash("❌ Invalid date format!", "danger")
                return redirect(url_for("register", step="1"))
            
            session['dob'] = dob
            return redirect(url_for("register", step="2"))

        return render_template("step1.html")

    elif step == "2":
        if request.method == "POST":
            # Validate height and weight
            try:
                height = float(request.form['height'])
                weight = float(request.form['weight'])
                
                if not (50 <= height <= 300):
                    flash("❌ Height must be between 50 and 300 cm!", "danger")
                    return redirect(url_for("register", step="2"))
                
                if not (20 <= weight <= 500):
                    flash("❌ Weight must be between 20 and 500 kg!", "danger")
                    return redirect(url_for("register", step="2"))
                    
            except ValueError:
                flash("❌ Height and weight must be valid numbers!", "danger")
                return redirect(url_for("register", step="2"))
            
            session['height'] = request.form['height']
            session['weight'] = request.form['weight']
            
            # Ensure activity level is selected
            activity_level = request.form.get('activity-level')
            if not activity_level:
                flash("❌ Please select an activity level!", "danger")
                return redirect(url_for("register", step="2"))
            
            session['activity-level'] = activity_level
            return redirect(url_for("register", step="3"))

        return render_template("step2.html")

    elif step == "3":
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form.get('confirm-password')
            
            # FIX: Validate email format
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                flash("❌ Invalid email format!", "danger")
                return redirect(url_for('register', step="3"))
            
            # FIX: Validate password confirmation
            if password != confirm_password:
                flash("❌ Passwords do not match!", "danger")
                return redirect(url_for('register', step="3"))
            
            # FIX: Validate password length
            if len(password) < 10:
                flash("❌ Password must be at least 10 characters!", "danger")
                return redirect(url_for('register', step="3"))
            
            # Check for spaces in password
            if ' ' in password:
                flash("❌ Password cannot contain spaces!", "danger")
                return redirect(url_for('register', step="3"))
            
            session['email'] = email
            session['password'] = password

            success = User.register(
                email=session['email'],
                password=session['password'],
                first_name=session['first-name'],
                last_name=session['last-name'],
                gender=session['gender'],
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
                Welcome to CalorieFlow!

                Please verify your email by clicking the link below:

                {verify_link}
                """

                mail_service.send_email(
                subject="Verify Your Email",
                recipients=[email],
                body=body
                )

                session.clear()
                flash("✅ Registration successful! Check your email to verify your account.", "success")
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

    return "<p>Your email has been verified successfully! ✅</p>"

@app.route('/send_reset_code', methods=['POST'])
def send_reset_code():
    email = request.form['email']

    sql = "SELECT user_id FROM user WHERE email=%s"
    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    if not user:
        flash("❌ No account found with this email.", "danger")
        return redirect(url_for('getmail'))

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
        return redirect(url_for('getmail'))

    if request.method == 'GET':
        return render_template('new_password.html')

    password = request.form['password']
    confirm = request.form['confirm_password']

    if password != confirm:
        flash("❌ Passwords do not match.", "danger")
        return redirect(url_for('new_password'))
    
    if len(password) < 10:
        flash("❌ Password must be at least 10 characters!", "danger")
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

@app.route("/home", methods=["GET"])
def home():
    if 'user' not in session:
        return redirect(url_for('login'))

    userID = session['user']
    user = User.get_user_by_id(userID)

    if not user:
        return redirect(url_for('login'))

    today = date.today().strftime("%Y-%m-%d")

    # 💧 WATER
    water_today = WaterIntake.getDailyTotal(userID, today)
    water_goal = WaterIntake.calculateDailyGoal(userID)

    # 😴 SLEEP
    latest_sleep = Sleep.get_latest_sleep(userID)
    sleep_minutes = 0
    if latest_sleep and latest_sleep.hours_slept:
        sleep_minutes = int(latest_sleep.hours_slept * 60)

    sleep_percentage = min((sleep_minutes / 480) * 100, 100)

    return render_template(
        "home.html",

        # USER
        user=user,
        first_name=user.first_name,

        # CALORIES
        kcal=user.get_recommended_calories(),

        # WATER
        water_today=water_today,
        water_goal=water_goal,

        # SLEEP
        sleep_minutes=sleep_minutes,
        sleep_percentage=sleep_percentage

    )

@app.route("/sleep/add", methods=["POST"])
def log_sleep():
    if 'user' not in session:
        return redirect(url_for('login'))

    hours = int(request.form["hours"])
    minutes = int(request.form["minutes"])

    total_hours = round(hours + minutes / 60, 2)

    Sleep.log_sleep(
        user_id=session['user'],
        hours=total_hours
    )

    return redirect(url_for("home"))


# FIX: Add missing routes
@app.route('/meals')
def meals():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('meal.html')

@app.route('/add_meals')
def add_meals():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('AddingMeals.html')

@app.route('/workouts')
def workouts():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('Workouts.html')


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
            gender = request.form.get("gender").upper()  # FIX: Ensure uppercase
            height = request.form.get("height")
            weight = request.form.get("weight")
            activity = request.form.get("activity")
            
            # Validate inputs
            try:
                height_val = float(height)
                weight_val = float(weight)
                
                if not (50 <= height_val <= 300):
                    flash("❌ Height must be between 50 and 300 cm!", "danger")
                    return redirect(url_for('settings'))
                
                if not (20 <= weight_val <= 500):
                    flash("❌ Weight must be between 20 and 500 kg!", "danger")
                    return redirect(url_for('settings'))
                    
            except (ValueError, TypeError):
                flash("❌ Invalid height or weight!", "danger")
                return redirect(url_for('settings'))

            sql = '''
                UPDATE user
                SET first_name=%s,last_name=%s,email=%s,date_of_birth=%s,gender=%s,height=%s,current_weight=%s,activity_level=%s
                WHERE user_id=%s
                '''
            cursor.execute(sql,(first_name,last_name,email,dob,gender,height,weight,activity,userID))
            db.commit()
            
            flash("✅ Settings updated successfully!", "success")

            user = User.get_user_by_id(userID)

            return render_template('settings.html',
                                    first_name = user.first_name,
                                    last_name = user.last_name,
                                    email = user.email,
                                    dob=user.dob.strftime('%Y-%m-%d') if user.dob else '',
                                    gender=user.gender,
                                    height = user.height,
                                    weight=user.weight,
                                    activity = user.activity)
        elif user:
            return render_template('settings.html',
                                    first_name = user.first_name,
                                    last_name = user.last_name,
                                    email = user.email,
                                    dob=user.dob.strftime('%Y-%m-%d') if user.dob else '',
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
        flash("❌ New passwords do not match", "danger")
        return redirect(url_for('settings'))
    
    if len(new_password) < 10:
        flash("❌ Password must be at least 10 characters!", "danger")
        return redirect(url_for('settings'))

    user = User.get_user_by_id(userID)

    if not user.check_password(current_password):
        flash("❌ Current password is incorrect", "danger")
        return redirect(url_for('settings'))
    
    hashed = hashlib.sha256(new_password.encode()).hexdigest()
    sql = "UPDATE user SET password_hash=%s WHERE user_id=%s"
    cursor.execute(sql, (hashed, userID))
    db.commit()

    flash("✅ Password updated successfully!", "success")
    return redirect(url_for('settings'))


@app.route("/progress")
def progress():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    user_id = session["user"]

    today = datetime.today().date()
    week_start = today - timedelta(days=today.weekday() + 1)

    daily = Progress.get_weekly_daily_summary(user_id, week_start)
    water = Progress.get_weekly_water(user_id, week_start)
    sleep = Progress.get_weekly_sleep(user_id, week_start)
    summary = Progress.get_weekly_summary_boxes(user_id, week_start)
    macros = Progress.get_weekly_macros(user_id, week_start)


    return render_template(
        "progress.html",
        daily=daily,
        water=water,
        sleep=sleep,
        total_water_l=summary['total_water_l'],
        avg_sleep=summary['avg_sleep'],
        macros=macros
    )



@app.route('/logout',methods=["POST","GET"])
def logout():
    if 'user' in session:
        session.clear()
        return redirect(url_for('start'))


# ---------- JSON API endpoints for Activity / Workout / Goal / Sleep ----------

def _require_user():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return None


@app.route("/api/activities", methods=["GET", "POST"])
def activities_api():
    if request.method == "GET":
        keyword = request.args.get("q")
        category = request.args.get("category")
        if keyword:
            activities = Activity.search_activity(keyword)
        else:
            activities = Activity.get_activity_list(category=category)
        return jsonify([a.to_dict() for a in activities])

    # POST: create new activity (admin/owner only; requires login)
    auth = _require_user()
    if auth:
        return auth

    data = request.get_json(silent=True) or request.form
    name = data.get("activity_name")
    category = data.get("activity_category")
    calories = data.get("calories_per_minute")
    description = data.get("description")

    if not name or not category or calories is None:
        return jsonify({"error": "activity_name, activity_category, and calories_per_minute are required"}), 400
    try:
        calories_value = float(calories)
    except ValueError:
        return jsonify({"error": "calories_per_minute must be numeric"}), 400

    activity = Activity.add_new_activity(name, category, calories_value, description)
    return jsonify(activity.to_dict()), 201


@app.route("/api/workouts", methods=["GET", "POST"])
def workouts_api():
    auth = _require_user()
    if auth:
        return auth
    user_id = session["user"]

    if request.method == "GET":
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        limit = request.args.get("limit", 50)
        try:
            limit_value = int(limit) if limit else 50
        except ValueError:
            return jsonify({"error": "limit must be an integer"}), 400

        workouts = Workout.get_workout_history(user_id, start_date=start_date, end_date=end_date, limit=limit_value)
        return jsonify([w.to_dict() for w in workouts])

    data = request.get_json(silent=True) or request.form
    activity_type = data.get("activity_type")
    duration = data.get("duration")
    intensity = data.get("intensity", "moderate")
    workout_date = data.get("workout_date")
    workout_time = data.get("workout_time")
    calories_burned = data.get("calories_burned")

    if not activity_type or duration is None:
        return jsonify({"error": "activity_type and duration are required"}), 400
    try:
        duration_value = int(duration)
        calories_value = int(calories_burned) if calories_burned is not None else None
    except ValueError:
        return jsonify({"error": "duration and calories_burned must be numeric"}), 400

    try:
        workout = Workout.log_workout(
            user_id=user_id,
            activity_type=activity_type,
            duration=duration_value,
            workout_date=workout_date,
            workout_time=workout_time,
            intensity=intensity,
            calories_burned=calories_value,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(workout.to_dict()), 201


@app.route("/api/workouts/<int:workout_id>", methods=["PATCH", "DELETE"])
def workout_detail_api(workout_id):
    auth = _require_user()
    if auth:
        return auth
    user_id = session["user"]

    if request.method == "DELETE":
        deleted = Workout.delete_workout(workout_id, user_id=user_id)
        if not deleted:
            return jsonify({"error": "Workout not found"}), 404
        return "", 204

    data = request.get_json(silent=True) or {}
    numeric_fields = ("duration", "calories_burned")
    fields = {}
    for key in (
        "activity_type",
        "duration",
        "workout_date",
        "workout_time",
        "calories_burned",
        "intensity",
    ):
        value = data.get(key)
        if value is None:
            continue
        if key in numeric_fields:
            try:
                value = int(value)
            except ValueError:
                return jsonify({"error": f"{key} must be numeric"}), 400
        fields[key] = value

    try:
        updated = Workout.update_workout(workout_id, user_id=user_id, **fields)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updated:
        return jsonify({"error": "Workout not found"}), 404

    workout = Workout.get_workout_history(user_id, limit=None)
    current = next((w for w in workout if w.workout_id == workout_id), None)
    return jsonify(current.to_dict() if current else {"workout_id": workout_id}), 200


@app.route("/meals", methods=["GET", "POST"])
def meals():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']

    if request.method == "POST":
        meal = Meal(
            mealID=None,
            userID=user_id,
            mealName=request.form["mealName"],
            mealDate=request.form["mealDate"],
            mealTime=request.form["mealTime"],
            mealType=request.form["mealType"],
            totalCalories=float(request.form["totalCalories"]),
            totalProtein=float(request.form["totalProtein"]),
            totalCarbs=float(request.form["totalCarbs"]),
            totalFats=float(request.form["totalFats"])
        )
        meal.logMeal()

        return redirect(url_for("meals"))

    meals = Meal.getMealHistory(user_id)
    return render_template("meal.html", meals=meals)



@app.route("/foods", methods=["GET", "POST"])
def foods():
    if request.method == "POST":
        food = Food(
            foodID=None,
            foodName=request.form["food_name"],
            category=request.form["category"],
            servingSize=request.form["serving_size"],
            servingUnit=request.form["serving_unit"],
            calories=request.form["calories"],
            protein=request.form["protein"],
            carbohydrates=request.form["carbohydrates"],
            fats=request.form["fats"],
            fiber=request.form["fiber"],
            sugar=request.form["sugar"]
        )
        food.addNewFood()

    foods = Food.searchFood("")
    return render_template("foods.html", foods=foods)


@app.route("/foods/search")
def search_food():
    keyword = request.args.get("q", "")
    foods = Food.searchFood(keyword)
    return render_template("foods.html", foods=foods)


@app.route("/mealfood", methods=["GET", "POST"])
def meal_food():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']
    meals = Meal.getMealHistory(user_id)
    foods = Food.searchFood("")

    if request.method == "POST":
        entry = MealFood(
            mealFoodID=None,
            mealID=request.form["meal_id"],
            foodID=request.form["food_id"],
            quantity=request.form["quantity"],
            caloriesConsumed=request.form["calories_consumed"]
        )
        entry.addFoodToMeal()

    return render_template("meal_food.html", meals=meals, foods=foods)


@app.route("/water", methods=["GET", "POST"])
def water():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']

    if request.method == "POST":
        water = WaterIntake(
            waterIntakeID=None,
            userID=user_id,
            amount=float(request.form["amount"]),
            unit=request.form["unit"],
            loggedAt=None
        )
        water.addIntake()

    history = WaterIntake.getIntakeHistory(user_id)
    total = WaterIntake.getDailyTotal(user_id)
    return render_template("water.html", history=history, total=total)



@app.route("/api/goals", methods=["GET", "POST"])
def goals_api():
    auth = _require_user()
    if auth:
        return auth
    user_id = session["user"]

    if request.method == "GET":
        status = request.args.get("status")
        goals = Goal.get_goals_for_user(user_id, status=status)
        return jsonify([g.to_dict() for g in goals])

    data = request.get_json(silent=True) or request.form
    goal_type = data.get("goal_type")
    if not goal_type:
        return jsonify({"error": "goal_type is required"}), 400

    def _parse_optional_int(value):
        if value is None or value == "":
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def _parse_optional_float(value):
        if value is None or value == "":
            return None
        try:
            return float(value)
        except ValueError:
            return None

    target_weight = _parse_optional_float(data.get("target_weight"))
    daily_calorie_target = _parse_optional_int(data.get("daily_calorie_target"))
    start_date = data.get("start_date")
    target_date = data.get("target_date")
    status = data.get("status", "active")

    goal = Goal.create_goal(
        user_id=user_id,
        goal_type=goal_type,
        target_weight=target_weight,
        daily_calorie_target=daily_calorie_target,
        start_date=start_date,
        target_date=target_date,
        status=status,
    )
    return jsonify(goal.to_dict()), 201


@app.route("/api/goals/<int:goal_id>", methods=["PATCH"])
def goal_detail_api(goal_id):
    auth = _require_user()
    if auth:
        return auth
    user_id = session["user"]

    data = request.get_json(silent=True) or {}
    fields = {}
    for key in ("goal_type", "start_date", "target_date", "status"):
        if key in data and data.get(key) is not None:
            fields[key] = data.get(key)

    for numeric_field, parser in (
        ("target_weight", float),
        ("daily_calorie_target", int),
    ):
        if numeric_field in data and data.get(numeric_field) is not None:
            try:
                fields[numeric_field] = parser(data.get(numeric_field))
            except ValueError:
                return jsonify({"error": f"{numeric_field} must be numeric"}), 400

    try:
        updated = Goal.update_goal(goal_id, user_id=user_id, **fields)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updated:
        return jsonify({"error": "Goal not found"}), 404

    goal = Goal.get_goal_by_id(goal_id, user_id=user_id)
    return jsonify(goal.to_dict() if goal else {"goal_id": goal_id}), 200


@app.route("/api/sleep", methods=["GET", "POST"])
def sleep_api():
    auth = _require_user()
    if auth:
        return auth
    user_id = session["user"]

    if request.method == "GET":
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        limit = request.args.get("limit", 30)
        try:
            limit_value = int(limit) if limit else 30
        except ValueError:
            return jsonify({"error": "limit must be numeric"}), 400

        sleep_logs = Sleep.get_sleep_history(user_id, start_date=start_date, end_date=end_date, limit=limit_value)
        return jsonify([s.to_dict() for s in sleep_logs])

    data = request.get_json(silent=True) or request.form
    sleep_date = data.get("sleep_date")
    bedtime = data.get("bedtime")
    wake_time = data.get("wake_time")
    sleep_quality = data.get("sleep_quality")
    notes = data.get("notes")
    hours_slept = data.get("hours_slept")

    try:
        hours_value = float(hours_slept) if hours_slept not in (None, "") else None
    except ValueError:
        return jsonify({"error": "hours_slept must be numeric"}), 400

    sleep_log = Sleep.log_sleep(
        user_id=user_id,
        sleep_date=sleep_date,
        bedtime=bedtime,
        wake_time=wake_time,
        sleep_quality=sleep_quality,
        notes=notes,
        hours_slept=hours_value,
    )
    return jsonify(sleep_log.to_dict()), 201


@app.route("/api/sleep/<int:sleep_log_id>", methods=["PATCH", "DELETE"])
def sleep_detail_api(sleep_log_id):
    auth = _require_user()
    if auth:
        return auth
    user_id = session["user"]

    if request.method == "DELETE":
        deleted = Sleep.delete_sleep_log(sleep_log_id, user_id=user_id)
        if not deleted:
            return jsonify({"error": "Sleep log not found"}), 404
        return "", 204

    data = request.get_json(silent=True) or {}
    fields = {}
    for key in ("sleep_date", "bedtime", "wake_time", "sleep_quality", "notes"):
        if key in data and data.get(key) is not None:
            fields[key] = data.get(key)

    if "hours_slept" in data and data.get("hours_slept") is not None:
        try:
            fields["hours_slept"] = float(data.get("hours_slept"))
        except ValueError:
            return jsonify({"error": "hours_slept must be numeric"}), 400

    try:
        updated = Sleep.update_sleep_log(sleep_log_id, user_id=user_id, **fields)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not updated:
        return jsonify({"error": "Sleep log not found"}), 404

    sleep_entries = Sleep.get_sleep_history(user_id, limit=None)
    current = next((s for s in sleep_entries if s.sleep_log_id == sleep_log_id), None)
    return jsonify(current.to_dict() if current else {"sleep_log_id": sleep_log_id}), 200


if __name__ == "__main__":
    app.run(debug=True)
