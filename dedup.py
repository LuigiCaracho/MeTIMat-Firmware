"""
Class to deduplicate URLs
"""

import time


class Deduplicator:
    def __init__(self, timeout):
        self.timeout = timeout
        self.last_seen = {}

    def is_new(self, value):
        now = time.time()

        if value in self.last_seen:
            if now - self.last_seen[value] < self.timeout:
                return False

        self.last_seen[value] = now
        return True
