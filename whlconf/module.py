from typing import Union, List

import discord
from discord.ext import commands

from core import logging

from ..whl.database import Beam, Channel

bot_log = logging.Bot.logger()


class WhlCnf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="beam")
    async def beam(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply(
                "list, add, activate, deactivate, delete, "
                "add_admin, delete_admin, block_user, unblock_user"
            )

    @beam.command(name="list")
    async def beam_list(self, ctx):
        reply: List[str] = []
        for beam in Beam.get_all():
            reply.append(beam.__discord_str__())

        if len(reply):
            await ctx.reply("\n".join(reply))
        else:
            await ctx.reply("None yet!")

    @beam.command(name="add")
    async def beam_add(self, ctx, name: str):
        beam = Beam.add(name=name, active=True)
        await ctx.reply(beam.__discord_str__())

    @beam.command(name="activate")
    async def beam_activate(self, ctx, name: str):
        beam = Beam.get(name=name)
        if beam is None:
            await ctx.reply("No such beam.")
            return
        beam.active = True
        beam.save()
        await ctx.reply(beam.__discord_str__())

    @beam.command(name="deactivate")
    async def beam_deactivate(self, ctx, name: str):
        beam = Beam.get(name=name)
        if beam is None:
            await ctx.reply("No such beam.")
            return
        beam.active = False
        beam.save()
        await ctx.reply(beam.__discord_str__())

    @beam.command(name="delete")
    async def beam_delete(self, ctx, name: str):
        deleted = Beam.get(name=name).delete()
        await ctx.reply("Done." if deleted else "No such beam.")

    @beam.command(name="add-admin")
    async def beam_add_admin(self, ctx, uid: Union[discord.User, int]):
        if type(uid) is discord.User:
            uid = uid.id

    # TODO add_admin, delete_admin, block_user, unblock_user

    @commands.group(name="channel")
    async def channel(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply(
                "list, add, activate, deactivate, delete, add_admin, delete_admin"
            )

    @channel.command(name="list")
    async def channel_list(self, ctx, beam_name: str):
        beam = Beam.get(name=beam_name)
        if beam is None:
            await ctx.reply("No such beam.")
            return
        reply: List[str] = []
        for channel in beam.channels:
            reply.append(channel.__discord_str__())
        if len(reply):
            await ctx.reply("\n".join(reply))
        else:
            await ctx.reply("None yet!")

    @channel.command(name="add")
    async def channel_add(
        self, ctx, beam_name: str, channel_id: Union[discord.TextChannel, int]
    ):
        if Beam.get(name=beam_name) is None:
            await ctx.reply("No such beam.")
            return
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id

        ch = Channel.add(beam_name=beam_name, channel_id=channel_id, active=True)
        await ctx.reply(ch.__discord_str__())

    @channel.command(name="activate")
    async def channel_activate(
        self, ctx, beam_name: str, channel_id: Union[discord.TextChannel, int]
    ):
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id
        ch = Channel.get(channel_id=channel_id)
        if ch is None:
            await ctx.repy("No such channel.")
            return
        ch.active = True
        ch.save()
        await ctx.reply(ch.__discord_str__())

    @channel.command(name="deactivate")
    async def channel_deactivate(
        self, ctx, beam_name: str, channel_id: Union[discord.TextChannel, int]
    ):
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id
        ch = Channel.get(channel_id=channel_id)
        if ch is None:
            await ctx.repy("No such channel.")
            return
        ch.active = False
        ch.save()
        await ctx.reply(ch.__discord_str__())

    @channel.command(name="delete")
    async def channel_delete(
        self, ctx, beam_name: str, channel_id: Union[discord.TextChannel, int]
    ):
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id
        deleted = Channel.delete(channel_id=channel_id)
        await ctx.reply("Done." if deleted else "No such channel.")

    # TODO add_admin, delete_admin


def setup(bot) -> None:
    bot.add_cog(WhlCnf(bot))
