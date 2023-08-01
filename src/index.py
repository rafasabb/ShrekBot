import os
import pickle
from pathlib import Path

import dotenv

dotenv.load_dotenv()

INDEX_FILE = os.getenv("INDEX_FILE")

path = Path(__file__).parent / "../data"


class Index:
    index: int

    def __init__(self):
        self.index = self.load_index_from_file()

    def get_index(self) -> int:
        return self.index

    def update_index(self):
        self.index += 1
        self.save_index_to_file()

    def save_index_to_file(self):
        with open(f'{path}\\{INDEX_FILE}', 'wb') as f:
            pickle.dump(self.index, f)

    @staticmethod
    def load_index_from_file() -> int:
        try:
            with open(f'{path}\\{INDEX_FILE}', 'rb') as f:
                return int(pickle.load(f))
        except EnvironmentError:
            return 0
