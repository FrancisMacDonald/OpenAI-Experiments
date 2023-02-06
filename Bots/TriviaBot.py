import asyncio
import random
from datetime import timedelta, datetime

import discord

from Bots.AbstractDiscordBot import AbstractDiscordBot
from Games.Trivia import Trivia


class TriviaBot(AbstractDiscordBot):
    _trivia = None
    _time_up = None
    _answered = False

    _channels: dict[int, discord.channel.TextChannel] = {}

    async def process_on_ready(self):
        for channel_id in self._channels:
            self._channels[channel_id] = self._bot.get_channel(channel_id)

        self._answered = True
        self._bot.loop.create_task(self.ask_question_loop(), name="ask_question_loop")
        self._bot.loop.create_task(self.start_double_points_mode_loop(), name="start_double_points_mode_loop")

    async def process_on_message(self, message):
        print(f"{message.author}: {message.content} - {message.channel.name} ({message.channel.id})")
        await self.check_command(message)

    def __init__(self, discord_bot_token, openai_api_key, trivia_channel_id, general_channel_id):
        self._channels[trivia_channel_id] = None
        self._channels[general_channel_id] = None
        self._leaderboard_file_name = 'triviabot_leaderboard.txt'
        self._time_up = None

        super().__init__(discord_bot_token)
        self._trivia = Trivia(openai_api_key, self._leaderboard_file_name)


    def get_seconds_remaining_until_next_question(self):
        return round((self._time_up - datetime.now()).total_seconds())

    # Discord functions
    def get_leaderboard_as_embed(self):
        leaderboard_embed = discord.Embed(title="Trivia Leaderboard", description=self._trivia.get_leaderboard_as_text())
        leaderboard_embed.set_footer(text="Change topics with !topics")
        return leaderboard_embed

    def get_active_question_as_embed(self):
        answers = f"A)\t**{self._trivia.active_question[1]}**\n" \
                  f"B)\t**{self._trivia.active_question[2]}**\n" \
                  f"C)\t**{self._trivia.active_question[3]}**\n" \
                  f"D)\t**{self._trivia.active_question[4]}**\n"

        embed = discord.Embed(title=f"{self._trivia.active_question[0]}", description=answers, type='rich', color=discord.Color.blue())
        embed.set_footer(text="Answer with A, B, C, or D")

        return embed

    async def ask_question_loop(self):
        while True:
            if self._answered:
                await self._trivia.generate_new_question()
                self._answered = False

                for channel_id in self._channels:
                    channel = self._channels[channel_id]
                    await channel.send(embed=self.get_active_question_as_embed())
            else:
                self._trivia.clear_all_guesses()

            seconds_between_questions = 20
            self._time_up = datetime.now() + timedelta(seconds=seconds_between_questions)
            await asyncio.sleep(seconds_between_questions)

    async def check_guess(self, message):
        # check if the message is from the bot
        if message.author == self._bot.user:
            return

        # check if there is an active question
        if self._trivia.active_question is None:
            return

        # check if the message is a guess
        if len(message.content) != 1:
            return

        until_next_question = self.get_seconds_remaining_until_next_question()
        second_name = "seconds" if until_next_question > 1 else "second"

        if message.author.name in self._trivia.guessed_this_question:
            responses = [
                f"{message.author.name}, you can guess again in {until_next_question} {second_name}",
                f"Easy there {message.author.name}! You can guess again in {until_next_question} {second_name}",
                f"Slow down {message.author.name}! You can guess again in {until_next_question} {second_name}",
                f"Patience {message.author.name}! You can guess again in {until_next_question} {second_name}",
                f"Be patient {message.author.name}! You can guess again in {until_next_question} {second_name}",
            ]
            random_response = random.choice(responses)
            await message.channel.send(random_response)
            return

        if self._trivia.guess_question_user(message.content, message.author.name):
            await message.channel.send(f"{message.author.name} is correct!")
            # await message.add_reaction("👍")
            self._answered = True
            await message.channel.send(embed=self.get_leaderboard_as_embed())
            await message.channel.send(f"Next question in {until_next_question} {second_name}...")
        else:
            # thumbs down message
            await message.add_reaction("👎")

    async def check_command(self, message):
        if message.author == self._bot.user:
            return

        # check if the message is in a channel that the bot is listening to
        if message.channel.id in self._channels:
            if message.content == "!trivia":
                await message.channel.send(embed=self.get_active_question_as_embed())
            elif message.content == "!leaderboard":
                await message.channel.send(embed=self.get_leaderboard_as_embed())
            # check if the message content contains !topic followed by a topic
            elif message.content.startswith("!topics"):
                # change the topics
                new_topics = message.content.replace("!topics", "").strip()
                if len(new_topics) > 3:
                    self._trivia.change_prompt_topics(new_topics)
                    await message.channel.send(f"Topics have been changed to {new_topics}")
                else:
                    await message.channel.send(f"Topics are currently {self._trivia.prompt_topics}")
                    await message.channel.send(f"Use !topics followed by a comma seperated list of topics to change the topics")

            # elif message.content == "!reset":
            #     self._trivia.reset_game()
            #     await message.channel.send("Trivia has been reset!")
            else:
                await self.check_guess(message)

    async def start_double_points_mode_loop(self):
        while True:
            _random_additional_seconds = random.randint(0, 60 * 30)
            await asyncio.sleep((60 * 30) + _random_additional_seconds)
            self._trivia.start_double_points_mode()
            await self._send_message_to_channels_as_embed("Double points mode has started! Earn double points for the next 2 minutes!")
            await asyncio.sleep(60 * 2)
            self._trivia.stop_double_points_mode()
            await self._send_message_to_channels_as_embed("Double points mode has ended!")

    async def _send_message_to_channels_as_embed(self, param):
        for channel_id in self._channels:
            channel = self._channels[channel_id]
            embed = discord.Embed(title=param, type='rich', color=discord.Color.dark_red())
            await channel.send(embed=embed)

    def is_connected_to_server(self):
        return len(self._bot.guilds) > 0
