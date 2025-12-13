from database import cursor, db

class MealFood:

    def __init__(self, mealFoodID, mealID, foodID, quantity, caloriesConsumed):
        self.mealFoodID = mealFoodID
        self.mealID = mealID
        self.foodID = foodID
        self.quantity = quantity
        self.caloriesConsumed = caloriesConsumed

    def addFoodToMeal(self):
        sql = """
        INSERT INTO meal_food
        (meal_id, food_id, quantity, calories_consumed)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            self.mealID,
            self.foodID,
            self.quantity,
            self.caloriesConsumed
        )
        cursor.execute(sql, values)
        db.commit()

    def removeFoodFromMeal(self):
        sql = "DELETE FROM meal_food WHERE meal_food_id=%s"
        cursor.execute(sql, (self.mealFoodID,))
        db.commit()

    def updateQuantity(self, newQuantity, newCaloriesConsumed):
        sql = """
        UPDATE meal_food
        SET quantity=%s, calories_consumed=%s
        WHERE meal_food_id=%s
        """
        cursor.execute(sql, (newQuantity, newCaloriesConsumed, self.mealFoodID))
        db.commit()

        self.quantity = newQuantity
        self.caloriesConsumed = newCaloriesConsumed

    @staticmethod
    def getFoodsInMeal(mealID):
        sql = """
        SELECT meal_food_id, meal_id, food_id, quantity, calories_consumed
        FROM meal_food
        WHERE meal_id = %s
        """
        cursor.execute(sql, (mealID,))
        result = cursor.fetchall()
        entries = []
        for row in result:
            entries.append(MealFood(*row))
        return entries

    def __str__(self):
        return f"MealFood entry: Meal {self.mealID}, Food {self.foodID}, Qty {self.quantity}"
