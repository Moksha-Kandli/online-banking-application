CREATE TABLE IF NOT EXISTS IS601_Transactions(
    -- this will be like the bank project transactions table (pairs of transactions)
    id int AUTO_INCREMENT PRIMARY KEY ,
    AccountSrc int,
    AccountDest int,
    BalanceChange int,
    TransactionType varchar(15) not null COMMENT 'The type of transaction that occurred',
    Memo varchar(240) default null COMMENT  'Any extra details to attach to the transaction',
    Created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
    ExpectedTotal int,
    FOREIGN KEY (AccountSrc) REFERENCES IS601_Accounts(id),
    FOREIGN KEY (AccountDest) REFERENCES IS601_Accounts(id),
    constraint ZeroTransferNotAllowed CHECK(BalanceChange != 0)
)