import decimal
from collections.abc import Iterable

import sqlalchemy as sa
from flask import Blueprint, render_template
from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
)
from wtforms.validators import DataRequired

from app.extensions import db
from app.models.ledger import LedgerAccount
from app.utils import htmx_only

blueprint = Blueprint("accounts", __name__)


class AddLedgerAccountForm(FlaskForm):
    account_name = StringField("Account", validators=[DataRequired()])
    account_label = StringField("Label", validators=[DataRequired()])
    account_class = SelectField(
        "Class",
        choices=[
            ("BALANCE_SHEET", "Balance Sheet (1)"),
            ("INCOME_STATEMENT", "Income Statement (2)"),
        ],
        validators=[DataRequired()],
    )
    account_type = SelectField(
        "Type",
        choices=[
            ("ASSET", "Asset (1)"),
            ("LIABILITY", "Liability (2)"),
            ("EQUITY", "Equity (3)"),
            ("REVENUE", "Revenue (4)"),
            ("EXPENSE", "Expense (5)"),
        ],
        validators=[DataRequired()],
    )


@blueprint.route("/", methods=["GET"])
def index():
    form = AddLedgerAccountForm()
    accounts = db.session.scalars(
        sa.select(LedgerAccount).order_by(LedgerAccount.account_name)
    ).all()
    return render_template("accounts/index.html", accounts=accounts, form=form)


@blueprint.route("/taccounts", methods=["GET"])
def taccounts():
    def _calculate_balance(accounts: Iterable[LedgerAccount]):
        _sum = decimal.Decimal("0")
        for account in accounts:
            _type, balance = account.balance
            if _type == "debit":
                _sum += balance
            else:
                _sum -= balance
        return _sum

    asset_accounts = db.session.scalars(
        sa.select(LedgerAccount)
        .order_by(LedgerAccount.account_name)
        .where(LedgerAccount.account_type == LedgerAccount.AccountType.ASSET)
    ).all()
    asset_balance = _calculate_balance(asset_accounts)
    liability_accounts = db.session.scalars(
        sa.select(LedgerAccount)
        .order_by(LedgerAccount.account_name)
        .where(
            sa.or_(
                LedgerAccount.account_type == LedgerAccount.AccountType.LIABILITY,
                LedgerAccount.account_type == LedgerAccount.AccountType.EQUITY,
            )
        )
    ).all()
    liability_balance = _calculate_balance(liability_accounts)
    expense_accounts = db.session.scalars(
        sa.select(LedgerAccount)
        .order_by(LedgerAccount.account_name)
        .where(LedgerAccount.account_type == LedgerAccount.AccountType.EXPENSE)
    ).all()
    expense_balance = _calculate_balance(expense_accounts)
    revenue_accounts = db.session.scalars(
        sa.select(LedgerAccount)
        .order_by(LedgerAccount.account_name)
        .where(LedgerAccount.account_type == LedgerAccount.AccountType.REVENUE)
    ).all()
    revenue_balance = _calculate_balance(revenue_accounts)
    return render_template(
        "accounts/taccounts.html",
        asset_accounts=asset_accounts,
        asset_balance=asset_balance,
        liability_accounts=liability_accounts,
        liability_balance=liability_balance,
        expense_accounts=expense_accounts,
        expense_balance=expense_balance,
        revenue_accounts=revenue_accounts,
        revenue_balance=revenue_balance,
    )


# HTMX Only Views
@blueprint.route("/_/account", methods=["POST"])
@htmx_only
def htmx_add_account():
    # TODO: Handle errors
    form = AddLedgerAccountForm()
    if form.validate_on_submit():
        account = LedgerAccount(
            account_name=form.account_name.data,
            account_label=form.account_label.data,
            account_class={
                "BALANCE_SHEET": LedgerAccount.AccountClass.BALANCE_SHEET,
                "INCOME_STATEMENT": LedgerAccount.AccountClass.INCOME_STATEMENT,
            }[form.account_class.data],
            account_type={
                "ASSET": LedgerAccount.AccountType.ASSET,
                "LIABILITY": LedgerAccount.AccountType.LIABILITY,
                "EQUITY": LedgerAccount.AccountType.EQUITY,
                "REVENUE": LedgerAccount.AccountType.REVENUE,
                "EXPENSE": LedgerAccount.AccountType.EXPENSE,
            }[form.account_type.data],
        )
        db.session.add(account)
        db.session.commit()

    accounts = db.session.scalars(
        sa.select(LedgerAccount).order_by(LedgerAccount.account_name)
    ).all()
    return render_template("accounts/partials/account-list.html", accounts=accounts)
