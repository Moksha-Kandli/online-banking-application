from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms.validators import ValidationError
from sql.db import DB
from flask import flash

class CreateAccountForm(FlaskForm):
    amount = StringField("Amount to be deposited", validators = [DataRequired()])
    submit = SubmitField("Register")
    def check_if_amount_is_sufficient(amount):
        if amount < 5:
            flash("There was an error in creating your account. Make sure you have entered a minimum amount of $5.", "danger")
        else:
            return True

class GetAccountForm(FlaskForm):
    submit = SubmitField("Get Accounts")

class DepositForm(FlaskForm):
    account_id = StringField("Account ID", validators = [DataRequired()])
    deposit_amount = StringField("Deposit Amount", validators = [DataRequired()])
    memo = StringField("Memo", validators = [Optional()])
    submit = SubmitField("Deposit")

class WithdrawForm(FlaskForm):
    account_id = StringField("Account ID", validators = [DataRequired()])
    withdraw_amount = StringField("Withdrawal amount", validators = [DataRequired()])
    memo = StringField("Memo", validators = [Optional()])
    submit = SubmitField("Withdraw")

class Transfer_own_accountsForm(FlaskForm):
    account_src = StringField("Source Account", validators = [DataRequired()])
    account_dest = StringField("Destination Account", validators = [DataRequired()])
    amount = StringField("Amount to be transferred", validators = [DataRequired()])
    memo = StringField("Memo", validators = [Optional()])
    submit = SubmitField("Transfer")
    def check_if_above_balance(user_id, amount):
        result = DB.selectOne("SELECT balance FROM IS601_Accounts balance WHERE user_id = %s", user_id)
        if result.status and amount >= 5:
            if result < amount:
                flash("Insufficient balance in your account.", "danger")
            else:
                return True
        else:
            flash("There was an error in creating your account. Make sure you have entered a minimum amount of $5.")

class Transfer_to_other_accountsForm(FlaskForm):
    account_src = StringField("Source Account", validators = [DataRequired()])
    dest_account_ln = StringField("Destination Account last name", validators = [DataRequired()])
    dest_account_last4 = StringField("Destination Account last 4 digits", validators = [DataRequired()])
    amount = StringField("Amount to be transferred", validators = [DataRequired()])
    memo = StringField("Memo", validators = [Optional()])
    submit = SubmitField("Transfer")
    def check_if_above_balance(user_id, amount):
        result = DB.selectOne("SELECT balance FROM IS601_Accounts balance WHERE user_id = %s", user_id)
        if result.status and amount >= 5:
            if result < amount:
                flash("Insufficient balance in your account.", "danger")
            else:
                return True
        else:
            flash("There was an error in creating your account. Make sure you have entered a minimum amount of $5.")

class Transaction_history(FlaskForm):
    account_number = StringField("Source Account", validators = [DataRequired()])
    submit = SubmitField("Submit")