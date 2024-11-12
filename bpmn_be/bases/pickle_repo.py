import pickle

from bpmn_be.bases.in_memory_repo import InMemoryRepo
from bpmn_be.bases.repo import T_id, T_obj


class PickleRepo(InMemoryRepo[T_id, T_obj]):
    def __init__(self, filename):
        super().__init__()
        self._filename = filename

    def load(self):
        try:
            with open(self._filename, 'rb') as f:
                self._storage = pickle.load(f)
        except FileNotFoundError:
            pass

    def save(self):
        with open(self._filename, 'wb') as f:
            pickle.dump(self._storage, f)
