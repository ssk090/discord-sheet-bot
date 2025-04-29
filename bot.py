import discord
from discord.ext import commands
from discord import app_commands
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Logging
logging.basicConfig(level=logging.INFO)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './credentials.json'
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True  # Enable for legacy commands and webhook messages
bot = commands.Bot(command_prefix='/', intents=intents)
tree = bot.tree  # For slash commands

# Helper functions
def calculate_total():
    amounts = sheet.col_values(2)[1:]
    return sum(map(float, amounts))

def add_expense(item: str, amount: float):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([item, amount, now], table_range="A2")
    return now

# Events
@bot.event
async def on_ready():
    await tree.sync()
    logging.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_guild_join(guild):
    logging.info(f"Joined new guild: {guild.name}")
    if guild.system_channel:
        await guild.system_channel.send(
            "👋 Hello! I'm your expense tracker. Use `/add`, `/total`, and `/list` to manage your expenses!"
        )

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author == bot.user:
        return

    content = message.content.strip()
    command = content.lower()

    if command.startswith("/add"):
        try:
            _, *item_parts, amount = content.split()
            item = " ".join(item_parts)
            amount = float(amount)
            date = add_expense(item, amount)
            await message.channel.send(f"✅ Added: **{item}** – ₹{amount:.2f} on `{date}`")
        except ValueError:
            await message.channel.send("❌ Error: 'amount' must be a number. Usage: `/add <item> <amount>`")
        except Exception as e:
            logging.exception("Error in /add via on_message")
            await message.channel.send(f"❌ Unexpected error: {e}")

    elif command == "/total":
        try:
            total = calculate_total()
            await message.channel.send(f"💰 Total Expenses: ₹{total:.2f}")
        except Exception as e:
            logging.exception("Error in /total via on_message")
            await message.channel.send(f"❌ Error: {e}")

    elif command == "/list":
        try:
            records = sheet.get_all_records()
            if not records:
                await message.channel.send("No records found.")
                return

            formatted = "\n".join(
                f"📌 **{r['Expense']}** – ₹{r['Amount']} on {r['Date']}" for r in records[-5:]
            )
            await message.channel.send(f"🧾 Last 5 entries:\n{formatted}")
        except Exception as e:
            logging.exception("Error in /list via on_message")
            await message.channel.send(f"❌ Error: {e}")

    # Let normal command handlers work too
    await bot.process_commands(message)

# Legacy command
@bot.command()
async def add(ctx, *, input_text: str = None):
    try:
        if not input_text:
            await ctx.reply("❌ Usage: `/add <item> <amount>`", mention_author=False)
            return

        *item_parts, amount = input_text.strip().split()
        item = " ".join(item_parts)
        amount = float(amount)

        date = add_expense(item, amount)
        await ctx.reply(f"✅ Added: **{item}** – ₹{amount:.2f} on `{date}`", mention_author=False)
        await ctx.message.add_reaction("✅")

    except ValueError:
        await ctx.reply("❌ Error: 'amount' must be a number. Usage: `/add <item> <amount>`", mention_author=False)
    except Exception as e:
        logging.exception("Error in legacy /add")
        await ctx.reply(f"❌ Unexpected error: {e}", mention_author=False)

@bot.command(name="total")
async def show_total(ctx):
    try:
        total = calculate_total()
        await ctx.reply(f"💰 Total Expenses: ₹{total:.2f}", mention_author=False)
    except Exception as e:
        await ctx.reply(f"❌ Error: {e}", mention_author=False)

@bot.command(name="list")
async def list_expenses_legacy(ctx):
    try:
        records = sheet.get_all_records()
        if not records:
            await ctx.reply("No records found.", mention_author=False)
            return

        formatted = "\n".join(
            f"📌 **{r['Expense']}** – ₹{r['Amount']} on {r['Date']}" for r in records[-5:]
        )
        await ctx.reply(f"🧾 Last 5 entries:\n{formatted}", mention_author=False)
    except Exception as e:
        await ctx.reply(f"❌ Error: {e}", mention_author=False)

# Slash commands
@tree.command(name="add", description="Add a new expense")
@app_commands.describe(item="The item name", amount="The amount in rupees")
async def slash_add(interaction: discord.Interaction, item: str, amount: float):
    try:
        date = add_expense(item, amount)
        await interaction.response.send_message(
            f"✅ Added: **{item}** – ₹{amount:.2f} on `{date}`"
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

@tree.command(name="total", description="Show total expenses")
async def slash_total(interaction: discord.Interaction):
    try:
        total = calculate_total()
        await interaction.response.send_message(f"💰 Total Expenses: ₹{total:.2f}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

@tree.command(name="list", description="List recent expenses")
async def slash_list(interaction: discord.Interaction):
    try:
        records = sheet.get_all_records()
        if not records:
            await interaction.response.send_message("No records found.")
            return

        formatted = "\n".join(
            f"📌 **{r['Expense']}** – ₹{r['Amount']} on {r['Date']}" for r in records[-5:]
        )
        await interaction.response.send_message(f"🧾 Last 5 entries:\n{formatted}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}")

# Run the bot
bot.run(DISCORD_TOKEN)
