# VouchBot

A Discord selfbot designed for backing up and restoring vouches from your discord server.

## Features

- **Backup**: Backs up your discord reps
- **Restore**: restores your vouches and sends to hook
- **List**: see all backups

## Installation

### Prerequisites

- Python 3.8 or higher
- Discord account token

### Step 1: Clone or download this repository

```bash
git clone https://github.com/technixgodly/Vouch-Restorer.git
cd Vouch-Restorer
```

Or simply download the `vouch.py` file.

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

Or install the required packages manually:

```bash
pip install discord.py-self python-dotenv
```

### Step 3: Create a .env file

Create a file named `.env` in the same directory as the script with the following content:

```
DISCORD_TOKEN=your_discord_token_here
```

Replace `your_discord_token_here` with your actual Discord token.

## ⚠️ Important Note on Selfbots

This is a selfbot which means it a user account instead of a bot account. Please be aware:

1. Selfbots violate Discord's Terms of Service
2. Using self-bots can result in your account getting terminated
3. This tool is for educational purposes only
4. Use at your own risk

## Usage

### Running the bot

```bash
python vouch.min.py
```

### Commands

| Command | Description |
|---------|-------------|
| `$vouch help` | Show help and available commands |
| `$vouch backup` | Backup all vouch messages in the current channel |
| `$vouch list` | List all available backups |
| `$vouch restore [filename]` | Restore vouches from a backup to the current channel |

### Backup Process

1. Go to the channel you wish to backup
2. Run `$vouch backup`
3. Wait for it process to complete
4. A JSON file will be created with a filename like `vouch_backup_channelname_timestamp.json`

### Restore Process

1. Navigate to the Discord channel where you want to restore vouches
2. Run `$vouch list` to see available backup files
3. Run `$vouch restore filename.json`
4. The bot will create a webhook and post all vouches with usernames and avatars
5. Progress will be shown as messages are restored


## Credits

This tool uses the [discord.py-self](https://github.com/dolfies/discord.py-self) library. 
