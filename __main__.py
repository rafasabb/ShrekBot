import os

import discord
import dotenv

from src.discord_client import DiscordClient
from src.mode import Mode

dotenv.load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.message_content = True
    client = DiscordClient(intents=intents, mode=Mode.LOGS)
    client.run(DISCORD_TOKEN)
