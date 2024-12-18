from flask import Flask, Blueprint, render_template, flash, redirect, url_for,current_app, session, request
from accounts.accounts import get_account, create_account
from sql.db import DB
from accounts.forms import CreateAccountForm, GetAccountForm, DepositForm, WithdrawForm, Transfer_own_accountsForm, Transfer_to_other_accountsForm, Transaction_history

from flask_login import login_user, login_required, logout_user, current_user
from accounts.models import Account
from flask_bcrypt import Bcrypt
from flask_paginate import Pagination, get_page_args

bcrypt = Bcrypt()

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard',template_folder='templates')

def __init__(self, id = -1, balance = 0):
        self.id = id
        self.balance = balance

@dashboard.route("/landing_page_dashboard", methods=["GET"])
@login_required
def landing_page_dashboard():
    return render_template("landing_page_dashboard.html")

@dashboard.route("/create_account", methods=["GET", "POST"])
@login_required
def create_account():
    form = CreateAccountForm()
    user_id = current_user.get_id()
    if form.validate_on_submit():
        try:
            account_type = "Checking"
            AccountSrc = 1
            BalanceChange = form.amount.data
            TransactionType = "initial deposit"
            Memo = "minimum"
            if int(form.amount.data) >= 5:
                result = DB.insertOne("INSERT INTO IS601_Accounts (balance, user_id, account_type) values (%s, %s, %s)", form.amount.data, user_id, account_type)
                result1 = DB.update("UPDATE IS601_Accounts SET account_number = LPAD((SELECT LAST_INSERT_ID()), 12, 0) where id = LAST_INSERT_ID()")
                Dest = DB.selectOne("SELECT id from IS601_Accounts WHERE id = LAST_INSERT_ID()")
                Destdata = Dest.row
                AccountDest = Destdata["id"]
                result2 = Account().transfer(AccountSrc, AccountDest, BalanceChange, TransactionType, Memo)
                result3 = DB.update("UPDATE IS601_Accounts SET balance = (balance-%s) WHERE id = %s", BalanceChange, AccountSrc)
                last_insert_id = DB.selectOne("SELECT MAX(id) FROM IS601_Transactions")
                last_insert_data = last_insert_id.row
                last_inserted_id = last_insert_data["MAX(id)"]
                last_but_1_inserted_id = last_inserted_id - 1
                trial = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountDest, last_inserted_id)
                trial1 = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountSrc, last_but_1_inserted_id)
                if result and result1 and result2 and result3:
                    flash(f"Created Account", "success")
                    return render_template("landing_page_dashboard.html")
            else:
                flash("Please enter a minimum amount of $5 to create your account.", "danger")
        except Exception as e:
            flash(f"Error creating Account {e}", "danger")
    return render_template("create_account.html", form=form)

@dashboard.route("/my_accounts", methods=["GET", "POST"])
@login_required
def my_accounts():
    rows = []
    form = GetAccountForm()
    user_id = current_user.get_id()
    if form.validate_on_submit():
        try:
            result = DB.selectAll("SELECT account_number, account_type, modified, balance FROM IS601_Accounts WHERE user_id = %s LIMIT 5", user_id)
            if result.status and result.rows:
                rows = result.rows
                flash(f"Your accounts were found.", "success")
            else:
                flash("No accounts to show.")
        except Exception as e:
            flash(f"Error finding Account {e}", "danger")
    return render_template("my_accounts.html", form=form, rows=rows)

@dashboard.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    form = DepositForm()
    user_id = current_user.get_id()
    if form.validate_on_submit():
        try:
            AccountSrc = 1
            AccountDest = form.account_id.data
            BalanceChange = form.deposit_amount.data
            TransactionType = "deposit"
            Memo = form.memo.data
            result1 = Account().transfer(AccountSrc, AccountDest, BalanceChange, TransactionType, Memo)
            result2 = DB.update("UPDATE IS601_Accounts SET balance = (balance-%s) WHERE id = %s", BalanceChange, AccountSrc)
            last_insert_id = DB.selectOne("SELECT MAX(id) FROM IS601_Transactions")
            last_insert_data = last_insert_id.row
            last_inserted_id = last_insert_data["MAX(id)"]
            last_but_1_inserted_id = last_inserted_id - 1
            trial = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountDest, last_inserted_id)
            trial1 = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountSrc, last_but_1_inserted_id)
            if result1 and result2:
                flash("Successfully deposited into your Account", "success")
        except Exception as e:
            flash("An error occured while depositing the money. Please try again.", "danger")
    return render_template("deposit.html", form=form)

@dashboard.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    form = WithdrawForm()
    user_id = current_user.get_id()
    if form.validate_on_submit():
        try:
            AccountSrc = form.account_id.data
            balance = DB.selectOne("SELECT balance FROM IS601_Accounts WHERE id = %s", AccountSrc)
            balance_data = balance.row
            if balance_data["balance"] < int(form.withdraw_amount.data):
                flash("Insufficient balance. Please enter an amount less than or equal to your available balance.", "danger")
            elif int(form.withdraw_amount.data) < 0:
                flash("Please enter a valid amount of greater than 0 to withdraw.", "danger")
            else:
                #result = DB.update("UPDATE IS601_Accounts SET balance = (balance - %s) WHERE user_id = %s and id = %s", form.withdraw_amount.data, user_id, form.account_id.data)
                AccountSrc = form.account_id.data
                AccountDest = 1
                BalanceChange = form.withdraw_amount.data
                TransactionType = "withdraw"
                Memo = form.memo.data
                result1 = Account().transfer(AccountSrc, AccountDest, BalanceChange, TransactionType, Memo)
                result2 = DB.update("UPDATE IS601_Accounts SET balance = (balance-%s) WHERE id = %s", BalanceChange, AccountSrc)
                last_insert_id = DB.selectOne("SELECT MAX(id) FROM IS601_Transactions")
                last_insert_data = last_insert_id.row
                last_inserted_id = last_insert_data["MAX(id)"]
                last_but_1_inserted_id = last_inserted_id - 1
                trial = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountDest, last_inserted_id)
                trial1 = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountSrc, last_but_1_inserted_id)
                if result1 and result2:
                    flash(f"Successfully withdrawn", "success")
                else:
                    flash("Something went wrong while withdrawing the amount. Please try again.", "danger")
        except Exception as e:
            flash(f"Error occured while withdrawing the money. Please try again.", "danger")
    return render_template("withdraw.html", form=form)

@dashboard.route("/transfer_to_own_accounts", methods=["GET", "POST"])
@login_required
def transfer_to_own_accounts():
    form = Transfer_own_accountsForm()
    user_id = current_user.get_id()
    if form.validate_on_submit():
        try:
            AccountSrc = form.account_src.data
            balance = DB.selectOne("SELECT balance FROM IS601_Accounts WHERE id = %s", AccountSrc)
            balance_data = balance.row
            if balance_data["balance"] < int(form.amount.data):
            #if int(form.withdraw_amount.data) < 0:
                flash("Insufficient balance. Cannot transfer more funds than they have. Please enter an amount less than or equal to your available balance.", "danger")
                #flash("Please enter a valid amount of greater than 0 to withdraw.", "danger")
            else:
                AccountDest = form.account_dest.data
                BalanceChange = form.amount.data
                TransactionType = "transfer"
                Memo = form.memo.data
                if AccountSrc == AccountDest:
                    flash("Cannot transfer to the same account.", "danger")
                elif int(BalanceChange) < 0:
                    flash("Cannot transfer negative amount. Please enter a proper value.", "danger")
                else:
                    result = Account().transfer(AccountSrc, AccountDest, BalanceChange, TransactionType, Memo)
                    result1 = DB.update("UPDATE IS601_Accounts set balance = (balance - %s) WHERE user_id = %s and id = %s", form.amount.data, user_id, form.account_src.data)
                    last_insert_id = DB.selectOne("SELECT MAX(id) FROM IS601_Transactions")
                    last_insert_data = last_insert_id.row
                    last_inserted_id = last_insert_data["MAX(id)"]
                    last_but_1_inserted_id = last_inserted_id - 1
                    trial = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountDest, last_inserted_id)
                    trial1 = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountSrc, last_but_1_inserted_id)
                    if result and result1:
                        flash("Successfully transfered into your Account", "success")
        except Exception as e:
            flash("An error occured while transfering the money. Please try again.", "danger")
    return render_template("transfer_own_accounts.html", form=form)

@dashboard.route("/transfer_to_other_accounts", methods=["GET", "POST"])
@login_required
def transfer_to_other_accounts():
    form = Transfer_to_other_accountsForm()
    user_id = current_user.get_id()
    if form.validate_on_submit():
        try:
            AccountSrc = form.account_src.data
            balance = DB.selectOne("SELECT balance FROM IS601_Accounts WHERE id = %s", AccountSrc)
            balance_data = balance.row
            if balance_data["balance"] < int(form.amount.data):
                flash("Insufficient balance. Cannot transfer more funds than they have. Please enter an amount less than or equal to your available balance.", "danger")
            elif int(form.amount.data) < 0:
                flash("Please enter a valid amount of greater than 0 to transfer.", "danger")
            else:
                last_name = form.dest_account_ln.data
                last_4 = form.dest_account_last4.data
                TransactionType = "ext-transfer"
                BalanceChange = form.amount.data
                Memo = form.memo.data
                account_id = last_4[-2:]
                #user_id_dest = DB.selectOne("SELECT id FROM IS601_Users WHERE last_name = %s", last_name)
                AcctDest = DB.selectOne("SELECT id FROM IS601_Accounts WHERE user_id = (SELECT id FROM IS601_Users WHERE last_name = %s) AND id = %s", last_name, account_id)
                AcctDestRow = AcctDest.row
                AccountDest = AcctDestRow["id"] 
                result = Account().transfer(AccountSrc, AccountDest, BalanceChange, TransactionType, Memo)
                result1 = DB.update("UPDATE IS601_Accounts set balance = (balance - %s) WHERE user_id = %s and id = %s", form.amount.data, user_id, form.account_src.data)
                last_insert_id = DB.selectOne("SELECT MAX(id) FROM IS601_Transactions")
                last_insert_data = last_insert_id.row
                last_inserted_id = last_insert_data["MAX(id)"]
                last_but_1_inserted_id = last_inserted_id - 1
                trial = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountDest, last_inserted_id)
                trial1 = DB.update("UPDATE IS601_Transactions SET ExpectedTotal = (SELECT balance FROM IS601_Accounts WHERE id = %s) WHERE id = %s", AccountSrc, last_but_1_inserted_id)
                if result and result1:
                    flash("Successfully tranfered to the user's Account", "success")
        except Exception as e:
            flash(str(e))
            flash("An error occured while transfering the money. Please try again.", "danger")
    return render_template("transfer_to_other_accounts.html", form=form)

@dashboard.route("/transaction_history", methods=["GET", "POST"])
@login_required
def transaction_history():
    rows = []
    pagination_rows = []
    page = []
    per_page = []
    pagination = []
    form = Transaction_history()
    user_id = current_user.get_id()
    if form.validate_on_submit():
        try:
            result = DB.selectAll("""
            SELECT AccountSrc, AccountDest, BalanceChange, TransactionType, Memo, Created 
            FROM IS601_Transactions WHERE AccountSrc = %s or AccountDest = %s""", form.account_number.data, form.account_number.data)
            if result.status and result.rows:
                rows = result.rows
                def get_rows(offset = 0, per_page =10):
                    return rows[offset: offset+per_page]
                page, per_page, offset = get_page_args(page_parameter="page", per_page_parameter="per_page")
                total = len(rows)
                pagination_rows = get_rows(offset=offset, per_page = per_page)
                pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
                flash(f"Your transactions were found.", "success")
            else:
                flash("No transactions to show.")
        except Exception as e:
            flash(f"Error finding Account {e}", "danger")
    return render_template("transaction_history.html", form=form, rows=pagination_rows, page=page, per_page=per_page, pagination=pagination)