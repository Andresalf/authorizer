import json
from collections import namedtuple
from app.ports.json_api import JSONApi
from app.adapters.in_memory_account_repo import InMemoryAccountRepo


OPERATION_ENTITY_ACCOUNT = "account"
OPERATION_ENTITY_TRANSACTION = "transaction"
Operation = namedtuple('Operation', ('entity', 'json_payload'))

def get_operation(payload: str) -> Operation:
    payload = json.loads(payload)
    if OPERATION_ENTITY_ACCOUNT in payload:
        return Operation(
            entity=OPERATION_ENTITY_ACCOUNT,
            json_payload=json.dumps(payload[OPERATION_ENTITY_ACCOUNT])
        )
    if OPERATION_ENTITY_TRANSACTION in payload:
        return Operation(
            entity=OPERATION_ENTITY_TRANSACTION,
            json_payload=json.dumps(payload[OPERATION_ENTITY_TRANSACTION])
        )

    return None


line_input = input()
repo = InMemoryAccountRepo()
api = JSONApi(repo)
results = []

while line_input:
    try:
        operation = get_operation(line_input)
        if operation.entity == OPERATION_ENTITY_ACCOUNT:
            results.append(api.create_account(operation.json_payload))
        if operation.entity == OPERATION_ENTITY_TRANSACTION:
            results.append(api.authorize_transaction(operation.json_payload))

        line_input = input()
    except EOFError:
        break

for result in results:
    print(result)