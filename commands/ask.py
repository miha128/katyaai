import discord
from discord import app_commands
import asyncio
import yaml
import openai
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

system_message = config['openai']['system_message']

openai_client = openai.AsyncOpenAI(
    api_key=config['openai']['api_key'],
    base_url=config['openai']['base_url']
)
model = config['openai']['model']

async def setup(bot):
    @app_commands.command(
        name="ask",
        description="Query the center of the flash for information..."
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(prompt="Your question about ixfap.com...")
    async def ask_command(interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        reasoning_msg = await interaction.followup.send("<:CenterOfTheFlash:1386299040676970606> Reasoning...")
        
        try:
            if not prompt:
                return await reasoning_msg.edit(content=f"❌ You haven't asked me anything, {interaction.user.mention}")

            response = await openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            )
            
            ai_response = response.choices[0].message.content
            
            # Process response
            final_content = ai_response.split("</think>")[-1].strip() if "</think>" in ai_response else ai_response
            await reasoning_msg.edit(content=final_content[:2000])
            
        except Exception as e:
            await reasoning_msg.edit(content=f"⚠️ Error: {str(e)}")
            print(f"Error in ask command: {e}")

    bot.tree.add_command(ask_command)
