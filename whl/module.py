from discord.ext import commands

from core import logging

bot_log = logging.Bot.logger()


class Whl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot) -> None:
    bot.add_cog(Whl(bot))
