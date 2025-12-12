from flask import Blueprint, request, jsonify
from meal_food import MealFood

meal_food_api = Blueprint("meal_food_api", __name__)

@meal_food_api.post("/meal_food")
def add_food_to_meal():
    data = request.json
    entry = MealFood(
        mealFoodID=None,
        mealID=data["meal_id"],
        foodID=data["food_id"],
        quantity=data["quantity"],
        caloriesConsumed=data["calories_consumed"]
    )
    entry.addFoodToMeal()
    return jsonify({"message": "Food added to meal"}), 201


@meal_food_api.put("/meal_food/<int:mf_id>")
def update_meal_food(mf_id):
    data = request.json
    entry = MealFood(mf_id, data["meal_id"], data["food_id"], data["new_quantity"], data["new_calories"])
    entry.updateQuantity(data["new_quantity"], data["new_calories"])
    return jsonify({"message": "Meal food updated"})


@meal_food_api.delete("/meal_food/<int:mf_id>")
def delete_meal_food(mf_id):
    entry = MealFood(mf_id, None, None, None, None)
    entry.removeFoodFromMeal()
    return jsonify({"message": "Meal food removed"})
