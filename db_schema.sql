CREATE TABLE fighters (
    fighter_id INT AUTO_INCREMENT PRIMARY KEY,
    fighter_details_link VARCHAR(255) UNIQUE NOT NULL,
    fighter_name VARCHAR(100),
    height FLOAT,
    weight INT,
    reach FLOAT,
    stance VARCHAR(50),
    date_of_birth DATE,
    significant_strikes_per_minute FLOAT,
    striking_accuracy_per FLOAT,
    strikes_absorbed_per_minute FLOAT,
    strike_defence_per FLOAT,
    average_takedowns_per_15_minutes FLOAT,
    takedown_accuracy_per FLOAT,
    takedown_defence_per FLOAT,
    average_submission_attempts_per_15_min FLOAT,
    wins INT,
    losses INT,
    draws INT
);


CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_link VARCHAR(255) UNIQUE NOT NULL,
    event_name VARCHAR(255),
    event_date DATE,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100)
);


CREATE TABLE fights (
    fight_id INT AUTO_INCREMENT PRIMARY KEY,
    fight_conclusion_link VARCHAR(255) UNIQUE NOT NULL,
    event_link VARCHAR(255),
    fighter_1_id INT,
    fighter_2_id INT,
    weight_class VARCHAR(50),
    method VARCHAR(50),
    FOREIGN KEY (event_link) REFERENCES events(event_link),
    FOREIGN KEY (fighter_1_id) REFERENCES fighters(fighter_id),
    FOREIGN KEY (fighter_2_id) REFERENCES fighters(fighter_id)
);


CREATE TABLE fight_stats (
    fight_stat_id INT AUTO_INCREMENT PRIMARY KEY,
    fight_conclusion_link VARCHAR(255),
    fighter_1_alias VARCHAR(100),
    fighter_2_alias VARCHAR(100),
    fighter_1_fight_conclusion CHAR(1),
    fighter_2_fight_conclusion CHAR(1),
    fighter_1_knockdowns INT,
    fighter_2_knockdowns INT,
    fighter_1_significant_strikes_per FLOAT,
    fighter_2_significant_strikes_per FLOAT,
    fighter_1_takedowns_per FLOAT,
    fighter_2_takedowns_per FLOAT,
    fighter_1_submission_attempts FLOAT,
    fighter_2_submission_attempts FLOAT,
    fighter_1_reversals FLOAT,
    fighter_2_reversals FLOAT,
    fighter_1_strikes_landed INT,
    fighter_1_strikes_attempted INT,
    fighter_2_strikes_landed INT,
    fighter_2_strikes_attempted INT,
    FOREIGN KEY (fight_conclusion_link) REFERENCES fights(fight_conclusion_link)
);

