# runs the trivia bot
import os

from Bots.TriviaBot import TriviaBot

# get the discord bot token from the environment variables
my_discord_bot_token = os.environ.get("DISCORD_BOT_TOKEN")
# get the openai api key from the environment variables
my_openai_api_key = os.environ.get("OPENAI_API_KEY")
# get the trivia channel id from the environment variables
trivia_channel_id = int(os.environ.get("TRIVIA_CHANNEL_ID"))
# get the general channel id from the environment variables
# general_channel_id = int(os.environ.get("GENERAL_CHANNEL_ID"))

trivia_bot = TriviaBot(discord_bot_token=my_discord_bot_token, openai_api_key=my_openai_api_key, channels_ids=[trivia_channel_id])


@trivia_bot.bot.event
async def on_ready():
    await trivia_bot.on_ready()


@trivia_bot.bot.event
async def on_message(message):
    await trivia_bot.on_message(message)


trivia_bot.start()
