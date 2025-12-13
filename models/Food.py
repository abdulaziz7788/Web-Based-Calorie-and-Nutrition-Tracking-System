from database import cursor, db

class Food:

    def __init__(self, foodID, foodName, category, servingSize, servingUnit,
                 calories, protein, carbohydrates, fats, fiber, sugar):
        
        self.foodID = foodID
        self.foodName = foodName
        self.category = category
        self.servingSize = servingSize
        self.servingUnit = servingUnit
        self.calories = calories
        self.protein = protein
        self.carbohydrates = carbohydrates
        self.fats = fats
        self.fiber = fiber
        self.sugar = sugar

    @staticmethod
    def searchFood(keyword):
        sql = """
        SELECT food_id, food_name, category, serving_size, serving_unit,
               calories, protein, carbohydrates, fats, fiber, sugar
        FROM foods
        WHERE food_name LIKE %s
        """
        cursor.execute(sql, (f"%{keyword}%",))
        result = cursor.fetchall()
        foods = []
        for row in result:
            foods.append(Food(*row))
        return foods

    @staticmethod
    def getFoodDetails(foodID):
        sql = """
        SELECT food_id, food_name, category, serving_size, serving_unit,
               calories, protein, carbohydrates, fats, fiber, sugar
        FROM foods
        WHERE food_id = %s
        """
        cursor.execute(sql, (foodID,))
        row = cursor.fetchone()
        return Food(*row) if row else None

    def addNewFood(self):
        sql = """
        INSERT INTO foods
        (food_name, category, serving_size, serving_unit,
         calories, protein, carbohydrates, fats, fiber, sugar)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        values = (
            self.foodName, self.category, self.servingSize, self.servingUnit,
            self.calories, self.protein, self.carbohydrates,
            self.fats, self.fiber, self.sugar
        )
        cursor.execute(sql, values)
        db.commit()

    def __str__(self):
        return f"{self.foodName} ({self.servingSize}{self.servingUnit})"
