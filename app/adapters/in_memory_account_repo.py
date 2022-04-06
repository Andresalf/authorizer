from typing import List
from app.domain.account import Account
from app.domain.account_repository import AccountRepository


class InMemoryAccountRepo(AccountRepository):
    def __init__(self):
        self.accounts = {}

    def add(self, account: Account) -> Account:
        self.accounts[account.account_id] = account
        return account

    def get(self, account_id):
        return self.accounts.get(account_id)

    def all(self) -> List[Account]:
        return list(self.accounts.values())