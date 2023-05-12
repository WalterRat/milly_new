import discord
import sqlite3
import re
from discord.ext import commands
from discord.ext.commands import TextChannelConverter
from utils import db_settings

class Roles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def alloch(self, ctx, *, channel_ids):
        channel_ids = re.split(r'[;,\n\s]\s*', channel_ids)
        conn = sqlite3.connect('roles.db')
        cursor = conn.cursor()
        feedback = ''
        for channel_id in channel_ids:
            channel = await TextChannelConverter().convert(ctx, channel_id)
            exists = cursor.execute("SELECT channel_id FROM Channels WHERE channel_id=?", (channel.id,)).fetchone()
            if exists == None or exists[0] == None:
                cursor.execute('INSERT INTO Channels (channel_id) VALUES (?)', (channel.id,))
            feedback += channel.mention + '\n'
        conn.commit()

        allowed_channels = cursor.execute('SELECT channel_id FROM Channels').fetchall()
        db_settings.allowed_channels = list(x[0] for x in allowed_channels)
        conn.close()
        await ctx.send('Эти каналы были добавлены в список: \n' + feedback)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def disalloch(self, ctx, *, channel_ids):
        channel_ids = re.split(r'[;,\n\s]\s*', channel_ids)
        conn = sqlite3.connect('roles.db')
        cursor = conn.cursor()
        feedback = ''
        for channel_id in channel_ids:
            channel = await TextChannelConverter().convert(ctx, channel_id)
            cursor.execute("DELETE FROM Channels WHERE channel_id = ?", (channel.id,))
            feedback += channel.mention + '\n'
        conn.commit()
        allowed_channels = cursor.execute('SELECT channel_id FROM Channels').fetchall()
        db_settings.allowed_channels = list(x[0] for x in allowed_channels)
        conn.close()
        await ctx.send('Эти каналы были удалены: \n' + feedback)



    @commands.command()
    @commands.has_permissions(administrator = True)
    async def givemaster(self, ctx, member: discord.Member, role: discord.Role):
        conn = sqlite3.connect('roles.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Roles (master_id, role_id) VALUES (?,?)', (member.id, role.id,))
        conn.commit()
        conn.close()
        await ctx.send('Добавила в БД.')


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rmmaster(self, ctx, member: discord.Member):
        conn = sqlite3.connect('roles.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Roles WHERE master_id = ?', (member.id,))
        conn.commit()
        conn.close()
        await ctx.send('Удалила из БД.')


    @commands.command()
    async def giverole(self, ctx, member: discord.Member):
        conn = sqlite3.connect('roles.db')
        cursor = conn.cursor()
        role_id = cursor.execute('SELECT role_id FROM Roles WHERE master_id = ?', (ctx.author.id,)).fetchone()
        conn.close()
        if role_id == None:
            await ctx.send('Нет доступа.')
            return
        role = ctx.guild.get_role(role_id[0])
        await member.add_roles(role)
        await ctx.send('Гость выдан: ' + member.display_name)


    @commands.command()
    async def rmrole(self, ctx, member: discord.Member):
        conn = sqlite3.connect('roles.db')
        cursor = conn.cursor()
        role_id = cursor.execute('SELECT role_id FROM Roles WHERE master_id = ?', (ctx.author.id,)).fetchone()
        conn.close()
        if role_id == None:
            await ctx.send('Нет доступа.')
            return
        role = ctx.guild.get_role(role_id[0])
        await member.remove_roles(role)
        await ctx.send('Гость у ' + member.display_name + ' удалён.')
