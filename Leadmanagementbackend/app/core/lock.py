import threading


class LockManager:

    def __init__(self):
        self._locks = {}
        self._manager_lock = threading.Lock()

    def get_lock(self, key: str) -> threading.Lock:

        with self._manager_lock:
            if key not in self._locks:
                self._locks[key] = threading.Lock()

            return self._locks[key]


lead_lock_manager = LockManager()