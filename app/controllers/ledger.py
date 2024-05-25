import datetime as dt

import sqlalchemy as sa
from flask import Blueprint, abort, render_template
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    FieldList,
    Form,
    FormField,
    SelectField,
    StringField,
)
from wtforms.validators import DataRequired

from app.extensions import db
from app.models.ledger import LedgerAccount, LedgerEntry
from app.services.ledger import LedgerEntryBuilder
from app.utils import htmx_only

blueprint = Blueprint("ledger", __name__)


class AddLedgerEntryItemForm(Form):
    type_ = SelectField(
        "Type", choices=[("D", "Debit"), ("C", "Credit")], validators=[DataRequired()]
    )
    account = SelectField("Account", validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired()])


class AddLedgerEntryForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    items = FieldList(FormField(AddLedgerEntryItemForm))


def _prepare_form(form: AddLedgerEntryForm):
    accounts = db.session.scalars(
        sa.select(LedgerAccount).order_by(LedgerAccount.account_name)
    ).all()
    choices = [
        (str(account.account_id), f"{account.account_name} - {account.account_label}")
        for account in accounts
    ]
    for item in form.items:
        item.form.account.choices = choices  # type: ignore


@blueprint.route("/", methods=["GET", "POST", "DELETE"])
def index():
    form = AddLedgerEntryForm()
    _prepare_form(form)
    entries = db.session.scalars(sa.select(LedgerEntry)).all()
    return render_template("ledger/index.html", entries=entries, form=form)


# HTMX Only Views
@blueprint.route("/_/entry/item", methods=["POST"])
@htmx_only
def htmx_add_entry_item():
    form = AddLedgerEntryForm()
    form.items.append_entry()
    _prepare_form(form)
    return render_template("ledger/partials/entry-items.html", form=form)


@blueprint.route("/_/entry/item/<item_id>", methods=["DELETE"])
@htmx_only
def htmx_del_entry_item(item_id: str):
    form = AddLedgerEntryForm()
    entries = [item for item in form.items if item.id != item_id]
    while len(form.items) > 0:
        form.items.pop_entry()
    for entry in entries:
        form.items.append_entry(entry.data)
    _prepare_form(form)
    return render_template("ledger/partials/entry-items.html", form=form)


@blueprint.route("/_/entry", methods=["POST"])
@htmx_only
def htmx_add_entry():
    # TODO: Handle errors
    form = AddLedgerEntryForm()
    _prepare_form(form)
    if form.validate_on_submit():
        builder = LedgerEntryBuilder(
            dt.datetime.combine(form.date.data, dt.datetime.min.time())  # type: ignore
        )
        for item in form.items:
            account = db.session.get(LedgerAccount, item.account.data)
            if account is None:
                abort(500)
            if item.type_.data == "D":
                builder.add_debit(account, item.amount.data)
            else:
                builder.add_credit(account, item.amount.data)
        entry = builder.build()
        db.session.add(entry)
        db.session.commit()

    entries = db.session.scalars(sa.select(LedgerEntry)).all()
    return render_template("ledger/partials/ledger-entries.html", entries=entries)
