CREATE TABLE Daily_summary(
	summary_id int primary key auto_increment,
    user_id int NOT NULL,
    summary_date DATE NOT NULL,
    total_calories_consumed FLOAT DEFAULT 0 CHECK(total_calories_consumed >= 0),
	total_calories_burned FLOAT DEFAULT 0 CHECK(total_calories_burned >= 0),
    net_calories FLOAT,
    total_protein FLOAT DEFAULT 0 CHECK(total_protein >= 0),
    total_carb FLOAT DEFAULT 0 CHECK(total_carb >= 0),
    total_fat FLOAT DEFAULT 0 CHECK(total_fat >= 0),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	UNIQUE(user_id, summary_date),

    FOREIGN KEY (user_id) REFERENCES User(user_id)
		ON DELETE CASCADE
);