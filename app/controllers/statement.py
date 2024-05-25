from collections.abc import Iterable

import sqlalchemy as sa
from flask import Blueprint, render_template

from app.extensions import db
from app.models.ledger import LedgerAccount
from app.services.statement import StatementEntry

blueprint = Blueprint("statement", __name__)


def _add_statement_entry(root: StatementEntry, name: str, prefixes: Iterable[str]):
    entry = root.add_entry(name)
    for account in db.session.scalars(
        sa.select(LedgerAccount).where(
            sa.or_(
                sa.false(),
                *[LedgerAccount.account_name.startswith(prefix) for prefix in prefixes],
            )
        )
    ):
        entry.update_balance(account.account_balance)


@blueprint.route("/", methods=["GET"])
def index():
    assets = StatementEntry("Actif")
    liabilities = StatementEntry("Passif")
    expenses = StatementEntry("Charges")
    revenue = StatementEntry("Produits")

    # Actif
    fixed_assets = assets.add_entry("Actifs Immobilises")
    _add_statement_entry(fixed_assets, "II", ["21"])
    _add_statement_entry(fixed_assets, "IC", ["22", "23", "24", "25", "26", "27"])
    _add_statement_entry(fixed_assets, "IF", ["28"])

    current_assets = assets.add_entry("Actifs Circulants")
    _add_statement_entry(current_assets, "STOCK", ["3"])
    _add_statement_entry(current_assets, "CrCom", ["40"])
    _add_statement_entry(current_assets, "CrAutres", ["41"])
    _add_statement_entry(current_assets, "TRES", ["50", "51", "52", "53"])
    _add_statement_entry(current_assets, "CASH", ["54", "55", "57", "58"])
    # TODO: Compte Regularisation Actif

    # Passif
    capital = liabilities.add_entry("Capitaux Propres")
    _add_statement_entry(capital, "APP", ["11"])
    _add_statement_entry(capital, "PVR", ["12"])
    _add_statement_entry(capital, "RES", ["13"])
    _add_statement_entry(capital, "REP", ["14"])
    _add_statement_entry(capital, "REP", ["15"])
    _add_statement_entry(liabilities, "PROV", ["16"])
    _add_statement_entry(liabilities, "DETTES LT", ["17"])
    liabilities_ct = liabilities.add_entry("DETTES CT")
    _add_statement_entry(liabilities_ct, "DFinEch", ["42"])
    _add_statement_entry(liabilities_ct, "DFinCT", ["43"])
    _add_statement_entry(liabilities_ct, "DComCT", ["44"])
    _add_statement_entry(liabilities_ct, "Acomptes", ["46"])
    _add_statement_entry(liabilities_ct, "DFSS", ["45"])
    _add_statement_entry(liabilities_ct, "DAutresCT", ["48"])
    # TODO: Compte Regularisation Passif

    # Charges
    ch_expl = expenses.add_entry("ChExp")
    _add_statement_entry(ch_expl, "Approvisionnement et marchandises", ["60"])
    _add_statement_entry(ch_expl, "Services et biens divers", ["61"])
    _add_statement_entry(ch_expl, "Remunerations", ["62"])
    _add_statement_entry(ch_expl, "Amortissements, RDV et Provisions", ["63"])
    _add_statement_entry(ch_expl, "Autres charges d'exploitation", ["64"])
    ch_fin = expenses.add_entry("ChFin")
    _add_statement_entry(ch_fin, "Charges financieres recurrentes", ["65"])
    _add_statement_entry(expenses, "I. Soc", ["67"])

    # Produits
    pr_expl = revenue.add_entry("PrExp")
    _add_statement_entry(pr_expl, "Chiffres d'affaires", ["70", "71"])
    _add_statement_entry(pr_expl, "Prod. immobilisee", ["72"])
    _add_statement_entry(pr_expl, "Autres produits d'exploitation", ["74"])
    pr_fin = revenue.add_entry("PrFin")
    _add_statement_entry(pr_fin, "Produits financiers recurrents", ["75"])

    return render_template(
        "financial_statement/index.html",
        assets=assets,
        liabilities=liabilities,
        expenses=expenses,
        revenue=revenue,
    )
