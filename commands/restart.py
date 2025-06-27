import discord
from discord import app_commands
import yaml
from utils import get_command_modules

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

config["owner_ids"] = [int(i) for i in config.get("owner_ids", [])]

async def setup(bot):
    @app_commands.command(
        name="restart",
        description="Reload all command modules"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def restart_command(interaction: discord.Interaction):
        if interaction.user.id not in config["owner_ids"]:
            return await interaction.response.send_message(
                "⛔ You must be a bot owner to use this command!",
                ephemeral=True
            )

        try:
            await interaction.response.send_message("🔄 Reloading all modules...", ephemeral=True)

            # Unload all current extensions
            for ext in list(bot.extensions.keys()):
                await bot.unload_extension(ext)

            # Reload using the utility function
            for module in get_command_modules():
                await bot.load_extension(module)
                print(f"✅ Reloaded: {module}")

            # Sync commands
            if config.get('guild_id'):
                guild = discord.Object(id=int(config['guild_id']))
                bot.tree.copy_global_to(guild=guild)
                await bot.tree.sync(guild=guild)

            await bot.tree.sync()

            await interaction.followup.send("✅ All modules reloaded and commands synced!", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"⚠️ Restart failed: {str(e)}", ephemeral=True)
            print(f"Restart error: {e}")

    bot.tree.add_command(restart_command)
