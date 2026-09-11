import discord
from discord import app_commands
from discord.ext import commands
from cogs import manage_roles


class Milly(commands.Bot):
    def __init__(self):
        # Только стандартные intents: slash-командам не нужен ни Message Content,
        # ни Server Members, ни Presence.
        intents = discord.Intents.default()
        super().__init__(command_prefix=commands.when_mentioned, intents=intents, help_command=None)

    async def setup_hook(self):
        await self.add_cog(manage_roles.Roles(self))
        # Регистрирует slash-команды глобально. После первого запуска
        # Discord может показывать их до часа.
        await self.tree.sync()


client = Milly()


@client.event
async def on_ready():
    print('I`m ready')


@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        message = 'Нет доступа.'
    else:
        message = 'Что-то пошло не так.'
        command = interaction.command.name if interaction.command else '?'
        print(f'Ошибка в /{command}: {error!r}')
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


client.run('token')
