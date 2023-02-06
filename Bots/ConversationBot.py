import random

import openai

from AbstractDiscordBot import AbstractDiscordBot


class ConversationBot(AbstractDiscordBot):
    def __init__(self, discord_bot_token, openai_api_key, initial_prompt):
        super().__init__(discord_bot_token, openai_api_key)
        self._initial_prompt = initial_prompt

    _you_name = ""
    _bot_name = ""
    _full_prompt = ""

    async def talk(self, ctx, *, message):
        self._full_conversation += f"{ctx.author.name}: {message}"

    async def get_talk(self, ctx):
        if ctx.message.author == self.bot.user:
            return

        ctx.message.content = ctx.message.content.replace('!talk', '')
        conversation = self.query_openai(ctx.message.content)

        if conversation:
            random_number = random.randint(0, 10)
            print(random_number)
            if random_number == 0:
                conversation = conversation.upper()

            await ctx.send(f'{conversation}')

    async def process_on_message(self, message):
        # 1055909966411743372 is OpenAI
        if message.author.id == 1055909966411743372 and self._talk_length < self._max_talk_length:
            self._talk_length += 1
            conversation = self.query_openai(message.content)

            if conversation:
                await message.channel.send(f"!openai {conversation}")

        # 830663175325220885 is FM
        if message.author.id == 830663175325220885:
            pass

    def query_openai(self, text):
        openai.api_key = self._openai_api_key
        self.full_conversation += f"{self._you_name}: {text}\n{self._bot_name}: "

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=self.full_conversation,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[f"{self._you_name}:", f"{self._bot_name}:"]
        )

        if response is not None and response['choices'] is not None and len(response['choices']) > 0 and response['choices'][0]['text'] is not None:
            self.full_conversation += f"{response['choices'][0]['text']}\n"
            return response['choices'][0]['text']
        else:
            return None
