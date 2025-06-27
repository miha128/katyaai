import discord
from discord import app_commands
import yaml
from utils import get_command_modules
import re 

def tofullwidth(s):
    result = []
    for char in s:
        if char == ' ':
            result.append('\u3000')
        elif char == '.':
            result.append('\uFF0E')
        elif '!' <= char <= '~':
            result.append(chr(ord(char) + 0xFEE0))
        else:
            result.append(char)
    return ''.join(result)

async def setup(bot):
    @app_commands.command(
        name="fullwidth",
        description="Converts text into fullwidth"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def restart_command(interaction: discord.Interaction, text: str):
        await interaction.response.defer()
        try:
            if text:
                response = tofullwidth(text)[:2000]
            else:
                response = f"No text to italicize {interaction.user.mention}."
            await interaction.followup.send(response)
        except Exception as e:
            await interaction.followup.send(f"An error has occured: {str(e)}")
    bot.tree.add_command(restart_command)
