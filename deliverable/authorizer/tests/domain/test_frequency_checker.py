from app.domain.transaction import Transaction
from app.domain.frequency_checker import FrequencyChecker
from app.domain.utils import from_iso_to_datetime
from app.domain.constants import *


def test_high_frequency_small_interval():
    FrequencyChecker.queue.clear()
    transaction_1 = Transaction(
        merchant="Burger King",
        amount=20,
        created_at=from_iso_to_datetime("2019-02-13T11:00:00.000Z")
    )
    transaction_2 = Transaction(
        merchant="Habbib's",
        amount=20,
        created_at=from_iso_to_datetime("2019-02-13T11:00:01.000Z")
    )
    transaction_3 = Transaction(
        merchant="McDonald's",
        amount=20,
        created_at=from_iso_to_datetime("2019-02-13T11:01:01.000Z")
    )
    transaction_4 = Transaction(
        merchant="Subway",
        amount=20,
        created_at=from_iso_to_datetime("2019-02-13T11:01:31.000Z")
    )
    transaction_5 = Transaction(
        merchant="Burger King",
        amount=10,
        created_at=from_iso_to_datetime("2019-02-13T12:00:00.000Z")
    )

    assert FrequencyChecker.get_violation(transaction_1) == None
    assert FrequencyChecker.get_violation(transaction_2) == None
    assert FrequencyChecker.get_violation(transaction_3) == None
    assert FrequencyChecker.get_violation(transaction_4) == HIGH_FREQUENCY_SMALL_INTERVAL
    assert FrequencyChecker.get_violation(transaction_5) == None

def test_is_doubled_transaction():
    FrequencyChecker.queue.clear()
    transaction_1 = Transaction(
        merchant="Burger King",
        amount=20,
        created_at=from_iso_to_datetime("2019-02-13T11:00:00.000Z")
    )
    transaction_2 = Transaction(
        merchant="McDonald's",
        amount=10,
        created_at=from_iso_to_datetime("2019-02-13T11:00:01.000Z")
    )
    transaction_3 = Transaction(
        merchant="Burger King",
        amount=20,
        created_at=from_iso_to_datetime("2019-02-13T11:00:02.000Z")
    )
    transaction_4 = Transaction(
        merchant="Burger King",
        amount=15,
        created_at=from_iso_to_datetime("2019-02-13T11:00:03.000Z")
    )

    assert FrequencyChecker.get_violation(transaction_1) == None
    assert FrequencyChecker.get_violation(transaction_2) == None
    assert FrequencyChecker.get_violation(transaction_3) == DOUBLED_TRANSACTION
    assert FrequencyChecker.get_violation(transaction_4) == None