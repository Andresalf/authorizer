from typing import TYPE_CHECKING
from app.domain.constants import *
from app.domain.frequency_checker import FrequencyChecker

if TYPE_CHECKING:
    # Prevent circular imports
    from app.domain.transaction import Transaction
    from app.domain.account_repository import AccountRepository


def get_account_violations(acc_repo: 'AccountRepository'):
    violations = []
    if len(acc_repo.all()) != 0:
        violations.append(ACCOUNT_ALREADY_INITIALIZED)

    return violations

def get_transaction_violations(trx: 'Transaction', acc_repo: 'AccountRepository'):
    violations = []
    if len(acc_repo.all()) == 0:
        violations.append(ACCOUNT_NOT_INITIALIZED)
    else:
        account = acc_repo.all()[0]
        if not account.active_card:
            violations.append(CARD_NOT_ACTIVE)
        if trx.amount > account.available_limit:
            violations.append(INSUFFICIENT_LIMIT)
        frequency_violation = FrequencyChecker.get_violation(trx, violations)
        if frequency_violation:
            violations.append(frequency_violation)
        if trx.merchant in account.deny_list:
            violations.append(MERCHANT_DENIED)

    return violations