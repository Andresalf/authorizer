import json
from app.domain.account import Account
from app.domain.account_repository import AccountRepository
from app.domain.transaction import Transaction
from app.domain.utils import from_iso_to_datetime


class JSONApi:
    def __init__(self, acc_repo: AccountRepository):
        self.acc_repo = acc_repo

    def create_account(self, payload: str) -> str:
        payload = json.loads(payload)
        account = Account(
            active_card=payload["active-card"],
            available_limit=payload["available-limit"]
        )
        saved_acc, violations = account.save(self.acc_repo)

        return self.result_to_json(saved_acc, violations)

    def authorize_transaction(self, payload: str) -> str:
        payload = json.loads(payload)
        transaction = Transaction(
            merchant=payload["merchant"],
            amount=payload["amount"],
            created_at=from_iso_to_datetime(payload["time"])
        )
        affected_acc, violations = transaction.authorize(self.acc_repo)

        return self.result_to_json(affected_acc, violations)

    def result_to_json(self, account, violations):
        return json.dumps(
            {
                "account": {
                    "active-card": account.active_card,
                    "available-limit": account.available_limit
                    #"deny-list": account.deny_list
                } if account else {},
                "violations": violations
            }
        )

