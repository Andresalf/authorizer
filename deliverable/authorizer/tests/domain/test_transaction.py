import uuid
from app.domain.transaction import Transaction


def test_transaction_defaults():
    trx_id = str(uuid.uuid4())
    transaction = Transaction()

    assert transaction.transaction_id != trx_id
    assert transaction.merchant == ""
    assert transaction.amount == 0