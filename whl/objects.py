import asyncio
import re
from typing import List, Optional, Set

import discord
from discord.ext import commands

from core import logging

from .database import Channel, User

bot_log = logging.Bot.logger()


class WormholeMessage:
    __active_wormholes: Set[Channel] = set()

    @classmethod
    def refresh(cls):
        active_wormholes: Set[Channel] = set()

        for wormhole in Channel.get_all():
            if wormhole.active and wormhole.beam.active:
                active_wormholes.add(wormhole)

        cls.__active_wormholes = active_wormholes

    def __init__(self, bot: commands.Bot, message: discord.Message):
        self.bot = bot

        self.message = message
        self.wormhole = Channel.get(channel_id=message.channel.id)
        self.beam = self.wormhole.beam
        self.author = User.get(
            channel_id=self.wormhole.channel_id,
            user_id=message.author.id,
        )

        lines: List[str] = message.content.split("\n")
        for a in message.attachments:
            lines.append(a.url)
        self.content = "\n".join(lines)

        self.mentioned_users = self.get_mentioned_users()

        self.sent: Set[discord.Message] = set()

    def __repr__(self) -> str:
        return (
            f'<WormholeMessage author="{self.author}" wormhole="{self.wormhole}" '
            f' lines="{self.lines}">'
        )

    @property
    def valid(self) -> bool:
        return len(self.content) > 0

    @property
    def should_be_deleted(self) -> bool:
        return len(self.message.attachments) == 0

    def get_mentioned_users(self):
        tags: List[str] = re.findall(r"\(\(([^\(\)]*)\)\)", self.message.content)
        users = [User.get_by_name(beam=self.beam.name, name=tag) for tag in tags]
        return users

    def format(self, wormhole: Channel) -> str:
        content = self.content
        for user in self.mentioned_users:
            print(f" iterating: {user.dump()}")
            if user.channel_id == wormhole.channel_id:
                content = content.replace(f"(({user.name}))", f"<@!{user.user_id}>")
            else:
                content = content.replace(f"(({user.name}))", f"**__{user.name}__**")
        return content

    async def send(self):
        tasks = set()
        for wormhole in self.__active_wormholes:
            task = asyncio.ensure_future(
                self.send_to(wormhole),
            )
            tasks.add(task)
        await asyncio.gather(*tasks, return_exceptions=True)

        if not self.should_be_deleted:
            await self.message.add_reaction("✅")

    async def send_to(self, wormhole: Channel):
        channel = self.bot.get_channel(wormhole.channel_id)
        if channel is None:
            await bot_log(
                self.message.author,
                self.message.channel,
                f"Can't send to {wormhole.channel_id}.",
            )
            return
        formatted = self.format(wormhole)
        message = await channel.send(formatted)
        self.sent.add(message)
