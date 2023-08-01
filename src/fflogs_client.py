import base64
import functools
import json
import os
import pickle
from datetime import datetime
from io import StringIO
from pathlib import Path

import dotenv
import pandas as pd
import requests

from src.pulls import Pulls

dotenv.load_dotenv()

GUILD_ID = os.getenv("GUILD_ID")
ZONE_ID = os.getenv("ZONE_ID")
FFLOGS_ID = os.getenv("FFLOGS_ID")
FFLOGS_SECRET = os.getenv("FFLOGS_SECRET")
TOKEN_FILE = os.getenv("TOKEN_FILE")

path = Path(__file__).parent / "../data"


class FFLogsClient:
    current_start_time: int
    current_code: str
    pulls: Pulls
    access_token: str
    expires_in: int
    loaded: bool
    time_stamp_now: int

    def __init__(self):
        self.current_start_time = 0
        self.current_code = ""
        self.pulls = Pulls()

        self.access_token, self.expires_in, self.loaded = self.load_token_from_file()

        ct = datetime.now()
        self.time_stamp_now = int(ct.timestamp() * 1000)

        if self.loaded is False or self.expires_in < self.time_stamp_now:
            self.access_token, self.expires_in = self.get_token()
            self.save_token_to_file(self.access_token, self.expires_in)

        self.get_latest_report()

    def get_wipe_count(self) -> int:
        if self.current_code == "":
            self.get_latest_report()
            return 0

        fights = self.get_pulls()
        new_start = self.current_start_time
        wipe_count = 0

        for fight in fights:
            if fight['startTime'] > self.current_start_time:
                if not fight['kill'] and fight['size'] == 8:
                    wipe_count += 1
                new_start = fight['startTime']

        self.current_start_time = new_start

        print(wipe_count)
        return wipe_count

    def get_latest_report(self):
        replacements = ("1️⃣", GUILD_ID), ("2️⃣", ZONE_ID)
        payload = "{\"query\":\"{reportData{reports(guildID:1️⃣,zoneID:2️⃣){data{code,startTime}}}}\"}"
        payload = functools.reduce(lambda a, kv: a.replace(*kv), replacements, payload)

        print(payload)

        io = self.fetch_from_api(self.access_token, payload)

        try:
            current = json.load(io)['data']['reportData']['reports']['data'][0]
            log_time = current["startTime"]

            print(f'{log_time} / {self.time_stamp_now}')

            dt_log = pd.Timestamp(log_time, unit='ms', tz="America/Sao_Paulo")
            dt_now = pd.Timestamp(self.time_stamp_now, unit='ms', tz="America/Sao_Paulo")

            print(f'{dt_log} / {dt_now}')

            if dt_log.day == dt_now.day:
                print(f'{dt_log.day} / {dt_now.day}')
                self.current_code = current["code"]
                print(self.current_code)
            else:
                print(f'{dt_log.day} / {dt_now.day}')
                self.current_code = ""
        except IndexError:
            self.current_code = ""

    def get_pulls(self) -> list[dict]:
        payload = "{\"query\":\"{reportData{report(code:\\\"1️⃣\\\"){fights{kill,startTime,size}}}}\"}"
        payload = payload.replace("1️⃣", self.current_code)

        io = self.fetch_from_api(self.access_token, payload)
        fights = json.load(io)['data']['reportData']['report']['fights']

        return fights

    @staticmethod
    def fetch_from_api(token: str, payload: str):
        url = "https://www.fflogs.com/api/v2/client"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = requests.request("GET", url, data=payload, headers=headers)
        print(f'{StringIO(response.text)} | {type(StringIO(response.text))}')
        return StringIO(response.text)

    @staticmethod
    def get_token() -> tuple[str, int]:
        url = "https://www.fflogs.com/oauth/token"
        payload = "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"grant_type\"\r\n\r\nclient_credentials\r\n-----011000010111000001101001--\r\n"
        auth = FFLogsClient.encode_base64(f"{FFLOGS_ID}:{FFLOGS_SECRET}")
        headers = {
            'Content-Type': "multipart/form-data; boundary=---011000010111000001101001",
            'Authorization': f"Basic {auth}"
        }
        print(f"{FFLOGS_ID}:{FFLOGS_SECRET}")
        print(headers)
        response = requests.request("POST", url, data=payload, headers=headers)
        io = StringIO(response.text)
        n_json = json.load(io)
        print(n_json)

        ct = datetime.now()
        ts = int(ct.timestamp() * 1000)
        expires = int(ts) + int(n_json['expires_in'])
        print(f'current {ts} :: expires {expires}')

        return n_json['access_token'], expires

    @staticmethod
    def encode_base64(message) -> str:
        message_bytes = message.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)

        return base64_bytes.decode("ascii")

    @staticmethod
    def load_token_from_file() -> tuple[str, str, bool]:
        try:
            with open(f'{path}\\{TOKEN_FILE}', 'rb') as f:
                tp = pickle.load(f)
                print("Loading Token")
                return tp[0], tp[1], True
        except EnvironmentError:
            print("Failed to Load Token")
            return "", "", False

    @staticmethod
    def save_token_to_file(access_token, expires_in):
        tp = (access_token, expires_in)
        with open(f'{path}\\{TOKEN_FILE}', 'wb') as f:
            print("Saving Token")
            pickle.dump(tp, f)
