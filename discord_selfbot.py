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

# Configure logging to reduce noise
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s - %(message)s'
)
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
                print(f"[Conversation] Timeout for channel {channel_id}, resetting...")
                del self.conversations[channel_id]
            else:
                # Update last activity time
                conv['last_activity'] = current_time
                return conv['client']
        
        # Create new conversation
        print(f"[Conversation] Creating new conversation for channel {channel_id}")
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
            print(f"[Conversation] Reset conversation for channel {channel_id}")
            return True
        return False
    
    def cleanup_expired(self):
        """Remove all expired conversations."""
        current_time = datetime.now()
        expired = []
        
        for channel_id, conv in self.conversations.items():
            if current_time - conv['last_activity'] > timedelta(minutes=self.timeout_minutes):
                expired.append(channel_id)
        
        for channel_id in expired:
            del self.conversations[channel_id]
            print(f"[Cleanup] Removed expired conversation for channel {channel_id}")


class DiscordAIBot(discord.Client):
    """Discord selfbot with AI capabilities."""
    
    def __init__(self, binx_token: str, *args, **kwargs):
        """
        Initialize the Discord selfbot.
        
        Args:
            binx_token: BinX authentication token
        """
        super().__init__(*args, **kwargs)
        self.binx_token = binx_token
        self.conversation_manager = ConversationManager(timeout_minutes=20)
        self.cleanup_task = None
    
    async def setup_hook(self):
        """Setup background tasks."""
        # Start cleanup task
        self.cleanup_task = self.loop.create_task(self.cleanup_conversations())
    
    async def cleanup_conversations(self):
        """Background task to cleanup expired conversations."""
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                self.conversation_manager.cleanup_expired()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"[Error] Cleanup task error: {e}")
                await asyncio.sleep(60)
    
    async def on_ready(self):
        """Called when the bot is ready."""
        print(f"[Discord] Logged in as {self.user.name} ({self.user.id})")
        print(f"[Discord] Selfbot ready! Monitoring messages...")
        print(f"[Info] Commands:")
        print(f"  - Use '/ai <prompt>' to ask the AI")
        print(f"  - Use '/ai reset' to clear conversation history")
        print(f"  - Conversations auto-clear after 20 minutes of inactivity")
    
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
            prompt = message.content[4:].strip().lower()
            
            # Check for reset subcommand
            if prompt == 'reset':
                await self.handle_reset(message)
            else:
                # Regular AI prompt
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
            except:
                pass
            
            # Reset the conversation
            was_reset = self.conversation_manager.reset(channel_id)
            
            # Send confirmation
            if was_reset:
                response = await message.channel.send("✅ Conversation history has been reset!")
            else:
                response = await message.channel.send("ℹ️ No active conversation to reset.")
            
            # Auto-delete confirmation after 3 seconds
            await asyncio.sleep(3)
            try:
                await response.delete()
            except:
                pass
        
        except Exception as e:
            print(f"[Error] Reset command error: {e}")
            await message.channel.send(f"❌ Error resetting conversation: {str(e)}")
    
    async def handle_ai_prompt(self, message: discord.Message):
        """
        Handle AI prompt and send response as text file.
        
        Args:
            message: Discord message object
        """
        try:
            # Extract the prompt (remove '/ai ' prefix)
            prompt = message.content[4:].strip()
            
            if not prompt or prompt.lower() == 'reset':
                await message.channel.send("❌ Please provide a prompt after `/ai`")
                return
            
            # Get conversation client for this channel
            channel_id = str(message.channel.id)
            client = self.conversation_manager.get_or_create(channel_id, self.binx_token)
            
            # Send "thinking" indicator
            thinking_msg = await message.channel.send("🤔 Thinking...")
            
            try:
                # Send message to AI
                response = client.send_message(prompt)
                
                if not response:
                    await thinking_msg.edit(content="❌ No response from AI. Please try again.")
                    return
                
                # Create temporary text file with response
                import tempfile
                timestamp = int(time.time())
                filename = f"ai_response_{timestamp}.txt"
                
                # Use system temp directory (works on all platforms)
                temp_dir = tempfile.gettempdir()
                filepath = os.path.join(temp_dir, filename)
                
                # Write response to file with word wrapping
                with open(filepath, 'w', encoding='utf-8') as f:
                    # Write header
                    f.write(f"Prompt: {prompt}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # Write response with proper word wrapping
                    f.write(self._wrap_text(response, width=80))
                
                # Send file
                with open(filepath, 'rb') as f:
                    file = discord.File(f, filename=filename)
                    await message.channel.send(
                        content="✨ Here's your AI response:",
                        file=file
                    )
                
                # Delete temporary file
                try:
                    os.remove(filepath)
                except:
                    pass  # Ignore errors on Windows file cleanup
                
                # Delete the "thinking" message
                try:
                    await thinking_msg.delete()
                except:
                    pass
            
            except KeyboardInterrupt:
                await thinking_msg.edit(content="⚠️ Response interrupted.")
            except Exception as e:
                error_msg = str(e)
                print(f"[Error] AI request error: {error_msg}")
                await thinking_msg.edit(content=f"❌ Error: {error_msg}")
        
        except Exception as e:
            print(f"[Error] Message handling error: {e}")
            await message.channel.send(f"❌ Error: {str(e)}")
    
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
        return token
    
    # Get script directory (works on all platforms)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try binx_token.txt in script directory
    token_file = os.path.join(script_dir, 'binx_token.txt')
    if os.path.exists(token_file):
        with open(token_file, 'r', encoding='utf-8') as f:
            token = f.read().strip()
            if token:
                return token
    
    # Try old location (binx-ai/binx_token.txt) for backward compatibility
    old_token_file = os.path.join(script_dir, 'binx-ai', 'binx_token.txt')
    if os.path.exists(old_token_file):
        with open(old_token_file, 'r', encoding='utf-8') as f:
            token = f.read().strip()
            if token:
                return token
    
    return None


def main():
    """Main entry point for the selfbot."""
    # Load environment variables
    load_dotenv()
    
    # Get Discord token
    discord_token = os.getenv('DISCORD_TOKEN')
    if not discord_token:
        print("[Error] DISCORD_TOKEN not found in .env file!")
        print("[Info] Please create a .env file with your Discord token:")
        print("       DISCORD_TOKEN=your_token_here")
        exit(1)
    
    # Get BinX token
    binx_token = load_binx_token()
    
    if not binx_token:
        print("[Error] BinX token not found!")
        print("[Info] Please add BINX_TOKEN to your .env file:")
        print("       BINX_TOKEN=your_token_here")
        print("[Info] Or create binx_token.txt with your token")
        exit(1)
    
    print("[Info] Starting Discord AI Selfbot...")
    print(f"[Info] BinX token loaded: {binx_token[:20]}...")
    
    # Create and run bot (selfbots don't use intents)
    # chunk_guilds_at_startup=False disables member list scraping
    bot = DiscordAIBot(binx_token, chunk_guilds_at_startup=False)
    
    try:
        bot.run(discord_token, log_handler=None)  # Disable default logging
    except KeyboardInterrupt:
        print("\n[Info] Shutting down...")
    except Exception as e:
        print(f"[Error] Fatal error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

