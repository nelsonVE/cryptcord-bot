import asyncio
import discord

from discord.ext import commands, tasks

from api import Coin


class CryptoBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.coins_id = ['plant-vs-undead-token', 'smooth-love-potion', ]
        self.main_coin = 'slp'
        self.__temp_index = None
        self.instances = []
        self.get_coin_instances()

    def get_coin_instances(self):
        for coin_id in self.coins_id:
            self.instances.append(Coin(coin_id))

    async def change_status(self, status: str, activity_type=discord.ActivityType.watching):
        """
        Updates the bot status (activity)
        """
        activity = discord.Activity(name=status, type=activity_type)
        await self.bot.change_presence(status=discord.Status.online, activity=activity)

    def get_emoji_number(self, number: int):
        """
        Gets an emoji number by its pos.
        """
        return ('1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟')[int(number)]

    @tasks.loop(seconds=60.0)
    async def update_status(self):
        for instance in self.instances:
            instance.update_coin_info()
            if instance.symbol == self.main_coin:
                price = round(instance.current_usd_price, 2)
                percent = round(instance.day_change_percent, 2)
                emoji = '⬆️' if percent > 0 else '⬇️'

                status = \
                    f"{instance.symbol.upper()}: {price}$ {percent}% {emoji}"

                print(status)
                await self.change_status(status)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Connected :)')
        self.update_status.start()

    @commands.command()
    async def force_start(self, ctx):
        await self.update_status()
        await ctx.send('Start forced!')

    @commands.command()
    async def add_coin(self, ctx, url: str=None):
        if not url or not ('coingecko.com' in url and '/coins/' in url):
            return await ctx.send(f":white_check_mark: No coingecko url provided")

        url_parts = url.split('/')
        coin_id = url_parts[-1]
        self.coins_id.append(coin_id)
        self.instances = []
        self.get_coin_instances()

        await ctx.send(f":white_check_mark: Coin added!")

    async def change_coin(self, ctx):
        coin = self.instances[self.__temp_index]
        self.main_coin = coin.symbol
        await ctx.send(f":white_check_mark: Main coin changed to: {coin.name}")
        await self.update_status()
        self.__temp_index = None

    def reverse_emoji_reaction(self, reaction: str):
        for index in range(0, 10):
            emoji = self.get_emoji_number(index)
            if emoji == str(reaction.emoji):
                self.__temp_index = index
                break

    @commands.command()
    async def coins(self, ctx):
        def check_reaction(reaction, user):
            self.reverse_emoji_reaction(reaction)
            print(self.__temp_index)
            return user != self.bot.user

        await self.update_status()
        coins = ''
        emojis = []

        for index, instance in enumerate(self.instances):
            emoji = self.get_emoji_number(index)
            emojis.append(emoji)
            coins += f">\t{emoji}. {instance.symbol.upper()}: {instance.name}\n"

        message = await ctx.send(f"> Available coins:\n{coins}")
        [await message.add_reaction(emoji) for emoji in emojis]
        try:
            await self.bot.wait_for(
                "reaction_add",
                timeout=10.0,
                check=check_reaction
            )
        except asyncio.TimeoutError:
            pass
        else:
            if self.__temp_index is not None:
                await self.change_coin(ctx)