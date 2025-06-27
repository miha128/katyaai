import discord
from discord import app_commands
import yaml
import time
import os
import asyncio
from utils import get_command_modules
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse
import threading
blocked_keywords = ["motoreta", "ngrok", "wasmer"]
firefox_driver = None
driver_lock = threading.Lock()

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

ffprofile = config.get('ffprofile', None)

def init_firefox():
    global firefox_driver

    if firefox_driver is not None:
        return

    print("Lazy-loading firefox driver... (one time only)...")
    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--width=1440")
    options.add_argument("--height=1080")

    # 🔧 If ffprofile is set and exists, use it
    if ffprofile and os.path.exists(ffprofile):
        print(f"🧩 Using Firefox profile at: {ffprofile}")
        profile = FirefoxProfile(ffprofile)

        # download and autoplay settings
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", "/tmp")
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("pdfjs.disabled", False)
        profile.set_preference("browser.download.useDownloadDir", False)

        # block images and media
        profile.set_preference("permissions.default.image", 2)
        profile.set_preference("media.autoplay.default", 0)

        options.profile = profile
    else:
        print("⚠️ No valid ffprofile set or file not found. Using default profile.")
    firefox_driver = webdriver.Firefox(options=options)
    print("✅ Firefox driver created successfully")

def wait_for_page_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def _take_screenshot_sync(url, path, timeout=10):
    """Synchronous screenshot function to be run in thread"""
    global firefox_driver
    
    with driver_lock:  
        if firefox_driver is None:
            init_firefox()
        
        firefox_driver.get(url)
        try:
            WebDriverWait(firefox_driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("✅ Page loaded completely.")
        except TimeoutException:
            print("⚠️ Page did not finish loading in time. Taking screenshot anyway.")
            # for archive.org / other sites
        time.sleep(3)
        firefox_driver.save_screenshot(path)

        # Clean up
        firefox_driver.get("about:blank")

async def take_screenshot_async(url, path, timeout=10):
    try:
        await asyncio.to_thread(_take_screenshot_sync, url, path, timeout)
    except Exception as e:
        raise e

def sanitize_and_validate_url(input_url: str) -> str | None:
    parsed_initial = urlparse(input_url)
    
    disallowed_schemes = {"file", "smb", "ftp", "data", "javascript"}
    if parsed_initial.scheme in disallowed_schemes:
        return None

    if not parsed_initial.scheme:
        input_url = "https://" + input_url
        parsed = urlparse(input_url)
    else:
        parsed = parsed_initial

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None

    hostname = parsed.hostname
    if not hostname:
        return None

    lowered_url = input_url.lower()
    for keyword in blocked_keywords:
        if keyword.lower() in lowered_url:
            print(f"[BLOCKED] URL contains blocked keyword: {keyword}")
            return None

    try:
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)

        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved:
            print(f"[BLOCKED] IP address {ip} is not allowed (private/loopback)")
            return None
    except (socket.gaierror, ValueError):
        return None

async def setup(bot):
    @app_commands.command(name="preview", description="Take a screenshot of a web page and return")
    @app_commands.describe(url="The website URL to capture")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def screenshot_safe(interaction: discord.Interaction, url: str):
        await interaction.response.defer()

        safe_url = sanitize_and_validate_url(url)
        if not safe_url:
            await interaction.followup.send(
                "### *The current Content Security Policy for KatyaView disallows URLs of this type.*",
                ephemeral=True
            )
            return
        # generate unique filename to prevent conflicts
        timestamp = int(time.time() * 1000)
        screenshot_path = f"screenshot_{timestamp}_{interaction.user.id}.png"
        
        try:
            start_time = time.perf_counter()

            await take_screenshot_async(safe_url, screenshot_path)

            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            with open(screenshot_path, "rb") as f:
                file = discord.File(f, filename="screenshot.png")
                await interaction.followup.send(
                    f"External process of capturing <{safe_url}> took **{elapsed_ms}ms**",
                    file=file
                )

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
        finally:
            if os.path.exists(screenshot_path):
                try:
                    os.remove(screenshot_path)
                except OSError:
                    pass
    
    bot.tree.add_command(screenshot_safe)