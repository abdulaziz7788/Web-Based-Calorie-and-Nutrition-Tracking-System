CREATE TABLE food (
    food_id INT AUTO_INCREMENT PRIMARY KEY,
    food_name VARCHAR(100) NOT NULL,
    serving_size DECIMAL(6,2),
    serving_unit VARCHAR(30)
);
