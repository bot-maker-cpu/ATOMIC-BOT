# detective_rpg_bot.py
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
from openai import OpenAI
import random
import asyncio

# ---------------- CONFIG ----------------
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ OPENROUTER_API_KEY not set")
MODEL = "mistralai/mistral-7b-instruct"
MAX_LABEL_LEN = 80

def shorten(text):
    return text[:77] + "..." if len(text) > MAX_LABEL_LEN else text
# ---------------- AI SETUP ----------------
ai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


# ---------------- GAME STORAGE ----------------
games = {}  # user_id -> game state
multiplayer_sessions = {}  # session_id -> list of player IDs

# ---------------- HELPER FUNCTIONS ----------------
import asyncio

async def ai_generate(prompt: str):
    """Ask the AI for a response (OpenRouter + Discord safe)."""
    try:
        loop = asyncio.get_running_loop()
        completion = await loop.run_in_executor(
            None,
            lambda: ai.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "HTTP-Referer": "https://discord.com",
                    "X-Title": "Detective RPG Bot"
                }
            )
        )
        return completion.choices[0].message.content[:2000]
    except Exception as e:
        return f"⚠️ AI Error: {e}"
def create_game_state(multiplayer=False):
    """Initial state of the detective game."""
    suspects = ["Mr. Black", "Ms. Scarlet", "Prof. Plum", "Col. Mustard"]
    items = ["Mysterious Letter", "Blood-stained Knife", "Broken Watch", "Diary"]
    return {
        "stage": "start",
        "suspects": random.sample(suspects, k=3),
        "clues": random.sample(items, k=2),
        "inventory": [],
        "choices_history": [],
        "game_over": False,
        "time_elapsed": 0,  # in minutes
        "multiplayer": multiplayer,
        "hints_used": 0
    }

# ---------------- BUTTON VIEWS ----------------
class ChoiceView(View):
    def __init__(self, user_id, options):
        super().__init__(timeout=600)
        self.user_id = user_id

        for opt_text, opt_value in options.items():
            clean_label = shorten(
                opt_text
                .replace("**", "")
                .replace("__", "")
                .replace("*", "")
                .strip()
            )

            button = Button(
    label=shorten(opt_text),
    style=discord.ButtonStyle.primary
)
            button.callback = self.make_callback(opt_value)
            self.add_item(button)

    def make_callback(self, choice_value):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ This is not your game!", ephemeral=True)
                return
            await handle_choice(interaction, choice_value)
            self.stop()
        return callback

# ---------------- GAME LOGIC ----------------
async def start_game(interaction: discord.Interaction, multiplayer=False):
    state = create_game_state(multiplayer)
    games[interaction.user.id] = state
    await send_ai_intro(interaction, state)

async def send_ai_intro(interaction: discord.Interaction, state):
    """Generate the intro scene and first choices."""
    prompt = f"""
You are a master detective game storyteller. 
Create a 2-hour immersive detective RPG intro. 
Suspects: {', '.join(state['suspects'])}.
Clues: {', '.join(state['clues'])}.
Give 2 options for the player to choose first. Keep text < 500 words.
Return text and choices in this format:
TEXT: <story text>
CHOICES:
- Option1: <description>
- Option2: <description>
"""
    ai_text = await ai_generate(prompt)

    try:
        text_part, choices_part = ai_text.split("CHOICES:")
        options = {}
        for line in choices_part.strip().split("\n"):
            if ":" in line:
                opt_name, opt_desc = line.split(":", 1)
               options[shorten(opt_desc.strip())] = opt_name.strip()
    except:
        text_part = ai_text
        options = {"Continue": "next"}

    embed = discord.Embed(title="🕵️ Detective RPG", description=text_part, color=0x5865F2)
    embed.add_field(name="Clues", value=", ".join(state["inventory"]) or "None", inline=False)
    view = ChoiceView(interaction.user.id, options)
    await interaction.followup.send(embed=embed, view=view)

async def handle_choice(interaction: discord.Interaction, choice):
    """Handle user choice and advance game state."""
    state = games.get(interaction.user.id)
    if not state or state["game_over"]:
        await interaction.response.send_message("❌ Game not found or already ended.", ephemeral=True)
        return

    state["choices_history"].append(choice)
    state["time_elapsed"] += random.randint(5, 15)  # simulate time passage

    # Random AI-generated events
    events = [
        f"You found a hidden clue: {random.choice(['Cigarette Butt', 'Secret Note', 'Fingerprint'])}.",
        f"A suspect acts suspiciously: {random.choice(state['suspects'])}.",
        "A dead end! Nothing useful here.",
        "A sudden twist reveals a new suspect."
    ]
    ai_event = random.choice(events)
    state["inventory"].append(ai_event)

    # Automatic hint system
    hint_text = ""
    if state["time_elapsed"] % 30 == 0 and state["hints_used"] < 3:
        hint_text = f"\n💡 Hint: Consider reviewing your clues and suspects carefully."
        state["hints_used"] += 1

    # Game over conditions
    if state["time_elapsed"] > 120:  # 2 hours simulated
        state["game_over"] = True
        await interaction.response.send_message(f"⏳ Time's up! Game over.\nInventory: {state['inventory']}")
        return

    if "Wrong accusation" in choice:
        state["game_over"] = True
        await interaction.response.send_message(f"❌ You accused the wrong suspect! Game over.\nInventory: {state['inventory']}")
        return

    # Next AI scene
    prompt = f"""
Continue the detective RPG story.
Previous choices: {state['choices_history']}.
Inventory: {state['inventory']}.
Generate next story scene and 2-3 options for the player.
Include branching paths, random side plots, and possible game over triggers.
Format:
TEXT: <story>
CHOICES:
- Option1: <desc>
- Option2: <desc>
- Option3: <desc>
"""
    ai_text = await ai_generate(prompt)

    try:
        text_part, choices_part = ai_text.split("CHOICES:")
        options = {}
        for line in choices_part.strip().split("\n"):
            if ":" in line:
                opt_name, opt_desc = line.split(":", 1)
                options[opt_desc.strip()] = opt_name.strip()
    except:
        text_part = ai_text
        options = {"Continue": "next"}

    embed = discord.Embed(
    title="🕵️ Detective RPG",
    description=text_part + hint_text,
    color=0x5865F2
)

embed.add_field(
    name="Clues",
    value=", ".join(state["inventory"]) or "None",
    inline=False
)

view = ChoiceView(interaction.user.id, options)

await interaction.response.edit_message(embed=embed, view=view)

# ---------------- SLASH COMMANDS ----------------
# ---------------- MODULE SETUP ----------------
# ---------------- MODULE SETUP ----------------
def setup(bot: commands.Bot):

    @bot.tree.command(name="detective", description="Start your detective RPG adventure")
    async def detective(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        asyncio.create_task(start_game(interaction, multiplayer=False))

    @bot.tree.command(
        name="detective-multi",
        description="Start a multiplayer detective RPG adventure"
    )
    async def detective_multi(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        asyncio.create_task(start_game(interaction, multiplayer=True))
        await interaction.followup.send(
            "👥 Multiplayer mode activated! Invite friends to play together."
        )
