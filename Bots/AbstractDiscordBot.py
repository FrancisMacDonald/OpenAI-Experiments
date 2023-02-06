from abc import ABC, abstractmethod

import discord
from discord.ext import commands


class AbstractDiscordBot(ABC):
    def __init__(self, discord_bot_token):
        self._discord_bot_token = discord_bot_token
        self._discord_intents = discord.Intents.all()
        self._bot = commands.Bot(command_prefix='!', intents=self._discord_intents)

    async def get_last_message(self, ctx):
        messages = [message async for message in ctx.channel.history(limit=3, oldest_first=False)]
        if messages is not None:
            return messages[1].content
        else:
            return None

    @abstractmethod
    async def process_on_message(self, message):
        pass

    @abstractmethod
    async def process_on_ready(self):
        pass

    async def on_message(self, message):
        await self._bot.process_commands(message)
        if message.author == self._bot.user:
            return

        await self.process_on_message(message)

    async def on_ready(self):
        print("Bot is ready!")
        print("Name: {}".format(self._bot.user.name))
        print("ID: {}".format(self._bot.user.id))

        for guild in self._bot.guilds:
            for channel in guild.channels:
                print(f"guild: {guild.name} - channel: {channel.name} ({channel.id}) - type: {channel.type} - category: {channel.category}")

        await self.process_on_ready()

    def start(self):
        self._bot.run(self._discord_bot_token)

    @property
    def bot(self):
        return self._bot
