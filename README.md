# Discord AI Selfbot with BinX Integration

A Discord selfbot that integrates BinX AI, allowing you to interact with AI directly from your Discord chats. Short responses are sent as text messages, longer responses as files, with persistent conversation history per channel.

## ⚠️ Important Warning

**Using selfbots is against Discord's Terms of Service.** This tool is for educational purposes only. Use at your own risk. Your account may be banned if you use this.

## ✨ Features

- 🤖 **AI Integration**: Use BinX AI directly from Discord
- 💬 **Persistent Conversations**: Maintains conversation context per channel
- 📝 **Smart Response Delivery**: Short responses (<2000 chars) sent as text messages, longer ones as `.txt` files
- ⏰ **Auto-Cleanup**: Conversations auto-reset after 20 minutes of inactivity
- 🔄 **Manual Reset**: Use `/ai reset` command to clear conversation history
- 🥷 **Stealth Mode**: Uses reactions and delays to work in more servers (enabled by default)
- 🛡️ **Permission Handling**: Gracefully handles channels where you lack permissions
- 🧹 **Auto-Delete**: Removes command traces when bot can't respond
- 🚀 **Simple Setup**: Easy configuration with `.env` file

## 🚀 Quick Start

> **Windows Users**: See [WINDOWS.md](WINDOWS.md) for Windows-specific instructions and use `start_selfbot.bat`

### 1. Install Dependencies

**Linux/Mac:**
```bash
# Easy way - use the startup script
./start_selfbot.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
REM Easy way - use the batch script
start_selfbot.bat

REM Or manually:
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements-windows.txt
```

> **Note**: Windows uses `requirements-windows.txt` which includes `audioop-lts` for Python 3.13+ compatibility. Linux/Mac use `requirements.txt`.

### 2. Configure Tokens

Copy the example environment file and edit it with your tokens:

```bash
cp .env.example .env
nano .env  # or use any text editor
```

You need two tokens:

#### Discord Token (User Token)

**Method 1: Browser Local Storage (Easiest)**
1. Open Discord in your web browser (discord.com)
2. Press `F12` to open Developer Tools
3. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. In the left sidebar, expand **Local Storage**
5. Click on `https://discord.com`
6. Find the key named `token`
7. Copy the value (remove the surrounding quotes)
8. Add it to `.env` as `DISCORD_TOKEN`

**Method 2: Console Commands**
1. Open Discord in browser and press `F12`
2. Go to **Console** tab
3. Try these commands (one should work):

```javascript
// Try this first:
window.webpackChunkdiscord_app.push([[Math.random()],{},e=>{Object.values(e.c).find(e=>e?.exports?.default?.getToken).exports.default.getToken()}])

// Or this:
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()

// Or simply:
JSON.parse(localStorage.token)
```

4. Copy the token that appears
5. Add it to `.env` as `DISCORD_TOKEN`

**Method 3: Network Tab**
1. Press `F12` → **Network** tab
2. Reload Discord page (F5)
3. Find any request to `discord.com/api`
4. Click it and look at **Headers** → **Request Headers**
5. Find `Authorization` and copy everything after "Bearer "
6. Add it to `.env` as `DISCORD_TOKEN`

#### BinX AI Token
1. Visit [binx.cc](https://binx.cc) and login
2. Press `F12` to open Developer Tools
3. Go to the **Network** tab
4. Navigate to AI Chat and send a test message
5. Find the `/api/ai-chat` request in the Network tab
6. Copy the `Authorization` header value (remove 'Bearer ' prefix)
7. Add it to `.env` as `BINX_TOKEN`

Alternatively, you can create a `binx_token.txt` file in the project root with your token.

### 3. Run the Selfbot

**Linux/Mac:**
```bash
./start_selfbot.sh
# Or: python3 discord_selfbot.py
```

**Windows:**
```cmd
start_selfbot.bat
REM Or: python discord_selfbot.py
```

You should see:
```
[Info] Starting Discord AI Selfbot...
[Info] BinX token loaded: ...
[Discord] Logged in as YourName (123456789)
[Discord] Selfbot ready! Monitoring messages...
```

## 📖 Usage

### Prompt the AI

Send a message starting with `/ai` followed by your prompt:

```
/ai What is quantum computing?
```

The bot will:
1. React with 🤔 to your message while processing (if it has permission)
2. Send your prompt to BinX AI
3. Return the response as:
   - **Text message** if response is under 2000 characters
   - **`.txt` file** if response is 2000+ characters (with formatted header)
4. Replace 🤔 with ✅ when complete

### Reset Conversation

Clear the conversation history for the current channel:

```
/ai reset
```

The command message and confirmation will auto-delete after 3 seconds.

### Auto-Cleanup

Conversations automatically reset after **20 minutes** of inactivity. This keeps the conversation context fresh and prevents memory buildup.

### Status Reactions

The bot uses reactions on your message to show status (when permissions allow):
- 🤔 - Processing your request
- ✅ - Response sent successfully
- ❌ - Error occurred
- 🚫 - Missing permissions to send in this channel
- ⚠️ - Request was interrupted or couldn't complete
- ⏱️ - Waiting for slow mode/rate limit

**Reactions are optional** - if the bot can't react in a channel, it will still send the response!

This is **much more stealthy** than sending status messages!

### Slow Mode & Rate Limit Handling

The bot automatically handles Discord's slow mode and rate limits:
- **Automatic retry** - Waits the required time and retries up to 3 times
- **Smart delays** - Respects Discord's rate limit headers
- **No crashes** - Gracefully handles all rate limit scenarios
- **Visual feedback** - Shows ⏱️ reaction when waiting for rate limits

Works perfectly in channels with slow mode enabled (5s, 10s, 30s, etc.)!

## 🎯 How It Works

### Conversation Management

- Each Discord channel gets its own conversation context
- Messages are stored in conversation history
- AI responses maintain context from previous messages
- Inactive conversations are automatically cleaned up

### Response Delivery

The bot intelligently chooses how to send responses:

**Short Responses (< 2000 characters):**
- Sent as regular Discord messages
- Instant readability without downloading
- Natural conversation flow

**Long Responses (≥ 2000 characters):**
- Sent as `.txt` files with formatted header:
  ```
  Prompt: Your question here
  ==================================================

  AI response content here...
  ```

This approach:
- ✅ Optimizes readability for short responses
- ✅ Handles long responses without Discord's 2000-char message limit
- ✅ Easy to save and share
- ✅ Preserves formatting
- ✅ Avoids message spam

## 🛠️ Configuration

### Stealth Mode (Recommended)

**Enabled by default** - Stealth mode adds human-like delays to avoid detection:
- Waits 0.5-1.5 seconds before processing (simulates reading time)
- Waits 0.5-2.0 seconds before responding (simulates typing time)
- Makes the bot appear more natural and less automated

The bot now **always uses reactions** instead of messages for status updates (🤔 → ✅) and sends only the file response without extra text.

To disable stealth mode delays, add to your `.env` file:
```bash
STEALTH_MODE=false
```

**Why stealth mode helps:**
- Some servers have strict anti-bot measures
- Discord's API can reject instant automated responses
- Human-like delays prevent rate limiting
- Reduces the chance of being flagged as a bot

**When to disable:**
- If you want instant responses
- For debugging purposes
- If delays are annoying you

### Conversation Timeout

To change the 20-minute auto-cleanup timeout, edit `discord_selfbot.py`:

```python
# In DiscordAIBot.__init__
self.conversation_manager = ConversationManager(timeout_minutes=30)  # Change to 30 minutes
```

### Command Prefix

To change the `/ai` prefix, edit the `on_message` method:

```python
if message.content.startswith('/ai '):  # Change '/ai ' to your preferred prefix
```

## 📁 Project Structure

```
discord-chat-ai/
├── discord_selfbot.py       # Main selfbot application
├── binx_client.py            # BinX AI client (self-contained)
├── start_selfbot.sh          # Linux/Mac startup script
├── start_selfbot.bat         # Windows startup script
├── requirements.txt          # Python dependencies (only 3!)
├── .env                      # Your configuration (create from .env.example)
├── .env.example              # Configuration template
├── binx_token.txt            # Optional: BinX token file
├── README.md                 # This file
├── QUICKSTART.md             # Quick setup guide
└── WINDOWS.md                # Windows-specific guide
```

## 🐛 Troubleshooting

### "DISCORD_TOKEN not found"
- Make sure you created `.env` file from `.env.example`
- Check that your Discord token is correctly copied (no extra spaces)

### "BinX token not found"
- Add `BINX_TOKEN` to `.env` file, OR
- Create `binx_token.txt` with your token in the project root

### "Improper token has been passed"
- Your Discord token is invalid or expired
- Get a fresh token using the steps in configuration

### No response from AI
- Check your internet connection
- Verify your BinX token is valid
- Try resetting the conversation with `/ai reset`

### Bot not responding to commands
- Make sure you're sending from YOUR account (selfbot only responds to your messages)
- Check that the message starts exactly with `/ai ` (with a space)

### "404 Not Found (error code: 10008): Unknown Message"
This error means Discord rejected the bot's message. Solutions:
- **Enable stealth mode** (enabled by default) - uses reactions instead of messages
- The bot may be detected in certain servers with strict anti-bot measures
- Try using the bot in DMs or your own servers first
- Make sure you have permission to send messages in that channel

### Works in some servers but not others
This is normal! Different servers have different security settings:
- **Stealth mode** (enabled by default) helps with most servers
- Bot gracefully handles permission issues by auto-deleting commands
- If you lack send permissions, the command is removed automatically (no trace)
- Some servers have strict anti-automation measures
- Servers with verification requirements may block selfbot behavior
- Consider using the bot primarily in trusted servers or DMs

### Slow mode delays my responses
This is expected behavior:
- The bot automatically detects and respects slow mode
- It will wait the required time and retry sending
- You'll see a ⏱️ reaction when waiting for rate limits
- This prevents errors and ensures your response gets through
- The bot will retry up to 3 times if needed

### "Missing permissions" errors
The bot handles permission issues gracefully:

**Can't send messages:**
- Bot detects the permission error immediately
- Automatically **deletes your `/ai` command** to leave no trace
- Adds 🚫 reaction if possible (or silently fails)
- No crashes or error spam

**Can't react:**
- Reactions are **completely optional**
- Bot still sends the response (text or file)
- Some channels restrict who can add reactions
- You just won't see status indicators (🤔, ✅, etc.)

This ensures the bot **works in all servers where you have basic message permissions**!

## 🔧 Advanced Usage

### Using as a Library

You can import and use the conversation manager in your own scripts:

```python
from discord_selfbot import ConversationManager

# Create manager
manager = ConversationManager(timeout_minutes=20)

# Get or create conversation
client = manager.get_or_create("channel_id", "your_binx_token")

# Send message
response = client.send_message("Hello AI!")

# Reset conversation
manager.reset("channel_id")
```

### Background Cleanup

The selfbot runs a background task that checks for expired conversations every minute. This keeps memory usage low and ensures stale conversations don't persist.

## 📝 Notes

- This is a **selfbot**, not a regular bot
- Only works with your own Discord account
- Responds only to messages YOU send
- Uses your account's permissions and rate limits
- **Against Discord TOS** - use at your own risk

## 🔗 Related Projects

- [BinX AI](https://binx.cc) - The AI service used by this selfbot
- [discord.py-self](https://github.com/dolfies/discord.py-self) - Discord selfbot library

## ⚖️ License

This project is for educational purposes only. Use responsibly and at your own risk.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

**Made for educational purposes. Use responsibly.** ⚠️

