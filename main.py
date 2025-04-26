import discord
from discord import app_commands
from openai import AsyncOpenAI
from datetime import datetime as dt
from datetime import timedelta
import platform
import time

start_time = time.time()
message_count = 0

BOT_TOKEN = "MTM.."

command_name = "ask"
command_desc = "Ask the AI a question"

# change with your preferred openai compatible API
base_url = "http://localhost:1234/v1" # for example, here i used LM Studio's server
model = "motoreta"
api_key = "API key here"

beforeprompt = f"Today's date: {dt.now().strftime('%B %d %Y')}. You are currently roleplaying as a helpful robot which will respond to a user's query. Keep your answers short. Be clear and concise. The user's query is: "

my_client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(my_client)
# For LMS / literally any self hosted AI client the api key isn't really needed and can be left as default
openai_client = AsyncOpenAI(base_url=base_url, api_key=api_key)

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
        title="Bot info:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Server",
        value=f"**Endpoint:** <{base_url}> \n"
              f"**Model:** {model}",
        inline=False
    )
    
    embed.add_field(
        name="System info",
        value=f"**OS:** {platform.system()} {platform.release()}\n"
              f"**Python:** {platform.python_version()}",
        inline=False
    )
    
    embed.add_field(
        name="Statistics",
        value=f"**Uptime:** {uptime_str}\n"
              f"**Messages Processed:** {message_count}",
        inline=False
    )
    
    embed.set_footer(text=f"https://github.com/miha128/slashcord \nSystem time: {dt.now().strftime('%B %d %Y')}")
    
    await interaction.response.send_message(embed=embed)
    
@tree.command(
    name=command_name,
    description=command_desc
)
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(prompt="Prompt to send to the AI")
async def interaction(interaction: discord.Interaction, prompt: str = None):
    # ask discord for more time
    await interaction.response.defer()
    global message_count
    message_count += 1
    # for openai refer to their docs
    try:
        if prompt:
            print(f'Query: {prompt} Asked by: {interaction.user.name} Total messages: {message_count}')
            fullprompt = beforeprompt + prompt
            chat_completion = await openai_client.chat.completions.create(
                messages=[{"role": "user", "content": fullprompt}],
                model=model
            )
            ai_response = chat_completion.choices[0].message.content
            trimmed = ai_response[:1970]
            response = f"{interaction.user.mention},\n{trimmed}"
        else:
            response = f"You haven't asked me anything {interaction.user.mention}."
            
        # send the response after
        await interaction.followup.send(response)
    except Exception as e:
        await interaction.followup.send(f"An error has occured: {str(e)}")

@my_client.event 
async def on_ready():
    print(f'\n\nBOT URL: https://discord.com/oauth2/authorize?client_id={my_client.user.id}&integration_type=1&scope=applications.commands\n\n')
    print(f'Logged in as {my_client.user} (ID: {my_client.user.id})')
    print('------')
    await tree.sync()

if __name__ == "__main__":
    my_client.run(BOT_TOKEN)
