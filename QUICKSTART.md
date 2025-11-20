# Quick Start Guide - Discord AI Selfbot

> **Windows Users**: Use `start_selfbot.bat` instead of `.sh` commands. See [WINDOWS.md](WINDOWS.md) for detailed Windows setup.

## ⚡ 60-Second Setup

### Step 1: Get Your Discord Token

**Easiest Method - Local Storage:**
1. Open Discord in browser (discord.com)
2. Press `F12` → **Application** tab (or **Storage** in Firefox)
3. Left sidebar: **Local Storage** → `https://discord.com`
4. Find key `token` and copy its value (remove quotes)

**Alternative - Console:**
```javascript
JSON.parse(localStorage.token)
```
Or try:
```javascript
window.webpackChunkdiscord_app.push([[Math.random()],{},e=>{Object.values(e.c).find(e=>e?.exports?.default?.getToken).exports.default.getToken()}])
```

### Step 2: Get Your BinX Token
1. Go to [binx.cc](https://binx.cc) and login
2. Press `F12` → Network tab
3. Go to AI Chat and send a message
4. Find `/api/ai-chat` request
5. Copy the `Authorization` header (remove "Bearer ")

### Step 3: Configure

**Linux/Mac:**
```bash
cp .env.example .env
nano .env  # Add your tokens
```

**Windows:**
```cmd
copy .env.example .env
notepad .env
```

### Step 4: Run

**Linux/Mac:**
```bash
./start_selfbot.sh
```

**Windows:**
```cmd
start_selfbot.bat
```

## 🎮 Usage

### Send AI Prompts
```
/ai What is artificial intelligence?
```

### Reset Conversation
```
/ai reset
```

### Auto-Cleanup
- Conversations auto-reset after 20 minutes of inactivity

### Response Format
- **Short responses** (<2000 chars): Sent as regular text messages
- **Long responses** (≥2000 chars): Sent as `.txt` file attachments

### Permission Handling
- Bot gracefully handles channels where you lack permissions
- Automatically deletes your command if it can't respond (no trace left)

## ⚠️ Important

- **This is a selfbot** (against Discord TOS)
- Use at your own risk
- Only responds to YOUR messages
- Don't spam or abuse

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.

## 🆘 Quick Troubleshooting

**Not working?**
- Check tokens in `.env` are correct
- Make sure you're sending from YOUR account
- Try `/ai reset` if AI doesn't respond
- Check `python3 discord_selfbot.py` output for errors

**Still stuck?**
- Read the full README.md
- Check that binx-ai folder is present
- Verify Python 3.8+ is installed

