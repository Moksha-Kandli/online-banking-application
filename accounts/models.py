from common.utils import JsonSerializable
from flask import flash
from sql.db import DB

class Account(JsonSerializable):
    def __init__(self, id = -1, balance = 0):
        self.id = id
        self.balance = balance
    def deposit(self, change = 0, AccountSrc = -1, TransactionType="", Memo = ""):
        return self.transfer(AccountSrc, self.id, change, TransactionType, Memo)
    def withdraw(self, change = 0, AccountDest = -1, TransactionType="", Memo=""):
        return self.transfer(self.id, AccountDest, change, TransactionType, Memo)
    def transfer(self, AccountSrc, AccountDest, BalanceChange, TransactionType, Memo):
        from sql.db import DB
        DB.getDB().autocommit = True
        BalanceChange = int(BalanceChange)
        if BalanceChange > 0:
            BalanceChange *= -1
        query = """
        INSERT INTO IS601_Transactions
        (AccountSrc, AccountDest, BalanceChange, TransactionType, Memo) VALUES
        (%s, %s, %s, %s, %s)
        """
        pairs = []
        pairs.append((AccountSrc, AccountDest, BalanceChange, TransactionType, Memo))
        pairs.append((AccountDest, AccountSrc, BalanceChange * -1 , TransactionType, Memo))
        try:
            result = DB.insertMany(query, pairs)
            if result.status:
                flash("Recored transations pairs", "success")
                if self.__update_balance(AccountDest):
                    DB.getDB().commit()
                    return True
        except Exception as e:
            print("Error recording point history", e)
            DB.getDB().rollback()
        return False
    def __update_balance(self, AccountDest):
        from sql.db import DB
        from flask import session
        from flask_login import current_user
        try:
            user_id = current_user.get_id()
            result1 = DB.update("""
            UPDATE IS601_Accounts set balance = 
            (SELECT IFNULL(SUM(BalanceChange), 0) FROM IS601_Transactions WHERE AccountSrc = %(acct)s)
            WHERE id = %(acct)s
            """, {"acct":int(self.id)})
            result2 = DB.update("UPDATE IS601_Accounts set balance = (SELECT SUM(BalanceChange) FROM IS601_Transactions WHERE AccountSrc = %(acct)s) WHERE id = %(acct)s", {"acct":AccountDest})
            if result1.status and result2.status:
                result = DB.selectOne("SELECT balance FROM IS601_Accounts WHERE id = %s", self.id)
                if result.status and result.row:
                    self.balance = result.row["balance"]
                    from flask import session
                    from flask_login import current_user
                    session["user"] = current_user.toJson()
                    return True
        except Exception as e:
            flash(str(e))
            flash("Error updating balance", e)
            DB.getDB().rollback()
        return False