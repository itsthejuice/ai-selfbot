#!/usr/bin/env python3
"""
Discord Selfbot with BinX AI Integration
Allows users to interact with BinX AI directly from Discord chats.
"""

import discord
import asyncio
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from dotenv import load_dotenv

# Import BinX AI client (local)
from binx_client import BinXChatClient

# Configure logging with color support
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        # Add timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Format: [HH:MM:SS] [LEVEL] Message
        log_msg = f"{self.BOLD}[{timestamp}]{self.RESET} {color}[{record.levelname}]{self.RESET} {record.getMessage()}"
        
        if record.exc_info:
            log_msg += '\n' + self.formatException(record.exc_info)
        
        return log_msg

# Configure root logger
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger = logging.getLogger('discord_selfbot')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Suppress discord.py-self's noisy logs
logging.getLogger('discord').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)
logging.getLogger('discord.client').setLevel(logging.ERROR)
logging.getLogger('discord.http').setLevel(logging.ERROR)
logging.getLogger('discord.state').setLevel(logging.CRITICAL)


class ConversationManager:
    """Manages persistent conversations with auto-cleanup."""
    
    def __init__(self, timeout_minutes: int = 20):
        """
        Initialize conversation manager.
        
        Args:
            timeout_minutes: Minutes of inactivity before auto-clearing conversation
        """
        self.conversations: Dict[str, Dict] = {}
        self.timeout_minutes = timeout_minutes
    
    def get_or_create(self, channel_id: str, binx_token: str) -> BinXChatClient:
        """
        Get existing conversation or create a new one.
        
        Args:
            channel_id: Discord channel ID
            binx_token: BinX authentication token
        
        Returns:
            BinXChatClient instance for the channel
        """
        current_time = datetime.now()
        
        # Check if conversation exists and is still active
        if channel_id in self.conversations:
            conv = self.conversations[channel_id]
            last_activity = conv['last_activity']
            
            # Check if conversation has timed out
            if current_time - last_activity > timedelta(minutes=self.timeout_minutes):
                logger.info(f"Conversation timeout for channel {channel_id} (inactive for {self.timeout_minutes} minutes)")
                del self.conversations[channel_id]
            else:
                # Update last activity time
                conv['last_activity'] = current_time
                logger.debug(f"Using existing conversation for channel {channel_id}")
                return conv['client']
        
        # Create new conversation
        logger.info(f"Creating new conversation for channel {channel_id}")
        client = BinXChatClient(binx_token)
        self.conversations[channel_id] = {
            'client': client,
            'last_activity': current_time
        }
        return client
    
    def reset(self, channel_id: str) -> bool:
        """
        Reset conversation for a specific channel.
        
        Args:
            channel_id: Discord channel ID
        
        Returns:
            True if conversation was reset, False if it didn't exist
        """
        if channel_id in self.conversations:
            self.conversations[channel_id]['client'].reset_conversation()
            self.conversations[channel_id]['last_activity'] = datetime.now()
            logger.info(f"Conversation reset for channel {channel_id}")
            return True
        logger.debug(f"No active conversation found for channel {channel_id}")
        return False
    
    def cleanup_expired(self):
        """Remove all expired conversations."""
        current_time = datetime.now()
        expired = []
        
        for channel_id, conv in self.conversations.items():
            if current_time - conv['last_activity'] > timedelta(minutes=self.timeout_minutes):
                expired.append(channel_id)
        
        if expired:
            logger.info(f"Cleaning up {len(expired)} expired conversation(s)")
        
        for channel_id in expired:
            del self.conversations[channel_id]
            logger.debug(f"Removed expired conversation for channel {channel_id}")


class DiscordAIBot(discord.Client):
    """Discord selfbot with AI capabilities."""
    
    def __init__(self, binx_token: str, stealth_mode: bool = True, *args, **kwargs):
        """
        Initialize the Discord selfbot.
        
        Args:
            binx_token: BinX authentication token
            stealth_mode: If True, uses reactions and delays to avoid detection
        """
        super().__init__(*args, **kwargs)
        self.binx_token = binx_token
        self.conversation_manager = ConversationManager(timeout_minutes=20)
        self.cleanup_task = None
        self.stealth_mode = stealth_mode
        
        if self.stealth_mode:
            logger.info("Stealth mode enabled - using reactions and human-like delays")
    
    async def send_with_retry(self, channel, file=None, content=None, max_retries=3):
        """
        Send a message with automatic retry for rate limits and slow mode.
        
        Args:
            channel: Discord channel to send to
            file: Optional file to attach
            content: Optional message content
            max_retries: Maximum number of retry attempts
        
        Returns:
            The sent message object, or None if failed
        """
        for attempt in range(max_retries):
            try:
                if file:
                    return await channel.send(file=file, content=content)
                else:
                    return await channel.send(content=content)
            
            except discord.errors.HTTPException as e:
                # Handle permissions error (403 - code 50013)
                if e.status == 403 or e.code == 50013:
                    logger.error(f"Missing permissions to send message in this channel: {e}")
                    return None  # Don't retry, we don't have permission
                
                # Handle rate limiting (429)
                if e.status == 429:
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 5
                    logger.warning(f"Rate limited! Waiting {retry_after:.1f}s before retry (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_after)
                    continue
                
                # Handle slow mode (error code 20016)
                if e.code == 20016:
                    # Extract wait time from error message
                    import re
                    match = re.search(r'(\d+)\s*second', str(e))
                    wait_time = int(match.group(1)) if match else 5
                    logger.warning(f"Slow mode active! Waiting {wait_time}s before retry (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time + 1)  # Add 1 second buffer
                    continue
                
                # Other HTTP errors
                logger.error(f"HTTP error sending message: {e}")
                if attempt == max_retries - 1:
                    raise
            
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                if attempt == max_retries - 1:
                    raise
        
        return None
    
    async def setup_hook(self):
        """Setup background tasks."""
        # Start cleanup task
        self.cleanup_task = self.loop.create_task(self.cleanup_conversations())
    
    async def cleanup_conversations(self):
        """Background task to cleanup expired conversations."""
        await self.wait_until_ready()
        logger.info("Started conversation cleanup task (runs every 60 seconds)")
        while not self.is_closed():
            try:
                self.conversation_manager.cleanup_expired()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Cleanup task error: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info("=" * 60)
        logger.info(f"Discord selfbot connected successfully!")
        logger.info(f"Logged in as: {self.user.name} ({self.user.id})")
        logger.info(f"Discord.py version: {discord.__version__}")
        logger.info("=" * 60)
        logger.info("Available commands:")
        logger.info("  • /ai <prompt>  - Ask the AI a question")
        logger.info("  • /ai reset     - Clear conversation history")
        logger.info(f"Conversations auto-expire after {self.conversation_manager.timeout_minutes} minutes of inactivity")
        logger.info("Response delivery: Short (<2000 chars) = text message, Long (≥2000 chars) = file")
        logger.info("Status reactions (optional): 🤔 = processing, ✅ = complete, 🚫 = no permissions")
        logger.info("Reactions are optional - bot works fine without them!")
        if self.stealth_mode:
            logger.info("Stealth mode active - using human-like delays")
        logger.info("Permission handling: Auto-deletes commands when can't respond (no trace)")
        logger.info("Slow mode & rate limit handling enabled - automatic retry with backoff")
        logger.info("=" * 60)
        logger.info("Selfbot is now monitoring messages...")
    
    async def on_message(self, message: discord.Message):
        """
        Handle incoming messages.
        
        Args:
            message: Discord message object
        """
        # Only respond to our own messages
        if message.author.id != self.user.id:
            return
        
        # Check for /ai commands
        if message.content.startswith('/ai '):
            prompt = message.content[4:].strip()
            channel_info = f"{message.guild.name if message.guild else 'DM'} / #{message.channel.name if hasattr(message.channel, 'name') else 'DM'}"
            
            # Check for reset subcommand
            if prompt.lower() == 'reset':
                logger.info(f"Reset command received in {channel_info}")
                await self.handle_reset(message)
            else:
                # Regular AI prompt
                logger.info(f"AI prompt received in {channel_info}: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
                await self.handle_ai_prompt(message)
            return
    
    async def handle_reset(self, message: discord.Message):
        """
        Handle the /ai reset command.
        
        Args:
            message: Discord message object
        """
        try:
            channel_id = str(message.channel.id)
            
            # Try to delete the command message
            try:
                await message.delete()
                logger.debug(f"Deleted reset command message in channel {channel_id}")
            except Exception as e:
                logger.debug(f"Could not delete command message: {e}")
            
            # Reset the conversation
            was_reset = self.conversation_manager.reset(channel_id)
            
            # Send confirmation with retry logic
            try:
                if was_reset:
                    logger.info(f"Conversation reset successful for channel {channel_id}")
                    response = await self.send_with_retry(message.channel, content="✅ Conversation history has been reset!")
                else:
                    logger.info(f"No active conversation found to reset for channel {channel_id}")
                    response = await self.send_with_retry(message.channel, content="ℹ️ No active conversation to reset.")
                
                if response:
                    # Auto-delete confirmation after 3 seconds
                    await asyncio.sleep(3)
                    try:
                        await response.delete()
                        logger.debug("Deleted confirmation message")
                    except:
                        pass
            except discord.errors.Forbidden:
                logger.error("Missing permissions to send messages in this channel")
            except discord.errors.NotFound:
                logger.error("Channel not found or inaccessible")
            except Exception as e:
                logger.error(f"Cannot send reset confirmation: {e}")
        
        except Exception as e:
            logger.error(f"Reset command error: {e}", exc_info=True)
            try:
                await self.send_with_retry(message.channel, content=f"❌ Error resetting conversation: {str(e)}")
            except Exception as send_error:
                logger.error(f"Could not send error message: {send_error}")
    
    async def handle_ai_prompt(self, message: discord.Message):
        """
        Handle AI prompt and send response as text file.
        
        Args:
            message: Discord message object
        """
        original_message = message
        
        try:
            # Extract the prompt (remove '/ai ' prefix)
            prompt = message.content[4:].strip()
            
            if not prompt or prompt.lower() == 'reset':
                logger.warning("Empty prompt provided")
                try:
                    await message.add_reaction("❌")
                except Exception as e:
                    logger.debug(f"Cannot react in this channel: {e}")
                return
            
            # Get conversation client for this channel
            channel_id = str(message.channel.id)
            logger.info(f"Getting conversation client for channel {channel_id}")
            client = self.conversation_manager.get_or_create(channel_id, self.binx_token)
            
            # Add small human-like delay
            if self.stealth_mode:
                import random
                delay = random.uniform(0.5, 1.5)
                logger.debug(f"Stealth mode: waiting {delay:.2f}s before processing")
                await asyncio.sleep(delay)
            
            # Try to add thinking reaction (optional - don't fail if we can't)
            can_react = False
            try:
                await message.add_reaction("🤔")
                can_react = True
                logger.debug("Added thinking reaction")
            except discord.errors.Forbidden:
                logger.warning("Missing permissions to react - continuing without reactions")
            except discord.errors.NotFound:
                logger.warning("Message not found for reaction - continuing without reactions")
            except Exception as e:
                logger.warning(f"Cannot add reaction (continuing anyway): {e}")
            
            try:
                # Send message to AI
                logger.info(f"Sending message to BinX AI (length: {len(prompt)} chars)")
                response = client.send_message(prompt)
                
                if not response:
                    logger.warning("Received empty response from AI")
                    if can_react:
                        try:
                            await original_message.remove_reaction("🤔", self.user)
                            await original_message.add_reaction("❌")
                        except:
                            pass
                    return
                
                logger.info(f"Received AI response (length: {len(response)} chars)")
                
                # Stealth mode: Add typing delay before sending response
                if self.stealth_mode:
                    # Simulate reading/typing time (0.5-2 seconds)
                    import random
                    typing_delay = random.uniform(0.5, 2.0)
                    logger.debug(f"Stealth mode: simulating typing delay {typing_delay:.2f}s")
                    await asyncio.sleep(typing_delay)
                
                # Send response - use text message for short responses, file for long ones
                sent_message = None
                
                # Check if response fits in a Discord message (2000 char limit)
                if len(response) < 2000:
                    # Send as normal text message
                    logger.info("Response is short enough - sending as text message")
                    try:
                        sent_message = await self.send_with_retry(message.channel, content=response)
                        
                        if sent_message:
                            logger.info("Response message sent to Discord")
                        else:
                            logger.error("Failed to send response message (likely missing permissions)")
                            # Delete the prompt message to leave no trace
                            try:
                                await original_message.delete()
                                logger.info("Deleted prompt message (no permissions to respond)")
                            except Exception as del_error:
                                logger.debug(f"Could not delete prompt message: {del_error}")
                                # If we can't delete, at least try to update reactions
                                if can_react:
                                    try:
                                        await original_message.remove_reaction("🤔", self.user)
                                        await original_message.add_reaction("⚠️")
                                    except:
                                        pass
                            return  # Exit gracefully
                    
                    except discord.errors.HTTPException as e:
                        # Handle permissions error specifically
                        if e.status == 403 or e.code == 50013:
                            logger.error(f"Missing permissions to send message in this channel")
                            # Delete the prompt message to leave no trace
                            try:
                                await original_message.delete()
                                logger.info("Deleted prompt message (no permissions to respond)")
                            except Exception as del_error:
                                logger.debug(f"Could not delete prompt message: {del_error}")
                                # If we can't delete, at least try to remove reactions
                                if can_react:
                                    try:
                                        await original_message.remove_reaction("🤔", self.user)
                                    except:
                                        pass
                            return  # Exit gracefully without crashing
                        
                        elif e.code == 20016:
                            # Slow mode - update reaction to show we're waiting
                            logger.warning(f"Slow mode prevents sending: {e}")
                            if can_react:
                                try:
                                    await original_message.add_reaction("⏱️")
                                except:
                                    pass
                        raise
                
                else:
                    # Response is too long - send as file
                    logger.info("Response is too long - sending as file")
                    
                    # Create temporary text file with response
                    import tempfile
                    timestamp = int(time.time())
                    filename = f"ai_response_{timestamp}.txt"
                    
                    # Use system temp directory (works on all platforms)
                    temp_dir = tempfile.gettempdir()
                    filepath = os.path.join(temp_dir, filename)
                    logger.debug(f"Creating response file: {filepath}")
                    
                    # Write response to file with word wrapping
                    with open(filepath, 'w', encoding='utf-8') as f:
                        # Write header
                        f.write(f"Prompt: {prompt}\n")
                        f.write("=" * 80 + "\n\n")
                        
                        # Write response with proper word wrapping
                        f.write(self._wrap_text(response, width=80))
                    
                    logger.info(f"Response file created: {filename}")
                    
                    try:
                        # Create discord.File from filepath - discord.py will handle file opening/closing
                        file = discord.File(filepath, filename=filename)
                        sent_message = await self.send_with_retry(message.channel, file=file)
                        
                        if sent_message:
                            logger.info("Response file sent to Discord")
                        else:
                            logger.error("Failed to send response file (likely missing permissions)")
                            # Delete the prompt message to leave no trace
                            try:
                                await original_message.delete()
                                logger.info("Deleted prompt message (no permissions to respond)")
                            except Exception as del_error:
                                logger.debug(f"Could not delete prompt message: {del_error}")
                                # If we can't delete, at least try to update reactions
                                if can_react:
                                    try:
                                        await original_message.remove_reaction("🤔", self.user)
                                        await original_message.add_reaction("⚠️")
                                    except:
                                        pass
                            return  # Exit gracefully
                    
                    except discord.errors.HTTPException as e:
                        # Handle permissions error specifically
                        if e.status == 403 or e.code == 50013:
                            logger.error(f"Missing permissions to send file in this channel")
                            # Delete the prompt message to leave no trace
                            try:
                                await original_message.delete()
                                logger.info("Deleted prompt message (no permissions to respond)")
                            except Exception as del_error:
                                logger.debug(f"Could not delete prompt message: {del_error}")
                                # If we can't delete, at least try to remove reactions
                                if can_react:
                                    try:
                                        await original_message.remove_reaction("🤔", self.user)
                                    except:
                                        pass
                            return  # Exit gracefully without crashing
                        
                        elif e.code == 20016:
                            # Slow mode - update reaction to show we're waiting
                            logger.warning(f"Slow mode prevents sending: {e}")
                            if can_react:
                                try:
                                    await original_message.add_reaction("⏱️")
                                except:
                                    pass
                        raise
                    
                    finally:
                        # Delete temporary file
                        try:
                            os.remove(filepath)
                            logger.debug(f"Deleted temporary file: {filepath}")
                        except Exception as e:
                            logger.debug(f"Could not delete temporary file: {e}")
                
                # Remove thinking reaction and add checkmark (if we have permission)
                if can_react:
                    try:
                        await original_message.remove_reaction("🤔", self.user)
                        await original_message.add_reaction("✅")
                        logger.debug("Removed thinking reaction and added checkmark")
                    except Exception as e:
                        logger.debug(f"Could not update reactions: {e}")
            
            except KeyboardInterrupt:
                logger.warning("AI response interrupted by user")
                
                # Clean up reaction (if we have permission)
                if can_react:
                    try:
                        await original_message.remove_reaction("🤔", self.user)
                        await original_message.add_reaction("⚠️")
                    except:
                        pass
            except Exception as e:
                error_msg = str(e)
                logger.error(f"AI request error: {error_msg}", exc_info=True)
                
                # Clean up reaction and show error (if we have permission)
                if can_react:
                    try:
                        await original_message.remove_reaction("🤔", self.user)
                        await original_message.add_reaction("❌")
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Message handling error: {e}", exc_info=True)
            # Try to add error reaction if possible (but don't fail if we can't)
            try:
                await original_message.add_reaction("❌")
            except Exception as react_error:
                logger.debug(f"Could not add error reaction: {react_error}")
    
    def _wrap_text(self, text: str, width: int = 80) -> str:
        """
        Wrap text to specified width while preserving paragraphs and code blocks.
        
        Args:
            text: Text to wrap
            width: Maximum line width
        
        Returns:
            Wrapped text
        """
        import textwrap
        
        lines = text.split('\n')
        wrapped_lines = []
        in_code_block = False
        
        for line in lines:
            # Check for code block markers
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                wrapped_lines.append(line)
                continue
            
            # Don't wrap code blocks or empty lines
            if in_code_block or not line.strip():
                wrapped_lines.append(line)
                continue
            
            # Check if line is a list item or special formatting
            if line.strip().startswith(('- ', '* ', '+ ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ', '#')):
                # Wrap list items with proper indentation
                wrapped = textwrap.fill(
                    line,
                    width=width,
                    subsequent_indent='  ',
                    break_long_words=False,
                    break_on_hyphens=False
                )
                wrapped_lines.append(wrapped)
            else:
                # Regular paragraph wrapping
                wrapped = textwrap.fill(
                    line,
                    width=width,
                    break_long_words=False,
                    break_on_hyphens=False
                )
                wrapped_lines.append(wrapped)
        
        return '\n'.join(wrapped_lines)


def load_binx_token() -> Optional[str]:
    """
    Load BinX token from various sources.
    
    Returns:
        Token string if found, None otherwise
    """
    # Try .env file first
    token = os.getenv('BINX_TOKEN')
    if token:
        logger.debug("BinX token loaded from .env file")
        return token
    
    # Get script directory (works on all platforms)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try binx_token.txt in script directory
    token_file = os.path.join(script_dir, 'binx_token.txt')
    if os.path.exists(token_file):
        with open(token_file, 'r', encoding='utf-8') as f:
            token = f.read().strip()
            if token:
                logger.debug(f"BinX token loaded from {token_file}")
                return token
    
    # Try old location (binx-ai/binx_token.txt) for backward compatibility
    old_token_file = os.path.join(script_dir, 'binx-ai', 'binx_token.txt')
    if os.path.exists(old_token_file):
        with open(old_token_file, 'r', encoding='utf-8') as f:
            token = f.read().strip()
            if token:
                logger.debug(f"BinX token loaded from {old_token_file} (legacy location)")
                return token
    
    logger.error("BinX token not found in any location")
    return None


def main():
    """Main entry point for the selfbot."""
    logger.info("=" * 60)
    logger.info("Discord AI Selfbot - Starting Up")
    logger.info("=" * 60)
    
    # Load environment variables
    logger.info("Loading environment variables from .env file...")
    load_dotenv()
    
    # Get Discord token
    discord_token = os.getenv('DISCORD_TOKEN')
    if not discord_token:
        logger.error("DISCORD_TOKEN not found in .env file!")
        logger.info("Please create a .env file with your Discord token:")
        logger.info("  DISCORD_TOKEN=your_token_here")
        exit(1)
    
    logger.info("Discord token loaded successfully")
    
    # Get BinX token
    logger.info("Loading BinX AI token...")
    binx_token = load_binx_token()
    
    if not binx_token:
        logger.error("BinX token not found!")
        logger.info("Please add BINX_TOKEN to your .env file:")
        logger.info("  BINX_TOKEN=your_token_here")
        logger.info("Or create binx_token.txt with your token")
        exit(1)
    
    logger.info(f"BinX token loaded: {binx_token[:20]}...")
    
    # Get stealth mode setting (default: True)
    stealth_mode = os.getenv('STEALTH_MODE', 'true').lower() in ('true', '1', 'yes', 'on')
    logger.info(f"Stealth mode: {'enabled' if stealth_mode else 'disabled'}")
    
    # Create and run bot (selfbots don't use intents)
    # chunk_guilds_at_startup=False disables member list scraping
    logger.info("Initializing Discord selfbot...")
    bot = DiscordAIBot(binx_token, stealth_mode=stealth_mode, chunk_guilds_at_startup=False)
    
    try:
        logger.info("Connecting to Discord...")
        bot.run(discord_token, log_handler=None)  # Disable default logging
    except KeyboardInterrupt:
        logger.info("Received shutdown signal (Ctrl+C)")
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()

