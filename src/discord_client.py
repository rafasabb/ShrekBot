import asyncio
import functools
import os
import typing
from pathlib import Path

import discord
import dotenv
import keyboard
import numpy as np
import pandas as pd
from pandas import DataFrame

from src.fflogs_client import FFLogsClient
from src.index import Index
from src.mode import Mode

dotenv.load_dotenv()

HOTKEY = os.getenv("HOTKEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SCRIPT_CSV_FILE = os.getenv("SCRIPT_CSV_FILE")
IMAGE_CSV_FILE = os.getenv("IMAGE_CSV_FILE")

path = Path(__file__).parent / "../data"


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


class DiscordClient(discord.Client):
    mode: Mode
    index: Index
    fflogs_client: FFLogsClient

    def __init__(self, *, intents, mode, **options):
        super().__init__(intents=intents, **options)
        self.mode = mode
        self.index = Index()
        self.fflogs_client = FFLogsClient()
        self.data_df = self.get_data_frame(SCRIPT_CSV_FILE, ["CHARACTER", "DIALOG"])
        self.image_df = self.get_data_frame(IMAGE_CSV_FILE, ["CHARACTER", "LINK"])

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        if self.mode == Mode.HOTKEY:
            self.loop.create_task(await self.check_hotkey())
        elif self.mode == Mode.LOGS:
            self.loop.create_task(await self.check_logs())

    async def send_embed_to_channel(self, name, description, image_url):
        embed = discord.Embed(title=name, description=description, color=discord.Color.blue())
        embed.set_thumbnail(url=image_url)

        channel = self.get_channel(int(CHANNEL_ID))
        await channel.send(embed=embed)

    @to_thread
    async def check_hotkey(self):
        while True:
            if keyboard.is_pressed(HOTKEY):
                name, description = self.get_next_data(self.index.get_index())
                self.index.update_index()
                image_url = self.get_image(name)
                await self.send_embed_to_channel(name, description, image_url)
            await asyncio.sleep(2)

    @to_thread
    async def check_logs(self):
        while True:
            wipe_count = self.fflogs_client.get_wipe_count()

            while wipe_count > 0:
                name, description = self.get_next_data(self.index.get_index())
                self.index.update_index()
                image_url = self.get_image(name)
                wipe_count -= 1
                await self.send_embed_to_channel(name, description, image_url)
                await asyncio.sleep(2)
            await asyncio.sleep(30)

    def get_next_data(self, ni) -> tuple[str, str]:
        return self.data_df.loc[ni, 'CHARACTER'], self.data_df.loc[ni, 'DIALOG']

    def get_image(self, name) -> tuple[str, str]:
        return self.image_df.loc[self.image_df['CHARACTER'] == name]["LINK"].values[0]

    @staticmethod
    def get_data_frame(file: str, names: list[str]) -> DataFrame:
        return pd.read_csv(f'{path}\\{file}', names=names, on_bad_lines='skip').replace(np.nan, '', regex=True)
