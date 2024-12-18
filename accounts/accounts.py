from sql.db import DB
from flask import flash
from flask import session
from flask_login import current_user
def get_account(user_id):
    account = {"id":-1, "balance":0}
    try:
        result = DB.selectOne("SELECT id, balance FROM IS601_Accounts WHERE user_id = %s", user_id)
        if result.status and result.row:
            account["id"] = result.row["id"]
            account["balance"] = result.row["balance"]
            return account
    except Exception as e:
        print("Error getting account" ,e)
        flash("Error fetching account", "danger")

def create_account(user_id):
    account = {"id":-1, "balance":0}
    try:
        result = DB.insertOne("INSERT INTO IS601_Accounts (user_id) values (%s)", user_id)
        if result.status:
            account["id"] = DB.db.fetch_eof_status()["insert_id"]
            account["account_type"] = "Checking"
            flash("Account created", "success")
            return account
    except Exception as e:
        print("error creating account", e)
        flash("Error creating account", "danger")
    return None # shouldn't occur
