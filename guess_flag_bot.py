import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
import asyncio

FLAG_CODES_URL = "https://flagcdn.com/en/codes.json"
FLAG_IMAGE_URL = "https://flagcdn.com/w320/{code}.png"

class GuessFlag(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_games = {}   # channel_id -> answer
        self.flag_codes = {}     # code -> country name

    # ---------------- LOAD COUNTRY CODES ----------------
    async def load_flag_codes(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(FLAG_CODES_URL) as resp:
                self.flag_codes = await resp.json()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.flag_codes:
            await self.load_flag_codes()
        print("🌍 GuessFlag: Country codes loaded")

    # ---------------- PICK RANDOM FLAG ----------------
    def get_random_flag(self):
        code, country = random.choice(list(self.flag_codes.items()))
        flag_url = FLAG_IMAGE_URL.format(code=code)
        return country.lower(), flag_url

    # ---------------- SLASH COMMAND ----------------
    @app_commands.command(
        name="guessflag",
        description="🌍 Guess the country from its flag!"
    )
    async def guessflag(self, interaction: discord.Interaction):

        channel_id = interaction.channel_id

        if channel_id in self.active_games:
            await interaction.response.send_message(
                "⚠️ A flag game is already running here!",
                ephemeral=True
            )
            return

        answer, flag_url = self.get_random_flag()
        self.active_games[channel_id] = answer

        embed = discord.Embed(
            title="🌍 Guess The Flag",
            description="💬 Type the **country name** in chat\n⏱️ You have **20 seconds**",
            color=discord.Color.blurple()
        )
        embed.set_image(url=flag_url)

        await interaction.response.send_message(embed=embed)

        await asyncio.sleep(20)

        if channel_id in self.active_games:
            await interaction.followup.send(
                f"⏰ Time up! The answer was **{answer.title()}**"
            )
            self.active_games.pop(channel_id)

    # ---------------- MESSAGE CHECK ----------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        if channel_id not in self.active_games:
            return

        correct = self.active_games[channel_id]
        user_answer = message.content.lower().strip()

        if user_answer == correct:
            await message.channel.send(
                f"✅ Correct! {message.author.mention} guessed **{correct.title()}** 🎉"
            )
            self.active_games.pop(channel_id)

# ---------------- SETUP FUNCTION ----------------
async def setup(bot: commands.Bot):
    await bot.add_cog(GuessFlag(bot))
