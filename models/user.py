import hashlib
from database import cursor, db
from datetime import datetime

class User:

    def __init__(self, email, first_name, last_name, gender, dob, weight, height, activity):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.dob = dob
        self.weight = weight
        self.height = height
        self.activity = activity

    @classmethod
    def get_user_by_id(cls, user_id):
        sql = """
        SELECT email, first_name, last_name, gender, date_of_birth, current_weight, height, activity_level
        FROM user
        WHERE user_id = %s
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        if result:
            email, first_name, last_name, gender, dob, weight, height, activity = result
            return cls(
                email=email,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                dob=dob.strftime("%Y-%m-%d") if isinstance(dob, datetime) else dob,
                weight=float(weight),
                height=float(height),
                activity=activity
            )
        else:
            return None

    @staticmethod
    def register(email, password, first_name, last_name, gender, dob, weight, height, activity):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        sql = """
        INSERT INTO user
        (email, password_hash, first_name, last_name, gender,
        date_of_birth, current_weight, height, activity_level)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            email, hashed_password, first_name, last_name,
            gender, dob, weight, height, activity
        )

        try:
            cursor.execute(sql, values)
            db.commit()
            return True
        except:
            return False

    @staticmethod
    def login(email, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        sql = "SELECT user_id FROM user WHERE email=%s AND password_hash=%s"
        cursor.execute(sql, (email, hashed_password))
        return cursor.fetchone()



    def calculateBMR(self):
        birth_date = self.dob
        today = datetime.today().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        if self.gender.upper() in ["MALE"]:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * age + 5
        elif self.gender.upper() in ["FEMALE"]:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * age - 161
        else:
            raise ValueError("Gender must be 'Male' or 'Female'")
        
        return bmr
    
    def get_recommended_calories(self):
        bmr = self.calculateBMR()

        activity_multipliers = {
            "not-very-active": 1.2,
            "lightly-active": 1.375,
            "active": 1.55,
            "Very-Active": 1.725
        }

        multiplier = activity_multipliers.get(self.activity, 1.2)

        tdee = bmr * multiplier
        return round(tdee, 2)
