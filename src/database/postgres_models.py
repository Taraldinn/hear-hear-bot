"""
PostgreSQL Database Models for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com

SQLAlchemy models for PostgreSQL database backend.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    BigInteger,
    JSON,
    ForeignKey,
    Index,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ReactionRoleModeEnum(enum.Enum):
    """Enum for reaction role modes"""

    unique = "unique"
    verify = "verify"
    reversed = "reversed"
    binding = "binding"
    temporary = "temporary"


class Guild(Base):
    """Guild/Server configuration"""

    __tablename__ = "guilds"

    id = Column(BigInteger, primary_key=True)  # Discord guild ID
    name = Column(String(100), nullable=False)
    prefix = Column(String(10), default="!", nullable=False)
    language = Column(String(5), default="en", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)

    # Feature toggles
    moderation_enabled = Column(Boolean, default=True)
    logging_enabled = Column(Boolean, default=True)
    timer_enabled = Column(Boolean, default=True)
    reaction_roles_enabled = Column(Boolean, default=True)

    # Moderation settings
    mod_log_channel = Column(BigInteger, nullable=True)
    automod_enabled = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reaction_role_configs = relationship("ReactionRoleConfig", back_populates="guild")
    user_settings = relationship("UserSetting", back_populates="guild")
    timers = relationship("Timer", back_populates="guild")

    __table_args__ = (Index("idx_guild_name", "name"),)


class User(Base):
    """User data across all guilds"""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # Discord user ID
    username = Column(String(32), nullable=False)
    discriminator = Column(String(4), nullable=False)
    global_name = Column(String(32), nullable=True)

    # User preferences
    language = Column(String(5), default="en")
    timezone = Column(String(50), default="UTC")

    # Stats
    commands_used = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    guild_settings = relationship("UserSetting", back_populates="user")

    __table_args__ = (
        Index("idx_user_username", "username"),
        Index("idx_user_last_seen", "last_seen"),
    )


class UserSetting(Base):
    """User settings per guild"""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    guild_id = Column(BigInteger, ForeignKey("guilds.id"), nullable=False)

    # Per-guild user settings
    notifications_enabled = Column(Boolean, default=True)
    language_override = Column(String(5), nullable=True)  # Override global language

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="guild_settings")
    guild = relationship("Guild", back_populates="user_settings")

    __table_args__ = (Index("idx_user_guild", "user_id", "guild_id", unique=True),)


class ReactionRoleConfig(Base):
    """Configuration for reaction role messages"""

    __tablename__ = "reaction_role_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, nullable=False, unique=True)
    channel_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, ForeignKey("guilds.id"), nullable=False)

    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    mode = Column(Enum(ReactionRoleModeEnum), default=ReactionRoleModeEnum.unique)

    # Optional settings
    self_destruct = Column(
        Integer, nullable=True
    )  # seconds until message self-destructs
    blacklist_roles = Column(
        JSON, default=list
    )  # roles that can't use this reaction role
    whitelist_roles = Column(
        JSON, default=list
    )  # only these roles can use this reaction role

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    guild = relationship("Guild", back_populates="reaction_role_configs")
    reaction_roles = relationship("ReactionRole", back_populates="config")

    __table_args__ = (
        Index("idx_rr_config_message", "message_id"),
        Index("idx_rr_config_guild", "guild_id"),
        Index("idx_rr_config_channel", "channel_id"),
    )


class ReactionRole(Base):
    """Individual reaction-role mapping"""

    __tablename__ = "reaction_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(Integer, ForeignKey("reaction_role_configs.id"), nullable=False)
    message_id = Column(BigInteger, nullable=False)

    emoji = Column(String(100), nullable=False)  # Unicode or custom emoji ID
    role_id = Column(BigInteger, nullable=False)
    role_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Usage tracking
    max_uses = Column(
        Integer, nullable=True
    )  # Max number of people who can have this role
    current_uses = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    config = relationship("ReactionRoleConfig", back_populates="reaction_roles")

    __table_args__ = (
        Index("idx_rr_message_emoji", "message_id", "emoji", unique=True),
        Index("idx_rr_role", "role_id"),
    )


class Timer(Base):
    """Timer information for debate rounds"""

    __tablename__ = "timers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.id"), nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=True)  # Timer display message

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Timer settings
    duration = Column(Integer, nullable=False)  # Total duration in seconds
    remaining = Column(Integer, nullable=False)  # Remaining time in seconds

    # Timer state
    is_active = Column(Boolean, default=False)
    is_paused = Column(Boolean, default=False)
    auto_next = Column(Boolean, default=False)

    # Timer timestamps
    started_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    guild = relationship("Guild", back_populates="timers")

    __table_args__ = (
        Index("idx_timer_guild", "guild_id"),
        Index("idx_timer_channel", "channel_id"),
        Index("idx_timer_active", "is_active"),
    )


class CommandLog(Base):
    """Log of command usage for analytics"""

    __tablename__ = "command_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Command info
    command_name = Column(String(50), nullable=False)
    command_type = Column(String(20), default="slash")  # slash, prefix, context

    # Discord info
    user_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=True)  # Can be null for DMs
    channel_id = Column(BigInteger, nullable=False)

    # Execution info
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Integer, nullable=True)  # milliseconds

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_cmd_log_command", "command_name"),
        Index("idx_cmd_log_user", "user_id"),
        Index("idx_cmd_log_guild", "guild_id"),
        Index("idx_cmd_log_timestamp", "timestamp"),
    )


class DebateSession(Base):
    """Debate session tracking"""

    __tablename__ = "debate_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)

    # Session info
    name = Column(String(100), nullable=False)
    format = Column(String(50), default="parliamentary")  # Format type
    status = Column(
        String(20), default="preparing"
    )  # preparing, active, paused, completed

    # Participants
    prop_team = Column(JSON, default=list)  # List of user IDs
    opp_team = Column(JSON, default=list)  # List of user IDs
    judges = Column(JSON, default=list)  # List of user IDs

    # Session settings
    prep_time = Column(Integer, default=900)  # 15 minutes prep
    speech_times = Column(JSON, default=dict)  # Speech duration settings

    # Session tracking
    current_round = Column(String(50), nullable=True)
    rounds_completed = Column(JSON, default=list)

    # Metadata
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_debate_guild", "guild_id"),
        Index("idx_debate_channel", "channel_id"),
        Index("idx_debate_status", "status"),
    )


# Database utility functions
async def create_tables(engine):
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine):
    """Drop all tables (use with caution!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Migration utilities
async def migrate_from_mongodb(mongo_db, postgres_session):
    """
    Migrate data from MongoDB to PostgreSQL

    Args:
        mongo_db: MongoDB database instance
        postgres_session: PostgreSQL session
    """
    # This would contain migration logic from MongoDB collections
    # to PostgreSQL tables - implementation would depend on existing data structure
    pass
