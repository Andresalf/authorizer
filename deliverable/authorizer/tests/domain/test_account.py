import uuid

from app.domain.account import Account

def test_account_existing_account_id():
    account_id = str(uuid.uuid4())

    assert Account(account_id).account_id == account_id

def test_account_defaults():
    account_id = str(uuid.uuid4())
    account = Account()

    assert account.account_id != account_id
    assert account.active_card == False
    assert account.available_limit == 0