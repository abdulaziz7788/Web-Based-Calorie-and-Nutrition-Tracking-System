from database import cursor, db

class Meal:

    def __init__(self, mealID, userID, mealName, mealDate, mealTime,
                 mealType, totalCalories, totalProtein, totalCarbs, totalFats):
        
        self.mealID = mealID
        self.userID = userID
        self.mealName = mealName
        self.mealDate = mealDate
        self.mealTime = mealTime
        self.mealType = mealType
        self.totalCalories = totalCalories
        self.totalProtein = totalProtein
        self.totalCarbs = totalCarbs
        self.totalFats = totalFats

    def logMeal(self):
        sql = """
        INSERT INTO meals
        (user_id, meal_name, meal_date, meal_time, meal_type,
         total_calories, total_protein, total_carbs, total_fats)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        values = (
            self.userID, self.mealName, self.mealDate, self.mealTime,
            self.mealType, self.totalCalories, self.totalProtein,
            self.totalCarbs, self.totalFats
        )
        cursor.execute(sql, values)
        db.commit()

    def updateMeal(self, **updates):
        set_clause = ", ".join(f"{key}=%s" for key in updates.keys())
        values = list(updates.values())
        values.append(self.mealID)

        sql = f"UPDATE meals SET {set_clause} WHERE meal_id=%s"
        cursor.execute(sql, tuple(values))
        db.commit()

        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def deleteMeal(self):
        sql = "DELETE FROM meals WHERE meal_id=%s"
        cursor.execute(sql, (self.mealID,))
        db.commit()

    @staticmethod
    def getMealHistory(userID):
        sql = """
        SELECT meal_id, user_id, meal_name, meal_date, meal_time, meal_type,
               total_calories, total_protein, total_carbs, total_fats
        FROM meals
        WHERE user_id = %s
        ORDER BY meal_date DESC, meal_time DESC
        """
        cursor.execute(sql, (userID,))
        result = cursor.fetchall()
        meals = []
        for row in result:
            meals.append(Meal(*row))
        return meals

    def calculateNutrients(self):
        return {
            "calories": self.totalCalories,
            "protein": self.totalProtein,
            "carbs": self.totalCarbs,
            "fats": self.totalFats
        }

    def __str__(self):
        return f"Meal: {self.mealName} ({self.mealType}) - {self.totalCalories} kcal"
