from collections import deque
from app.domain.constants import *

class FrequencyChecker:
    INTERVAL_IN_MINS = 2
    MAX_TRXS_PER_INTERVAL = 3
    queue = deque()

    @staticmethod
    def _remove_older_transactions(trx):
        greater_time_index = None
        for i in range(len(FrequencyChecker.queue)):
            diff = trx.created_at - FrequencyChecker.queue[i].created_at
            if diff.total_seconds() > FrequencyChecker.INTERVAL_IN_MINS * 60:
                greater_time_index = i
                break

        if greater_time_index is not None:
            for _ in range(len(FrequencyChecker.queue) - greater_time_index):
                FrequencyChecker.queue.pop()

    @staticmethod
    def _high_frequency_is_good():
        if len(FrequencyChecker.queue) >= FrequencyChecker.MAX_TRXS_PER_INTERVAL:
            return False

        return True

    @staticmethod
    def _is_doubled_transaction(trx):
        doubled_found = False
        for i in range(len(FrequencyChecker.queue)):
            this_trx = FrequencyChecker.queue[i]
            if trx.merchant == this_trx.merchant and trx.amount == this_trx.amount:
                doubled_found = True
                break

        return doubled_found

    @staticmethod
    def register_transaction(trx):
        if trx not in FrequencyChecker.queue:
            FrequencyChecker.queue.appendleft(trx)

    @staticmethod
    def get_violation(trx, existing_violations=None):
        FrequencyChecker._remove_older_transactions(trx)
        if not FrequencyChecker._high_frequency_is_good():
            return HIGH_FREQUENCY_SMALL_INTERVAL
        if FrequencyChecker._is_doubled_transaction(trx):
            return DOUBLED_TRANSACTION

        if not existing_violations:
            FrequencyChecker.register_transaction(trx)

        return None
