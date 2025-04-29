import discord
from discord.ext import commands
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

# Setup logging
logging.basicConfig(level=logging.INFO)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './credentials.json'

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# Discord bot setup
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Helper functions
def calculate_total():
    amounts = sheet.col_values(2)[1:]  # Skip header
    return sum(map(float, amounts))

def add_expense(item: str, amount: float):
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([item, amount, current_datetime], table_range="A2")
    return current_datetime

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')

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
        logging.exception("Error in /add")
        await ctx.reply(f"❌ Unexpected error: {e}", mention_author=False)

@bot.command(name="total")
async def show_total(ctx):
    try:
        total = calculate_total()
        await ctx.reply(f"💰 Total Expenses: ₹{total:.2f}", mention_author=False)
    except Exception as e:
        logging.exception("Error in /total")
        await ctx.reply(f"❌ Error: {e}", mention_author=False)

@bot.command()
async def list(ctx):
    try:
        # Fetch all records from the Google Sheet
        records = sheet.get_all_records()

        # Format the records for display
        if not records:
            await ctx.reply("No records found.", mention_author=False)
            return

        formatted_records = "\n".join(
            [f"📌**{record['Expense']}** - ₹{record['Amount']} on {record['Date']}" for record in records]
        )

        # Reply with all records
        await ctx.reply(f"**All Records:**\n{formatted_records}", mention_author=False)
    except Exception as e:
        await ctx.reply(f'Error: {e}', mention_author=False)

# Run the bot
bot.run(DISCORD_TOKEN)
