from bdb import Breakpoint
import json
import pytest
from app.adapters.in_memory_account_repo import InMemoryAccountRepo
from app.domain.constants import *
from app.domain.frequency_checker import FrequencyChecker
from app.ports.json_api import JSONApi


@pytest.fixture(scope="function", autouse=True)
def clear_frequency_checker_queue():
    FrequencyChecker.queue.clear()

def test_create_account():
    payload = '{"active-card": false, "available-limit": 750}'
    repo = InMemoryAccountRepo()
    api = JSONApi(repo)

    result = json.loads(api.create_account(payload))
    accounts_in_repo = repo.all()

    assert len(accounts_in_repo) == 1
    assert accounts_in_repo[0].active_card == result["account"]["active-card"]
    assert accounts_in_repo[0].available_limit == result["account"]["available-limit"]
    assert len(result["violations"]) == 0


def test_create_two_accounts():
    first_payload = '{"active-card": false, "available-limit": 175}'
    second_payload = '{"active-card": false, "available-limit": 350}'
    repo = InMemoryAccountRepo()
    api = JSONApi(repo)

    first_result = json.loads(api.create_account(first_payload))
    second_result = json.loads(api.create_account(second_payload))
    accounts_in_repo = repo.all()

    assert len(accounts_in_repo) == 1
    assert accounts_in_repo[0].active_card == first_result["account"]["active-card"]
    assert accounts_in_repo[0].available_limit == first_result["account"]["available-limit"]
    assert len(first_result["violations"]) == 0
    assert accounts_in_repo[0].active_card == second_result["account"]["active-card"]
    assert accounts_in_repo[0].available_limit == second_result["account"]["available-limit"]
    assert len(second_result["violations"]) == 1
    assert second_result["violations"] == [ACCOUNT_ALREADY_INITIALIZED]

def test_authorize_trx_with_no_account_initialized():
    payload = '{"merchant": "Uber Eats", "amount": 25, "time": "2020-12-01T11:07:00.000Z"}'
    acc_repo = InMemoryAccountRepo()
    api = JSONApi(acc_repo)

    result = json.loads(api.authorize_transaction(payload))
    accounts_in_repo = acc_repo.all()

    assert len(accounts_in_repo) == 0
    assert not result["account"]
    assert len(result["violations"]) == 1
    assert result["violations"] == [ACCOUNT_NOT_INITIALIZED]

def test_authorize_trx_with_available_limit_on_account():
    acc_payload = '{"active-card": true, "available-limit": 100}'
    trx_payload = '{"merchant": "Burger King", "amount": 20, "time": "2019-02-13T11:00:00.000Z"}'
    acc_repo = InMemoryAccountRepo()
    api = JSONApi(acc_repo)
    api.create_account(acc_payload)
    accounts_in_repo = acc_repo.all()
    assert len(accounts_in_repo) == 1
    account_in_repo = accounts_in_repo[0]

    trx_result = json.loads(api.authorize_transaction(trx_payload))

    assert account_in_repo.active_card == True
    assert account_in_repo.available_limit == 80
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 80
    assert len(trx_result["violations"]) == 0

def test_authorize_trx_with_no_active_card_on_account():
    acc_payload = '{"active-card": false, "available-limit": 100}'
    trx_payload = '{"merchant": "Burger King", "amount": 20, "time": "2019-02-13T11:00:00.000Z"}'
    acc_repo = InMemoryAccountRepo()
    api = JSONApi(acc_repo)
    api.create_account(acc_payload)
    assert len(acc_repo.all()) == 1

    trx_result = json.loads(api.authorize_transaction(trx_payload))

    assert trx_result["account"]["active-card"] == False
    assert trx_result["account"]["available-limit"] == 100
    assert trx_result["violations"] == [CARD_NOT_ACTIVE]

def test_authorize_trx_with_insufficient_limit_on_account():
    acc_payload = '{"active-card": true, "available-limit": 1000}'
    trx_payload = '{"merchant": "Vivara", "amount": 1250, "time": "2019-02-13T11:00:00.000Z"}'
    acc_repo = InMemoryAccountRepo()
    api = JSONApi(acc_repo)
    api.create_account(acc_payload)
    assert len(acc_repo.all()) == 1

    trx_result = json.loads(api.authorize_transaction(trx_payload))

    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 1000
    assert trx_result["violations"] == [INSUFFICIENT_LIMIT]

def test_trxs_high_frequency_small_interval():
    acc_payload = '{"active-card": true, "available-limit": 100}'
    trx_payload_1 = '{"merchant": "Burger King", "amount": 20, "time": "2019-02-13T11:00:00.000Z"}'
    trx_payload_2 = '{"merchant": "Habbib\'s", "amount": 20, "time": "2019-02-13T11:00:01.000Z"}'
    trx_payload_3 = '{"merchant": "McDonald\'s", "amount": 20, "time": "2019-02-13T11:01:01.000Z"}'
    trx_payload_4 = '{"merchant": "Subway", "amount": 20, "time": "2019-02-13T11:01:31.000Z"}'
    trx_payload_5 = ' {"merchant": "Burger King", "amount": 10, "time": "2019-02-13T12:00:00.000Z"}'
    acc_repo = InMemoryAccountRepo()
    api = JSONApi(acc_repo)
    api.create_account(acc_payload)
    assert len(acc_repo.all()) == 1

    trx_result = json.loads(api.authorize_transaction(trx_payload_1))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 80
    assert trx_result["violations"] == []

    trx_result = json.loads(api.authorize_transaction(trx_payload_2))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 60
    assert trx_result["violations"] == []

    trx_result = json.loads(api.authorize_transaction(trx_payload_3))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 40
    assert trx_result["violations"] == []

    trx_result = json.loads(api.authorize_transaction(trx_payload_4))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 40
    assert trx_result["violations"] == [HIGH_FREQUENCY_SMALL_INTERVAL]

    trx_result = json.loads(api.authorize_transaction(trx_payload_5))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 30
    assert trx_result["violations"] == []

def test_doubled_transaction():
    acc_payload = '{"active-card": true, "available-limit": 100}'
    trx_payload_1 = '{"merchant": "Burger King", "amount": 20, "time": "2019-02-13T11:00:00.000Z"}'
    trx_payload_2 = '{"merchant": "McDonald\'s", "amount": 10, "time": "2019-02-13T11:00:01.000Z"}'
    trx_payload_3 = '{"merchant": "Burger King", "amount": 20, "time": "2019-02-13T11:00:02.000Z"}'
    trx_payload_4 = '{"merchant": "Burger King", "amount": 15, "time": "2019-02-13T11:00:03.000Z"}'
    acc_repo = InMemoryAccountRepo()
    api = JSONApi(acc_repo)
    api.create_account(acc_payload)
    assert len(acc_repo.all()) == 1

    trx_result = json.loads(api.authorize_transaction(trx_payload_1))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 80
    assert trx_result["violations"] == []

    trx_result = json.loads(api.authorize_transaction(trx_payload_2))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 70
    assert trx_result["violations"] == []

    trx_result = json.loads(api.authorize_transaction(trx_payload_3))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 70
    assert trx_result["violations"] == [DOUBLED_TRANSACTION]

    trx_result = json.loads(api.authorize_transaction(trx_payload_4))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 55
    assert trx_result["violations"] == []

def test_multiple_violations():
    acc_payload = '{"active-card": true, "available-limit": 100}'
    trx_payload_1 = '{"merchant": "McDonald\'s", "amount": 10, "time": "2019-02-13T11:00:01.000Z"}'
    trx_payload_2 = '{"merchant": "Burger King", "amount": 20, "time": "2019-02-13T11:00:02.000Z"}'
    trx_payload_3 = '{"merchant": "Burger King", "amount": 5, "time": "2019-02-13T11:00:07.000Z"}'
    trx_payload_4 = '{"merchant": "Burger King", "amount": 5, "time": "2019-02-13T11:00:08.000Z"}'
    trx_payload_5 = '{"merchant": "Burger King", "amount": 150, "time": "2019-02-13T11:00:18.000Z"}'
    trx_payload_6 = '{"merchant": "Burger King", "amount": 190, "time": "2019-02-13T11:00:22.000Z"}'
    trx_payload_7 = '{"merchant": "Burger King", "amount": 15, "time": "2019-02-13T12:00:27.000Z"}'
    acc_repo = InMemoryAccountRepo()
    api = JSONApi(acc_repo)
    api.create_account(acc_payload)
    assert len(acc_repo.all()) == 1

    trx_result = json.loads(api.authorize_transaction(trx_payload_1))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 90
    assert trx_result["violations"] == []

    trx_result = json.loads(api.authorize_transaction(trx_payload_2))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 70
    assert trx_result["violations"] == []

    trx_result = json.loads(api.authorize_transaction(trx_payload_3))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 65
    assert trx_result["violations"] == []

    trx_result = json.loads(api.authorize_transaction(trx_payload_4))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 65
    assert trx_result["violations"] == [HIGH_FREQUENCY_SMALL_INTERVAL]

    trx_result = json.loads(api.authorize_transaction(trx_payload_5))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 65
    assert trx_result["violations"] == [INSUFFICIENT_LIMIT, HIGH_FREQUENCY_SMALL_INTERVAL]

    trx_result = json.loads(api.authorize_transaction(trx_payload_6))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 65
    assert trx_result["violations"] == [INSUFFICIENT_LIMIT, HIGH_FREQUENCY_SMALL_INTERVAL]

    trx_result = json.loads(api.authorize_transaction(trx_payload_7))
    assert trx_result["account"]["active-card"] == True
    assert trx_result["account"]["available-limit"] == 50
    assert trx_result["violations"] == []