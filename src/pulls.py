import os
from pathlib import Path

import dotenv
import pandas as pd
from pandas import DataFrame

dotenv.load_dotenv()

ROOT_DIR = os.path.abspath(os.curdir)
PULLS_FILE = os.getenv("PULLS_FILE")

path = Path(__file__).parent / "../data"


class Pulls:
    pulls_df: DataFrame

    def __init__(self):
        self.pulls_df = self.from_csv()

    def add_pull(self, code: str, kill: bool, start_time: int, size: int):
        if kill or size != 8:
            return -1
        self.pulls_df = pd.concat([self.pulls_df, pd.DataFrame.from_records([{'Code': code, 'StartTime': start_time}])])
        self.to_csv()

    def check_if_pull_exists(self, code: str, start_time: int):
        return self.pulls_df.loc[(self.pulls_df['Code'] == code) & (self.pulls_df['StartTime'] == start_time)].any().all()

    def to_csv(self):
        self.pulls_df.to_csv(f'{path}\\{PULLS_FILE}', index=False, encoding='utf-8')

    @staticmethod
    def from_csv() -> DataFrame:
        try:
            return pd.read_csv(f'{path}\\{PULLS_FILE}', index_col=False, encoding='utf-8')
        except EnvironmentError:
            return pd.DataFrame(columns=["Code", "StartTime"])
