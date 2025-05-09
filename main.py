import discord
from discord import app_commands
from openai import AsyncOpenAI
from datetime import datetime as dt
from datetime import timedelta
import platform
import time
import re
import random
import os
import sys
import aiohttp

start_time = time.time()
message_count = 0
# bot token goes here
BOT_TOKEN = ""
COBALT_INSTANCE = ""
API_KEY = "none"  # if required, for cobalt

# change with your preferred openai compatible API
base_url = "http://localhost:1234/v1" # for example, here i used LM Studio's server
model = "granite-3.3-2b-instruct"
api_key = "API key here" # not needed for local LLM, just make sure it's not empty if you're using a local one or leave as default
command_name = "ask"
command_desc = "Ask the AI a question"

def tofullwidth(s):
    result = []
    for char in s:
        if char == ' ':
            # Replace space with full-width space (U+3000)
            result.append('\u3000')
        elif char == '.':
            # Replace period with full-width period (U+FF0E)
            result.append('\uFF0E')
        elif '!' <= char <= '~':
            # Convert ASCII characters to their full-width versions
            result.append(chr(ord(char) + 0xFEE0))
        else:
            # Keep other characters unchanged
            result.append(char)
    return ''.join(result)


def encode(text):
    encoded_chars = []
    for c in text:
        code = ord(c)
        if 0 < code < 0x7f:  # 0x7f is 127
            new_code = code + 0xe0000
        else:
            new_code = code
        encoded_chars.append(chr(new_code))
    return ''.join(encoded_chars)

def decode(text):
    decoded_chars = []
    for c in text:
        code = ord(c)
        if 0xe0000 < code < 0xe007f:  # 0xe007f is 917631
            new_code = code - 0xe0000
        else:
            new_code = code
        decoded_chars.append(chr(new_code))
    return ''.join(decoded_chars)


def randomitalicize(text, italic_prob=0.7, bold_prob=0.5):
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

    # Create translation tables
    italic_trans = str.maketrans(original, italic_replacement)
    bold_italic_trans = str.maketrans(original, bold_italic_replacement)

    # Split text into tokens (preserving punctuation with words)
    tokens = re.findall(r'\S+|\n', text)  # Split on whitespace but keep original tokens

    processed_tokens = []
    for token in tokens:
        # Split into word part and non-word suffix
        match = re.match(r'^(\w[\w\']*)(\W*)$', token)
        if not match:
            # No word part, keep as is
            processed_tokens.append(token)
            continue

        word_part, suffix = match.groups()
        # Determine style
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
    

def italicize(text):
    original_lower = 'qwertyuiopasdfghjklzxcvbnm'
    original_upper = 'QWERTYUIOPASDFGHJKLZXCVBNM'
    original_numbers = '0123456789'
    original = original_lower + original_upper + original_numbers  # Combine all

    # Generate replacements for lowercase, uppercase, and numbers
    replacement = ''.join([
        # Lowercase letters start at 0x1D622 (Mathematical Italic)
        chr(0x1D622 + (ord(c) - ord('a'))) if c.islower() 
        # Uppercase letters start at 0x1D608
        else chr(0x1D608 + (ord(c) - ord('A'))) if c.isupper() 
        # Numbers start at 0x1D7F6 (Mathematical Italic digits)
        else chr(0x1D7F6 + (ord(c) - ord('0'))) 
        for c in original
    ])

    # Create translation table and apply
    translation_table = str.maketrans(original, replacement)
    return text.translate(translation_table)

my_client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(my_client)
openai_client = AsyncOpenAI(base_url=base_url, api_key=api_key)

@tree.command(
    name="italicize",
    description="Italicize text"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(text="Text to italicize")
async def italicze(interaction: discord.Interaction, text: str):
    # ask discord for more time
    await interaction.response.defer()
    try:
        if text:
            response = italicize(text)[:2000]
        else:
            response = f"No text to italicize {interaction.user.mention}."
        await interaction.followup.send(response)
    except Exception as e:
        await interaction.followup.send(f"An error has occured: {str(e)}")

@tree.command(
    name="fullwidth",
    description="Convert text to fullwidth"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(text="Text to convert to fullwidth")
async def fw(interaction: discord.Interaction, text: str):
    # ask discord for more time
    await interaction.response.defer()
    try:
        if text:
            response = tofullwidth(text)[:2000]
        else:
            response = f"No text to italicize {interaction.user.mention}."
        await interaction.followup.send(response)
    except Exception as e:
        await interaction.followup.send(f"An error has occured: {str(e)}")


@tree.command(
    name="randomitalicize",
    description="Randomly italicizes text"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(text="Text to italicize")
async def ranitalicze(interaction: discord.Interaction, text: str):
    # ask discord for more time
    await interaction.response.defer()
    try:
        if text:
            response = randomitalicize(text)[:2000]
        else:
            response = f"No text to randomitalicize {interaction.user.mention}."
        await interaction.followup.send(response)
    except Exception as e:
        await interaction.followup.send(f"An error has occured: {str(e)}")


@tree.command(
    name="encode",
    description="Encode text in 3y3code"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(text="Text to encode")
async def encodee(interaction: discord.Interaction, text: str):
    # ask discord for more time
    await interaction.response.defer()
    try:
        if text:
            response = encode(text)[:2000]
        else:
            response = f"No text to encode {interaction.user.mention}."
        await interaction.followup.send(response)
    except Exception as e:
        await interaction.followup.send(f"An error has occured: {str(e)}")

@tree.command(
    name="decode",
    description="Decodes text in 3y3code"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(text="Text to decode")
async def decodee(interaction: discord.Interaction, text: str):
    # ask discord for more time
    await interaction.response.defer()
    try:
        if text:
            response = decode(text)[:2000]
        else:
            response = f"No text to encode {interaction.user.mention}."
        await interaction.followup.send(response)
    except Exception as e:
        await interaction.followup.send(f"An error has occured: {str(e)}")

@tree.command(
    name="info",
    description="Show statistics"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    
async def info(interaction: discord.Interaction):
    uptime_seconds = time.time() - start_time
    uptime_str = str(timedelta(seconds=uptime_seconds)).split(".")[0]
    #embed
    embed = discord.Embed(
        title= f"Statistics (system time: {dt.now().strftime('%B %d %Y')}):",
        color=discord.Color.blue()
    )
    embed.set_author(name="GitHub",
                 url="https://github.com/miha128/katyaai",
                 icon_url="https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png")
                 
    embed.add_field(
        name="Server",
        value=f"**Endpoint:** <{base_url}> \n"
              f"**Model:** {model}",
        inline=False
    )
    
    embed.add_field(
        name="System info",
        value=f"**OS:** {platform.system()} {os.name} {sys.platform} {platform.release()} {platform.version()}\n"
              f"**Misc:** {platform.architecture()} {platform.machine()} {platform.node()} {platform.processor()}\n"
              f"**Python:** {platform.python_version()} {platform.python_build()} {platform.python_compiler()} {platform.python_branch()} {platform.python_implementation()}",
        inline=False
    )
    
    embed.add_field(
        name="Statistics",
        value=f"**Uptime:** {uptime_str}\n"
              f"**Messages Processed:** {message_count}",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)
    
@tree.command(
    name=command_name,
    description=command_desc
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(prompt="Prompt to send to the AI")
async def interaction(interaction: discord.Interaction, prompt: str):
    # ask discord for more time
    await interaction.response.defer()
    global message_count
    message_count += 1
    # for openai refer to their docs
    try:
        if prompt:
            print(f'Query: {prompt} Asked by: {interaction.user.name} Total messages: {message_count}')
            fullprompt = f"Today's date: {dt.now().strftime('%B %d %Y')}. You are currently roleplaying as a helpful robot which will respond to a user's query. Keep your answers short. Be clear and concise. The user's query is: " + prompt
            chat_completion = await openai_client.chat.completions.create(
                messages=[{"role": "user", "content": fullprompt}],
                model=model
            )
            ai_response = chat_completion.choices[0].message.content
            response = f"{ai_response}"[:2000]
        else:
            response = f"You haven't asked me anything {interaction.user.mention}."
            
        # send the response after
        response = italicize(response)
        await interaction.followup.send(response)
    except Exception as e:
        await interaction.followup.send(f"An error has occured: {str(e)}")

@tree.command(
    name="askplain",
    description="Answer in plaintext format"
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(prompt="Prompt to send to the AI")
async def interaction(interaction: discord.Interaction, prompt: str):
    # ask discord for more time
    await interaction.response.defer()
    global message_count
    message_count += 1
    # for openai refer to their docs
    try:
        if prompt:
            print(f'Query: {prompt} Asked by: {interaction.user.name} Total messages: {message_count}')
            fullprompt = f"Today's date: {dt.now().strftime('%B %d %Y')}. You are currently roleplaying as a helpful robot which will respond to a user's query. Keep your answers short. Be clear and concise. The user's query is: " + prompt
            chat_completion = await openai_client.chat.completions.create(
                messages=[{"role": "user", "content": fullprompt}],
                model=model
            )
            ai_response = chat_completion.choices[0].message.content
            response = f"{ai_response}"[:2000]
        else:
            response = f"You haven't asked me anything {interaction.user.mention}."
            
        # send the response after
        await interaction.followup.send(response)
    except Exception as e:
        await interaction.followup.send(f"An error has occured: {str(e)}")
        
@tree.command(
    name="cobalt",
    description="Download a video using KatyaAI's own processing instance."
)
@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(url="currently supported: bilibili, bluesky, dailymotion, facebook, instagram, loom, ok, pinterest, reddit, rutube, snapchat, soundcloud, streamable, tiktok, tumblr, twitch, twitter, vimeo, vk, xiaohongshu, youtube")
async def cobalt_command(interaction: discord.Interaction, url: str):
    await interaction.response.defer()
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    
    if API_KEY:
        headers["Authorization"] = f"Api-Key {API_KEY}"
    
    payload = {
        "url": url,
        "videoQuality": "480",
        "downloadMode": "auto",
        "youtubeVideoCodec": "h264"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                COBALT_INSTANCE,
                headers=headers,
                json=payload
            ) as response:
                data = await response.json()
                
                if data.get('status') in ['redirect', 'tunnel']:
                    await interaction.followup.send(f"[Download]({data['url']})")
                elif data.get('status') == 'picker':
                    items = "\n".join([f"{item['type']}: {item['url']}" for item in data['picker'][:3]])
                    await interaction.followup.send(
                        f"Multiple media options found. First 3 items:\n{items}"
                    )
                elif data.get('status') == 'error':
                    error_msg = data.get('error', {}).get('code', 'Unknown error')
                    await interaction.followup.send(f"Error: {error_msg}")
                else:
                    await interaction.followup.send("Unexpected response from API")
                    
    except aiohttp.ClientError as e:
        await interaction.followup.send(f"Network error: {str(e)}")
    except json.JSONDecodeError:
        await interaction.followup.send("Invalid response from API server")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")
        
@my_client.event 
async def on_ready():
    print(f'\n\nBOT URL: https://discord.com/oauth2/authorize?client_id={my_client.user.id}&integration_type=1&scope=applications.commands\n\n')
    print(f'Logged in as {my_client.user} (ID: {my_client.user.id})')
    print('------')
    await tree.sync()

if __name__ == "__main__":
    my_client.run(BOT_TOKEN)
