import discord
from discord import app_commands
import asyncio
import yt_dlp as youtube_dl
from pathlib import Path
import os
import re
import logging
import time
import random
import string
import subprocess

# Set up paths
parent_dir = Path(__file__).parent.parent
downloads_path = parent_dir / 'temporary' / 'downloads'
downloads_path.mkdir(parents=True, exist_ok=True)

# Set up logger
logger = logging.getLogger('download_command')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(downloads_path.parent / 'downloads.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

YTDL_OPTIONS = {
    'outtmpl': str(downloads_path / '%(title)s.%(ext)s'),
    'restrictfilenames': True,
    'noplaylist': True,
    'no_warnings': True,
    'merge_output_format': 'mp4',
    'format': 'best'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def random_filename(ext="mp4"):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32)) + f".{ext}"

async def compress_file(input_path, output_path):
    try:
        base_dir = Path(__file__).resolve().parent.parent
        ffmpeg_path = base_dir / "tools" / "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        
        command = [
            str(ffmpeg_path),
            "-y",
            "-i", str(input_path),
            "-b:v", "200k",
            "-b:a", "64k", 
            "-vf", "scale=trunc(iw*0.5/2)*2:trunc(ih*0.5/2)*2",
            str(output_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        return_code = await process.wait()
        return return_code == 0
        
    except Exception as e:
        print(f"Compression error: {e}")
        return False
async def setup(bot):
    @app_commands.command(
        name="download",
        description="Download media from YouTube, Twitter, etc. and send as attachment"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(
        url="URL to download (YouTube, Twitter, TikTok, etc.)",
        format="File format (best, mp4, audio, etc.)"
    )
    async def download_command(interaction: discord.Interaction, url: str, format: str = "best"):
        await interaction.response.defer(thinking=True)

        try:
            ytdl_options = YTDL_OPTIONS.copy()
            if format.lower() == "audio":
                ytdl_options['format'] = 'bestaudio'
                ytdl_options['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ytdl_options['format'] = format

            random_name = random_filename()
            ytdl_options['outtmpl'] = str(downloads_path / random_name)

            # Download media
            start_time = time.time()
            with youtube_dl.YoutubeDL(ytdl_options) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                filename = ydl.prepare_filename(info)

            if not os.path.exists(filename):
                await interaction.followup.send("❌ Download failed: File not found.")
                return

            file_size = os.path.getsize(filename)
            download_time = time.time() - start_time
            final_path = filename

            # Compress if too big
            if file_size > MAX_FILE_SIZE:
                compressed_path = downloads_path / random_filename("mp4")
                success = compress_file(filename, compressed_path)
                if success and os.path.getsize(compressed_path) <= MAX_FILE_SIZE:
                    os.remove(filename)
                    final_path = compressed_path
                else:
                    os.remove(filename)
                    if compressed_path.exists():
                        os.remove(compressed_path)
                    await interaction.followup.send(
                        f"⚠️ File too large to send, even after compression ({file_size / (1024 * 1024):.1f}MB)."
                    )
                    return

            # Upload
            with open(final_path, 'rb') as f:
                await interaction.followup.send(
                    content=(
                        f"✅ **{info.get('title', 'Media')}**\n"
                        f"⏱️ Download time: {download_time:.1f}s | "
                        f"📦 Size: {os.path.getsize(final_path)/(1024*1024):.1f}MB\n"
                        f"🔗 Original URL: <{url}>"
                    ),
                    file=discord.File(f, filename=Path(final_path).name)
                )

            os.remove(final_path)
            logger.info(f"Successfully downloaded and sent: {url} ({interaction.user})")

        except youtube_dl.DownloadError as e:
            logger.warning(f"DownloadError: {str(e)}")
            await interaction.followup.send(f"❌ Download error: `{str(e)}`")
        except Exception as e:
            logger.error("Unexpected error", exc_info=True)
            await interaction.followup.send(f"⚠️ Unexpected error: `{str(e)}`")

    bot.tree.add_command(download_command)
    logger.info("Download command loaded")
