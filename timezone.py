import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import pytz
import dateparser
import datetime

TZ_FILE = "timezones.json"

# ---------- STORAGE ----------
def load_timezones():
    if not os.path.exists(TZ_FILE):
        return {}
    with open(TZ_FILE, "r") as f:
        return json.load(f)

def save_timezones(data):
    with open(TZ_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- SETUP FUNCTION ----------
def setup_timezone_system(bot: commands.Bot):

    # -------- SLASH COMMAND --------
    @bot.tree.command(name="set-timezone", description="Set your timezone (example: Asia/Kolkata)")
    async def set_timezone(interaction: discord.Interaction, timezone: str):
        if timezone not in pytz.all_timezones:
            return await interaction.response.send_message(
                "❌ Invalid timezone.\nExample: `Asia/Kolkata`",
                ephemeral=True
            )

        data = load_timezones()
        data[str(interaction.user.id)] = timezone
        save_timezones(data)

        await interaction.response.send_message(
            f"✅ Timezone saved as **{timezone}**",
            ephemeral=True
        )

    # -------- MESSAGE LISTENER --------
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        data = load_timezones()
        sender_tz = data.get(str(message.author.id))
        if not sender_tz:
            return

        parsed = dateparser.parse(
            message.content,
            settings={"RETURN_AS_TIMEZONE_AWARE": False}
        )

        if not parsed:
            return

        # Store timestamp inside the button ID
        timestamp = int(parsed.timestamp())

        view = discord.ui.View(timeout=60)

        btn = discord.ui.Button(
            label="🔁 New timezone detected – translate it",
            style=discord.ButtonStyle.primary,
            custom_id=f"tz:{message.author.id}:{timestamp}"
        )

        async def button_callback(interaction: discord.Interaction):
            data = load_timezones()

            viewer_tz = data.get(str(interaction.user.id))
            if not viewer_tz:
                return await interaction.response.send_message(
                    "❌ You haven’t set your timezone.\nUse `/set-timezone` first.",
                    ephemeral=True
                )

            sender_zone = pytz.timezone(sender_tz)
            viewer_zone = pytz.timezone(viewer_tz)

            sender_time = datetime.datetime.fromtimestamp(timestamp, sender_zone)
            viewer_time = sender_time.astimezone(viewer_zone)

            await interaction.response.send_message(
                "🕒 **Converted Time**\n"
                f"**From:** {sender_tz}\n"
                f"**Your Timezone:** {viewer_tz}\n\n"
                f"📅 **{viewer_time.strftime('%A, %B %d %Y')}**\n"
                f"⏰ **{viewer_time.strftime('%I:%M %p')}**",
                ephemeral=True
            )

        btn.callback = button_callback
        view.add_item(btn)

        await message.reply(
            content="🕒 **Time detected in message**",
            view=view
        )

        await bot.process_commands(message)
