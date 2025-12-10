-- ================================
-- User Table
-- ================================
CREATE TABLE User(
    user_id int primary key auto_increment,
    email varchar(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    CHECK (first_name NOT REGEXP '[0-9]'),
    last_name varchar(50) NOT NULL,
    CHECK (last_name NOT REGEXP '[0-9]'),
    gender ENUM('MALE','FEMALE','OTHER') NOT NULL,
    date_of_birth date NOT NULL,
    CHECK(date_of_birth BETWEEN '1930-01-01' AND '2020-01-01'),
    current_weight FLOAT,
    CHECK(current_weight BETWEEN 30 AND 250),
    height FLOAT,
    CHECK(height BETWEEN 90 AND 220),
    activity_level ENUM('not-very-active','lightly-active','active','Very-Active') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP
);

-- ================================
-- User_goal Table
-- ================================
CREATE TABLE User_goal(
    goal_id int auto_increment primary key,
    goal_type ENUM('WEIGHT','CALORIES','STEPS','SLEEP','BETTER_HEALTH') NOT NULL,
    user_id int NOT NULL,
    target_value float CHECK(target_value > 0),
    target_unit varchar(20),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date date NOT NULL,
    end_date date NOT NULL,
    
    CHECK(end_date >= start_date),
    UNIQUE(user_id,goal_type,start_date),

    Foreign key (user_id) references User(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ================================
-- Notes for Backend Developers
-- ================================
/*
  - The fields target_value and target_unit are designed to work with ANY goal type.
  - Example: if goal_type = 'STEPS', target_value may represent steps and target_unit may be 'steps' or 'meter'.
  - If goal_type = 'WEIGHT', target_value may represent kilograms, and so on.

  - IMPORTANT:
    Backend must implement validation logic using IF statements
    to ensure that each goal_type receives the correct target_value and target_unit.
*/
