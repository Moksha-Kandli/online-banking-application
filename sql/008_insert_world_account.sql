INSERT INTO IS601_Accounts (account_number, user_id, account_type) VALUES ('000000000000', -1, 'world') ON DUPLICATE KEY UPDATE user_id = null;