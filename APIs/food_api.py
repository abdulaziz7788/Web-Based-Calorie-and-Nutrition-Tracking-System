from flask import Blueprint, request, jsonify
from food import Food

food_api = Blueprint("food_api", __name__)

@food_api.post("/foods")
def add_food():
    data = request.json
    food = Food(
        foodID=None,
        foodName=data["food_name"],
        category=data["category"],
        servingSize=data["serving_size"],
        servingUnit=data["serving_unit"],
        calories=data["calories"],
        protein=data["protein"],
        carbohydrates=data["carbohydrates"],
        fats=data["fats"],
        fiber=data["fiber"],
        sugar=data["sugar"]
    )
    food.addNewFood()
    return jsonify({"message": "Food added"}), 201


@food_api.get("/foods/search")
def search_food():
    keyword = request.args.get("q", "")
    results = Food.searchFood(keyword)
    return jsonify([
        {
            "food_id": f.foodID,
            "food_name": f.foodName,
            "category": f.category,
            "serving_size": f.servingSize,
            "serving_unit": f.servingUnit,
            "calories": f.calories,
            "protein": f.protein,
            "carbohydrates": f.carbohydrates,
            "fats": f.fats,
            "fiber": f.fiber,
            "sugar": f.sugar
        }
        for f in results
    ])


@food_api.get("/foods/<int:food_id>")
def get_food_details(food_id):
    food = Food.getFoodDetails(food_id)
    if not food:
        return jsonify({"error": "Food not found"}), 404
    return jsonify({
        "food_id": food.foodID,
        "food_name": food.foodName,
        "category": food.category,
        "serving_size": food.servingSize,
        "serving_unit": food.servingUnit,
        "calories": food.calories,
        "protein": food.protein,
        "carbohydrates": food.carbohydrates,
        "fats": food.fats,
        "fiber": food.fiber,
        "sugar": food.sugar
    })
