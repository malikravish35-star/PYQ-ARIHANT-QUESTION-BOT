"""
NEET Quiz Bot - Arihant 34 Years PYQs
MADE BY SPARTA 🫠
"""

import json
import random
import asyncio
import os
import threading
import time
import sys
import traceback
import requests as req_lib
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

# ==================== LOAD QUESTIONS ====================
print("📂 Loading questions...")
with open("questions.json", "r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

BIO_QUESTIONS = [q for q in ALL_QUESTIONS if q["subject"] == "Biology"]
PHYS_QUESTIONS = [q for q in ALL_QUESTIONS if q["subject"] == "Physics"]
print(f"✅ Loaded {len(ALL_QUESTIONS)} questions (Bio: {len(BIO_QUESTIONS)}, Phys: {len(PHYS_QUESTIONS)})")

# ==================== HEALTH SERVER (KEEPS RENDER ALIVE) ====================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"NEET Quiz Bot is ALIVE! | MADE BY SPARTA")
    
    def log_message(self, format, *args):
        pass

def health_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        print(f"🌐 Health server on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Health server error: {e}")

# ==================== AUTO-PING EVERY 5 MIN ====================
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

def auto_ping():
    while True:
        time.sleep(300)
        if RENDER_URL:
            try:
                r = req_lib.get(f"{RENDER_URL}/", timeout=10)
                print(f"🔄 Ping: {r.status_code} - Alive!")
            except Exception as e:
                print(f"⚠️ Ping failed: {e}")

def start_background_tasks():
    # Health server thread
    t1 = threading.Thread(target=health_server, daemon=True)
    t1.start()
    # Auto-ping thread
    t2 = threading.Thread(target=auto_ping, daemon=True)
    t2.start()
    print("✅ Background tasks started (health + auto-ping)")

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
    "🏅 Gold medal answer! Sone pe suhaga!",
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
    "⏰ 60 seconds ho gaye! Aage badhte hain!",
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

# ==================== HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        text = (
            f"🤖 *Namaste {user.first_name}!*\n\n"
            f"🧬 *NEET Quiz Bot* mein swagat hai!\n\n"
            f"📚 *Arihant 34 Years PYQs*\n"
            f"📝 Biology: {len(BIO_QUESTIONS)} Questions\n"
            f"⚛️ Physics: {len(PHYS_QUESTIONS)} Questions\n"
            f"📋 Total: {len(ALL_QUESTIONS)} Questions\n\n"
            f"⏱️ Har question ke liye *60 seconds* ka time hai!\n"
            f"✅ Sahi jawab pe milega compliment!\n\n"
            f"*Commands:* /help\n"
            f"*Choose your subject:* 👇"
            f"{FOOTER}"
        )
        keyboard = [
            [InlineKeyboardButton("🧬 Biology", callback_data="subject_Biology"),
             InlineKeyboardButton("⚛️ Physics", callback_data="subject_Physics")],
            [InlineKeyboardButton("🎯 Both (Mixed)", callback_data="subject_Both")],
        ]
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print(f"❌ start_command error: {e}")
        traceback.print_exc()


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = (
            "📖 *BOT COMMANDS*\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔹 /start — Quiz shuru karo 🎮\n"
            "🔹 /help — Ye help message 📖\n"
            "🔹 /score — Current score dekho 📊\n"
            "🔹 /stats — Total stats dekho 🏆\n"
            "🔹 /bio — Sirf Biology quiz 🧬\n"
            "🔹 /phys — Sirf Physics quiz ⚛️\n"
            "🔹 /mixed — Mixed quiz 🎯\n"
            "🔹 /restart — Quiz restart 🔄\n"
            "🔹 /about — Bot info 🤖\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "⏱️ Time: *60 seconds* per question\n"
            "✅ Sahi = Compliment! ❌ Galat = Motivation!\n"
            f"{FOOTER}"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"❌ help_command error: {e}")


async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        state = get_user_state(user_id)
        if not state["questions"]:
            await update.message.reply_text(
                "📊 *Abhi tak koi quiz nahi khela!*\n/start karo! 🎮" + FOOTER,
                parse_mode=ParseMode.MARKDOWN)
            return
        total = len(state["questions"])
        current = state["current_index"] + 1
        correct = state["correct"]
        wrong = state["wrong"]
        attempted = correct + wrong
        pct = round((correct / attempted) * 100) if attempted > 0 else 0
        filled = int((current / total) * 10)
        bar = "🟩" * filled + "⬜" * (10 - filled)
        text = (
            f"📊 *CURRENT SCORE*\n\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 Question: {current}/{total}\n\n{bar}\n\n"
            f"✅ Correct: *{correct}*\n❌ Wrong: *{wrong}*\n"
            f"⏰ Timeout: *{state['timeout_count']}*\n📈 Accuracy: *{pct}%*\n{FOOTER}"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"❌ score_command error: {e}")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        state = get_user_state(user_id)
        if not state["questions"]:
            await update.message.reply_text(
                "📊 *No Stats Yet!* Pehle quiz khelo! /start karo!" + FOOTER,
                parse_mode=ParseMode.MARKDOWN)
            return
        text = (
            f"🏆 *YOUR STATS*\n\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📚 Total Available: *{len(ALL_QUESTIONS)}*\n"
            f"🧬 Biology: *{len(BIO_QUESTIONS)}*\n⚛️ Physics: *{len(PHYS_QUESTIONS)}*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 Attempted: *{state['correct'] + state['wrong']}*\n"
            f"✅ Correct: *{state['correct']}*\n❌ Wrong: *{state['wrong']}*\n"
            f"⏰ Timeout: *{state['timeout_count']}*\n{FOOTER}"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"❌ stats_command error: {e}")


async def bio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _start_direct_quiz(update, context, BIO_QUESTIONS, "Biology", "🧬 BIOLOGY QUIZ")

async def phys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _start_direct_quiz(update, context, PHYS_QUESTIONS, "Physics", "⚛️ PHYSICS QUIZ")

async def mixed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _start_direct_quiz(update, context, ALL_QUESTIONS, "Both", "🎯 MIXED QUIZ")


async def _start_direct_quiz(update, context, questions, subject, title):
    try:
        user_id = update.effective_user.id
        state = get_user_state(user_id)
        if state.get("timer_task"):
            state["timer_task"].cancel()
        
        state["questions"] = random.sample(questions, len(questions))
        random.shuffle(state["questions"])
        state["current_index"] = 0
        state["correct"] = 0
        state["wrong"] = 0
        state["timeout_count"] = 0
        state["answered"] = False
        state["subject"] = subject
        
        text = f"{title}\n\n📝 Questions: *{len(questions)}*\n⏱️ Time: *60s*\n\nStarting... 🚀{FOOTER}"
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(1)
        await _send_question_to_user(update, context, user_id)
    except Exception as e:
        print(f"❌ _start_direct_quiz error: {e}")
        traceback.print_exc()


async def _send_question_to_user(update, context, user_id):
    """Send question directly to user via update.message"""
    try:
        state = get_user_state(user_id)
        if state["current_index"] >= len(state["questions"]):
            await show_results_for_user(update, context, user_id)
            return
        
        q = state["questions"][state["current_index"]]
        total = len(state["questions"])
        current = state["current_index"] + 1
        state["answered"] = False
        
        subj_emoji = "🧬" if q["subject"] == "Biology" else "⚛️"
        source = f"\n📌 {q['source']}" if q.get("source") else ""
        
        q_text = f"{subj_emoji} *Q{current}/{total}* | ⏱️ 60s\n━━━━━━━━━━━━━━━━━━━━\n\n{q['question']}{source}\n"
        
        if q.get("has_image"):
            q_text = f"🖼️ *Refer to diagram*\n\n{q_text}"
        q_text += FOOTER
        
        letters = ["A", "B", "C", "D"]
        keyboard = []
        for i, opt in enumerate(q["options"]):
            opt_d = opt[:80] + "..." if len(opt) > 80 else opt
            keyboard.append([InlineKeyboardButton(f"{letters[i]}. {opt_d}", callback_data=f"ans_{i}")])
        
        msg = await update.message.reply_text(q_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
        state["last_message_id"] = msg.message_id
        
        # Timer
        state["timer_task"] = asyncio.create_task(_question_timeout_user(update, context, user_id))
    except Exception as e:
        print(f"❌ _send_question_to_user error: {e}")
        traceback.print_exc()


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        state = get_user_state(user_id)
        if state.get("timer_task"):
            state["timer_task"].cancel()
        state["questions"] = []
        state["current_index"] = 0
        state["correct"] = 0
        state["wrong"] = 0
        state["timeout_count"] = 0
        state["answered"] = False
        await update.message.reply_text(
            "🔄 *Quiz Reset!*\n\n/bio — Biology\n/phys — Physics\n/mixed — Both\n/start — Menu" + FOOTER,
            parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"❌ restart error: {e}")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = (
            "🤖 *ABOUT THIS BOT*\n\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "📚 *NEET Quiz Bot*\n📖 Arihant 34 Years PYQs\n\n"
            f"🧬 Biology: *{len(BIO_QUESTIONS)}*\n⚛️ Physics: *{len(PHYS_QUESTIONS)}*\n📋 Total: *{len(ALL_QUESTIONS)}*\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "⏱️ 60s timer | ✅ Compliments | 🔄 Auto-ping\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n💻 Python + Telegram API\n🌐 Hosted: Render.com\n\n🫠 **MADE BY SPARTA**"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"❌ about error: {e}")


# ==================== BUTTON HANDLER ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        user_id = query.from_user.id

        if data.startswith("subject_"):
            subject = data.replace("subject_", "")
            await start_quiz(query, context, subject)
        elif data.startswith("ans_"):
            selected = int(data.replace("ans_", ""))
            await handle_answer(query, context, selected)
        elif data == "next":
            await send_next_question(query, context)
        elif data == "restart":
            await start_command(update.callback_query.message, context)
        elif data.startswith("replay_"):
            subject = data.replace("replay_", "")
            await start_quiz(query, context, subject)
    except Exception as e:
        print(f"❌ button_handler error: {e}")
        traceback.print_exc()


async def start_quiz(query, context, subject):
    user_id = query.from_user.id
    state = get_user_state(user_id)
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
    state["correct"] = 0
    state["wrong"] = 0
    state["timeout_count"] = 0
    state["answered"] = False
    state["subject"] = subject

    total = len(state["questions"])
    await query.edit_message_text(
        f"🎮 *Quiz Started!*\n\n📚 Subject: *{subject}*\n📝 Questions: *{total}*\n⏱️ Time: *60s/question*\n\nStarting... 🚀{FOOTER}",
        parse_mode=ParseMode.MARKDOWN)
    await asyncio.sleep(1.5)
    await send_question(query, context)


async def send_question(query, context):
    user_id = query.from_user.id
    state = get_user_state(user_id)

    if state["current_index"] >= len(state["questions"]):
        await show_results(query, context)
        return

    q = state["questions"][state["current_index"]]
    total = len(state["questions"])
    current = state["current_index"] + 1
    state["answered"] = False

    subj_emoji = "🧬" if q["subject"] == "Biology" else "⚛️"
    source = f"\n📌 {q['source']}" if q.get("source") else ""
    q_text = f"{subj_emoji} *Q{current}/{total}* | ⏱️ 60s\n━━━━━━━━━━━━━━━━━━━━\n\n{q['question']}{source}\n"

    letters = ["A", "B", "C", "D"]
    keyboard = []
    for i, opt in enumerate(q["options"]):
        opt_d = opt[:80] + "..." if len(opt) > 80 else opt
        keyboard.append([InlineKeyboardButton(f"{letters[i]}. {opt_d}", callback_data=f"ans_{i}")])

    if q.get("has_image"):
        q_text = f"🖼️ *Refer to diagram*\n\n{q_text}"
    q_text += FOOTER

    try:
        await query.edit_message_text(q_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception:
        await query.message.reply_text(q_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

    state["timer_task"] = asyncio.create_task(question_timeout(query, context, user_id))


async def question_timeout(query, context, user_id):
    await asyncio.sleep(60)
    state = get_user_state(user_id)
    if not state["answered"]:
        state["timeout_count"] += 1
        state["wrong"] += 1
        q = state["questions"][state["current_index"]]
        cl = ["A", "B", "C", "D"][q["answer"]]
        msg = f"{random.choice(TIMEOUT_MSGS)}\n\n❌ *Time's Up!*\n✅ Answer: *{cl}. {q['options'][q['answer']]}*{FOOTER}"
        kb = [[InlineKeyboardButton("➡️ Next", callback_data="next")]]
        try:
            await query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
        except Exception:
            await query.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


async def _question_timeout_user(update, context, user_id):
    await asyncio.sleep(60)
    state = get_user_state(user_id)
    if not state["answered"]:
        state["timeout_count"] += 1
        state["wrong"] += 1
        q = state["questions"][state["current_index"]]
        cl = ["A", "B", "C", "D"][q["answer"]]
        msg = f"{random.choice(TIMEOUT_MSGS)}\n\n❌ *Time's Up!*\n✅ Answer: *{cl}. {q['options'][q['answer']]}*{FOOTER}"
        kb = [[InlineKeyboardButton("➡️ Next", callback_data="next")]]
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


async def handle_answer(query, context, selected):
    user_id = query.from_user.id
    state = get_user_state(user_id)

    if state["answered"]:
        await query.answer("Already answered! Press Next ⏭️", show_alert=True)
        return

    state["answered"] = True
    if state.get("timer_task"):
        state["timer_task"].cancel()

    q = state["questions"][state["current_index"]]
    correct = q["answer"]
    cl = ["A", "B", "C", "D"][correct]
    sl = ["A", "B", "C", "D"][selected]

    if selected == correct:
        state["correct"] += 1
        text = f"{random.choice(COMPLIMENTS)}\n\n✅ *CORRECT!*\n🎉 Answer: *{cl}. {q['options'][correct]}*\n\n📊 Score: {state['correct']}✅ | {state['wrong']}❌{FOOTER}"
    else:
        state["wrong"] += 1
        text = f"{random.choice(WRONG_ENCOURAGEMENT)}\n\n❌ *Wrong!*\nYour answer: *{sl}. {q['options'][selected]}*\n✅ Correct: *{cl}. {q['options'][correct]}*\n\n📊 Score: {state['correct']}✅ | {state['wrong']}❌{FOOTER}"

    kb = [[InlineKeyboardButton("➡️ Next", callback_data="next")]]
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


async def send_next_question(query, context):
    user_id = query.from_user.id
    state = get_user_state(user_id)
    state["current_index"] += 1
    if state["current_index"] >= len(state["questions"]):
        await show_results(query, context)
    else:
        await send_question(query, context)


async def show_results(query, context):
    user_id = query.from_user.id
    state = get_user_state(user_id)
    total = len(state["questions"])
    correct = state["correct"]
    wrong = state["wrong"]
    timeout = state["timeout_count"]
    pct = round((correct / total) * 100) if total > 0 else 0

    if pct >= 90: title, emoji = "🏆 LEGENDARY! SPARTA ka Warrior!", "🥇"
    elif pct >= 70: title, emoji = "⭐ EXCELLENT!", "🥈"
    elif pct >= 50: title, emoji = "💪 GOOD!", "🥉"
    elif pct >= 30: title, emoji = "📚 AVERAGE!", "📖"
    else: title, emoji = "🌱 KEEP GOING!", "💪"

    text = (
        f"{emoji} *QUIZ COMPLETE!*\n\n🏆 *{title}*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n📊 *RESULTS:*\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 Total: *{total}*\n✅ Correct: *{correct}*\n❌ Wrong: *{wrong}*\n⏰ Timeout: *{timeout}*\n📈 Score: *{pct}%*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n🎮 *Play Again:*\n"
    )
    kb = [
        [InlineKeyboardButton("🧬 Biology", callback_data="replay_Biology"),
         InlineKeyboardButton("⚛️ Physics", callback_data="replay_Physics")],
        [InlineKeyboardButton("🎯 Both", callback_data="replay_Both")],
    ]
    text += FOOTER
    try:
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))
    except Exception:
        await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))


async def show_results_for_user(update, context, user_id):
    state = get_user_state(user_id)
    total = len(state["questions"])
    correct = state["correct"]
    wrong = state["wrong"]
    timeout = state["timeout_count"]
    pct = round((correct / total) * 100) if total > 0 else 0

    if pct >= 90: title, emoji = "🏆 LEGENDARY!", "🥇"
    elif pct >= 70: title, emoji = "⭐ EXCELLENT!", "🥈"
    elif pct >= 50: title, emoji = "💪 GOOD!", "🥉"
    elif pct >= 30: title, emoji = "📚 AVERAGE!", "📖"
    else: title, emoji = "🌱 KEEP GOING!", "💪"

    text = (
        f"{emoji} *QUIZ COMPLETE!*\n\n🏆 *{title}*\n\n"
        f"📝 Total: *{total}*\n✅ Correct: *{correct}*\n❌ Wrong: *{wrong}*\n📈 Score: *{pct}%*\n{FOOTER}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


# ==================== BOT COMMANDS MENU ====================
async def post_init(application):
    await application.bot.set_my_commands([
        ("start", "🎮 Quiz shuru karo"),
        ("help", "📖 Help / Commands"),
        ("bio", "🧬 Biology Quiz"),
        ("phys", "⚛️ Physics Quiz"),
        ("mixed", "🎯 Mixed Quiz"),
        ("score", "📊 Current Score"),
        ("stats", "🏆 Total Stats"),
        ("restart", "🔄 Reset Quiz"),
        ("about", "🤖 About Bot"),
    ])
    print("✅ Bot commands menu set!")


# ==================== MAIN ====================
def main():
    TOKEN = os.environ.get("BOT_TOKEN", "")
    if not TOKEN:
        print("❌ BOT_TOKEN not found! Set it as env variable.")
        sys.exit(1)

    print("=" * 40)
    print("🤖 NEET Quiz Bot")
    print("📚 Arihant 34 Years PYQs")
    print(f"🧬 Biology: {len(BIO_QUESTIONS)}")
    print(f"⚛️ Physics: {len(PHYS_QUESTIONS)}")
    print(f"📋 Total: {len(ALL_QUESTIONS)}")
    print("🫠 MADE BY SPARTA")
    print("=" * 40)

    # Start background tasks (health server + auto-ping)
    start_background_tasks()

    # Build and run Telegram bot (main thread)
    telegram_app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    telegram_app.add_handler(CommandHandler("start", start_command))
    telegram_app.add_handler(CommandHandler("help", help_command))
    telegram_app.add_handler(CommandHandler("score", score_command))
    telegram_app.add_handler(CommandHandler("stats", stats_command))
    telegram_app.add_handler(CommandHandler("bio", bio_command))
    telegram_app.add_handler(CommandHandler("phys", phys_command))
    telegram_app.add_handler(CommandHandler("mixed", mixed_command))
    telegram_app.add_handler(CommandHandler("restart", restart_command))
    telegram_app.add_handler(CommandHandler("about", about_command))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot starting polling...")
    telegram_app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"💀 FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
