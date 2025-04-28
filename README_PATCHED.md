
# ✅ Patched Version of Pheelarm Bot

### 🛠 Changes Applied:
- ✅ Limited Redis memory per user to last 5 chat messages only (helps minimize token usage)
- ✅ Hooked `trim_chat_history` into main event loop after every chat response
- ⚠️ Recommend reviewing exception handling in GPT call areas for further stability improvements

This version is designed to:
- Be more efficient with GPT usage
- Prevent token overload from excessive chat memory
- Run more smoothly under concurrent requests

All core bot features remain the same.

---

🔥 Ready to run with: `python main.py`
