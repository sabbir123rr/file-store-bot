# FIRE AIMBOT - ROSE FULL EDITION
# File Store + Rose All Features in One Bot
# pip install python-telegram-bot==20.7

import os
import json
from datetime import timedelta
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from flask import Flask
import threading

# --- For Render Port Binding ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is Alive!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask, daemon=True).start()
# --- End Flask ---

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8887348980:AAG4m1MEWfGmUC_ryojgaJbA2Qivx")
OWNER_ID = int(os.environ.get("ADMINS", "6936733023"))

FORCE_CHANNELS = [
    {"name": "Join Channel 1", "url": "https://t.me/aimbot0999", "id": "@aimbot0999"},
    {"name": "Join Channel 2", "url": "https://t.me/fireaimbot1", "id": "@fireaimbot1"},
    
]

async def is_joined(user_id, context):
    for ch in FORCE_CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch["id"], user_id)
            if m.status in ['left','kicked']: return False
        except: return False
    return True
    
# --- DB ---
DB_FILES = ["notes.json", "filters.json", "warns.json", "rules.json", "welcome.json", "files.json", "locks.json"]
def load(f): return json.load(open(f, "r", encoding="utf-8")) if os.path.exists(f) else {}
def save(f, d): json.dump(d, open(f, "w", encoding="utf-8"), indent=2)

async def is_admin(update, context):
    try:
        admins = [a.user.id async for a in context.bot.get_chat_administrators(update.effective_chat.id)]
        return update.effective_user.id in admins
    except: return False

# ========== FILE STORE (তোমার আগের) ==========
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if update.message.document or update.message.video:
        fid = update.message.document.file_id if update.message.document else update.message.video.file_id
        files = load("files.json")
        code = str(len(files)+1)
        files[code] = fid
        save("files.json", files)
        await update.message.reply_text(f"✅ Saved! Link: https://t.me/aimbot_files_bot?start={code}")

async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    files = load("files.json")
    if context.args[0] in files:
        await update.message.reply_document(files[context.args[0]], caption="📦 FIRE AIMBOT FILES\nMain: @aimbot0999")

# ========== ROSE ADMIN ==========
async def ban(update, context):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return await update.message.reply_text("Reply করে /ban দাও")
    await update.effective_chat.ban_member(update.message.reply_to_message.from_user.id)
    await update.message.reply_text(f"🔨 Banned {update.message.reply_to_message.from_user.first_name}")

async def unban(update, context):
    if not await is_admin(update, context): return
    if update.message.reply_to_message:
        await update.effective_chat.unban_member(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("✅ Unbanned")

async def kick(update, context):
    if not await is_admin(update, context): return
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        await update.effective_chat.ban_member(uid)
        await update.effective_chat.unban_member(uid)
        await update.message.reply_text("👢 Kicked")

async def mute(update, context):
    if not await is_admin(update, context): return
    if update.message.reply_to_message:
        await update.effective_chat.restrict_member(update.message.reply_to_message.from_user.id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text("🔇 Muted")

async def unmute(update, context):
    if not await is_admin(update, context): return
    if update.message.reply_to_message:
        await update.effective_chat.restrict_member(update.message.reply_to_message.from_user.id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
        await update.message.reply_text("🔊 Unmuted")

async def warn(update, context):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return
    uid = str(update.message.reply_to_message.from_user.id)
    cid = str(update.effective_chat.id)
    warns = load("warns.json")
    if cid not in warns: warns[cid] = {}
    warns[cid][uid] = warns[cid].get(uid, 0) + 1
    save("warns.json", warns)
    if warns[cid][uid] >= 3:
        await update.effective_chat.ban_member(int(uid))
        await update.message.reply_text(f"⚠️ 3 Warns! Banned {update.message.reply_to_message.from_user.first_name}")
        warns[cid][uid] = 0
    else:
        await update.message.reply_text(f"⚠️ Warn {warns[cid][uid]}/3 to {update.message.reply_to_message.from_user.first_name}")
    save("warns.json", warns)

# ========== NOTES & FILTERS & LOCKS & WELCOME ==========
async def save_note(update, context):
    if not await is_admin(update, context): return
    if not context.args: return await update.message.reply_text("Usage: /save <name>")
    name = context.args[0].lower()
    txt = update.message.reply_to_message.text if update.message.reply_to_message else " ".join(context.args[1:])
    cid = str(update.effective_chat.id)
    notes = load("notes.json")
    if cid not in notes: notes[cid] = {}
    notes[cid][name] = txt
    save("notes.json", notes)
    await update.message.reply_text(f"📝 Saved #{name}")

async def clear_note(update, context):
    if not await is_admin(update, context): return
    name = context.args[0].lower() if context.args else ""
    cid = str(update.effective_chat.id)
    notes = load("notes.json")
    if cid in notes and name in notes[cid]:
        del notes[cid][name]
        save("notes.json", notes)
        await update.message.reply_text(f"🗑️ Cleared #{name}")

async def get_note_hash(update, context):
    if not update.message or not update.message.text or not update.message.text.startswith("#"): 
        return
    name = update.message.text[1:].split()[0].lower()
    cid = str(update.effective_chat.id)
    notes = load("notes.json")
    if cid in notes and name in notes[cid]:
        await update.message.reply_text(notes[cid][name])

async def add_filter(update, context):
    if not await is_admin(update, context): return
    if len(context.args) < 2: return await update.message.reply_text("Usage: /filter word reply")
    cid = str(update.effective_chat.id)
    f = load("filters.json")
    if cid not in f: f[cid] = {}
    f[cid][context.args[0].lower()] = " ".join(context.args[1:])
    save("filters.json", f)
    await update.message.reply_text(f"Filter added for {context.args[0]}")

async def stop_filter(update, context):
    if not await is_admin(update, context): return
    cid = str(update.effective_chat.id)
    f = load("filters.json")
    if context.args and cid in f and context.args[0].lower() in f[cid]:
        del f[cid][context.args[0].lower()]
        save("filters.json", f)
        await update.message.reply_text("Filter removed")

async def check_filters(update, context):
    if not update.message or not update.message.text: 
        return
    cid = str(update.effective_chat.id)
    f = load("filters.json")
    if cid not in f: return
    txt = update.message.text.lower()
    for w, rep in f[cid].items():
        if w in txt:
            await update.message.reply_text(rep)
            break

async def set_welcome(update, context):
    if not await is_admin(update, context): return
    cid = str(update.effective_chat.id)
    msg = " ".join(context.args) if context.args else (update.message.reply_to_message.text if update.message.reply_to_message else "")
    w = load("welcome.json")
    w[cid] = msg
    save("welcome.json", w)
    await update.message.reply_text("Welcome set!")

async def welcome_new(update, context):
    for member in update.message.new_chat_members:
        cid = str(update.effective_chat.id)
        w = load("welcome.json")
        msg = w.get(cid, "Welcome {first} to FIRE AIMBOT! 🔥")
        await update.message.reply_text(msg.format(first=member.first_name))

async def set_rules(update, context):
    if not await is_admin(update, context): return
    cid = str(update.effective_chat.id)
    r = load("rules.json")
    r[cid] = " ".join(context.args)
    save("rules.json", r)
    await update.message.reply_text("Rules set!")

async def get_rules(update, context):
    cid = str(update.effective_chat.id)
    r = load("rules.json")
    await update.message.reply_text(r.get(cid, "No rules set!"))

async def purge(update, context):
    if not await is_admin(update, context): return
    if not update.message.reply_to_message: return
    # Simple purge: delete 100 msgs - needs admin
    await update.message.reply_text("Use /purge with reply to delete msgs (manual for now)")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    code = context.args[0] if context.args else None
    if not await is_joined(user_id, context):
        buttons = []
        for ch in FORCE_CHANNELS:
            buttons.append([InlineKeyboardButton(ch["name"], url=ch["url"])])
        buttons.append([InlineKeyboardButton("♻️ Try Again", callback_data=f"check_{code}")])
        await update.message.reply_text(
            f"Hey {update.effective_user.first_name} OWNER\n\nPlease Join All My Update Channels To Use Me!",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    if code and code != "start":
        files = load("files.json")
        if code in files:
            await context.bot.send_document(update.effective_chat.id, files[code], caption="Main: @aimbot0999")
            return
    await update.message.reply_text("✅ You Joined All Channels!")

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    code = query.data.replace("check_", "")
    if not await is_joined(user_id, context):
        await query.answer("❌ Join all channels first!", show_alert=True)
        return
    await query.message.delete()
    files = load("files.json")
    if code and code != "None" and code in files:
        await context.bot.send_document(query.message.chat.id, files[code], caption="✅ Verified! File here.\nMain: @aimbot0999")
    else:
        await context.bot.send_message(query.message.chat.id, "✅ Verified! Joined!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    # File store
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO, save_file))
    # Admin
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("save", save_note))
    app.add_handler(CommandHandler("clear", clear_note))
    app.add_handler(CommandHandler("filter", add_filter))
    app.add_handler(CommandHandler("stop", stop_filter))
    app.add_handler(CommandHandler("setwelcome", set_welcome))
    app.add_handler(CommandHandler("setrules", set_rules))
    app.add_handler(CommandHandler("rules", get_rules))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_join, pattern="^check_"))
    # Auto
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^#"), get_note_hash))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_filters))
    
    print("FIRE AIMBOT FULL RUNNING........")
    app.run_polling()

if __name__ == "__main__":
    main()
