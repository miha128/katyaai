import discord
from discord.ext import commands
from utils import load_config, get_command_modules
import time 

config = load_config()


class Katya(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        start_time = time.perf_counter()  # <-- Start timer
        print("🔄 Loading command modules...")

        for module in get_command_modules():
            try:
                print(f"Loading module: {module}...")
                await self.load_extension(module)
                print(f"Successfully loaded: {module}")
            except Exception as e:
                print(f"❌ Failed to load {module}: {e}")

        guild_id = config.get('guild_id')
        if guild_id:
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Synced commands to guild: {guild_id}")
        
        await self.tree.sync()
        print("🌐 Synced global commands.")

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        print(f"\n Done! Time taken: {int(elapsed_ms)} milis")

katya = Katya()

@katya.event
async def on_ready():
    print(f'Logged in as {katya.user}, invite URL https://discord.com/oauth2/authorize?client_id={katya.user.id}&integration_type=1&scope=applications.commands')

katya.run(config['token'])
