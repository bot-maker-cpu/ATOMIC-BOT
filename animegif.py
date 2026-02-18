import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random
import time
from collections import deque

GIPHY_API_KEY = "wUDQNCof1Qm9wzWpF3abFiSyUD1DuO9m"

RATE_LIMIT = 100
TIME_WINDOW = 3600
request_log = deque()

ANIME_CATEGORIES = {
    "hug": "anime hug",
    "kiss": "anime kiss",
    "cry": "anime cry",
    "laugh": "anime laugh",
    "angry": "anime angry",
    "dance": "anime dance",
    "blush": "anime blush",
    "sad": "anime sad",
}

class AnimeGIF(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------- RATE LIMIT ----------
    def allowed(self):
        now = time.time()
        while request_log and now - request_log[0] > TIME_WINDOW:
            request_log.popleft()
        if len(request_log) >= RATE_LIMIT:
            return False
        request_log.append(now)
        return True

    # ---------- ANIME GIF ----------
    @app_commands.command(
        name="animegif",
        description="Get anime GIF by category"
    )
    @app_commands.choices(
        category=[
            app_commands.Choice(name=k, value=k)
            for k in ANIME_CATEGORIES.keys()
        ]
    )
    async def animegif(
        self,
        interaction: discord.Interaction,
        category: app_commands.Choice[str],
    ):
        await interaction.response.defer()

        if not self.allowed():
            await interaction.followup.send(
                "🚦 Rate limit reached (100/hour). Try later."
            )
            return

        query = ANIME_CATEGORIES[category.value]

        url = "https://api.giphy.com/v1/gifs/search"
        params = {
            "api_key": GIPHY_API_KEY,
            "q": query,
            "limit": 25,
            "rating": "pg-13",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    await interaction.followup.send("❌ GIPHY API error.")
                    return
                data = await resp.json()

        if not data["data"]:
            await interaction.followup.send("❌ No GIFs found.")
            return

        gif = random.choice(data["data"])
        gif_url = gif["images"]["original"]["url"]

        embed = discord.Embed(
            title=f"✨ Anime GIF — {category.value}",
            color=discord.Color.purple(),
        )
        embed.set_image(url=gif_url)

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AnimeGIF(bot))
