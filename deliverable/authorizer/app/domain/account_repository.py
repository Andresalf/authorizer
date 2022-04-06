import abc
from typing import List

from app.domain.account import Account


class AccountRepository(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def add(self, account: Account) -> Account:
        raise NotImplementedError

    @abc.abstractclassmethod
    def all(self) -> List[Account]:
        raise NotImplementedError
