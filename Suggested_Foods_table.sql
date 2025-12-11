CREATE TABLE IF NOT EXISTS foods (
    food_id INT AUTO_INCREMENT PRIMARY KEY,
    food_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    serving_size INT NOT NULL,
    serving_unit VARCHAR(20) NOT NULL,
    calories INT NOT NULL,
    protein FLOAT NOT NULL,
    carbohydrates FLOAT NOT NULL,
    fats FLOAT NOT NULL,
    fiber FLOAT NOT NULL,
    sugar FLOAT NOT NULL
);
