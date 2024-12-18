CREATE TABLE IF NOT EXISTS IS601_Accounts(
    id int AUTO_INCREMENT PRIMARY KEY,
    account_number varchar(12) unique DEFAULT NULL,
    user_id int,
    balance int DEFAULT 0,
    account_type VARCHAR(20) DEFAULT "Checking",
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES IS601_Users(id),
    check ((balance >= 0 OR user_id = -1) AND LENGTH(account_number) = 12)
)