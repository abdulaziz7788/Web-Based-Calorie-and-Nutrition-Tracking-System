CREATE TABLE meal_log (
    meal_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    food_id INT NOT NULL,
    meal_type_id INT NOT NULL,
    quantity DECIMAL(6,2),
    total_calories INT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food(food_id) ON DELETE CASCADE,
    FOREIGN KEY (meal_type_id) REFERENCES meal_type(meal_type_id)
);
