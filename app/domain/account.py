import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List
from app.domain.violations import get_account_violations

if TYPE_CHECKING:
    # Prevent circular imports
    from app.domain.account_repository import AccountRepository

@dataclass
class Account:
    account_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    active_card: bool = False
    available_limit: int = 0
    deny_list: List[str] = field(default_factory=list)

    def save(self, repo: 'AccountRepository'):
        violations = get_account_violations(repo)
        if not violations:
            return repo.add(self), []

        return repo.all()[0], violations

    def __hash__(self):
        return hash(self.account_id)
