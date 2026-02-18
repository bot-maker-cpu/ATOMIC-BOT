import os
import json
import random
import discord
from discord import app_commands
from discord.ext import commands, tasks
from openai import OpenAI
import asyncio

# ---------------- CONFIG ----------------
OPENROUTER_API_KEY = "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"
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MODEL = "mistralai/mistral-7b-instruct"

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

# ---------------- STORAGE ----------------
games = {}  # user_id: game_state
multiplayer_sessions = {}  # channel_id: session_data
leaderboard_file = "hide_seek_leaderboard.json"

# Load or create leaderboard
if os.path.exists(leaderboard_file):
    with open(leaderboard_file, "r") as f:
        leaderboard = json.load(f)
else:
    leaderboard = {}

# ---------------- BOT SETUP ----------------
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# ---------------- AI LOGIC ----------------
def get_game_scene(hider_choice, room_name="Room 1"):
    prompt = (
        f"A player is hiding in '{hider_choice}' inside {room_name}. Generate 2 decoy spots. "
        "Return ONLY JSON: {'spots': ['original', 'decoy1', 'decoy2'], 'story': '1-sentence scene describing the room'}"
    )
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)
        if hider_choice not in data["spots"]:
            data["spots"][0] = hider_choice
        return data
    except:
        # fallback
        return {"spots": [hider_choice, "Behind a crate", "Under a table"],
                "story": f"The {room_name} is dimly lit, filled with shadows..."}

# ---------------- HELPER ----------------
def update_leaderboard(user_id, name, points=1):
    if str(user_id) not in leaderboard:
        leaderboard[str(user_id)] = {"name": name, "points": points}
    else:
        leaderboard[str(user_id)]["points"] += points
    with open(leaderboard_file, "w") as f:
        json.dump(leaderboard, f, indent=2)

def get_leaderboard_top(n=10):
    top = sorted(leaderboard.items(), key=lambda x: x[1]["points"], reverse=True)[:n]
    return "\n".join([f"{v['name']}: {v['points']}" for k, v in top]) or "No data yet."

# ---------------- VIEWS ----------------
class SeekerView(discord.ui.View):
    def __init__(self, spots, winner_spot, hider, seeker, room_name):
        super().__init__(timeout=120)
        self.winner_spot = winner_spot
        self.hider = hider
        self.seeker = seeker
        self.room_name = room_name
        random.shuffle(spots)

        for spot in spots:
            btn = discord.ui.Button(label=spot, style=discord.ButtonStyle.primary)
            btn.callback = self.make_callback(spot)
            self.add_item(btn)

    def make_callback(self, spot):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.seeker.id:
                return await interaction.response.send_message("You aren't the seeker!", ephemeral=True)

            for child in self.children:
                child.disabled = True

            if spot == self.winner_spot:
                msg = f"🎯 **Found!** {self.hider.mention} was hiding {spot}!"
                update_leaderboard(self.seeker.id, self.seeker.name)
            else:
                # instead of miss message, just proceed to next room
                msg = f"➡️ Moving to the next room..."
            
            await interaction.response.edit_message(content=msg, view=self)
        return callback

class HiderOptionView(discord.ui.View):
    def __init__(self, seeker, room_name="Room 1"):
        super().__init__(timeout=60)
        self.seeker = seeker
        self.room_name = room_name
        options = ["Behind the sofa", "In the closet", "Under the bed", "Inside the fridge", "Behind the curtains"]

        for opt in random.sample(options, 3):
            btn = discord.ui.Button(label=opt, style=discord.ButtonStyle.secondary)
            btn.callback = self.make_callback(opt)
            self.add_item(btn)

    def make_callback(self, choice):
        async def callback(interaction: discord.Interaction):
            await interaction.response.edit_message(content="Selection locked! Generating room...", view=None)

            game_data = get_game_scene(choice, self.room_name)

            embed = discord.Embed(title="Hide and Seek", description=game_data['story'], color=0x2b2d31)
            view = SeekerView(game_data['spots'], choice, interaction.user, self.seeker, self.room_name)

            await interaction.channel.send(content=f"🕵️ {self.seeker.mention}, where is {interaction.user.mention}?", embed=embed, view=view)
        return callback

# ---------------- COMMANDS ----------------
# At the bottom of hide_seek_bot.py
def setup(bot: commands.Bot):
    @bot.tree.command(name="hide", description="Challenge someone to Hide and Seek!")
    async def hide(interaction: discord.Interaction, seeker: discord.Member):
        if seeker.id == interaction.user.id:
            return await interaction.response.send_message("You can't hide from yourself!", ephemeral=True)

        view = HiderOptionView(seeker)
        await interaction.response.send_message("🤫 **Shh!** Pick your hiding spot below. (Only you can see this)", view=view, ephemeral=True)

    @bot.tree.command(name="leaderboard", description="Show top Hide & Seek players")
    async def lb(interaction: discord.Interaction):
        top = get_leaderboard_top()
        embed = discord.Embed(title="🏆 Hide & Seek Leaderboard", description=top, color=0xf1c40f)
        await interaction.response.send_message(embed=embed)


