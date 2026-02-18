import discord
from discord.ext import commands
from discord import app_commands
import random, json, os, asyncio
from openai import OpenAI

# ───────── CONFIG ─────────

OPENROUTER_API_KEY = "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"
MODEL = "mistralai/mistral-7b-instruct"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

INV_FILE   = f"{DATA_DIR}/inventory.json"
COIN_FILE  = f"{DATA_DIR}/coins.json"
QUEUE_FILE = f"{DATA_DIR}/queue.json"
LB_FILE    = f"{DATA_DIR}/leaderboard.json"

lock = asyncio.Lock()

# ───────── LOAD / SAVE ─────────

def load(p): return json.load(open(p)) if os.path.exists(p) else {}
def save(p,d): json.dump(d, open(p,"w"), indent=4)

INV   = load(INV_FILE)
COIN  = load(COIN_FILE)
QUEUE = load(QUEUE_FILE)
LB    = load(LB_FILE)

# ───────── GAME DATA ─────────

CLASS_MAP = {
    "smg":"Assault","ar":"Assault","pistol":"Assault",
    "sniper":"Operator","shotgun":"Defender","lmg":"Defender"
}

WEAPON_CLASSES = {
    "Assault":{"atk":10,"crit":10},
    "Defender":{"atk":-3,"crit":0},
    "Operator":{"atk":5,"crit":20}
}

RARITY_MULT = {
    "Common":1,"Rare":1.2,"Epic":1.4,"Legendary":1.7,"Mythic":2
}

ARMORS = {
    "basic":{"hp":40,"cost":80},
    "reinforced":{"hp":80,"cost":160},
    "mythic":{"hp":140,"cost":300}
}

ATTACHMENTS = {
    "extended_mag":{"atk":5,"cost":120},
    "long_barrel":{"atk":8,"cost":160},
    "red_dot":{"crit":5,"cost":100}
}

PERKS = {
    "quick_fix":{"heal":20,"cost":200},
    "dead_silence":{"crit":10,"cost":250}
}

RANKS = [
    ("Bronze",0),("Silver",300),("Gold",800),
    ("Platinum",1500),("Diamond",2300),("Legendary",3500)
]

def get_rank(x):
    for r,v in reversed(RANKS):
        if x>=v: return r
    return "Bronze"

# ───────── ECONOMY ─────────

async def add_coins(uid, amt):
    async with lock:
        COIN[uid]=COIN.get(uid,0)+amt
        if amt>0: LB[uid]=LB.get(uid,0)+amt
        save(COIN_FILE,COIN)
        save(LB_FILE,LB)

# ───────── AI WEAPON ─────────

async def ai_weapon(wtype,name):
    prompt=f"""
ONLY JSON:
damage(20-80),
crit(5-25),
rarity(Common/Rare/Epic/Legendary/Mythic)
Weapon:{wtype} Name:{name}
"""
    r=client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"user","content":prompt}],
        temperature=0.2
    )
    return json.loads(r.choices[0].message.content)

# ───────── DAMAGE ─────────

def calc_damage(uid):
    w=INV[uid]["weapon"]
    dmg=int(w["stats"]["damage"]*RARITY_MULT[w["rarity"]])
    dmg+=WEAPON_CLASSES[w["class"]]["atk"]
    crit=w["stats"]["crit"]+WEAPON_CLASSES[w["class"]]["crit"]
    return dmg*2 if random.randint(1,100)<=crit else dmg

# ───────── PVP ─────────

async def pvp(ch,p1,p2):
    score={p1:0,p2:0}
    for r in range(3):
        d1=calc_damage(p1)
        d2=calc_damage(p2)
        score[p1]+=d1>d2
        score[p2]+=d2>d1
        await ch.send(f"⚔️ Round {r+1}: `{d1}` vs `{d2}`")
        await asyncio.sleep(1.5)
    win=max(score,key=score.get)
    await add_coins(win,60)
    await ch.send(f"🏆 <@{win}> wins **+60 coins**")

# ───────── COG ─────────

class Battleground(commands.Cog):
    def __init__(self, bot, ch):
        self.bot = bot
        self.channel_id = ch

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not msg.author.bot:
            await add_coins(str(msg.author.id), 1)
        await self.bot.process_commands(msg)

    # ── BUY WEAPON ──
    @app_commands.command(name="buyweapon")
    async def buyweapon(
        self,
        interaction: discord.Interaction,
        type: str,
        name: str
    ):
        await interaction.response.defer(thinking=True)	

        type = type.lower()
        uid = str(interaction.user.id)

        if type not in CLASS_MAP:
            return await interaction.followup.send("❌ Invalid weapon type")

        stats = await ai_weapon(type, name)
        cost = int(stats["damage"])

        if COIN.get(uid, 0) < cost:
            return await interaction.followup.send("❌ Not enough coins")

        await add_coins(uid, -cost)

        INV[uid] = {
            "weapon": {
                "type": type,
                "name": name.upper(),
                "stats": stats,
                "rarity": stats["rarity"],
                "class": CLASS_MAP[type],
                "attachments": []
            },
            "armor": None,
            "perks": []
        }

        save(INV_FILE, INV)

        await interaction.followup.send(
            f"🔫 **{name.upper()} BOUGHT**\n"
            f"Damage `{stats['damage']}` | Crit `{stats['crit']}%`\n"
            f"Rarity `{stats['rarity']}`"
        )

    # ── BUY ARMOR ──
    @app_commands.command(name="buyarmor")
    async def buyarmor(self, interaction: discord.Interaction, armor: str):
        uid = str(interaction.user.id)
        armor = armor.lower()

        if armor not in ARMORS:
            return await interaction.response.send_message("❌ Invalid armor")

        a = ARMORS[armor]
        if COIN.get(uid, 0) < a["cost"]:
            return await interaction.response.send_message("❌ Not enough coins")

        await add_coins(uid, -a["cost"])
        INV.setdefault(uid, {})["armor"] = a
        save(INV_FILE, INV)

        await interaction.response.send_message(f"🛡️ Armor equipped `{armor}`")

    # ── BUY ATTACHMENT ──
    @app_commands.command(name="buyattachment")
    async def buyattachment(self, interaction: discord.Interaction, attachment: str):
        uid = str(interaction.user.id)
        attachment = attachment.lower()

        if attachment not in ATTACHMENTS:
            return await interaction.response.send_message("❌ Invalid attachment")

        a = ATTACHMENTS[attachment]
        if COIN.get(uid, 0) < a["cost"]:
            return await interaction.response.send_message("❌ Not enough coins")

        await add_coins(uid, -a["cost"])
        INV[uid]["weapon"]["attachments"].append(attachment)
        save(INV_FILE, INV)

        await interaction.response.send_message(f"🔧 Attached `{attachment}`")

    # ── BUY PERK ──
    @app_commands.command(name="buyperk")
    async def buyperk(self, interaction: discord.Interaction, perk: str):
        uid = str(interaction.user.id)
        perk = perk.lower()

        if perk not in PERKS:
            return await interaction.response.send_message("❌ Invalid perk")

        p = PERKS[perk]
        if COIN.get(uid, 0) < p["cost"]:
            return await interaction.response.send_message("❌ Not enough coins")

        await add_coins(uid, -p["cost"])
        INV[uid]["perks"].append(perk)
        save(INV_FILE, INV)

        await interaction.response.send_message(f"✨ Perk `{perk}` equipped")

    # ── PROFILE ──
    @app_commands.command(name="profile")
    async def profile(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)
        w = INV.get(uid, {}).get("weapon", {}).get("name", "None")

        await interaction.response.send_message(
            f"🏅 Rank `{get_rank(LB.get(uid, 0))}`\n"
            f"💰 Coins `{COIN.get(uid, 0)}`\n"
            f"🔫 Weapon `{w}`"
        )

    # ── PVP ──
    @app_commands.command(name="join_pvp")
    async def join_pvp(self, interaction: discord.Interaction):
        uid = str(interaction.user.id)

        QUEUE[uid] = True
        save(QUEUE_FILE, QUEUE)

        await interaction.response.defer()
        await interaction.followup.send("⚔️ Joined PvP queue")

        if len(QUEUE) >= 2:
            p1, p2 = random.sample(list(QUEUE.keys()), 2)
            QUEUE.pop(p1)
            QUEUE.pop(p2)
            save(QUEUE_FILE, QUEUE)

            channel = self.bot.get_channel(self.channel_id)
            await pvp(channel, p1, p2)

# ───────── SETUP ─────────

async def setup(bot):
    await bot.add_cog(Battleground(bot,1468640265563668510))
    await bot.tree.sync()
