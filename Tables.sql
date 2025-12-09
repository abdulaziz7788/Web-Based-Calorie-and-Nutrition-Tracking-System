CREATE TABLE User(
		user_id int primary key auto_increment,
		email varchar(100) UNIQUE NOT NULL,
		password_hash VARCHAR(255)NOT NULL,
		first_name VARCHAR(50)NOT NULL,
		CHECK (first_name NOT REGEXP '[0-9]'),
		last_name varchar(50)NOT NULL,
		CHECK (last_name NOT REGEXP '[0-9]'),
		gender ENUM('MALE','FEMALE','OTHER')NOT NULL,
		date_of_birth date NOT NULL, 
		CHECK(date_of_birth BETWEEN '1930-01-01' AND '2020-01-01'),
		current_weight FLOAT, 
		check(current_weight BETWEEN 30 AND 250),
		height float, 
		check(height BETWEEN 90 AND 220),
		activity_level enum('not-very-active','lightly-active','active','Very-Active') NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
			ON UPDATE CURRENT_TIMESTAMP
);