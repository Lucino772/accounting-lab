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
    account = StringField("Account", validators=[DataRequired()])
    label = StringField("Label", validators=[DataRequired()])
    type_ = SelectField(
        "Type",
        choices=[
            ("ASSET", "Asset (1)"),
            ("LIABILITY", "Liability (2)"),
            ("REVENUE", "Revenue (4)"),
            ("EXPENSE", "Expense (5)"),
        ],
        validators=[DataRequired()],
    )


@blueprint.route("/", methods=["GET"])
def index():
    form = AddLedgerAccountForm()
    accounts = db.session.scalars(
        sa.select(LedgerAccount).order_by(LedgerAccount.account)
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
        .order_by(LedgerAccount.account)
        .where(LedgerAccount.type == LedgerAccount.Type.ASSET)
    ).all()
    asset_balance = _calculate_balance(asset_accounts)
    liability_accounts = db.session.scalars(
        sa.select(LedgerAccount)
        .order_by(LedgerAccount.account)
        .where(LedgerAccount.type == LedgerAccount.Type.LIABILITY)
    ).all()
    liability_balance = _calculate_balance(liability_accounts)
    expense_accounts = db.session.scalars(
        sa.select(LedgerAccount)
        .order_by(LedgerAccount.account)
        .where(LedgerAccount.type == LedgerAccount.Type.EXPENSE)
    ).all()
    expense_balance = _calculate_balance(expense_accounts)
    revenue_accounts = db.session.scalars(
        sa.select(LedgerAccount)
        .order_by(LedgerAccount.account)
        .where(LedgerAccount.type == LedgerAccount.Type.REVENUE)
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
            account=form.account.data,
            label=form.label.data,
            type={
                "ASSET": LedgerAccount.Type.ASSET,
                "LIABILITY": LedgerAccount.Type.LIABILITY,
                "REVENUE": LedgerAccount.Type.REVENUE,
                "EXPENSE": LedgerAccount.Type.EXPENSE,
            }[form.type_.data],
        )
        db.session.add(account)
        db.session.commit()

    accounts = db.session.scalars(
        sa.select(LedgerAccount).order_by(LedgerAccount.account)
    ).all()
    return render_template("accounts/partials/account-list.html", accounts=accounts)
