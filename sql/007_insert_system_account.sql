INSERT INTO IS601_Accounts (id, user_id, account_type) VALUES (-1, null, 'snt_sys_acct') ON DUPLICATE KEY UPDATE user_id = null;