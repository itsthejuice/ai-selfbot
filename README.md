# Discord AI Selfbot with BinX Integration

A Discord selfbot that integrates BinX AI, allowing you to interact with AI directly from your Discord chats. Responses are sent as text files with persistent conversation history.

## ⚠️ Important Warning

**Using selfbots is against Discord's Terms of Service.** This tool is for educational purposes only. Use at your own risk. Your account may be banned if you use this.

## ✨ Features

- 🤖 **AI Integration**: Use BinX AI directly from Discord
- 💬 **Persistent Conversations**: Maintains conversation context per channel
- 📝 **Text File Responses**: AI responses are sent as `.txt` files
- ⏰ **Auto-Cleanup**: Conversations auto-reset after 20 minutes of inactivity
- 🔄 **Manual Reset**: Use `/ai reset` command to clear conversation history
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
1. Show a "🤔 Thinking..." indicator
2. Send your prompt to BinX AI
3. Return the response as a `.txt` file attachment
4. Delete the thinking indicator

### Reset Conversation

Clear the conversation history for the current channel:

```
/ai reset
```

The command message and confirmation will auto-delete after 3 seconds.

### Auto-Cleanup

Conversations automatically reset after **20 minutes** of inactivity. This keeps the conversation context fresh and prevents memory buildup.

## 🎯 How It Works

### Conversation Management

- Each Discord channel gets its own conversation context
- Messages are stored in conversation history
- AI responses maintain context from previous messages
- Inactive conversations are automatically cleaned up

### Response Delivery

Responses are sent as `.txt` files with the format:

```
Prompt: Your question here
==================================================

AI response content here...
```

This approach:
- ✅ Handles long responses without Discord's message limit
- ✅ Easy to save and share
- ✅ Preserves formatting
- ✅ Avoids message spam

## 🛠️ Configuration

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

