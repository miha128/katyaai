import discord
from discord import app_commands
import yaml
from utils import get_command_modules

def transform(text):
    MARKER = "👁️"  # Eye emoji marker (2 characters: U+1F441 and U+FE0F)
    
    # Check if text starts and ends with the marker and has sufficient length
    if len(text) >= 4 and text.startswith(MARKER) and text.endswith(MARKER):
        # Decode mode
        inner_text = text[2:-2]
        decoded_chars = []
        for c in inner_text:
            code = ord(c)
            if 0xE0000 < code < 0xE007F:
                decoded_chars.append(chr(code - 0xE0000))
            else:
                decoded_chars.append(c)
        return ''.join(decoded_chars)
    else:
        # Encode mode
        encoded_chars = []
        for c in text:
            code = ord(c)
            if 0 < code < 0x7F:
                encoded_chars.append(chr(code + 0xE0000))
            else:
                encoded_chars.append(c)
        return MARKER + ''.join(encoded_chars) + MARKER

async def setup(bot):
    @app_commands.command(name="eye", description="Second-Sight 👁")
    @app_commands.describe(msg="Text to encode/decode")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def eye(interaction: discord.Interaction, msg: str):
        try:
                await interaction.response.send_message(
                    f"{transform(msg)}",
                )
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}")
    bot.tree.add_command(eye)
