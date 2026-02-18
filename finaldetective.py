import discord
from discord.ext import commands
from discord.ui import View, Button
from openai import OpenAI
import random, asyncio, os, re

# ---------------- CONFIG ----------------

OPENROUTER_API_KEY = "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"
if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ OPENROUTER_API_KEY not set")

MODEL = "mistralai/mistral-7b-instruct"
MAX_LABEL_LEN = 80
MIN_PLAYERS = 2
ROUND_LIMIT = 6

# ---------------- UTILS ----------------

def shorten(text: str) -> str:
    return text[:77] + "..." if len(text) > MAX_LABEL_LEN else text

def clean_label(text: str) -> str:
    text = re.sub(r"[*_~]", "", text)
    return shorten(text.strip())

# ---------------- AI ----------------

ai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

async def ai_generate(prompt: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: ai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        ).choices[0].message.content[:2000]
    )

# ---------------- GAME STATE ----------------

games = {}

def create_state(multiplayer=False):
    suspects = ["Mr. Black", "Ms. Scarlet", "Prof. Plum", "Col. Mustard"]
    return {
        "multiplayer": multiplayer,
        "players": [],
        "leader_index": 0,
        "stage": "lobby" if multiplayer else "story",
        "round": 0,
        "votes": {},
        "suspects": random.sample(suspects, 3),
        "history": [],
        "game_over": False,
    }

# ---------------- VIEWS ----------------

class LobbyView(View):
    def __init__(self, host_id):
        super().__init__(timeout=300)
        self.host_id = host_id

    @discord.ui.button(label="Join Game", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, _):
        state = games[self.host_id]
        if interaction.user.id not in state["players"]:
            state["players"].append(interaction.user.id)
        await interaction.response.send_message("✅ Joined!", ephemeral=True)

    @discord.ui.button(label="Start Case", style=discord.ButtonStyle.primary)
    async def start(self, interaction: discord.Interaction, _):
        if interaction.user.id != self.host_id:
            return await interaction.response.send_message("❌ Only host can start.", ephemeral=True)

        state = games[self.host_id]
        if len(state["players"]) < MIN_PLAYERS:
            return await interaction.response.send_message("❌ Not enough players.", ephemeral=True)

        state["stage"] = "story"
        await interaction.response.send_message("🕵️ Case started!")
        await send_scene(interaction, state)

class VoteView(View):
    def __init__(self, host_id, options):
        super().__init__(timeout=300)
        self.host_id = host_id
        self.options = options

        for opt in options:
            btn = Button(label=clean_label(opt), style=discord.ButtonStyle.primary)
            btn.callback = self.vote_callback(opt)
            self.add_item(btn)

    def vote_callback(self, choice):
        async def callback(interaction: discord.Interaction):
            state = games[self.host_id]
            if interaction.user.id not in state["players"]:
                return await interaction.response.send_message("❌ Not in game", ephemeral=True)

            state["votes"][interaction.user.id] = choice
            await interaction.response.send_message("🗳️ Vote cast!", ephemeral=True)

            if len(state["votes"]) == len(state["players"]):
                await resolve_votes(interaction, state)

        return callback

# ---------------- GAME FLOW ----------------

async def send_scene(interaction, state):
    leader = state["players"][state["leader_index"]]
    state["votes"].clear()

    prompt = f"""
You are a detective RPG narrator.

Suspects: {state['suspects']}
Previous actions: {state['history']}

Give 3 investigation choices.
Format:
TEXT:
CHOICES:
Option1:
Option2:
Option3:
"""

    text = await ai_generate(prompt)
    story, choices = text.split("CHOICES:")
    options = [line.split(":",1)[1].strip() for line in choices.splitlines() if ":" in line]

    embed = discord.Embed(title="🕵️ Detective Case", description=story)
    embed.add_field(name="👥 Players", value="\n".join(f"<@{p}>" for p in state["players"]))
    embed.add_field(name="🧭 Lead Detective", value=f"<@{leader}>")
    embed.set_footer(text=f"Round {state['round']+1}")

    view = VoteView(interaction.user.id, options)
    await interaction.followup.send(embed=embed, view=view)

async def resolve_votes(interaction, state):
    choice = max(set(state["votes"].values()), key=list(state["votes"].values()).count)
    state["history"].append(choice)
    state["round"] += 1
    state["leader_index"] = (state["leader_index"] + 1) % len(state["players"])

    if state["round"] >= ROUND_LIMIT:
        await final_accusation(interaction, state)
    else:
        await send_scene(interaction, state)

async def final_accusation(interaction, state):
    suspect = random.choice(state["suspects"])
    verdict = random.choice([True, False])

    msg = (
        f"🏆 **CASE SOLVED!** The culprit was **{suspect}**"
        if verdict else
        f"❌ **CASE FAILED** — The criminal escaped."
    )

    await interaction.followup.send(msg)

# ---------------- COMMANDS ----------------

def setup(bot: commands.Bot):

    @bot.tree.command(name="detective", description="Single-player detective RPG")
    async def detective(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        state = create_state()
        games[interaction.user.id] = state
        state["players"] = [interaction.user.id]
        await send_scene(interaction, state)

    @bot.tree.command(name="detective-multi", description="Multiplayer detective RPG")
    async def detective_multi(interaction: discord.Interaction):
        state = create_state(multiplayer=True)
        games[interaction.user.id] = state
        state["players"] = [interaction.user.id]

        embed = discord.Embed(
            title="🕵️ Multiplayer Detective Lobby",
            description="Click **Join Game**, then host starts the case.",
        )

        await interaction.response.send_message(embed=embed, view=LobbyView(interaction.user.id))
