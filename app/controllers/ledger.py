import datetime as dt

import sqlalchemy as sa
from flask import Blueprint, render_template
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
from app.models.ledger import LedgerEntry
from app.services.ledger import LedgerEntryBuilder
from app.utils import htmx_only

blueprint = Blueprint("ledger", __name__)


class LedgerEntryItemForm(Form):
    type_ = SelectField(
        "Type", choices=[("D", "Debit"), ("C", "Credit")], validators=[DataRequired()]
    )
    account = StringField("Account", validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired()])


class LedgerEntryForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    items = FieldList(FormField(LedgerEntryItemForm))


@blueprint.route("/", methods=["GET", "POST", "DELETE"])
def index():
    form = LedgerEntryForm()
    entries = db.session.scalars(sa.select(LedgerEntry)).all()
    return render_template("ledger/index.html", entries=entries, form=form)


# HTMX Only Views
@blueprint.route("/_/entry/item", methods=["POST"])
@htmx_only
def htmx_add_entry_item():
    form = LedgerEntryForm()
    form.items.append_entry()
    return render_template("ledger/partials/entry-items.html", form=form)


@blueprint.route("/_/entry/item/<item_id>", methods=["DELETE"])
@htmx_only
def htmx_del_entry_item(item_id: str):
    form = LedgerEntryForm()
    entries = [item for item in form.items if item.id != item_id]
    while len(form.items) > 0:
        form.items.pop_entry()
    for entry in entries:
        form.items.append_entry(entry.data)
    return render_template("ledger/partials/entry-items.html", form=form)


@blueprint.route("/_/entry", methods=["POST"])
@htmx_only
def htmx_add_entry():
    # TODO: Handle errors
    form = LedgerEntryForm()
    if form.validate_on_submit():
        builder = LedgerEntryBuilder(
            dt.datetime.combine(form.date.data, dt.datetime.min.time())  # type: ignore
        )
        for item in form.items:
            if item.type_.data == "D":
                builder.add_debit(item.account.data, item.amount.data)
            else:
                builder.add_credit(item.account.data, item.amount.data)
        entry = builder.build()
        db.session.add(entry)
        db.session.commit()

    entries = db.session.scalars(sa.select(LedgerEntry)).all()
    return render_template("ledger/partials/ledger-entries.html", entries=entries)
