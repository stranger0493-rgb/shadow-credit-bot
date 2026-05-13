import discord
from discord.ext import commands
import sqlite3

import os
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

conn = sqlite3.connect("credits.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    credits INTEGER
)
""")
conn.commit()

@bot.command()
@commands.has_permissions(manage_guild=True)
async def addcredits(ctx, member: discord.Member, amount: int):

    cursor.execute(
        "SELECT credits FROM users WHERE user_id = ?",
        (member.id,)
    )

    result = cursor.fetchone()

    if result is None:
        cursor.execute(
            "INSERT INTO users VALUES (?, ?)",
            (member.id, amount)
        )
    else:
        new_amount = result[0] + amount

        cursor.execute(
            "UPDATE users SET credits = ? WHERE user_id = ?",
            (new_amount, member.id)
        )

    conn.commit()

    await ctx.send(f"⚡ {member.mention} earned **{amount} Shadow Credits**!")

@bot.command()
async def credits(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    cursor.execute(
        "SELECT credits FROM users WHERE user_id = ?",
        (member.id,)
    )

    result = cursor.fetchone()

    if result is None:
        credits = 0
    else:
        credits = result[0]

    await ctx.send(f"💠 {member.mention} currently has **{credits} Shadow Credits**.")

@bot.command()
async def leaderboard(ctx):

    cursor.execute(
        "SELECT user_id, credits FROM users ORDER BY credits DESC LIMIT 10"
    )

    results = cursor.fetchall()

    msg = "🏆 **Shadow Credit Leaderboard** 🏆\n\n"

    for i, (user_id, credits) in enumerate(results, start=1):

        user = await bot.fetch_user(user_id)

        msg += f"⚔️ #{i} • {user.name} — 💠 {credits} Credits\n"

    await ctx.send(msg)

bot.run(TOKEN)