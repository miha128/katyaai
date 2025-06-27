import discord
from discord import app_commands
import yaml
from utils import get_command_modules
import re

def italicize(text):
    original_lower = 'qwertyuiopasdfghjklzxcvbnm'
    original_upper = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    original_numbers = '0123456789'
    original = original_lower + original_upper + original_numbers  
    replacement = ''.join([
        chr(0x1D622 + (ord(c) - ord('a'))) if c.islower() 
        else chr(0x1D608 + (ord(c) - ord('A'))) if c.isupper() 
        else chr(0x1D7F6 + (ord(c) - ord('0'))) 
        for c in original
    ])
    translation_table = str.maketrans(original, replacement)
    return text.translate(translation_table)
    
def italicize_random(text, italic_prob=1, bold_prob=0.5):
    original_lower = 'abcdefghijklmnopqrstuvwxyz'
    original_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    original_numbers = '0123456789'
    original = original_lower + original_upper + original_numbers
    italic_replacement = ''.join([
    chr(0x1D622 + (ord(c) - ord('a'))) if c.islower() else
    chr(0x1D608 + (ord(c) - ord('A'))) if c.isupper() else
    chr(0x1D7E2 + (ord(c) - ord('0')))
    for c in original
    ])
    bold_italic_replacement = ''.join([
    chr(0x1D656 + (ord(c) - ord('a'))) if c.islower() else
    chr(0x1D63C + (ord(c) - ord('A'))) if c.isupper() else
    chr(0x1D7CE + (ord(c) - ord('0')))
    for c in original
    ])
    italic_trans = str.maketrans(original, italic_replacement)
    bold_italic_trans = str.maketrans(original, bold_italic_replacement)
    tokens = re.findall(r'\S+|\n', text)  
    processed_tokens = []
    for token in tokens:
        match = re.match(r'^(\w[\w\']*)(\W*)$', token)
        if not match:
            processed_tokens.append(token)
            continue
        word_part, suffix = match.groups()
        rand = random.random()
        if rand < bold_prob:
            styled_word = word_part.translate(bold_italic_trans)
        elif rand < bold_prob + italic_prob:
            styled_word = word_part.translate(italic_trans)
        else:
            styled_word = word_part
        processed_token = styled_word + suffix
        processed_tokens.append(processed_token)

    return ' '.join(processed_tokens)

async def setup(bot):
    @app_commands.command(
        name="italicize",
        description="Italicize text"
    )
    @app_commands.describe(
        text="Text to italicize",
        style="Choose how the text should be italicized"
    )
    @app_commands.choices(style=[
        app_commands.Choice(name="Everything", value="normal"),
        app_commands.Choice(name="Random", value="random"),
    ])
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def italicize_command(
        interaction: discord.Interaction,
        text: str,
        style: app_commands.Choice[str]
    ):
        await interaction.response.defer()

        try:
            if style.value == "random":
                response = italicize_random(text)[:2000]
            else:
                response = italicize(text)[:2000]

            await interaction.followup.send(response)
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")

    bot.tree.add_command(italicize_command)
