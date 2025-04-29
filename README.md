# Discord Expense Tracker Bot

This is a Discord bot that helps you track expenses using Google Sheets. You can add expenses, view the total, and list all recorded expenses directly from your Discord server.

## Features

- Add expenses with a description and amount.
- View the total expenses.
- List all recorded expenses with details.
- Data is stored in a Google Sheet for easy access and management.

## Prerequisites

1. Python 3.8 or higher installed on your system.
2. A Google Cloud service account with access to Google Sheets API.
3. A Discord bot token.

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project directory (or use the provided `.env.sample` as a template) and add the following:

```env
DISCORD_TOKEN=your_discord_token_here
SPREADSHEET_ID=your_spreadsheet_id_here
```

- `DISCORD_TOKEN`: Your Discord bot token.
- `SPREADSHEET_ID`: The ID of the Google Sheet where expenses will be stored.

### 4. Add Google Service Account Credentials

Download the `credentials.json` file for your Google Cloud service account and place it in the project directory.

### 5. Prepare the Google Sheet

1. Create a Google Sheet with the following columns in the first row:
   - `Expense`
   - `Amount`
   - `Date`
2. Share the sheet with the service account email (found in `credentials.json`).

## Usage

### Start the Bot

Run the bot using the following command:

```bash
python bot.py
```

### Commands

- `/add <item> <amount>`: Add a new expense.  
  Example: `/add Coffee 150`
- `/total`: Show the total expenses.
- `/list`: List all recorded expenses.

## File Structure

```
.env                # Environment variables
.env.sample         # Sample environment variables file
bot.py              # Main bot script
credentials.json    # Google service account credentials
requirements.txt    # Python dependencies
```

## Security Notes

- **Do not share your `.env` or `credentials.json` files publicly.** These contain sensitive information.
- Use `.env.sample` as a template for sharing environment variable configurations.

## License

This project is licensed under the MIT License.
