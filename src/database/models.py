"""
Database Models for Hear! Hear! Bot
Author: aldinn
Email: kferdoush617@gmail.com
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ReactionRoleConfig:
    """Configuration for reaction role messages"""

    message_id: int
    channel_id: int
    guild_id: int
    title: str
    description: str
    mode: str  # unique, verify, reversed, binding, temporary
    self_destruct: Optional[int] = None  # seconds until message self-destructs
    blacklist_roles: List[int] = None  # roles that can't use this reaction role
    whitelist_roles: List[int] = None  # only these roles can use this reaction role
    created_at: datetime = None
    created_by: int = None

    def __post_init__(self):
        if self.blacklist_roles is None:
            self.blacklist_roles = []
        if self.whitelist_roles is None:
            self.whitelist_roles = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class ReactionRole:
    """Individual reaction-role mapping"""

    message_id: int
    emoji: str  # Can be unicode or custom emoji ID
    role_id: int
    role_name: str
    description: Optional[str] = None
    max_uses: Optional[int] = None  # Max number of people who can have this role
    current_uses: int = 0


@dataclass
class ModerationLog:
    """Moderation action log entry"""

    guild_id: int
    user_id: int
    moderator_id: int
    action: str  # ban, kick, mute, warn, etc.
    reason: str
    duration: Optional[int] = None  # seconds, for timed actions
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    case_id: Optional[str] = None  # unique case identifier

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class StickyRole:
    """Roles that persist when a user leaves and rejoins"""

    guild_id: int
    user_id: int
    role_ids: List[int]
    added_at: datetime = None

    def __post_init__(self):
        if self.added_at is None:
            self.added_at = datetime.utcnow()


@dataclass
class LoggingConfig:
    """Configuration for server logging"""

    guild_id: int
    message_logs_channel: Optional[int] = None
    member_logs_channel: Optional[int] = None
    server_logs_channel: Optional[int] = None
    moderation_logs_channel: Optional[int] = None
    join_leave_channel: Optional[int] = None
    invite_tracking: bool = False
    ignored_channels: List[int] = None
    ignored_users: List[int] = None
    ignored_prefixes: List[str] = None

    def __post_init__(self):
        if self.ignored_channels is None:
            self.ignored_channels = []
        if self.ignored_users is None:
            self.ignored_users = []
        if self.ignored_prefixes is None:
            self.ignored_prefixes = []


@dataclass
class GuildConfig:
    """Per-guild bot configuration"""

    guild_id: int
    prefix: List[str] = None
    language: str = "english"
    timezone: str = "UTC"
    mute_role_id: Optional[int] = None
    drama_channel_id: Optional[int] = None
    welcome_channel_id: Optional[int] = None
    farewell_channel_id: Optional[int] = None
    autorole_ids: List[int] = None

    def __post_init__(self):
        if self.prefix is None:
            self.prefix = [".", "?"]
        if self.autorole_ids is None:
            self.autorole_ids = []


@dataclass
class TemporaryRole:
    """Temporary role assignments"""

    guild_id: int
    user_id: int
    role_id: int
    expires_at: datetime
    assigned_by: int
    reason: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


# Database collection names
COLLECTIONS = {
    "reaction_roles": "reaction_roles",
    "reaction_role_configs": "reaction_role_configs",
    "moderation_logs": "moderation_logs",
    "sticky_roles": "sticky_roles",
    "logging_configs": "logging_configs",
    "guild_configs": "guild_configs",
    "temporary_roles": "temporary_roles",
    "infractions": "infractions",  # User infraction history
    "automod_rules": "automod_rules",  # Automated moderation rules
}
