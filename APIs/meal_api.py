from flask import Blueprint, request, jsonify
from meal import Meal

meal_api = Blueprint("meal_api", __name__)

@meal_api.post("/meals")
def add_meal():
    data = request.json
    meal = Meal(
        mealID=None,
        userID=data["user_id"],
        mealName=data["meal_name"],
        mealDate=data["meal_date"],
        mealTime=data["meal_time"],
        mealType=data["meal_type"],
        totalCalories=data["total_calories"],
        totalProtein=data["total_protein"],
        totalCarbs=data["total_carbs"],
        totalFats=data["total_fats"]
    )
    meal.logMeal()
    return jsonify({"message": "Meal added"}), 201


@meal_api.get("/meals/<int:user_id>")
def get_meal_history(user_id):
    meals = Meal.getMealHistory(user_id)
    return jsonify([
        {
            "meal_id": m.mealID,
            "user_id": m.userID,
            "meal_name": m.mealName,
            "meal_date": str(m.mealDate),
            "meal_time": str(m.mealTime),
            "meal_type": m.mealType,
            "total_calories": m.totalCalories,
            "total_protein": m.totalProtein,
            "total_carbs": m.totalCarbs,
            "total_fats": m.totalFats
        }
        for m in meals
    ])


@meal_api.put("/meals/<int:meal_id>")
def update_meal(meal_id):
    data = request.json
    meals = Meal.getMealHistory(data["user_id"])
    meal = next((m for m in meals if m.mealID == meal_id), None)
    if not meal:
        return jsonify({"error": "Meal not found"}), 404
    meal.updateMeal(**data["updates"])
    return jsonify({"message": "Meal updated"})


@meal_api.delete("/meals/<int:meal_id>")
def delete_meal(meal_id):
    data = request.json
    meals = Meal.getMealHistory(data["user_id"])
    meal = next((m for m in meals if m.mealID == meal_id), None)
    if not meal:
        return jsonify({"error": "Meal not found"}), 404
    meal.deleteMeal()
    return jsonify({"message": "Meal deleted"})
