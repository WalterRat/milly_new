import sqlite3
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from utils import db_settings

DB = 'roles.db'


def channel_allowed():
    """Администраторы могут использовать команду везде, остальные — только в разрешённых каналах."""
    def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        return interaction.channel_id in db_settings.allowed_channels
    return app_commands.check(predicate)


class Roles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description='Разрешить боту принимать команды в канале')
    @app_commands.describe(channel='Канал, в котором бот будет отвечать на команды')
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def alloch(self, interaction: discord.Interaction, channel: discord.TextChannel):
        conn = sqlite3.connect(DB)
        conn.execute('INSERT OR IGNORE INTO Channels (channel_id) VALUES (?)', (channel.id,))
        conn.commit()
        db_settings.allowed_channels = [row[0] for row in conn.execute('SELECT channel_id FROM Channels')]
        conn.close()
        await interaction.response.send_message('Канал добавлен в список: ' + channel.mention)

    @app_commands.command(description='Запретить боту принимать команды в канале')
    @app_commands.describe(channel='Канал, который нужно убрать из списка')
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def disalloch(self, interaction: discord.Interaction, channel: discord.TextChannel):
        conn = sqlite3.connect(DB)
        conn.execute('DELETE FROM Channels WHERE channel_id = ?', (channel.id,))
        conn.commit()
        db_settings.allowed_channels = [row[0] for row in conn.execute('SELECT channel_id FROM Channels')]
        conn.close()
        await interaction.response.send_message('Канал удалён из списка: ' + channel.mention)

    @app_commands.command(description='Назначить участника мастером роли')
    @app_commands.describe(member='Кто станет мастером', role='Роль, которую он сможет выдавать')
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def givemaster(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        conn = sqlite3.connect(DB)
        conn.execute('INSERT OR REPLACE INTO Roles (master_id, role_id) VALUES (?, ?)', (member.id, role.id))
        conn.commit()
        conn.close()
        await interaction.response.send_message('Добавила в БД.')

    @app_commands.command(description='Снять с участника статус мастера')
    @app_commands.describe(member='Кого лишить статуса мастера')
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    async def rmmaster(self, interaction: discord.Interaction, member: discord.Member):
        conn = sqlite3.connect(DB)
        conn.execute('DELETE FROM Roles WHERE master_id = ?', (member.id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message('Удалила из БД.')

    @app_commands.command(description='Выдать участнику свою гостевую роль')
    @app_commands.describe(member='Кому выдать роль')
    @app_commands.guild_only()
    @channel_allowed()
    async def giverole(self, interaction: discord.Interaction, member: discord.Member):
        role = await self._master_role(interaction)
        if role is None:
            return
        await member.add_roles(role)
        await interaction.response.send_message('Гость выдан: ' + member.display_name)

    @app_commands.command(description='Забрать у участника свою гостевую роль')
    @app_commands.describe(member='У кого забрать роль')
    @app_commands.guild_only()
    @channel_allowed()
    async def rmrole(self, interaction: discord.Interaction, member: discord.Member):
        role = await self._master_role(interaction)
        if role is None:
            return
        await member.remove_roles(role)
        await interaction.response.send_message('Гость у ' + member.display_name + ' удалён.')

    async def _master_role(self, interaction: discord.Interaction) -> Optional[discord.Role]:
        """Роль, закреплённая за мастером. Если её нет, отвечает пользователю и возвращает None."""
        conn = sqlite3.connect(DB)
        row = conn.execute('SELECT role_id FROM Roles WHERE master_id = ?', (interaction.user.id,)).fetchone()
        conn.close()
        if row is None:
            await interaction.response.send_message('Нет доступа.', ephemeral=True)
            return None
        role = interaction.guild.get_role(row[0])
        if role is None:
            await interaction.response.send_message('Роль из настроек больше не существует.', ephemeral=True)
        return role
