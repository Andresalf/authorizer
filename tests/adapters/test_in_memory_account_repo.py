from app.adapters.in_memory_account_repo import InMemoryAccountRepo
from app.domain.account import Account


def test_account_save():
    account = Account()
    account_repo = InMemoryAccountRepo()

    saved_acc, violations = account.save(account_repo)

    assert saved_acc.account_id == account.account_id
    assert len(violations) == 0
