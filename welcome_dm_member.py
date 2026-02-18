import discord
from discord.ext import commands

# ================= CONFIG =================
MEMBER_ROLE_NAME = "Member"  # must exist in server

# ================= DM CONTENT =================

RULES_MESSAGE = (
    "📜 **SERVER RULES — READ FIRST**\n\n"
    "1️⃣ 💬 Be respectful, no hate or bullying\n"
    "2️⃣ 🚫 No spam, floods, or ping abuse\n"
    "3️⃣ 🔒 Keep privacy, no doxxing allowed\n"
    "4️⃣ 📢 No ads unless staff-approved\n"
    "5️⃣ 👮 Follow staff, respect moderators\n"
    "6️⃣ 🎮 Stay on topic in channels\n"
    "7️⃣ ⚠️ No NSFW, illegal, or harmful stuff\n"
    "8️⃣ 🎤 No mic spam, loud or annoying\n"
    "9️⃣ 🛑 Hate speech = **instant ban**\n"
    "🔟 📬 Report issues directly to staff\n\n"
    "⚠️ Breaking rules may result in mutes, timeouts, or bans."
)

WELCOME_MESSAGE = (
    "📩 **Welcome to the Server! Read This Carefully 👇**\n\n"
    "👋 **Hey there! Welcome to Atomic Proton ⚛️** — "
    "a fully automated, feature-rich community powered by an advanced "
    "**Server Manager bot**.\n\n"
    "To unlock everything this server offers, please read this carefully.\n\n"

    "🔐 **FIRST STEP — VERIFY**\n"
    "Before using most commands:\n"
    "👉 Go to the server and run **/verify**\n"
    "Without verification, commands will be restricted.\n\n"

    "📜 **Server Rules (Short & Clear)**\n"
    "✅ Be respectful\n"
    "❌ No abuse, spam, or toxic language\n"
    "❌ No exploits or bot abuse\n"
    "🛡️ Staff decisions are final\n\n"

    "⚙️ **Core Bot Commands & Features**\n\n"

    "🛠️ **Moderation & Admin**\n"
    "/lockchannel – Lock a channel\n"
    "/unlockchannel – Unlock it\n"
    "/purge <amount> – Delete messages\n"
    "/slowmode <seconds> – Set chat cooldown\n"
    "/say – Bot speaks\n"
    "/createrole – Create a role\n"
    "/temprole – Give a role temporarily\n"
    "/ticketpanel – Open ticket panel\n\n"

    "💰 **XP, Economy & Levels**\n"
    "💬 Chat to earn XP automatically\n"
    "⭐ Level up every 100 XP\n"
    "/xp – View your stats\n"
    "/view-xp @user – View others\n"
    "/roleleaderboard – Top members\n"
    "/shop – XP role shop\n"
    "/buy @role – Buy roles with XP\n"
    "✨ Level-ups are announced automatically\n\n"

    "🕒 **Timezone & Smart Detection**\n"
    "/set-timezone – Set your timezone\n"
    "Type times like `6:30 pm`\n"
    "Click the button → instant conversion\n\n"

    "💤 **Utilities**\n"
    "/afk – Set AFK status\n"
    "/ping – Bot latency\n"
    "/botinfo – Bot stats\n"
    "/tempvc – Create temporary VC\n"
    "/verify – Get verified role\n\n"

    "⚔️ **BattlegroundMega — PvP System**\n"
    "/buyweapon – Buy AI-generated weapons\n"
    "/join_pvp – Join PvP queue\n"
    "/profile – View rank, coins & weapon\n"
    "💰 Coins earned by chatting\n"
    "🏆 PvP winners get bonus rewards\n\n"

    "🕵️ **Detective Mode (Multiplayer)**\n"
    "Interactive mystery & detective games\n"
    "Multiplayer supported, AI-powered\n"
    "(Use `/detective` commands)\n\n"

    "🌈 **SPECIAL PERK — RGB USERNAME**\n"
    "Once verified:\n"
    "✨ Dynamic RGB username role\n"
    "🌈 Auto color changing\n"
    "🚀 No setup needed\n\n"

    "🤖 **AI Assistant**\n"
    "Reply to the bot → it replies back\n"
    "/talk <question> – Ask AI directly\n\n"

    "🚀 **Final Note**\n"
    "This server is fully automated — explore & enjoy.\n"
    "If something breaks, contact staff via tickets.\n\n"
    "🔐 **Now verify using /verify and unlock everything.**\n\n"
    "**Welcome aboard — Atomic Proton ⚛️**"
)

# ================= COG =================

class WelcomeDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # ✅ Give Member role
        role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)
        if role:
            try:
                await member.add_roles(role, reason="Auto member role on join")
            except:
                pass

        # ✅ Send Rules FIRST, then Welcome message
        try:
            await member.send(RULES_MESSAGE)
            await member.send(WELCOME_MESSAGE)
        except discord.Forbidden:
            pass  # User has DMs closed


# ================= SETUP =================
async def setup(bot):
    await bot.add_cog(WelcomeDM(bot))
