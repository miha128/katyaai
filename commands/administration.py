import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

class DisableCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="disable", description="Disables a slash command by name.")
    @app_commands.describe(command_name="The name of the command to disable")
    async def disable(self, interaction: discord.Interaction, command_name: str):
        command = self.bot.tree.get_command(command_name)
        if command is None:
            await interaction.response.send_message(f"Command `{command_name}` not found.", ephemeral=True)
            return

        self.bot.tree.remove_command(command.name)
        await interaction.response.send_message(f"Command `{command.name}` has been disabled.", ephemeral=True)

    @app_commands.command(name="enable", description="Re-enables a previously disabled command by name.")
    @app_commands.describe(command_name="The name of the command to enable")
    async def enable(self, interaction: discord.Interaction, command_name: str):
        # Force re-syncing the module to re-register the command
        modules = [ext for ext in self.bot.extensions if ext.endswith(command_name)]
        if not modules:
            await interaction.response.send_message(f"No loaded module found ending with `{command_name}`.", ephemeral=True)
            return

        try:
            for module in modules:
                await self.bot.reload_extension(module)
            await interaction.response.send_message(f"Re-enabled `{command_name}`.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error reloading `{command_name}`: {e}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(DisableCommand(bot))