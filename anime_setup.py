import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import random
import json
import os
from datetime import datetime

# ================= CONFIG =================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mistral-7b-instruct"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GIPHY_API_KEY = "wUDQNCof1Qm9wzWpF3abFiSyUD1DuO9m"
DATA_DIR = "anime_data"
os.makedirs(DATA_DIR, exist_ok=True)

WATCHLIST_FILE = f"{DATA_DIR}/watchlists.json"
STATS_FILE = f"{DATA_DIR}/stats.json"
SUBSCRIPTIONS_FILE = f"{DATA_DIR}/subscriptions.json"

# ================= UTILS =================

def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ================= AI =================

async def ask_ai(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an anime expert assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENROUTER_URL, headers=headers, json=payload) as res:
            data = await res.json()
            return data["choices"][0]["message"]["content"]

# ================= MAIN COG =================

class AnimeSuite(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.watchlists = load_json(WATCHLIST_FILE, {})
        self.stats = load_json(STATS_FILE, {})
        self.subscriptions = load_json(SUBSCRIPTIONS_FILE, {})
        self.check_new_episodes.start()

    # -------------------------------------------------
    # 1️⃣ Anime Info
    # -------------------------------------------------
    @app_commands.command(name="anime")
    async def anime_info(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        text = await ask_ai(
            f"Give anime info with synopsis, genres, episodes, status, rating for {title}"
        )
        await interaction.followup.send(text[:2000])
        self._add_stat(interaction.user.id)

    # -------------------------------------------------
    # 2️⃣ Watch Lists
    # -------------------------------------------------
    @app_commands.command(name="watchlist_add")
    async def watchlist_add(self, interaction: discord.Interaction, anime: str):
        uid = str(interaction.user.id)
        self.watchlists.setdefault(uid, [])
        self.watchlists[uid].append(anime)
        save_json(WATCHLIST_FILE, self.watchlists)
        await interaction.response.send_message(
            f"✅ Added **{anime}** to your watchlist!"
        )

    @app_commands.command(name="watchlist")
    async def watchlist_show(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        wl = self.watchlists.get(uid, [])
        msg = "\n".join(wl) if wl else "No anime yet."
        await interaction.response.send_message(
            f"📺 **Your Watchlist:**\n{msg}"
        )

    # -------------------------------------------------
    # 3️⃣ Characters & Quotes
    # -------------------------------------------------
    @app_commands.command(name="character")
    async def character_info(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        text = await ask_ai(f"Give anime character biography of {name}")
        await interaction.followup.send(text[:2000])

    @app_commands.command(name="animequote")
    async def anime_quote(self, interaction: discord.Interaction):
        quote = await ask_ai("Give one iconic anime quote with anime name")
        await interaction.response.send_message(quote[:2000])

    # -------------------------------------------------
    # 4️⃣ Openings
    # -------------------------------------------------
    @app_commands.command(name="opening")
    async def opening(self, interaction: discord.Interaction, anime: str):
        info = await ask_ai(f"Name the opening songs of {anime}")
        await interaction.response.send_message(info[:2000])

    # -------------------------------------------------
    # 5️⃣ Anime Images
    # -------------------------------------------------
    @app_commands.command(name="animeimage", description="Get anime image from Giphy")
    async def anime_image(self, interaction: discord.Interaction, tag: str):
        await interaction.response.defer()

        url = "https://api.giphy.com/v1/gifs/search"
        params = {
            "api_key": GIPHY_API_KEY,
            "q": f"anime {tag}",
            "limit": 20,
            "rating": "pg-13"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()

        if not data["data"]:
            await interaction.followup.send("❌ No anime images found.")
            return

        gif = random.choice(data["data"])
        gif_url = gif["images"]["original"]["url"]

        await interaction.followup.send(gif_url)

    # -------------------------------------------------
    # 6️⃣ Games
    # -------------------------------------------------
    @app_commands.command(name="animequiz")
    async def anime_quiz(self, interaction: discord.Interaction):
        q = await ask_ai("Ask one anime quiz question with answer hidden")
        await interaction.response.send_message(q[:2000])

    # -------------------------------------------------
    # 7️⃣ Episode Notifications
    # -------------------------------------------------
    @app_commands.command(name="subscribe", description="Subscribe to anime episode notifications")
    async def subscribe(self, interaction: discord.Interaction, anime: str):
        await interaction.response.defer(ephemeral=True)

        gid = str(interaction.guild_id)
        uid = str(interaction.user.id)
        anime = anime.lower()

        self.subscriptions.setdefault(gid, {})
        self.subscriptions[gid].setdefault(anime, [])

        if uid in self.subscriptions[gid][anime]:
            await interaction.followup.send(
                f"⚠️ You are already subscribed to **{anime.title()}**"
            )
            return

        self.subscriptions[gid][anime].append(uid)
        save_json(SUBSCRIPTIONS_FILE, self.subscriptions)

        await interaction.followup.send(
            f"🔔 You are now subscribed to **{anime.title()}** episode notifications!"
        )

    # -------------------------------------------------
    # 8️⃣ Role Assignment
    # -------------------------------------------------
    @app_commands.command(name="anime_role")
    async def anime_role(self, interaction: discord.Interaction, role_name: str):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=role_name)

        if not role:
            role = await guild.create_role(name=role_name)

        await interaction.user.add_roles(role)
        await interaction.response.send_message(
            f"🎭 Role **{role_name}** assigned!"
        )

    # -------------------------------------------------
    # 9️⃣ Leaderboard
    # -------------------------------------------------
    @app_commands.command(name="leaderanime")
    async def leaderanime(self, interaction: discord.Interaction):
        top = sorted(self.stats.items(), key=lambda x: x[1], reverse=True)[:10]
        msg = "\n".join(f"<@{k}> : {v}" for k, v in top)
        await interaction.response.send_message(
            f"🏆 **Leaderboard**\n{msg if msg else 'No data yet.'}"
        )

    # -------------------------------------------------
    # 🔟 Fun
    # -------------------------------------------------
    @app_commands.command(name="animewave")
    async def anime_wave(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"👋 {interaction.user.mention} waves anime-style!"
        )

    # -------------------------------------------------
    # 1️⃣1️⃣ Manga
    # -------------------------------------------------
    @app_commands.command(name="manga")
    async def manga_info(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        info = await ask_ai(f"Give manga or light novel info for {title}")
        await interaction.followup.send(info[:2000])

    # -------------------------------------------------
    # 1️⃣2️⃣ Moderation
    # -------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        banned = ["spoiler", "leak"]
        if any(word in message.content.lower() for word in banned):
            await message.delete()
            await message.channel.send(
                f"⚠️ {message.author.mention} spoilers are not allowed!"
            )

    # -------------------------------------------------
    # 📊 Stats
    # -------------------------------------------------
    def _add_stat(self, uid):
        uid = str(uid)
        self.stats[uid] = self.stats.get(uid, 0) + 1
        save_json(STATS_FILE, self.stats)

    # -------------------------------------------------
    # 🔁 BACKGROUND TASK
    # -------------------------------------------------
    @tasks.loop(minutes=30)
    async def check_new_episodes(self):
        await self.bot.wait_until_ready()

        new_episode_available = random.choice([True, False])
        if not new_episode_available:
            return

        for guild_id, anime_data in self.subscriptions.items():
            guild = self.bot.get_guild(int(guild_id))
            if not guild or not guild.system_channel:
                continue

            for anime, users in anime_data.items():
                for user_id in users:
                    user = self.bot.get_user(int(user_id))
                    if user:
                        await guild.system_channel.send(
                            f"📢 **New Episode Alert!**\n"
                            f"{user.mention} a new episode of **{anime.title()}** is out! 🎉"
                        )

    @check_new_episodes.before_loop
    async def before_check_new_episodes(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.check_new_episodes.cancel()

# ================= SETUP =================

async def setup(bot: commands.Bot):
    await bot.add_cog(AnimeSuite(bot))
