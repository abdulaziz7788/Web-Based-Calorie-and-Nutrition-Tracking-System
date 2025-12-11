CREATE TABLE IF NOT EXISTS meal_food (
    meal_food_id INT AUTO_INCREMENT PRIMARY KEY,
    meal_id INT NOT NULL,
    food_id INT NOT NULL,
    quantity FLOAT NOT NULL,
    calories_consumed INT NOT NULL,

    FOREIGN KEY (meal_id) REFERENCES meals(meal_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (food_id) REFERENCES foods(food_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
