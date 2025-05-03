import os
import discord
import asyncio
import json
import datetime
from discord.ext import commands
from dotenv import load_dotenv

# env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create client instance
client = commands.Bot(command_prefix='$', self_bot=True)

# Ready event
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('VouchBot is ready!')
    print('------')

# Error handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        return
    await ctx.message.add_reaction('❌')
    print(f"Command error: {error}")
    await ctx.send(f"Error: {str(error)}", delete_after=5)

# Vouch command
@client.command(name="vouch")
async def vouch_command(ctx, action="help", *, args=None):
    """
    Backup and restore vouches (messages with +rep or -rep) from a channel.
    
    Usage:
    $vouch backup - Backup all vouches in the current channel
    $vouch list - List all available vouch backup files
    $vouch restore [filename] - Restore vouches from a backup file to the current channel
    $vouch help - Show this help message
    """
    if ctx.author.id != client.user.id:
        return
    
    if action == "help":
        help_text = (
            "**Vouch Command Help**\n"
            "```\n"
            "$vouch backup - Backup all vouches in the current channel\n"
            "$vouch list - List all available backup files\n"
            "$vouch restore [filename] - Restore vouches from a backup file to the current channel\n"
            "$vouch help - Show this help message\n"
            "```"
        )
        await ctx.send(help_text, delete_after=10)
        return
    
    elif action == "list":
        # Get all vouch backup files
        backup_files = [f for f in os.listdir('.') if f.startswith('vouch_backup_') and f.endswith('.json')]
        
        if not backup_files:
            await ctx.send("No vouch backup files found.")
            return
        
        # Sort files by modification time (newest first)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Format the list
        file_list = []
        for i, file in enumerate(backup_files, 1):
            # Get file size
            size_bytes = os.path.getsize(file)
            size_str = f"{size_bytes / 1024:.1f} KB" if size_bytes < 1024 * 1024 else f"{size_bytes / (1024 * 1024):.1f} MB"
            
            # Get modification time
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S')
            
            file_list.append(f"{i}. `{file}` ({size_str}, {mod_time})")
        
        # Send the list
        list_text = "\n".join(file_list)
        await ctx.send(f"**Available Vouch Backup Files:**\n{list_text}\n\nUse `$vouch restore [filename]` to restore vouches from a file.")
    
    elif action == "backup":
        # Send initial status message
        status_message = await ctx.send("Starting vouch backup... This may take a while.")
        
        # Get current date and time for backup timestamp
        backup_timestamp = datetime.datetime.now().isoformat()
        channel_name = ctx.channel.name
        backup_filename = f"vouch_backup_{channel_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            total_messages = 0
            vouch_messages = 0
            
            # init
            vouches = []
            
            # 
            status_update_interval = 5
            
            # Fetch all
            async for message in ctx.channel.history(limit=None):
                total_messages += 1
                
                # +rep or -rep
                message_content = message.content.strip()
                if message_content.lower().startswith(("+rep", "-rep")):
                    vouch_messages += 1
                    
                    # avatar URL
                    avatar_url = str(message.author.avatar.url) if message.author.avatar else None
                    
                    # vouch object
                    vouch_data = {
                        "username": message.author.name,
                        "user_id": message.author.id,
                        "display_name": message.author.display_name if hasattr(message.author, "display_name") else message.author.name,
                        "discriminator": message.author.discriminator,
                        "avatar_url": avatar_url,
                        "message_id": message.id,
                        "message_content": message.content,
                        "message_timestamp": message.created_at.isoformat(),
                        "message_type": "positive" if message_content.lower().startswith("+rep") else "negative",
                        "attachments": [{"url": attachment.url, "filename": attachment.filename} for attachment in message.attachments],
                        "embeds": [embed.to_dict() for embed in message.embeds],
                        "reactions": [{"emoji": str(reaction.emoji), "count": reaction.count} for reaction in message.reactions],
                        "message_reference": message.reference.message_id if message.reference else None,
                        "raw_message": {
                            "id": message.id,
                            "channel_id": message.channel.id,
                            "guild_id": message.guild.id if message.guild else None,
                            "content": message.content,
                            "clean_content": message.clean_content,
                            "created_at": message.created_at.isoformat(),
                            "edited_at": message.edited_at.isoformat() if message.edited_at else None,
                            "tts": message.tts,
                            "pinned": message.pinned,
                            "mention_everyone": message.mention_everyone,
                            "flags": message.flags.value
                        }
                    }
                    
                    vouches.append(vouch_data)
                
                if total_messages % status_update_interval == 0:
                    await status_message.edit(content=f"Processing messages: {total_messages} scanned, {vouch_messages} vouches found so far...")
            
            # prep backup data
            backup_data = {
                "backup_info": {
                    "timestamp": backup_timestamp,
                    "channel_id": ctx.channel.id,
                    "channel_name": ctx.channel.name,
                    "guild_id": ctx.guild.id if ctx.guild else None,
                    "guild_name": ctx.guild.name if ctx.guild else None,
                    "total_messages_scanned": total_messages,
                    "total_vouches_found": vouch_messages
                },
                "vouches": vouches
            }
            
            # save to json
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=4, ensure_ascii=False)
            
            
            await status_message.edit(content=f"✅ Vouch backup complete! Scanned {total_messages} messages and found {vouch_messages} vouches.\nSaved to `{backup_filename}`")
            
        except Exception as e:
            await status_message.edit(content=f"❌ Error during backup: {str(e)}")
            print(f"Error during vouch backup: {e}")
    
    elif action == "restore":
        if not args:
            await ctx.send("Please specify a backup file to restore from. Use `$vouch list` to see available files.")
            return
        
        filename = args.strip()
        
        
        if not os.path.exists(filename):
            await ctx.send(f"File not found: `{filename}`. Use `$vouch list` to see available files.")
            return
        
        # initial status message
        status_message = await ctx.send(f"Loading backup file `{filename}`...")
        
        try:
            # load backup
            with open(filename, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # fetch vouches
            vouches = backup_data.get("vouches", [])
            backup_info = backup_data.get("backup_info", {})
            
            if not vouches:
                await status_message.edit(content=f"No vouches found in the backup file.")
                return
            
            # create hook
            webhook_msg = await ctx.send("Creating webhook for restoration...")
            webhook = await ctx.channel.create_webhook(name="Vouch Restoration")

            await status_message.edit(content=f"Restoring {len(vouches)} vouches from `{filename}`...")
            restored_count = 0
            vouches.sort(key=lambda x: x.get("message_timestamp", ""))
            
            for vouch in vouches:
                username = vouch.get("username", "Unknown User")
                display_name = vouch.get("display_name", username)
                avatar_url = vouch.get("avatar_url")
                message_content = vouch.get("message_content", "")
                message_timestamp = vouch.get("message_timestamp", "")
                message_type = vouch.get("message_type", "unknown")
                try:
                    timestamp_dt = datetime.datetime.fromisoformat(message_timestamp)
                    formatted_time = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_time = message_timestamp
                embed = discord.Embed(
                    description=message_content,
                    color=discord.Color.green() if message_type == "positive" else discord.Color.red()
                )
                
                embed.set_author(name=display_name, icon_url=avatar_url)
                embed.set_footer(text=f"Original message sent at {formatted_time}")
                
                # Send msg
                try:
                    await webhook.send(
                        username=f'{display_name} (Vouch Restore)',
                        avatar_url=avatar_url,
                        embed=embed
                    )
                    restored_count += 1
                    
                    # anti rate limit
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Error sending webhook message: {e}")
                
                # update status
                if restored_count % 10 == 0:
                    await status_message.edit(content=f"Restoring vouches: {restored_count}/{len(vouches)} restored...")
            
            # delte hook
            await webhook.delete()
            
            # complete message
            source_info = f" from {backup_info.get('channel_name', 'unknown channel')}" if backup_info.get('channel_name') else ""
            await status_message.edit(content=f"✅ Vouch restoration complete! Restored {restored_count}/{len(vouches)} vouches{source_info}.")
            await webhook_msg.delete()
            
        except Exception as e:
            await status_message.edit(content=f"❌ Error during restoration: {str(e)}")
            print(f"Error during vouch restoration: {e}")
    
    else:
        await ctx.send(f"Unknown action: `{action}`. Use `$vouch help` for help.")


if __name__ == "__main__":
    if not TOKEN:
        print("Error: No Discord token found. Please add DISCORD_TOKEN to your .env file.")
    else:
        try:
            client.run(TOKEN)
        except Exception as e:
            print(f"Error running bot: {e}") 
