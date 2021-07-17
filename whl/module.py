import discord
from discord.ext import commands

import database
from core import logging, utils

from .database import Channel, User
from .objects import WormholeMessage


bot_log = logging.Bot.logger()
config = database.config.Config.get()


class Whl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        WormholeMessage.refresh()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore non-text messages
        if message.type is not discord.MessageType.default:
            return

        if message.author.bot:
            return

        wormhole = Channel.get(channel_id=message.channel.id)
        if wormhole is None:
            return

        if not wormhole.active:
            await bot_log.debug(
                message.author, message.channel, "Wormhole not active, abort."
            )
            return
        if not wormhole.beam.active:
            await bot_log.debug(
                message.author, message.channel, "Beam not active, abort."
            )

        wmessage = WormholeMessage(self.bot, message)

        if wmessage.should_be_deleted:
            await utils.Discord.delete_message(message)

        if not wmessage.valid:
            return

        await wmessage.send()

    @commands.command(name="register")
    async def register(self, ctx):
        if User.get(channel_id=ctx.channel.id, user_id=ctx.author.id) is not None:
            await ctx.author.send("You are already registered.")
            return

        wormhole = Channel.get(channel_id=ctx.channel.id)
        name = self._get_free_name(wormhole.beam.name, ctx.author.name)
        user = User(channel_id=ctx.channel.id, user_id=ctx.author.id, name=name)
        await ctx.author.send(
            f"You have been register in beam **{wormhole.beam.name}** as **{name}**."
        )

    @commands.group(name="set")
    async def set_(self, ctx):
        await utils.Discord.send_help(ctx)

    @set_.command(name="home")
    async def set_home(self, ctx):
        wormhole = Channel.get(ctx.channel.id)
        user = User.get(channel_id=ctx.channel.id, user_id=ctx.author.id)
        if user is None:
            await ctx.author.send("You have to register first.")
            return

        if user.channel_id == ctx.channel.id:
            await ctx.author.send("This channel is already your home.")
            return

        user.channel_id = ctx.channel.id
        user.save()

        await ctx.author.send(
            f"Your home in beam **{user.channel.beam.name}** "
            f"has been set to **#{ctx.channel.name}**."
        )

        await bot_log.info(ctx.author, ctx.channel, f"Home set to {ctx.channel.name}.")

    @set_.command(name="name")
    async def set_name(self, ctx, name: str):
        beam = ""
        user = User.get(channel_id=ctx.channel.id, user_id=ctx.author.id)

    def _get_free_name(self, beam_name: str, name: str):
        name = name.replace("*", "").replace("_", "").replace("(", "").replace(")", "")
        name = name[:20]
        user = User.get_by_name(beam_name, name)

        i = 1
        while user is not None:
            name = f"{name}{i}"
            user = User.get_by_name(beam_name, name)
            i += 1

        return name


def setup(bot) -> None:
    bot.add_cog(Whl(bot))
