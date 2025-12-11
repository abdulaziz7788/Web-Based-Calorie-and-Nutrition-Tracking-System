CREATE TABLE Water_intake(
	water_id int primary key auto_increment,
    user_id int NOT NULL,
    amount FLOAT NOT NULL DEFAULT 0 CHECK(amount >= 0),
    unit ENUM('ML', 'LITER', 'CUP') DEFAULT 'ML',
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY(user_id) REFERENCES User(user_id)
		ON DELETE CASCADE

);
CREATE INDEX idx_water_user ON Water_intake(user_id, logged_at);
-- Backend Rules:
-- - If unit = 'CUP', amount should be an integer (1 cup, 2 cups, etc.)
-- - If unit = 'LITER', typical amount is between 0.1 and 5 liters.
-- - If unit = 'ML', amount can be any decimal > 0.
-- - logged_at is auto-generated and must not be provided by the client.

