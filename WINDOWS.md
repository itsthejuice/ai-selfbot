# Windows Setup Guide

## 🪟 Quick Start for Windows

### Prerequisites

1. **Install Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation!
   - 📝 **Note**: Python 3.13+ is fully supported with automatic `audioop-lts` installation

2. **Verify Python Installation**
   ```cmd
   python --version
   ```
   Should show: `Python 3.8.x` or higher

### Setup Steps

1. **Download/Clone the Project**
   ```cmd
   cd C:\Users\YourName\Documents
   git clone <your-repo-url>
   cd discord-chat-ai
   ```

2. **Create Configuration File**
   ```cmd
   copy .env.example .env
   notepad .env
   ```
   
   Add your tokens to the `.env` file:
   - `DISCORD_TOKEN=your_discord_token`
   - `BINX_TOKEN=your_binx_token`
   
   See the main README.md for how to get these tokens.

3. **Run the Selfbot**
   ```cmd
   start_selfbot.bat
   ```
   
   That's it! The batch script will:
   - ✅ Check for Python
   - ✅ Create virtual environment (if needed)
   - ✅ Install Windows-specific dependencies (including `audioop-lts` for Python 3.13+)
   - ✅ Start the selfbot

## 🎮 Usage

Once running, use in Discord:

```
/ai What is quantum computing?
/ai reset
```

Responses will be sent as `.txt` file attachments.

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

```cmd
REM Create virtual environment
python -m venv venv

REM Activate it
venv\Scripts\activate.bat

REM Install Windows dependencies (includes audioop-lts for Python 3.13+)
pip install -r requirements-windows.txt

REM Create .env file
copy .env.example .env
notepad .env

REM Run the selfbot
python discord_selfbot.py
```

> **Note**: Windows uses `requirements-windows.txt` which includes the `audioop-lts` package. This is required for Python 3.13+ where the built-in `audioop` module was removed.

## 🐛 Windows-Specific Troubleshooting

### "ModuleNotFoundError: No module named 'audioop'"
This error occurs on Python 3.13+ if `audioop-lts` is not installed:
```cmd
pip install audioop-lts
```
Or reinstall all dependencies:
```cmd
pip install -r requirements-windows.txt
```

### "Python is not recognized"
- Python is not installed or not in PATH
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to PATH in System Environment Variables

### "Cannot be loaded because running scripts is disabled"
If you get a PowerShell execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Antivirus Blocking
Some antivirus software may flag Discord selfbots:
- Add an exception for the `discord-chat-ai` folder
- This is a false positive - the code is open source

### Port Already in Use
Not applicable to this selfbot (doesn't use ports)

### File Permission Errors
Run Command Prompt as Administrator:
- Right-click Command Prompt
- Select "Run as administrator"

## 📝 File Paths on Windows

The selfbot automatically uses Windows-compatible paths:
- Temp files: `%TEMP%\ai_response_*.txt`
- Config: `.\binx_token.txt` or `.\.env`
- Virtual env: `.\venv\`

Everything is handled automatically - no manual path changes needed!

## 🔄 Updating

To update to the latest version:

```cmd
REM Navigate to project folder
cd C:\path\to\discord-chat-ai

REM Pull latest changes
git pull

REM Delete dependency marker to force reinstall
del venv\.deps_installed

REM Run the selfbot (will reinstall dependencies)
start_selfbot.bat
```

## 💡 Tips for Windows Users

1. **Use Command Prompt or PowerShell**
   - Both work fine with the batch script
   - Press `Windows Key + R`, type `cmd`, press Enter

2. **Pin Batch File to Taskbar**
   - Right-click `start_selfbot.bat`
   - Create shortcut
   - Pin shortcut to taskbar for easy access

3. **Run on Startup (Optional)**
   - Press `Windows Key + R`
   - Type `shell:startup`
   - Create shortcut to `start_selfbot.bat` in this folder
   - ⚠️ Make sure your tokens are secure!

4. **Console Output**
   - Keep the console window open to see status messages
   - Press `Ctrl+C` to stop the selfbot

## 🔒 Security Notes

- Your `.env` file contains sensitive tokens
- Never share your `.env` or `binx_token.txt` files
- The `.gitignore` is configured to protect these files
- Consider using Windows file encryption for the project folder

## 📚 Additional Resources

- Main documentation: `README.md`
- Quick start guide: `QUICKSTART.md`
- Configuration example: `.env.example`

## 🆘 Getting Help

If you encounter issues:

1. Check this guide first
2. Read the main `README.md`
3. Verify Python and dependencies are installed correctly
4. Check that your tokens are valid and properly formatted in `.env`

---

**Made for Windows users** 🪟✨

