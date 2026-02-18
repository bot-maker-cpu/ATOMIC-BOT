# detective_rpg_bot.py

import discord
from discord.ext import commands
from discord.ui import View, Button
from openai import OpenAI
import random
import asyncio
import os
import re
# ---------------- CONFIG ----------------

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ OPENROUTER_API_KEY not set")

MODEL = "mistralai/mistral-7b-instruct"
MAX_LABEL_LEN = 80


def shorten(text: str) -> str:
    return text[:77] + "..." if len(text) > MAX_LABEL_LEN else text
def clean_label(text: str) -> str:
    # Remove markdown like **, __, _, *, `, ~
    text = re.sub(r"[*_`~]", "", text)
    return shorten(text.strip())

# ---------------- AI SETUP ----------------

ai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# ---------------- GAME STORAGE ----------------

games = {}  # user_id -> game state
multiplayer_sessions = {}  # reserved for future use


# ---------------- HELPER FUNCTIONS ----------------

async def ai_generate(prompt: str) -> str:
    """Ask the AI for a response (OpenRouter-safe)."""
    try:
        loop = asyncio.get_running_loop()
        completion = await loop.run_in_executor(
            None,
            lambda: ai.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                extra_headers={
                    "HTTP-Referer": "https://discord.com",
                    "X-Title": "Detective RPG Bot",
                },
            ),
        )
        return completion.choices[0].message.content[:2000]
    except Exception as e:
        return f"⚠️ AI Error: {e}"


def create_game_state(multiplayer=False) -> dict:
    suspects = ["Mr. Black", "Ms. Scarlet", "Prof. Plum", "Col. Mustard"]
    items = ["Mysterious Letter", "Blood-stained Knife", "Broken Watch", "Diary"]
    return {
        "stage": "start",
        "suspects": random.sample(suspects, k=3),
        "clues": random.sample(items, k=2),
        "inventory": [],
        "choices_history": [],
        "game_over": False,
        "time_elapsed": 0,
        "multiplayer": multiplayer,
        "hints_used": 0,
    }


# ---------------- BUTTON VIEW ----------------

class ChoiceView(View):
    def __init__(self, user_id: int, options: dict[str, str]):
        super().__init__(timeout=600)
        self.user_id = user_id

        for label_text, value in options.items():
            button = Button(
                label=clean_label(label_text),
                style=discord.ButtonStyle.primary
            )

            button.callback = self.make_callback(value)
            self.add_item(button)

    def make_callback(self, choice_value):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "❌ This is not your game!", ephemeral=True
                )
                return

            # ACK FAST
            await interaction.response.defer()

            # HANDLE LOGIC
            await handle_choice(interaction, choice_value)

            # stop old view
            self.stop()

        return callback


# ---------------- GAME LOGIC ----------------

async def start_game(interaction: discord.Interaction, multiplayer=False):
    state = create_game_state(multiplayer)
    games[interaction.user.id] = state
    await send_ai_intro(interaction, state)


async def send_ai_intro(interaction: discord.Interaction, state: dict):
    prompt = f"""
You are a master detective game storyteller.
Create an immersive detective RPG intro.

Suspects: {', '.join(state['suspects'])}
Clues: {', '.join(state['clues'])}

Give exactly 2 choices.

Format:
TEXT: <story>
CHOICES:
Option1: <desc>
Option2: <desc>
"""
    ai_text = await ai_generate(prompt)

try:
    text_part, choices_part = ai_text.split("CHOICES:")
    options = {}

    for line in choices_part.strip().splitlines():
        if ":" in line:
            name, desc = line.split(":", 1)
            options[clean_label(desc)] = name.strip()

except Exception:
    text_part = ai_text
    options = {"Continue the investigation": "continue"}

# ✅ ALWAYS build embed outside try/except
embed = discord.Embed(
    title="🕵️ Detective RPG",
    description=text_part.strip(),
    color=0x5865F2,
)
embed.add_field(
    name="Clues",
    value=", ".join(state["inventory"]) or "None",
    inline=False,
)

view = ChoiceView(interaction.user.id, options)
await interaction.response.edit_message(embed=embed, view=view)
# ✅ Send once, safely
 await interaction.followup.send(embed=embed, view=view)


async def handle_choice(interaction: discord.Interaction, choice: str):
    state = games.get(interaction.user.id)

    if not state or state["game_over"]:
        await interaction.response.send_message(
            "❌ Game not found or already ended.",
            ephemeral=True,
        )
        return

    state["choices_history"].append(choice)
    state["time_elapsed"] += random.randint(5, 15)

    events = [
        f"Hidden clue discovered: {random.choice(['Fingerprint', 'Secret Note', 'Cigarette Butt'])}.",
        f"{random.choice(state['suspects'])} behaves suspiciously.",
        "A dead end — nothing useful found.",
        "A shocking twist introduces a new angle.",
    ]

    state["inventory"].append(random.choice(events))

    hint_text = ""
    if state["time_elapsed"] % 30 == 0 and state["hints_used"] < 3:
        hint_text = "\n💡 Hint: Review suspects and clues carefully."
        state["hints_used"] += 1

    if state["time_elapsed"] > 120:
        state["game_over"] = True
        await interaction.response.edit_message(
            content="⏳ Time's up! Case closed.",
            embed=None,
            view=None,
        )
        return

    prompt = f"""
Continue the detective RPG.

Choices so far: {state['choices_history']}
Inventory: {state['inventory']}

Give 2–3 new options.

Format:
TEXT: <story>
CHOICES:
Option1: <desc>
Option2: <desc>
Option3: <desc>
"""
    ai_text = await ai_generate(prompt)

    async def send_ai_intro(interaction: discord.Interaction, state: dict):
    prompt = f"""
You are a master detective game storyteller.
Create an immersive detective RPG intro.

Suspects: {', '.join(state['suspects'])}
Clues: {', '.join(state['clues'])}

Give exactly 2 choices.

Format:
TEXT: <story>
CHOICES:
Option1: <desc>
Option2: <desc>
"""
    ai_text = await ai_generate(prompt)

    try:
        text_part, choices_part = ai_text.split("CHOICES:")
        options = {}

        for line in choices_part.strip().splitlines():
            if ":" in line:
                name, desc = line.split(":", 1)
                options[clean_label(desc)] = name.strip()

    except Exception:
        text_part = ai_text
        options = {"Continue the investigation": "continue"}

    embed = discord.Embed(
        title="🕵️ Detective RPG",
        description=text_part.strip(),
        color=0x5865F2,
    )
    embed.add_field(
        name="Clues",
        value=", ".join(state["inventory"]) or "None",
        inline=False,
    )

    view = ChoiceView(interaction.user.id, options)

    await interaction.followup.send(embed=embed, view=view)


# ---------------- MODULE SETUP ----------------

def setup(bot: commands.Bot):

    @bot.tree.command(
        name="detective",
        description="Start your detective RPG adventure",
    )
    async def detective(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        asyncio.create_task(start_game(interaction))

    @bot.tree.command(
        name="detective-multi",
        description="Start a multiplayer detective RPG adventure",
    )
    async def detective_multi(interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        asyncio.create_task(start_game(interaction, multiplayer=True))
        await interaction.followup.send(
            "👥 Multiplayer mode activated! Invite friends to play.",
            ephemeral=True,
        )
