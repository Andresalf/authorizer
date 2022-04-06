import uuid

import pytest
from app.adapters.in_memory_account_repo import InMemoryAccountRepo

from app.domain.account import Account
from app.domain.constants import MERCHANT_DENIED
from app.domain.frequency_checker import FrequencyChecker
from app.domain.transaction import Transaction
from app.domain.violations import get_transaction_violations

@pytest.fixture(scope="function", autouse=True)
def clear_frequency_checker_queue():
    FrequencyChecker.queue.clear()

def test_merchant_denied():
    trx_id = str(uuid.uuid4())
    trx = Transaction()
    trx.merchant = "merchant_1"
    account = Account()
    account.deny_list.append(trx.merchant)
    account.active_card = True
    repo = InMemoryAccountRepo()
    repo.add(account)

    violations = get_transaction_violations(trx, repo)

    assert violations == [MERCHANT_DENIED]

def test_merchant_not_denied():
    trx_id = str(uuid.uuid4())
    trx = Transaction()
    trx.merchant = "merchant_1"
    account = Account()
    account.deny_list.append("merchant_2")
    account.active_card = True
    repo = InMemoryAccountRepo()
    repo.add(account)

    violations = get_transaction_violations(trx, repo)

    assert violations == []