from database import cursor, db
from datetime import datetime

class WaterIntake:

    def __init__(self, waterIntakeID, userID, amount, unit, loggedAt):
        self.waterIntakeID = waterIntakeID
        self.userID = userID
        self.amount = amount
        self.unit = unit
        self.loggedAt = loggedAt

    def _validate(self):
        if self.unit == "CUP" and not float(self.amount).is_integer():
            raise ValueError("Amount must be a whole number for CUP.")

        if self.unit == "LITER" and not (0.1 <= self.amount <= 5):
            raise ValueError("LITER amount must be between 0.1 and 5 L.")

        if self.unit == "ML" and self.amount <= 0:
            raise ValueError("ML amount must be greater than 0.")

    def addIntake(self):
        self._validate()

        sql = """
        INSERT INTO Water_intake (user_id, amount, unit)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (self.userID, self.amount, self.unit))
        db.commit()

    def updateIntake(self, **updates):
        set_clause = ", ".join(f"{key}=%s" for key in updates.keys())
        values = list(updates.values())
        values.append(self.waterIntakeID)

        sql = f"UPDATE Water_intake SET {set_clause} WHERE water_id=%s"
        cursor.execute(sql, tuple(values))
        db.commit()

        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def deleteIntake(self):
        sql = "DELETE FROM Water_intake WHERE water_id=%s"
        cursor.execute(sql, (self.waterIntakeID,))
        db.commit()

    @staticmethod
    def getDailyTotal(userID, date_str=None):
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        sql = """
        SELECT SUM(amount) 
        FROM Water_intake
        WHERE user_id=%s AND DATE(logged_at)=%s
        """
        cursor.execute(sql, (userID, date_str))
        result = cursor.fetchone()
        return result[0] if result[0] else 0

    @staticmethod
    def getIntakeHistory(userID):
        sql = """
        SELECT water_id, user_id, amount, unit, logged_at
        FROM Water_intake
        WHERE user_id = %s
        ORDER BY logged_at DESC
        """
        cursor.execute(sql, (userID,))
        rows = cursor.fetchall()
        return [WaterIntake(*row) for row in rows]

    def __str__(self):
        return f"{self.amount} {self.unit} logged at {self.loggedAt}"
