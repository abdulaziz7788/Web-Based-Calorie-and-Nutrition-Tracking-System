CREATE TABLE nutritional_info (
    nutrition_id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT NOT NULL,
    calories INT,
    protein DECIMAL(5,2),
    carbohydrates DECIMAL(5,2),
    fat DECIMAL(5,2),
    total_fiber DECIMAL(5,2),
    total_sugar DECIMAL(5,2),

    FOREIGN KEY (food_id) REFERENCES food(food_id)
    ON DELETE CASCADE
);
