CREATE TABLE meal_food (
    meal_food_id INT AUTO_INCREMENT PRIMARY KEY,
    meal_id INT NOT NULL,
    food_id INT NOT NULL,
    quantity DECIMAL(6,2),
    total_calories INT,

    FOREIGN KEY (meal_id) REFERENCES meal_preset(preset_id)
    ON DELETE CASCADE,

    FOREIGN KEY (food_id) REFERENCES food(food_id)
    ON DELETE CASCADE
);
