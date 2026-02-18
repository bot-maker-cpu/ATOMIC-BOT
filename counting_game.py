import discord
from discord.ext import commands
from collections import defaultdict

class CountingGame(commands.Cog):
    def __init__(self, bot, channel_id: int):
        self.bot = bot
        self.channel_id = channel_id

        self.current_number = 0
        self.last_user_id = None
        self.counter_stats = defaultdict(int)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bots
        if message.author.bot:
            return

        # Only work in the counting channel
        if message.channel.id != self.channel_id:
            return

        content = message.content.strip()

        # Message must be a number
        if not content.isdigit():
            await message.channel.send(
                f"❌ {message.author.mention} only **numbers** are allowed here!"
            )
            return

        number = int(content)

        # Same user twice check
        if message.author.id == self.last_user_id:
            await message.channel.send(
                f"⚠️ {message.author.mention} you can't count **twice in a row**!"
            )
            return

        expected_number = self.current_number + 1

        # Wrong number check
        if number != expected_number:
            await message.channel.send(
                f"❌ {message.author.mention} sent the **wrong number**!\n"
                f"👉 Last number was **{self.current_number}**, but you typed **{number}**"
            )
            return

        # ✅ Correct number
        self.current_number = number
        self.last_user_id = message.author.id
        self.counter_stats[message.author.id] += 1

        try:
            await message.add_reaction("✅")
        except:
            pass

    @commands.command(name="topcounters")
    async def top_counters(self, ctx):
        if not self.counter_stats:
            await ctx.send("📊 No counters yet!")
            return

        sorted_users = sorted(
            self.counter_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        leaderboard = ""
        for i, (user_id, count) in enumerate(sorted_users, start=1):
            user = ctx.guild.get_member(user_id)
            name = user.display_name if user else "Unknown"
            leaderboard += f"**{i}. {name}** — {count}\n"

        await ctx.send(
            "🏆 **Top Counters** 🏆\n" + leaderboard
        )


async def setup(bot: commands.Bot):
    COUNTING_CHANNEL_ID = 1469196579335311390  # 🔴 put your channel ID here
    await bot.add_cog(CountingGame(bot, COUNTING_CHANNEL_ID))
