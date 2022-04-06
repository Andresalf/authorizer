from datetime import datetime
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from app.domain.violations import get_transaction_violations

if TYPE_CHECKING:
    # Prevent circular imports
    from app.domain.account_repository import AccountRepository

@dataclass
class Transaction:
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    merchant: str = ""
    amount: int = 0
    created_at: datetime = datetime.now()

    def authorize(self, acc_repo: 'AccountRepository'):
        violations = get_transaction_violations(self, acc_repo)
        account = self._get_affected_account(acc_repo)
        if not violations:
            account.available_limit -= self.amount

        return account, violations

    def _get_affected_account(self, acc_repo):
        account = None
        if len(acc_repo.all()) == 1:
            account = acc_repo.all()[0]

        return account

    def __hash__(self):
        return hash(self.transaction_id)

