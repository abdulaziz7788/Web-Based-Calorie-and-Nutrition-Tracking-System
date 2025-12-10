CREATE TABLE User_goal(
    goal_id int auto_increment primary key,
    goal_type ENUM('WEIGHT','CALORIES','STEPS','SLEEP','BETTER_HEALTH') NOT NULL,
    user_id int NOT NULL,
    target_value float CHECK(target_value > 0),
    target_unit varchar(10),
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
