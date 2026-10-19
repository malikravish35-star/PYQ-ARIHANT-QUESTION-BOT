"""
NEET Quiz Bot - Arihant 34 Years PYQs
MADE BY SPARTA 🫠
"""

import json
import random
import asyncio
import os
import time
import sys
import traceback
import requests as req_lib
from aiohttp import web
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

# ==================== LOAD QUESTIONS ====================
print("📂 Loading questions...", flush=True)
with open("questions.json", "r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

BIO_QUESTIONS = [q for q in ALL_QUESTIONS if q["subject"] == "Biology"]
PHYS_QUESTIONS = [q for q in ALL_QUESTIONS if q["subject"] == "Physics"]
print(f"✅ Loaded {len(ALL_QUESTIONS)} Qs (Bio:{len(BIO_QUESTIONS)}, Phys:{len(PHYS_QUESTIONS)})", flush=True)

# ==================== AUTO-PING EVERY 5 MIN ====================
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

async def auto_ping():
    while True:
        await asyncio.sleep(300)
        if RENDER_URL:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: req_lib.get(f"{RENDER_URL}/", timeout=10)
                )
                print(f"🔄 Ping OK", flush=True)
            except:
                pass

# ==================== HEALTH SERVER (aiohttp) ====================
async def health_handler(request):
    return web.Response(text="NEET Quiz Bot ALIVE! MADE BY SPARTA 🫠")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server on port {port}", flush=True)
    return runner

# ==================== COMPLIMENTS ====================
COMPLIMENTS = [
    "🔥 Kya baat hai! You're on FIRE!",
    "🌟 Brilliant! NEET topper material!",
    "💯 Absolutely perfect! Keep it up!",
    "🧠 Genius move! Your brain is sharp!",
    "⭐ Wah! You're a star performer!",
    "🚀 Rocket speed! Nothing can stop you!",
    "💪 Beast mode ON! Unstoppable!",
    "👏 Claps for you! Well deserved!",
    "🏆 Champion vibes! You're crushing it!",
    "✨ Shining bright! Future doctor confirmed!",
    "🎯 Bull's eye! Perfect aim!",
    "💎 Diamond answer! Precious knowledge!",
    "🦁 Sher! Lion-hearted answer!",
    "⚡ Electric! You're charged up!",
    "🎪 Masterclass! What an answer!",
    "🌈 Beautiful! That was flawless!",
    "🔑 You cracked it like a pro!",
    "🏅 Gold medal answer!",
    "🔥 Tandoor! Bilkan sahi jawab!",
    "💫 Supernova level answer!",
    "🎓 Professor level knowledge!",
    "🌟 SPARTA ka soldier! Mubarak ho!",
    "⚔️ Warrior mind! Correct strike!",
    "💥 BOOM! Sahi jawaab!",
    "🏹 Arjuna level accuracy!",
    "🌊 Tsunami of knowledge!",
]

WRONG_ENCOURAGEMENT = [
    "💪 No worries! Keep trying!",
    "📚 Learning from mistakes = Growth!",
    "🌱 Every wrong answer makes you stronger!",
    "🔄 Don't give up! Revision is key!",
    "🧭 Right path pe ho, bas thoda aur!",
    "📖 Review karo, next time pakka!",
    "🎯 Close one! Next time nail it!",
    "💡 Mistakes = proof you're trying!",
    "🌟 Haar ke baad hi jeet aati hai!",
    "⚡ Next question tera hoga!",
]

TIMEOUT_MSGS = [
    "⏰ Time's up! 60 seconds khatam!",
    "⏰ Time khatam! Agle question pe chalte hain!",
    "⏰ Clock tick tock... Time over!",
]

FOOTER = "\n\n━━━━━━━━━━━━━━━━━━━━\n🫠 **MADE BY SPARTA**"

# ==================== USER STATE ====================
user_data = {}

def get_user_state(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "questions": [], "current_index": 0,
            "correct": 0, "wrong": 0, "timeout_count": 0,
            "answered": False, "timer_task": None,
        }
    return user_data[user_id]

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"🤖 *Namaste {user.first_name}!*\n\n"
        f"🧬 *NEET Quiz Bot* mein swagat hai!\n\n"
        f"📚 *Arihant 34 Years PYQs*\n"
        f"📝 Biology: {len(BIO_QUESTIONS)} Questions\n"
        f"⚛️ Physics: {len(PHYS_QUESTIONS)} Questions\n"
        f"📋 Total: {len(ALL_QUESTIONS)} Questions\n\n"
        f"⏱️ Har question: *60 seconds*\n"
        f"✅ Sahi jawab = Compliment!\n\n"
        f"*Commands:* /help\n"
        f"*Choose subject:* 👇"
        f"{FOOTER}"
    )
    keyboard = [
        [InlineKeyboardButton("🧬 Biology", callback_data="subject_Biology"),
         InlineKeyboardButton("⚛️ Physics", callback_data="subject_Physics")],
        [InlineKeyboardButton("🎯 Both (Mixed)", callback_data="subject_Both")],
    ]
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *BOT COMMANDS*\n\n━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 /start — Quiz shuru karo 🎮\n"
        "🔹 /help — Help message 📖\n"
        "🔹 /bio — Biology quiz 🧬\n"
        "🔹 /phys — Physics quiz ⚛️\n"
        "🔹 /mixed — Mixed quiz 🎯\n"
        "🔹 /score — Current score 📊\n"
        "🔹 /stats — Total stats 🏆\n"
        "🔹 /restart — Reset quiz 🔄\n"
        "🔹 /about — Bot info 🤖\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "⏱️ 60s per question | ✅ Compliments!\n"
        f"{FOOTER}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_user_state(update.effective_user.id)
    if not state["questions"]:
        await update.message.reply_text("📊 Pehle quiz khelo! /start karo! 🎮" + FOOTER, parse_mode=ParseMode.MARKDOWN)
        return
    total = len(state["questions"])
    current = state["current_index"] + 1
    c, w = state["correct"], state["wrong"]
    pct = round((c / (c + w)) * 100) if (c + w) > 0 else 0
    filled = int((current / total) * 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)
    text = (f"📊 *SCORE*\n\n📝 Q: {current}/{total}\n\n{bar}\n\n"
            f"✅ Correct: *{c}*\n❌ Wrong: *{w}*\n📈 Accuracy: *{pct}%*\n{FOOTER}")
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_user_state(update.effective_user.id)
    c, w, t = state["correct"], state["wrong"], state["timeout_count"]
    text = (f"🏆 *STATS*\n\n📚 Available: *{len(ALL_QUESTIONS)}*\n"
            f"🧬 Bio: *{len(BIO_QUESTIONS)}* | ⚛️ Phys: *{len(PHYS_QUESTIONS)}*\n\n"
            f"📝 Attempted: *{c + w}*\n✅ Correct: *{c}*\n❌ Wrong: *{w}*\n⏰ Timeout: *{t}*\n{FOOTER}")
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def bio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _direct_start(update, BIO_QUESTIONS, "Biology", "🧬 BIOLOGY")

async def phys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _direct_start(update, PHYS_QUESTIONS, "Physics", "⚛️ PHYSICS")

async def mixed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _direct_start(update, ALL_QUESTIONS, "Both", "🎯 MIXED")


async def _direct_start(update, questions, subject, title):
    state = get_user_state(update.effective_user.id)
    if state.get("timer_task"):
        state["timer_task"].cancel()
    state["questions"] = random.sample(questions, len(questions))
    random.shuffle(state["questions"])
    state["current_index"] = 0
    state["correct"] = 0
    state["wrong"] = 0
    state["timeout_count"] = 0
    state["answered"] = False
    await update.message.reply_text(f"{title}\n📝 {len(questions)} Qs | ⏱️ 60s\n\nStarting... 🚀{FOOTER}", parse_mode=ParseMode.MARKDOWN)
    await asyncio.sleep(1)
    await _send_q(update, context, update.effective_user.id)


async def _send_q(update, context, user_id):
    state = get_user_state(user_id)
    if state["current_index"] >= len(state["questions"]):
        await _show_results_msg(update, user_id)
        return
    q = state["questions"][state["current_index"]]
    total = len(state["questions"])
    cur = state["current_index"] + 1
    state["answered"] = False
    em = "🧬" if q["subject"] == "Biology" else "⚛️"
    src = f"\n📌 {q['source']}" if q.get("source") else ""
    txt = f"{em} *Q{cur}/{total}* | ⏱️ 60s\n━━━━━━━━━━━━━━━━━━━━\n\n{q['question']}{src}\n"
    if q.get("has_image"):
        txt = f"🖼️ *Refer to diagram*\n\n{txt}"
    txt += FOOTER
    letters = ["A", "B", "C", "D"]
    kb = [[InlineKeyboardButton(f"{letters[i]}. {o[:80]}", callback_data=f"ans_{i}")] for i, o in enumerate(q["options"])]
    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
    state["timer_task"] = asyncio.create_task(_timeout(update, context, user_id))


async def _timeout(update, context, user_id):
    await asyncio.sleep(60)
    state = get_user_state(user_id)
    if not state["answered"]:
        state["timeout_count"] += 1
        state["wrong"] += 1
        q = state["questions"][state["current_index"]]
        cl = ["A", "B", "C", "D"][q["answer"]]
        txt = f"{random.choice(TIMEOUT_MSGS)}\n\n❌ Time's Up!\n✅ Ans: *{cl}. {q['options'][q['answer']]}*{FOOTER}"
        kb = [[InlineKeyboardButton("➡️ Next", callback_data="next")]]
        await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


async def _show_results_msg(update, user_id):
    state = get_user_state(user_id)
    total = len(state["questions"])
    c, w = state["correct"], state["wrong"]
    pct = round((c / total) * 100) if total > 0 else 0
    if pct >= 90: t, e = "🏆 LEGENDARY!", "🥇"
    elif pct >= 70: t, e = "⭐ EXCELLENT!", "🥈"
    elif pct >= 50: t, e = "💪 GOOD!", "🥉"
    else: t, e = "🌱 KEEP GOING!", "💪"
    txt = f"{e} *QUIZ COMPLETE!*\n\n{t}\n\n📝 {total} | ✅ {c} | ❌ {w} | 📈 {pct}%\n{FOOTER}"
    await update.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN)


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_user_state(update.effective_user.id)
    if state.get("timer_task"):
        state["timer_task"].cancel()
    state["questions"] = []
    state["current_index"] = 0
    state["correct"] = state["wrong"] = state["timeout_count"] = 0
    state["answered"] = False
    await update.message.reply_text("🔄 *Reset!*\n/bio | /phys | /mixed | /start" + FOOTER, parse_mode=ParseMode.MARKDOWN)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *NEET Quiz Bot*\n📖 Arihant 34 Yrs PYQs\n\n"
        f"🧬 Bio: *{len(BIO_QUESTIONS)}* | ⚛️ Phys: *{len(PHYS_QUESTIONS)}*\n📋 Total: *{len(ALL_QUESTIONS)}*\n\n"
        "⏱️ 60s | ✅ Compliments | 🔄 Auto-ping\n\n"
        "💻 Python + Telegram API\n🌐 Render.com\n\n🫠 **MADE BY SPARTA**"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ==================== CALLBACK HANDLER ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("subject_"):
        await start_quiz(query, context, data.replace("subject_", ""))
    elif data.startswith("ans_"):
        await handle_answer(query, int(data.replace("ans_", "")))
    elif data == "next":
        await send_next(query, context)
    elif data.startswith("replay_"):
        await start_quiz(query, context, data.replace("replay_", ""))


async def start_quiz(query, context, subject):
    state = get_user_state(query.from_user.id)
    if state.get("timer_task"):
        state["timer_task"].cancel()
    if subject == "Biology":
        state["questions"] = random.sample(BIO_QUESTIONS, len(BIO_QUESTIONS))
    elif subject == "Physics":
        state["questions"] = random.sample(PHYS_QUESTIONS, len(PHYS_QUESTIONS))
    else:
        state["questions"] = random.sample(ALL_QUESTIONS, len(ALL_QUESTIONS))
    random.shuffle(state["questions"])
    state["current_index"] = 0
    state["correct"] = state["wrong"] = state["timeout_count"] = 0
    state["answered"] = False
    total = len(state["questions"])
    await query.edit_message_text(
        f"🎮 *Started!*\n\n📚 {subject} | 📝 {total} Qs | ⏱️ 60s\n\nGoing... 🚀{FOOTER}",
        parse_mode=ParseMode.MARKDOWN)
    await asyncio.sleep(1.5)
    await send_question(query, context)


async def send_question(query, context):
    state = get_user_state(query.from_user.id)
    if state["current_index"] >= len(state["questions"]):
        await show_results(query, context)
        return
    q = state["questions"][state["current_index"]]
    total = len(state["questions"])
    cur = state["current_index"] + 1
    state["answered"] = False
    em = "🧬" if q["subject"] == "Biology" else "⚛️"
    src = f"\n📌 {q['source']}" if q.get("source") else ""
    txt = f"{em} *Q{cur}/{total}* | ⏱️ 60s\n━━━━━━━━━━━━━━━━━━━━\n\n{q['question']}{src}\n"
    if q.get("has_image"):
        txt = f"🖼️ *Refer to diagram*\n\n{txt}"
    txt += FOOTER
    letters = ["A", "B", "C", "D"]
    kb = [[InlineKeyboardButton(f"{letters[i]}. {o[:80]}", callback_data=f"ans_{i}")] for i, o in enumerate(q["options"])]
    try:
        await query.edit_message_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
    except:
        await query.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
    state["timer_task"] = asyncio.create_task(question_timeout(query, context, query.from_user.id))


async def question_timeout(query, context, user_id):
    await asyncio.sleep(60)
    state = get_user_state(user_id)
    if not state["answered"]:
        state["timeout_count"] += 1
        state["wrong"] += 1
        q = state["questions"][state["current_index"]]
        cl = ["A", "B", "C", "D"][q["answer"]]
        txt = f"{random.choice(TIMEOUT_MSGS)}\n\n❌ Time's Up!\n✅ Ans: *{cl}. {q['options'][q['answer']]}*{FOOTER}"
        kb = [[InlineKeyboardButton("➡️ Next", callback_data="next")]]
        try:
            await query.edit_message_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
        except:
            await query.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


async def handle_answer(query, selected):
    state = get_user_state(query.from_user.id)
    if state["answered"]:
        await query.answer("Already answered! Press Next ⏭️", show_alert=True)
        return
    state["answered"] = True
    if state.get("timer_task"):
        state["timer_task"].cancel()
    q = state["questions"][state["current_index"]]
    cl = ["A", "B", "C", "D"][q["answer"]]
    sl = ["A", "B", "C", "D"][selected]
    if selected == q["answer"]:
        state["correct"] += 1
        txt = f"{random.choice(COMPLIMENTS)}\n\n✅ *CORRECT!*\n🎉 *{cl}. {q['options'][q['answer']]}*\n\n📊 {state['correct']}✅ | {state['wrong']}❌{FOOTER}"
    else:
        state["wrong"] += 1
        txt = f"{random.choice(WRONG_ENCOURAGEMENT)}\n\n❌ *Wrong!*\nYou: *{sl}. {q['options'][selected]}*\n✅ Correct: *{cl}. {q['options'][q['answer']]}*\n\n📊 {state['correct']}✅ | {state['wrong']}❌{FOOTER}"
    kb = [[InlineKeyboardButton("➡️ Next", callback_data="next")]]
    await query.edit_message_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


async def send_next(query, context):
    state = get_user_state(query.from_user.id)
    state["current_index"] += 1
    if state["current_index"] >= len(state["questions"]):
        await show_results(query, context)
    else:
        await send_question(query, context)


async def show_results(query, context):
    state = get_user_state(query.from_user.id)
    total = len(state["questions"])
    c, w, t = state["correct"], state["wrong"], state["timeout_count"]
    pct = round((c / total) * 100) if total > 0 else 0
    if pct >= 90: title, emoji = "🏆 LEGENDARY!", "🥇"
    elif pct >= 70: title, emoji = "⭐ EXCELLENT!", "🥈"
    elif pct >= 50: title, emoji = "💪 GOOD!", "🥉"
    elif pct >= 30: title, emoji = "📚 AVERAGE!", "📖"
    else: title, emoji = "🌱 KEEP GOING!", "💪"
    txt = (f"{emoji} *QUIZ COMPLETE!*\n\n{title}\n\n━━━━━━━━━━━━━━━━━━━━\n"
           f"📝 Total: *{total}*\n✅ Correct: *{c}*\n❌ Wrong: *{w}*\n⏰ Timeout: *{t}*\n📈 Score: *{pct}%*\n\n"
           f"━━━━━━━━━━━━━━━━━━━━\n🎮 Play Again:\n")
    kb = [[InlineKeyboardButton("🧬 Biology", callback_data="replay_Biology"),
           InlineKeyboardButton("⚛️ Physics", callback_data="replay_Physics")],
          [InlineKeyboardButton("🎯 Both", callback_data="replay_Both")]]
    txt += FOOTER
    try:
        await query.edit_message_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
    except:
        await query.message.reply_text(txt, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))

# ==================== BOT INIT ====================
async def post_init(application):
    await application.bot.set_my_commands([
        ("start", "🎮 Quiz shuru karo"),
        ("help", "📖 Help"),
        ("bio", "🧬 Biology Quiz"),
        ("phys", "⚛️ Physics Quiz"),
        ("mixed", "🎯 Mixed Quiz"),
        ("score", "📊 Score"),
        ("stats", "🏆 Stats"),
        ("restart", "🔄 Reset"),
        ("about", "🤖 About"),
    ])
    print("✅ Commands menu set!", flush=True)

# ==================== MAIN ====================
async def main():
    TOKEN = os.environ.get("BOT_TOKEN", "")
    if not TOKEN:
        print("❌ BOT_TOKEN not set!", flush=True)
        sys.exit(1)

    print("=" * 40, flush=True)
    print("🤖 NEET Quiz Bot", flush=True)
    print(f"📚 {len(ALL_QUESTIONS)} Questions", flush=True)
    print("🫠 MADE BY SPARTA", flush=True)
    print("=" * 40, flush=True)

    # Start web server for Render health checks
    runner = await start_web_server()

    # Start auto-ping task
    asyncio.create_task(auto_ping())

    # Build Telegram bot
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("score", score_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("bio", bio_command))
    app.add_handler(CommandHandler("phys", phys_command))
    app.add_handler(CommandHandler("mixed", mixed_command))
    app.add_handler(CommandHandler("restart", restart_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot starting!", flush=True)

    # Initialize and start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    print("✅ Bot is LIVE and polling!", flush=True)

    # Keep running forever
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"💀 FATAL: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
