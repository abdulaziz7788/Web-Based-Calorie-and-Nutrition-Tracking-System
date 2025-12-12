from flask import Flask
from meal_api import meal_api
from food_api import food_api
from meal_food_api import meal_food_api
from water_api import water_api

app = Flask(__name__)

app.register_blueprint(meal_api)
app.register_blueprint(food_api)
app.register_blueprint(meal_food_api)
app.register_blueprint(water_api)

if __name__ == "__main__":
    app.run(debug=True)
