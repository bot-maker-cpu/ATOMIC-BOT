# ================= ACTIONS + ROAST COG =================

import random
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

# ---------- GIF STORAGE ----------
ACTION_GIFS = {
    "hug": [
        "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
        "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
        "https://media.giphy.com/media/HaC1WdpkL3W00/giphy.gif"
    ],
    "kiss": [
        "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
        "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif"
    ],
    "punch": [
        "https://media.giphy.com/media/xT9IgG50Fb7Mi0prBC/giphy.gif",
        "https://media.giphy.com/media/l1J3G5lf06vi58EIE/giphy.gif"
    ],
    "slap": [
        "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
        "https://media.giphy.com/media/Qumf2QovTD4QxHPjy5/giphy.gif"
    ],
    "shoot": [
    "https://giphy.com/gifs/cyber-marian-XD30R2uSWMsaot8CwT"
    "https://giphy.com/gifs/gun-bed-shotgun-3YNaQqbBw3YJy"
    "https://giphy.com/gifs/3o7TKqtGkUW07hDK9y"
    "https://giphy.com/gifs/jadeyanh-jadey-itsjadeyanh-18r1CgaLuLhqHgCdy2"
    "https://giphy.com/gifs/brownsugarapp-gun-shoot-black-caesar-l4nlWhecm3qN6cYtO9"
    "https://giphy.com/gifs/shoot-OgRsVkXWDLbXi"
    "https://giphy.com/gifs/xIytx7kHpq74c"
    "https://giphy.com/gifs/gun-guns-sdarezLLwzMkw"
    "https://giphy.com/gifs/brownsugarapp-shoot-murder-thug-PnhOSPReBR4F5NT5so"
    "https://giphy.com/gifs/ZEE5-sushantsinghrajput-amitsadh-amritapuri-JMAsACEgD4VOc3y8SN"
],

"angry": [
    "https://media.giphy.com/media/11tTNkNy1SdXGg/giphy.gif",  # anime rage
    "https://media.giphy.com/media/3ohhwF34cGDoFFhRfy/giphy.gif",
    "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",
    "https://media.giphy.com/media/1BXa2alBjrCXC/giphy.gif",
    "https://media.giphy.com/media/8UGoOaR1lA1uaAN892/giphy.gif"
],
    "highfive": [
        "https://media.giphy.com/media/3oEjHV0z8S7WM4MwnK/giphy.gif",
        "https://media.giphy.com/media/1xVbRS6j52YSzp9P7N/giphy.gif"
    ],
    "roast": [
        "https://media.giphy.com/media/3ohjURFVtJt2G8Q6LA/giphy.gif"
    ]
}

def gif(action):
    return random.choice(ACTION_GIFS[action])

# ---------- FALLBACK ROASTS ----------
FALLBACK_ROASTS = [
    "You have main-character confidence with background-NPC results.",
    "Your ideas load slower than 2G internet.",
    "You’re not stupid — just very creatively wrong.",
    "Even autocorrect gave up on you.",
    "Built different… like a beta version."
]

# ---------- FETCH ROAST ----------
async def fetch_roast():
    url = "https://evilinsult.com/generate_insult.php?lang=en&type=json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get("insult") or random.choice(FALLBACK_ROASTS)
    except:
        pass
    return random.choice(FALLBACK_ROASTS)

# ================= COG =================

class ActionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---- HUG ----
    @app_commands.command(name="hug")
    async def hug(self, interaction, user: discord.Member):
        e = discord.Embed(
            description=f"🤗 {interaction.user.mention} hugged {user.mention}",
            color=discord.Color.pink()
        )
        e.set_image(url=gif("hug"))
        await interaction.response.send_message(embed=e)

    # ---- KISS (SAFE) ----
    @app_commands.command(name="kiss")
    async def kiss(self, interaction, user: discord.Member):
        e = discord.Embed(
            description=f"💋 {interaction.user.mention} kissed {user.mention}",
            color=discord.Color.magenta()
        )
        e.set_image(url=gif("kiss"))
        await interaction.response.send_message(embed=e)

    # ---- SLAP ----
    @app_commands.command(name="slap")
    async def slap(self, interaction, user: discord.Member):
        e = discord.Embed(
            description=f"🖐️ {interaction.user.mention} slapped {user.mention}",
            color=discord.Color.red()
        )
        e.set_image(url=gif("slap"))
        await interaction.response.send_message(embed=e)

    # ---- PUNCH ----
    @app_commands.command(name="punch")
    async def punch(self, interaction, user: discord.Member):
        e = discord.Embed(
            description=f"👊 {interaction.user.mention} punched {user.mention}",
            color=discord.Color.dark_red()
        )
        e.set_image(url=gif("punch"))
        await interaction.response.send_message(embed=e)

    # ---- SHOOT ----
    @app_commands.command(name="shoot")
    async def shoot(self, interaction, user: discord.Member):
        e = discord.Embed(
            description=f"🔫 {interaction.user.mention} shoots at {user.mention} (movie style)",
            color=discord.Color.dark_gray()
        )
        e.set_image(url=gif("shoot"))
        await interaction.response.send_message(embed=e)

    # ---- ANGRY ----
    @app_commands.command(name="angry")
    async def angry(self, interaction):
        e = discord.Embed(
            description=f"😡 {interaction.user.mention} is angry",
            color=discord.Color.orange()
        )
        e.set_image(url=gif("angry"))
        await interaction.response.send_message(embed=e)

    # ---- HIGHFIVE ----
    @app_commands.command(name="highfive")
    async def highfive(self, interaction, user: discord.Member):
        e = discord.Embed(
            description=f"🙌 {interaction.user.mention} high-fived {user.mention}",
            color=discord.Color.green()
        )
        e.set_image(url=gif("highfive"))
        await interaction.response.send_message(embed=e)

    # ---- ROAST ----
    @app_commands.command(name="roast")
    async def roast(self, interaction, user: discord.Member):
        roast = await fetch_roast()
        e = discord.Embed(
            description=f"🔥 {interaction.user.mention} roasted {user.mention}\n\n🗯️ *{roast}*",
            color=discord.Color.gold()
        )
        e.set_image(url=gif("roast"))
        await interaction.response.send_message(embed=e)

# ================= SETUP =================

async def setup(bot: commands.Bot):
    await bot.add_cog(ActionCog(bot))
