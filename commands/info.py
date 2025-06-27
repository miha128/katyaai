import discord
from discord import app_commands
import yaml
import platform
import psutil
import shutil
import time
from datetime import timedelta

try:
    import pynvml
    pynvml.nvmlInit()
    gpu_enabled = True
except Exception:
    gpu_enabled = False

LAUNCH_TIME = time.time()

async def setup(bot):
    @app_commands.command(
        name="info",
        description="Shows information about KatyaServer."
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def info_command(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)  # or use ephemeral=True for hidden

        try:
            # CPU Info
            cpu_freq_info = psutil.cpu_freq()
            cpu_freq_display = f"{cpu_freq_info.current:.2f} MHz" if cpu_freq_info else "N/A"

            # Shard Info
            shard_id = interaction.guild.shard_id if interaction.guild else "DM"
            shard_count = bot.shard_count or "1"

            try:
                import cpuinfo
                cpu_name = cpuinfo.get_cpu_info().get("brand_raw", "Unknown CPU")
            except ImportError:
                cpu_name = platform.processor() or "Unknown CPU"

            # Uptime
            uptime_seconds = int(time.time() - LAUNCH_TIME)
            uptime_str = str(timedelta(seconds=uptime_seconds))

            # System stats
            os_name = platform.system()
            os_version = platform.version()
            py_version = platform.python_version()
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_cores = psutil.cpu_count(logical=True)
            ram = psutil.virtual_memory()
            disk = shutil.disk_usage("/")

            embed = discord.Embed(
                title="System & Bot Info",
                color=discord.Color.blurple()
            )

            embed.add_field(name="OS", value=f"{os_name} {os_version}", inline=False)
            embed.add_field(name="Python", value=py_version, inline=True)
            embed.add_field(name="Uptime", value=uptime_str, inline=True)
            embed.add_field(name="RAM", value=f"{ram.used // (1024 ** 2)} MB / {ram.total // (1024 ** 2)} MB", inline=True)
            embed.add_field(name="CPU", value=f"{cpu_usage}% ({cpu_cores} cores)", inline=True)
            embed.add_field(name="Disk", value=f"{disk.used // (1024 ** 3)} GB / {disk.total // (1024 ** 3)} GB", inline=True)
            embed.add_field(name="Latency", value=f"{bot.latency * 1000:.2f} ms", inline=True)
            embed.add_field(name="CPU Name", value=cpu_name, inline=False)
            embed.add_field(name="CPU Freq", value=cpu_freq_display, inline=True)
            embed.add_field(name="Shard", value=f"{shard_id} / {shard_count}", inline=True)

            # GPU Info
            if gpu_enabled:
                gpu_count = pynvml.nvmlDeviceGetCount()
                for i in range(gpu_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    usage = f"{mem.used // (1024 ** 2)} MB / {mem.total // (1024 ** 2)} MB"
                    embed.add_field(name=f"GPU {i}: {name}", value=usage, inline=False)
            else:
                embed.add_field(name="GPU", value="No GPU or NVML not available", inline=False)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                f"⚠️ Failed to get info: `{str(e)}`", ephemeral=True
            )

    bot.tree.add_command(info_command)
