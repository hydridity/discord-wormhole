from typing import Union, List, Optional

import discord
from discord.ext import commands

from core import logging, utils

from ..whl.database import Beam, Channel

bot_log = logging.Bot.logger()


class WhlCnf(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="beam")
    async def beam_(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply(
                "list, add, activate, deactivate, delete, "
                "add-admin, delete-admin, block-user, unblock-user"
            )

    @beam_.command(name="list")
    async def beam_list(self, ctx):
        reply: List[str] = []
        for beam in Beam.get_all():
            reply.append(beam.__discord_str__())

        if len(reply):
            await ctx.reply("\n".join(reply))
        else:
            await ctx.reply("None yet!")

    @beam_.command(name="info")
    async def beam_info(self, ctx, name: str):
        beam = Beam.get(name=name)
        if beam is None:
            await ctx.reply("No such beam.")
            return

        channel_list: List[str] = list()
        for channel in beam.channels:
            dc_channel: Optional[discord.TextChannel]
            dc_channel = self.bot.get_channel(channel.channel_id)
            if dc_channel is not None:
                channel_list.append(
                    f"**#{dc_channel.name}**, {dc_channel.guild.name} "
                    f"({dc_channel.id})"
                )
            else:
                channel_list.append(f"Unavailable **{channel.channel_id}**")

        admin_list: List[str] = list()
        for user in beam.admins:
            dc_user: Optional[discord.User]
            dc_user = self.bot.get_user(user.user_id)
            if dc_user is not None:
                admin_list.append(f"**{dc_user.name}** ({dc_user.id})")
            else:
                admin_list.append(f"Unavailable *{user.user_id}*")

        banned_list: List[str] = list()
        for user in beam.banned:
            dc_user: Optional[discord.User]
            dc_user = self.bot.get_user(user.user_id)
            if dc_user is not None:
                banned_list.append(f"**{dc_user.name}** ({dc_user.id})")
            else:
                banned_list.append(f"Unavailable *{user.user_id}*")

        embed = utils.Discord.create_embed(
            author=ctx.author, title=beam.name, description="Beam information"
        )
        embed.add_field(
            name="Channels",
            value="\n".join(channel_list),
            inline=False,
        )
        if len(admin_list):
            embed.add_field(
                name="Admins",
                value="\n".join(admin_list),
            )
        if len(banned_list):
            embed.add_field(
                name="Banned",
                value="\n".join(banned_list),
            )
        await ctx.reply(embed=embed)

    @beam_.command(name="add")
    async def beam_add(self, ctx, name: str):
        beam = Beam.add(name=name, active=True)
        await ctx.reply(beam.__discord_str__())

    @beam_.command(name="activate")
    async def beam_activate(self, ctx, name: str):
        beam = Beam.get(name=name)
        if beam is None:
            await ctx.reply("No such beam.")
            return
        beam.active = True
        beam.save()
        await ctx.reply(beam.__discord_str__())

    @beam_.command(name="deactivate")
    async def beam_deactivate(self, ctx, name: str):
        beam = Beam.get(name=name)
        if beam is None:
            await ctx.reply("No such beam.")
            return
        beam.active = False
        beam.save()
        await ctx.reply(beam.__discord_str__())

    @beam_.command(name="delete")
    async def beam_delete(self, ctx, name: str):
        deleted = Beam.get(name=name).delete()
        await ctx.reply("Done." if deleted else "No such beam.")

    @beam_.command(name="add-admin")
    async def beam_add_admin(self, ctx, beam: str, user_id: Union[discord.User, int]):
        if type(user_id) is discord.User:
            user_id = user_id.id
        beam = Beam.get(name=beam)
        if beam is None:
            await ctx.repy("No such beam.")
            return

        if len(list(filter(lambda a: a.user_id == user_id, beam.admins))):
            await ctx.reply("This user is already an admin in the beam.")
            return

        beam.add_admin(user_id)
        beam.save()

        user_in_beam: bool = False
        for channel in beam.channels:
            if len(list(filter(lambda u: u.user_id == user_id, channel.users))):
                user_in_beam = True
                break

        reply = [f"User **{user_id}** has been added as admin."]
        if not user_in_beam:
            reply.append("They are not in any of registered channels, though.")
        await ctx.reply(" ".join(reply))

    @beam_.command(name="delete-admin")
    async def beam_delete_admin(
        self, ctx, beam: str, user_id: Union[discord.User, int]
    ):
        if type(user_id) is discord.User:
            user_id = user_id.id
        beam = Beam.get(name=beam)
        if beam is None:
            await ctx.repy("No such beam.")
            return

        deleted = beam.delete_admin(user_id)
        await ctx.reply("Done." if deleted else "This user is not an admin.")

    @beam_.command(name="block-user")
    async def beam_block_user(self, ctx, beam: str, user_id: Union[discord.User, int]):
        if type(user_id) is discord.User:
            user_id = user_id.id
        beam = Beam.get(name=beam)
        if beam is None:
            await ctx.repy("No such beam.")
            return

        if len(list(filter(lambda a: a.user_id == user_id, beam.admins))):
            await ctx.reply("This user is already blocked.")
            return

        beam.add_admin(user_id)
        beam.save()

        user_in_beam: bool = False
        for channel in beam.channels:
            if len(list(filter(lambda u: u.user_id == user_id, channel.users))):
                user_in_beam = True
                break

        reply = [f"User **{user_id}** has been blocked."]
        if not user_in_beam:
            reply.append("They are not in any of registered channels, though.")
        await ctx.reply(" ".join(reply))

    @beam_.command(name="unblock-user")
    async def beam_unblock_user(
        self, ctx, beam: str, user_id: Union[discord.User, int]
    ):
        if type(user_id) is discord.User:
            user_id = user_id.id
        beam = Beam.get(name=beam)
        if beam is None:
            await ctx.repy("No such beam.")
            return

        deleted = beam.delete_admin(user_id)
        await ctx.reply("Done." if deleted else "This user is not blocked.")

    @commands.group(name="channel")
    async def channel_(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply(
                "list, add, activate, deactivate, delete, add_admin, delete_admin"
            )

    @channel_.command(name="info")
    async def channel_info(self, ctx, channel_id: Union[discord.TextChannel, int]):
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id
        db_channel = Channel.get(channel_id=channel_id)
        if db_channel is None:
            await ctx.reply("No such channel.")
            return

        dc_channel = self.bot.get_channel(channel_id)

        admin_list: List[str] = list()
        for user in db_channel.admins:
            dc_user: Optional[discord.User]
            dc_user = self.bot.get_user(user.user_id)
            if dc_user is not None:
                admin_list.append(f"**{dc_user.name}** ({dc_user.id})")
            else:
                admin_list.append(f"Unavailable *{user.user_id}*")

        embed = utils.Discord.create_embed(
            author=ctx.author,
            title=dc_channel.name if dc_channel else f"{channel_id}",
            description="Channel information",
        )
        embed.add_field(
            name="Beam",
            value=db_channel.beam.name,
            inline=False,
        )
        embed.add_field(
            name="Message count",
            value=db_channel.messages,
            inline=False,
        )
        if len(admin_list):
            embed.add_field(
                name="Admins",
                value="\n".join(admin_list),
            )
        await ctx.reply(embed=embed)

    @channel_.command(name="list")
    async def channel_list(self, ctx, beam: str):
        beam = Beam.get(name=beam)
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

    @channel_.command(name="add")
    async def channel_add(
        self, ctx, beam: str, channel_id: Union[discord.TextChannel, int]
    ):
        if Beam.get(name=beam) is None:
            await ctx.reply("No such beam.")
            return
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id

        ch = Channel.add(beam=beam, channel_id=channel_id, active=True)
        await ctx.reply(ch.__discord_str__())

    @channel_.command(name="activate")
    async def channel_activate(self, ctx, channel_id: Union[discord.TextChannel, int]):
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id
        ch = Channel.get(channel_id=channel_id)
        if ch is None:
            await ctx.repy("No such channel.")
            return
        ch.active = True
        ch.save()
        await ctx.reply(ch.__discord_str__())

    @channel_.command(name="deactivate")
    async def channel_deactivate(
        self, ctx, channel_id: Union[discord.TextChannel, int]
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

    @channel_.command(name="delete")
    async def channel_delete(self, ctx, channel_id: Union[discord.TextChannel, int]):
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id
        deleted = Channel.delete(channel_id=channel_id)
        await ctx.reply("Done." if deleted else "No such channel.")

    @channel_.command(name="add-admin")
    async def channel_add_admin(
        self,
        ctx,
        channel_id: Union[discord.TextChannel, int],
        user_id: Union[discord.User, int],
    ):
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id
        ch = Channel.get(channel_id=channel_id)
        if ch is None:
            await ctx.repy("No such channel.")
            return
        if type(user_id) is discord.User:
            user_id = user_id.id

        if len(list(filter(lambda a: a.user_id == user_id, ch.admins))):
            await ctx.reply("This user is already an admin in the channel.")
            return

        ch.add_admin(user_id)
        ch.save()

        user_in_channel: bool = False
        if len(list(filter(lambda u: u.user_id == user_id, ch.users))):
            user_in_channel = True

        reply = [f"User **{user_id}** has been added as admin."]
        if not user_in_channel:
            reply.append("They are not registered to the channel, though.")
        await ctx.reply(" ".join(reply))

    @channel_.command(name="delete-admin")
    async def channel_delete_admin(
        self,
        ctx,
        channel_id: Union[discord.TextChannel, int],
        user_id: Union[discord.User, int],
    ):
        if type(channel_id) is discord.TextChannel:
            channel_id = channel_id.id
        ch = Channel.get(channel_id=channel_id)
        if ch is None:
            await ctx.repy("No such channel.")
            return
        if type(user_id) is discord.User:
            user_id = user_id.id

        deleted = ch.delete_admin(user_id)
        await ctx.reply("Done." if deleted else "This user is not an admin.")


def setup(bot) -> None:
    bot.add_cog(WhlCnf(bot))
