import discord

def get_welcome_embed(member):
    embed = discord.Embed(
        title="⚛️ Atomic Proton — Setup Complete!",
        description=f"Hey {member.mention}! You are now **Verified**. Below is your guide to the server.",
        color=0x00FFCC
    )

    embed.add_field(
        name="🛠️ Moderation & Admin",
        value="`/lockchannel` • `/purge` • `/slowmode` • `/ticketpanel` • `/temprole`",
        inline=False
    )

    embed.add_field(
        name="💰 Economy & XP",
        value="`/xp` • `/view-xp` • `/roleleaderboard` • `/shop` • `/buy` \n*Earn XP automatically by chatting!*",
        inline=False
    )

    embed.add_field(
        name="⚔️ Battleground & Games",
        value="`/join_pvp` • `/profile` • `/buyweapon` • `/detective` \n*Earn coins and climb the ranks.*",
        inline=False
    )

    embed.add_field(
        name="🕒 Timezone & Utilities",
        value="`/set-timezone` • `/afk` • `/ping` • `/tempvc` \n*The bot auto-converts times in chat!*",
        inline=False
    )

    embed.add_field(
        name="🤖 AI Assistant",
        value="`/talk` or just **Reply** to any bot message to chat with the AI.",
        inline=False
    )

    embed.add_field(
        name="🌈 Special Perk",
        value="Chat friendly,stay active and you will be gifted @RGB role that will change your username color.",
        inline=False
    )

    embed.set_footer(text="Enjoy your stay! If you need help, open a ticket.")
    embed.set_thumbnail(url=member.display_avatar.url)
    
    return embed

async def send_verify_dm(member: discord.Member):
    try:
        embed = get_welcome_embed(member)
        await member.send(embed=embed)
    except discord.Forbidden:
        # Users with DMs off won't crash the bot
        pass

