from __future__ import annotations
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from database import database, session


class Beam(database.base):
    __tablename__ = "wormhole_beams"

    name = Column(String, primary_key=True)
    active = Column(Boolean)
    channels = relationship("Channel")
    admins = relationship("BeamAdmin")
    banned = relationship("BeamBanned")

    def __repr__(self) -> str:
        return f'<Beam name="{self.name}" active="{self.active}">'

    def __discord_str__(self) -> str:
        activity = "active" if self.active else "inactive"
        return (
            f"Beam **{self.name}** ({activity}) with "
            f"**{len(self.channels)}** channels, "
            f"**{len(self.admins)}** admins and **{len(self.banned)}** banned users."
        )

    def dump(self) -> dict:
        return {
            "name": self.name,
            "active": self.active,
            "channels": [c.dump() for c in self.channels],
            "admins": [a.user_id for a in self.admins],
            "banned": [b.user_id for b in self.banned],
        }

    @staticmethod
    def add(*, name: str, active: bool) -> Beam:
        beam = Beam(name=name, active=active)
        session.add(beam)
        return beam.save()

    @staticmethod
    def get(*, name: str) -> Optional[Beam]:
        beam = session.query(Beam).filter_by(name=name).one_or_none()
        return beam

    @staticmethod
    def get_all() -> List[Beam]:
        beams = session.query(Beam).all()
        return beams

    def save(self) -> Beam:
        session.commit()
        return self

    def delete(self) -> bool:
        num = session.query(Beam).filter_by(name=self.name).delete()
        session.commit()
        return num > 0

    def add_admin(self, user_id: int) -> Beam:
        admin = BeamAdmin(beam_name=self.name, user_id=user_id)
        if admin not in self.admins:
            self.admins.append(admin)
        self.save()
        return self

    def delete_admin(self, user_id: int) -> bool:
        num = (
            session.query(BeamAdmin)
            .filter_by(beam_name=self.name, user_id=user_id)
            .delete()
        )
        return num > 0


class Channel(database.base):
    __tablename__ = "wormhole_channels"

    channel_id = Column(BigInteger, primary_key=True)
    active = Column(Boolean)
    beam_name = Column(String, ForeignKey("wormhole_beams.name"))
    beam = relationship("Beam", back_populates="channels")
    users = relationship("User")
    admins = relationship("ChannelAdmin")
    messages = Column(Integer, default=0)

    def __repr__(self) -> str:
        return (
            f'<Channel channel_id="{self.chanel_id}" active="{self.active}" '
            f'beam_name="{self.beam_name}" messages="{self.messages}">'
        )

    def __discord_str__(self) -> str:
        return (
            f"Channel in beam **{self.beam_name}** with "
            f"**{len(self.users)}** users and **{len(self.admins)}** admins. "
            f"**{self.messages}** messages."
        )

    def dump(self) -> dict:
        return {
            "channel_id": self.channel_id,
            "active": self.active,
            "beam_name": self.beam_name,
            "admins": [a.user_id for a in self.admins],
            "messages": self.messages,
        }

    @staticmethod
    def add(*, beam: str, channel_id: int, active: bool) -> Channel:
        beam = Beam.get(name=beam)
        if beam is None:
            raise ValueError("No such beam.")

        channel = Channel(channel_id=channel_id, active=active)
        beam.channels.append(channel)
        channel.save()
        return channel

    @staticmethod
    def get(*, channel_id: int) -> Optional[Channel]:
        channel = session.query(Channel).filter_by(channel_id=channel_id).one_or_none()
        return channel

    def save(self) -> Channel:
        session.commit()
        return self

    def delete(self) -> bool:
        num = session.query(Channel).filter_by(channel_id=self.channel_id).delete()
        session.commit()
        return num > 0

    def add_admin(self, user_id: int) -> Beam:
        admin = ChannelAdmin(channel_id=self.channel_id, user_id=user_id)
        if admin not in self.admins:
            self.admins.append(admin)
        self.save()
        return self

    def delete_admin(self, user_id: int) -> bool:
        num = (
            session.query(ChannelAdmin)
            .filter_by(channel_id=self.channel_id, user_id=user_id)
            .delete()
        )
        return num > 0


class User(database.base):
    __tablename__ = "wormhole_users"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    channel_id = Column(BigInteger, ForeignKey("wormhole_channels.channel_id"))
    channel = relationship("Channel", back_populates="users")
    name = Column(String)

    def __repr__(self) -> str:
        return (
            f'<User idx="{self.idx}" user_id="{self.user_id}" '
            f'channel_id="{self.channel_id}" name="{self.name}">'
        )

    def __discord_str__(self) -> str:
        return f"User **{self.name}** in beam **{self.channel.beam.name}**."

    def dump(self) -> dict:
        return {
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "name": self.name,
        }

    @staticmethod
    def add(*, channel_id: int, user_id: int, name: str) -> User:
        channel = Channel.get(channel_id)
        if channel is None:
            raise ValueError("No such channel.")

        user = User(user_id=user_id, name=name)
        channel.users.append(user)
        user.save()
        return user

    @staticmethod
    def get(*, channel_id: int, user_id: int) -> Optional[User]:
        user = (
            session.query(User)
            .filter_by(user_id=user_id, channel_id=channel_id)
            .one_or_none()
        )
        return user

    def save(self) -> User:
        session.commit()
        return self

    def delete(self) -> bool:
        num = (
            session.query(User)
            .filter_by(user_id=self.user_id, channel_id=self.channel_id)
            .delete()
        )
        session.commit()
        return num > 0


class BeamAdmin(database.base):
    __tablename__ = "wormhole_beam_admins"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    beam_name = Column(String, ForeignKey("wormhole_beams.name"))
    user_id = Column(BigInteger)

    def __eq__(self, obj) -> bool:
        return (
            type(self) is type(obj)
            and self.beam_name == obj.beam_name
            and self.user_id == obj.user_id
        )

    def dump(self) -> dict:
        return {
            "beam_name": self.beam_name,
            "user_id": self.user_id,
        }


class BeamBanned(database.base):
    __tablename__ = "wormhole_beam_banned"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    beam_name = Column(String, ForeignKey("wormhole_beams.name"))
    user_id = Column(BigInteger)

    def __eq__(self, obj) -> bool:
        return (
            type(self) is type(obj)
            and self.beam_name == obj.beam_name
            and self.user_id == obj.user_id
        )

    def dump(self) -> dict:
        return {
            "beam_name": self.beam_name,
            "user_id": self.user_id,
        }


class ChannelAdmin(database.base):
    __tablename__ = "wormhole_channel_admins"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(BigInteger, ForeignKey("wormhole_channels.channel_id"))
    user_id = Column(BigInteger)

    def __eq__(self, obj) -> bool:
        return (
            type(self) is type(obj)
            and self.channel_id == obj.channel_id
            and self.user_id == obj.user_id
        )

    def dump(self) -> dict:
        return {
            "channel_id": self.channel_id,
            "user_id": self.user_id,
        }
