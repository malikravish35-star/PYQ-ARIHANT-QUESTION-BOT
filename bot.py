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
import requests as req_lib
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

# ==================== LOAD QUESTIONS ====================
with open("questions.json", "r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

BIO_QUESTIONS = [q for q in ALL_QUESTIONS if q["subject"] == "Biology"]
PHYS_QUESTIONS = [q for q in ALL_QUESTIONS if q["subject"] == "Physics"]

# ==================== FLASK APP (HEALTH CHECK FOR RENDER) ====================
app = Flask(__name__)

@app.route("/")
def health_check():
    return "🤖 NEET Quiz Bot is ALIVE! | MADE BY SPARTA 🫠"

@app.route("/health")
def health():
    return "OK", 200

# ==================== AUTO-PING ====================
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

def auto_ping():
    """Ping the bot's own URL every 5 minutes to keep alive"""
    while True:
        time.sleep(300)  # 5 minutes
        if RENDER_URL:
            try:
                resp = req_lib.get(f"{RENDER_URL}/", timeout=10)
                print(f"🔄 Auto-ping: {resp.status_code} - Bot alive!")
            except Exception as e:
                print(f"⚠️ Auto-ping failed: {e}")
        else:
            print("🔄 Auto-ping: No RENDER_EXTERNAL_URL set")

def start_auto_ping():
    """Start auto-ping in background thread"""
    t = threading.Thread(target=auto_ping, daemon=True)
    t.start()
    print("✅ Auto-ping started (every 5 minutes)")

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
    "🧬 Biology king/queen! DNA se jude ho!",
    "⚛️ Physics ninja! Force is with you!",
    "🔥 Tandoor! Bilkan sahi jawab!",
    "💫 Supernova level answer!",
    "🎓 Professor level knowledge!",
    "🌟 SPARTA ka soldier! Mubarak ho!",
    "⚔️ Warrior mind! Correct strike!",
    "🎯 Target locked, target hit!",
    "💥 BOOM! Sahi jawaab!",
    "🏹 Arjuna level accuracy!",
    "🔥 Agni Putra! Jwala si accuracy!",
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
            "questions": [],
            "current_index": 0,
            "correct": 0,
            "wrong": 0,
            "timeout_count": 0,
            "answered": False,
            "timer_task": None,
        }
    return user_data[user_id]


# ==================== HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        f"*Choose your subject:* 👇"
        f"{FOOTER}"
    )

    keyboard = [
        [
            InlineKeyboardButton("🧬 Biology", callback_data="subject_Biology"),
            InlineKeyboardButton("⚛️ Physics", callback_data="subject_Physics"),
        ],
        [
            InlineKeyboardButton("🎯 Both (Mixed)", callback_data="subject_Both"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    text = (
        "📖 *BOT COMMANDS*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 /start — Quiz shuru karo 🎮\n"
        "🔹 /help — Ye help message 📖\n"
        "🔹 /score — Current score dekho 📊\n"
        "🔹 /stats — Total stats dekho 🏆\n"
        "🔹 /bio — Sirf Biology quiz 🧬\n"
        "🔹 /phys — Sirf Physics quiz ⚛️\n"
        "🔹 /mixed — Mixed quiz dono subjects 🎯\n"
        "🔹 /restart — Quiz restart karo 🔄\n"
        "🔹 /about — Bot ke baare mein 🤖\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "⏱️ Har question ka time: *60 seconds*\n"
        "✅ Sahi jawab = Compliment!\n"
        "❌ Galat jawab = Encouragement!\n\n"
        "🧬 Biology: " + str(len(BIO_QUESTIONS)) + " Questions\n"
        "⚛️ Physics: " + str(len(PHYS_QUESTIONS)) + " Questions\n"
        "📋 Total: " + str(len(ALL_QUESTIONS)) + " Questions\n"
        f"{FOOTER}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def score_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /score command - show current quiz score"""
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    
    if not state["questions"]:
        await update.message.reply_text(
            "📊 *Abhi tak koi quiz nahi khela!*\n\n"
            "/start karo aur quiz shuru karo! 🎮"
            f"{FOOTER}",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    total = len(state["questions"])
    current = state["current_index"] + 1
    correct = state["correct"]
    wrong = state["wrong"]
    attempted = correct + wrong
    
    if attempted > 0:
        pct = round((correct / attempted) * 100)
    else:
        pct = 0
    
    # Progress bar
    filled = int((current / total) * 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)
    
    text = (
        f"📊 *CURRENT SCORE*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 Question: {current}/{total}\n\n"
        f"{bar}\n\n"
        f"✅ Correct: *{correct}*\n"
        f"❌ Wrong: *{wrong}*\n"
        f"⏰ Timeout: *{state['timeout_count']}*\n"
        f"📈 Accuracy: *{pct}%*\n"
        f"{FOOTER}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show overall stats"""
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    
    total_q = len(state["questions"])
    
    if total_q == 0:
        await update.message.reply_text(
            "📊 *No Stats Yet!*\n\n"
            "Pehle quiz khelo, phir stats dekhna! 🎮\n"
            "/start karo!"
            f"{FOOTER}",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    correct = state["correct"]
    wrong = state["wrong"]
    timeout = state["timeout_count"]
    total = len(ALL_QUESTIONS)
    
    text = (
        f"🏆 *YOUR STATS*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📚 Total Questions Available: *{total}*\n"
        f"🧬 Biology: *{len(BIO_QUESTIONS)}*\n"
        f"⚛️ Physics: *{len(PHYS_QUESTIONS)}*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 Questions Attempted: *{correct + wrong}*\n"
        f"✅ Correct: *{correct}*\n"
        f"❌ Wrong: *{wrong}*\n"
        f"⏰ Timeout: *{timeout}*\n"
        f"{FOOTER}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def bio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bio command - start Biology quiz directly"""
    # Create a fake callback query
    user = update.effective_user
    text = (
        f"🧬 *BIOLOGY QUIZ*\n\n"
        f"📝 Questions: *{len(BIO_QUESTIONS)}*\n"
        f"⏱️ Time: *60 seconds* per question\n\n"
        f"Starting... 🚀"
        f"{FOOTER}"
    )
    
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    # Set up state
    user_id = user.id
    state = get_user_state(user_id)
    if state.get("timer_task"):
        state["timer_task"].cancel()
    
    state["questions"] = random.sample(BIO_QUESTIONS, len(BIO_QUESTIONS))
    random.shuffle(state["questions"])
    state["current_index"] = 0
    state["correct"] = 0
    state["wrong"] = 0
    state["timeout_count"] = 0
    state["answered"] = False
    state["subject"] = "Biology"
    
    await asyncio.sleep(1.5)
    
    # Create a mock callback query to reuse send_question
    class MockQuery:
        def __init__(self, message, user_id):
            self.message = message
            self.from_user = update.effective_user
        
        async def edit_message_text(self, *args, **kwargs):
            return await self.message.reply_text(*args, **kwargs)
    
    mock_query = MockQuery(msg, user_id)
    await send_question(mock_query, context)


async def phys_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /phys command - start Physics quiz directly"""
    user = update.effective_user
    text = (
        f"⚛️ *PHYSICS QUIZ*\n\n"
        f"📝 Questions: *{len(PHYS_QUESTIONS)}*\n"
        f"⏱️ Time: *60 seconds* per question\n\n"
        f"Starting... 🚀"
        f"{FOOTER}"
    )
    
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    user_id = user.id
    state = get_user_state(user_id)
    if state.get("timer_task"):
        state["timer_task"].cancel()
    
    state["questions"] = random.sample(PHYS_QUESTIONS, len(PHYS_QUESTIONS))
    random.shuffle(state["questions"])
    state["current_index"] = 0
    state["correct"] = 0
    state["wrong"] = 0
    state["timeout_count"] = 0
    state["answered"] = False
    state["subject"] = "Physics"
    
    await asyncio.sleep(1.5)
    
    class MockQuery:
        def __init__(self, message):
            self.message = message
            self.from_user = update.effective_user
        
        async def edit_message_text(self, *args, **kwargs):
            return await self.message.reply_text(*args, **kwargs)
    
    mock_query = MockQuery(msg)
    await send_question(mock_query, context)


async def mixed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mixed command - start mixed quiz directly"""
    user = update.effective_user
    text = (
        f"🎯 *MIXED QUIZ (Biology + Physics)*\n\n"
        f"📝 Questions: *{len(ALL_QUESTIONS)}*\n"
        f"⏱️ Time: *60 seconds* per question\n\n"
        f"Starting... 🚀"
        f"{FOOTER}"
    )
    
    msg = await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    user_id = user.id
    state = get_user_state(user_id)
    if state.get("timer_task"):
        state["timer_task"].cancel()
    
    state["questions"] = random.sample(ALL_QUESTIONS, len(ALL_QUESTIONS))
    random.shuffle(state["questions"])
    state["current_index"] = 0
    state["correct"] = 0
    state["wrong"] = 0
    state["timeout_count"] = 0
    state["answered"] = False
    state["subject"] = "Both"
    
    await asyncio.sleep(1.5)
    
    class MockQuery:
        def __init__(self, message):
            self.message = message
            self.from_user = update.effective_user
        
        async def edit_message_text(self, *args, **kwargs):
            return await self.message.reply_text(*args, **kwargs)
    
    mock_query = MockQuery(msg)
    await send_question(mock_query, context)


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /restart command"""
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    
    if state.get("timer_task"):
        state["timer_task"].cancel()
        state["timer_task"] = None
    
    state["questions"] = []
    state["current_index"] = 0
    state["correct"] = 0
    state["wrong"] = 0
    state["timeout_count"] = 0
    state["answered"] = False
    
    await update.message.reply_text(
        "🔄 *Quiz Reset!*\n\n"
        "Naya quiz shuru karne ke liye:\n\n"
        "🔹 /bio — Biology\n"
        "🔹 /phys — Physics\n"
        "🔹 /mixed — Both Mixed\n"
        "🔹 /start — Subject choose karo"
        f"{FOOTER}",
        parse_mode=ParseMode.MARKDOWN
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    text = (
        "🤖 *ABOUT THIS BOT*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📚 *NEET Quiz Bot*\n"
        "📖 Arihant 34 Years PYQs\n\n"
        "🧬 Biology: " + str(len(BIO_QUESTIONS)) + " Questions\n"
        "⚛️ Physics: " + str(len(PHYS_QUESTIONS)) + " Questions\n"
        "📋 Total: " + str(len(ALL_QUESTIONS)) + " Questions\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "⏱️ 60 seconds timer per question\n"
        "✅ Compliments on correct answers\n"
        "🔄 Auto-ping every 5 minutes\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💻 *Built with:* Python + Telegram API\n"
        "🌐 *Hosted on:* Render.com\n"
        "📦 *Questions:* Arihant NEET 34 Yrs PYQs\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🫠 **MADE BY SPARTA**"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def start_quiz(query, context, subject):
    user_id = query.from_user.id
    state = get_user_state(user_id)

    if state.get("timer_task"):
        state["timer_task"].cancel()
        state["timer_task"] = None

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
        f"🎮 *Quiz Started!*\n\n"
        f"📚 Subject: *{subject}*\n"
        f"📝 Total Questions: *{total}*\n"
        f"⏱️ Time per question: *60 seconds*\n\n"
        f"Starting now... 🚀"
        f"{FOOTER}",
        parse_mode=ParseMode.MARKDOWN,
    )
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

    subject_emoji = "🧬" if q["subject"] == "Biology" else "⚛️"
    source_text = f"\n📌 Source: {q['source']}" if q.get("source") else ""

    question_text = (
        f"{subject_emoji} *Q{current}/{total}* | ⏱️ 60s\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{q['question']}\n"
        f"{source_text}\n"
    )

    letters = ["A", "B", "C", "D"]
    keyboard = []
    for i, opt in enumerate(q["options"]):
        opt_display = opt[:80] + "..." if len(opt) > 80 else opt
        keyboard.append([
            InlineKeyboardButton(f"{letters[i]}. {opt_display}", callback_data=f"ans_{i}")
        ])

    if q.get("has_image"):
        question_text = f"🖼️ *⬆️ IMAGE DIAGRAM - Refer to diagram*\n\n{question_text}"

    question_text += FOOTER

    try:
        await query.edit_message_text(question_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception:
        await query.message.reply_text(question_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

    state["timer_task"] = asyncio.create_task(question_timeout(query, context, user_id))


async def question_timeout(query, context, user_id):
    await asyncio.sleep(60)
    state = get_user_state(user_id)

    if not state["answered"]:
        state["timeout_count"] += 1
        state["wrong"] += 1
        q = state["questions"][state["current_index"]]
        correct_letter = ["A", "B", "C", "D"][q["answer"]]
        timeout_msg = random.choice(TIMEOUT_MSGS)
        result_text = (
            f"{timeout_msg}\n\n❌ *Time's Up!*\n"
            f"✅ Correct Answer: *{correct_letter}. {q['options'][q['answer']]}*"
            f"{FOOTER}"
        )
        keyboard = [[InlineKeyboardButton("➡️ Next Question", callback_data="next")]]
        try:
            await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await query.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_answer(query, context, selected):
    user_id = query.from_user.id
    state = get_user_state(user_id)

    if state["answered"]:
        await query.answer("Already answered! Press Next ⏭️", show_alert=True)
        return

    state["answered"] = True

    if state.get("timer_task"):
        state["timer_task"].cancel()
        state["timer_task"] = None

    q = state["questions"][state["current_index"]]
    correct = q["answer"]
    correct_letter = ["A", "B", "C", "D"][correct]
    selected_letter = ["A", "B", "C", "D"][selected]

    if selected == correct:
        state["correct"] += 1
        compliment = random.choice(COMPLIMENTS)
        result_text = (
            f"{compliment}\n\n✅ *CORRECT!*\n"
            f"🎉 Answer: *{correct_letter}. {q['options'][correct]}*\n\n"
            f"📊 Score: {state['correct']}✅ | {state['wrong']}❌"
            f"{FOOTER}"
        )
    else:
        state["wrong"] += 1
        encourage = random.choice(WRONG_ENCOURAGEMENT)
        result_text = (
            f"{encourage}\n\n❌ *Wrong!*\n"
            f"Your answer: *{selected_letter}. {q['options'][selected]}*\n"
            f"✅ Correct answer: *{correct_letter}. {q['options'][correct]}*\n\n"
            f"📊 Score: {state['correct']}✅ | {state['wrong']}❌"
            f"{FOOTER}"
        )

    keyboard = [[InlineKeyboardButton("➡️ Next Question", callback_data="next")]]
    await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))


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
    percentage = round((correct / total) * 100) if total > 0 else 0

    if percentage >= 90:
        title = "🏆 LEGENDARY! SPARTA ka Warrior!"
        emoji = "🥇"
    elif percentage >= 70:
        title = "⭐ EXCELLENT! Topper material!"
        emoji = "🥈"
    elif percentage >= 50:
        title = "💪 GOOD! Keep improving!"
        emoji = "🥉"
    elif percentage >= 30:
        title = "📚 AVERAGE! Revision needed!"
        emoji = "📖"
    else:
        title = "🌱 KEEP GOING! Practice more!"
        emoji = "💪"

    result_text = (
        f"{emoji} *QUIZ COMPLETE!*\n\n🏆 *{title}*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n📊 *RESULTS:*\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 Total Questions: *{total}*\n✅ Correct: *{correct}*\n"
        f"❌ Wrong: *{wrong}*\n⏰ Timeout: *{timeout}*\n📈 Score: *{percentage}%*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n🎮 *Play Again:*\n"
    )

    keyboard = [
        [
            InlineKeyboardButton("🧬 Biology", callback_data="replay_Biology"),
            InlineKeyboardButton("⚛️ Physics", callback_data="replay_Physics"),
        ],
        [
            InlineKeyboardButton("🎯 Both (Mixed)", callback_data="replay_Both"),
        ],
    ]

    result_text += FOOTER

    try:
        await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception:
        await query.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))


# ==================== TELEGRAM BOT RUNNER ====================
async def set_bot_commands(application):
    """Set bot commands menu"""
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


def run_telegram_bot():
    """Run the Telegram bot in a thread"""
    TOKEN = os.environ.get("BOT_TOKEN", "")
    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN not found!")
        return

    print("🤖 NEET Quiz Bot starting...")
    print(f"📚 Total questions: {len(ALL_QUESTIONS)}")
    print(f"🧬 Biology: {len(BIO_QUESTIONS)}")
    print(f"⚛️ Physics: {len(PHYS_QUESTIONS)}")

    telegram_app = Application.builder().token(TOKEN).post_init(set_bot_commands).build()
    
    # Add all command handlers
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

    print("✅ Telegram bot is running!")
    telegram_app.run_polling(drop_pending_updates=True)


# ==================== MAIN ====================
def main():
    """Main entry point - Flask + Telegram bot"""
    print("🚀 Starting NEET Quiz Bot...")
    print("🫠 MADE BY SPARTA")

    # Start auto-ping thread
    start_auto_ping()

    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Run Flask as main thread (handles health checks for Render)
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask health server starting on port {port}")
    print(f"🤖 Bot URL: {os.environ.get('RENDER_EXTERNAL_URL', 'N/A')}")
    print("✅ Bot is LIVE!")
    app.run(host="0.0.0.0", port=port, use_reloader=False)


if __name__ == "__main__":
    main()
