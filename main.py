import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument
from cogs import manage_roles
from utils import db_settings


intents = discord.Intents.default()
client = commands.Bot(commands.when_mentioned_or('m?'), intents = intents, case_insensitive = True)
#client.remove_command('help')
client.add_cog(manage_roles.Roles(client))

@client.event
async def on_ready():
    print('I`m ready')

@client.event
async def on_message(message):
    if message.author.guild_permissions.administrator:
        await client.process_commands(message)

    elif message.channel.id in db_settings.allowed_channels:
        await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send_help(ctx.command)
    else:
        pass

client.run('token')

