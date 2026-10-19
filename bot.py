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
import requests
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
with open("questions.json", "r", encoding="utf-8") as f:
    ALL_QUESTIONS = json.load(f)

BIO_QUESTIONS = [q for q in ALL_QUESTIONS if q["subject"] == "Biology"]
PHYS_QUESTIONS = [q for q in ALL_QUESTIONS if q["subject"] == "Physics"]

# ==================== AUTO-PING / KEEP ALIVE ====================
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"🤖 NEET Quiz Bot is ALIVE! | MADE BY SPARTA 🫠")

    def log_message(self, format, *args):
        pass  # Suppress logs

def run_health_server():
    """Run a simple HTTP server for health checks"""
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    print(f"🌐 Health server running on port {port}")
    server.serve_forever()

def auto_ping():
    """Ping the bot's own URL every 5 minutes to keep alive on Render"""
    while True:
        time.sleep(300)  # 5 minutes
        if RENDER_URL:
            try:
                resp = requests.get(f"{RENDER_URL}/", timeout=10)
                print(f"🔄 Auto-ping: {resp.status_code} - Bot alive!")
            except Exception as e:
                print(f"⚠️ Auto-ping failed: {e}")
        else:
            print("🔄 Auto-ping: No RENDER_EXTERNAL_URL set, skipping")

def start_keep_alive():
    """Start health server and auto-ping in background threads"""
    # Start health check server
    server_thread = threading.Thread(target=run_health_server, daemon=True)
    server_thread.start()
    
    # Start auto-ping thread
    ping_thread = threading.Thread(target=auto_ping, daemon=True)
    ping_thread.start()
    
    print("✅ Keep-alive system started (Health server + Auto-ping every 5 min)")

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
    """Handle /start command"""
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

    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button presses"""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    # Subject selection
    if data.startswith("subject_"):
        subject = data.replace("subject_", "")
        await start_quiz(query, context, subject)

    # Answer selection
    elif data.startswith("ans_"):
        selected = int(data.replace("ans_", ""))
        await handle_answer(query, context, selected)

    # Next question
    elif data == "next":
        await send_next_question(query, context)

    # Restart
    elif data == "restart":
        await start_command(update.callback_query.message, context)

    # Subject again after results
    elif data.startswith("replay_"):
        subject = data.replace("replay_", "")
        await start_quiz(query, context, subject)


async def start_quiz(query, context, subject):
    """Start quiz with selected subject"""
    user_id = query.from_user.id
    state = get_user_state(user_id)

    # Cancel any existing timer
    if state.get("timer_task"):
        state["timer_task"].cancel()
        state["timer_task"] = None

    # Select questions
    if subject == "Biology":
        state["questions"] = random.sample(BIO_QUESTIONS, min(len(BIO_QUESTIONS), len(BIO_QUESTIONS)))
    elif subject == "Physics":
        state["questions"] = random.sample(PHYS_QUESTIONS, min(len(PHYS_QUESTIONS), len(PHYS_QUESTIONS)))
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
    """Send the current question"""
    user_id = query.from_user.id
    state = get_user_state(user_id)

    if state["current_index"] >= len(state["questions"]):
        await show_results(query, context)
        return

    q = state["questions"][state["current_index"]]
    total = len(state["questions"])
    current = state["current_index"] + 1
    state["answered"] = False

    # Format question
    subject_emoji = "🧬" if q["subject"] == "Biology" else "⚛️"
    source_text = f"\n📌 Source: {q['source']}" if q.get("source") else ""

    question_text = (
        f"{subject_emoji} *Q{current}/{total}* | ⏱️ 60s\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{q['question']}\n"
        f"{source_text}\n"
    )

    # Build keyboard with options
    letters = ["A", "B", "C", "D"]
    keyboard = []
    for i, opt in enumerate(q["options"]):
        # Truncate long options for display
        opt_display = opt[:80] + "..." if len(opt) > 80 else opt
        keyboard.append([
            InlineKeyboardButton(
                f"{letters[i]}. {opt_display}",
                callback_data=f"ans_{i}"
            )
        ])

    # Image indicator for questions with images
    if q.get("has_image"):
        question_text = (
            f"🖼️ *⬆️ IMAGE DIAGRAM - Refer to diagram*\n\n"
            f"{question_text}"
        )

    question_text += FOOTER

    # Send or edit message
    try:
        await query.edit_message_text(
            question_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception:
        await query.message.reply_text(
            question_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # Start 60 second timer
    state["timer_task"] = asyncio.create_task(
        question_timeout(query, context, user_id)
    )


async def question_timeout(query, context, user_id):
    """Handle 60 second timeout for a question"""
    await asyncio.sleep(60)
    state = get_user_state(user_id)

    if not state["answered"]:
        state["timeout_count"] += 1
        state["wrong"] += 1

        q = state["questions"][state["current_index"]]
        correct_letter = ["A", "B", "C", "D"][q["answer"]]

        timeout_msg = random.choice(TIMEOUT_MSGS)
        result_text = (
            f"{timeout_msg}\n\n"
            f"❌ *Time's Up!*\n"
            f"✅ Correct Answer: *{correct_letter}. {q['options'][q['answer']]}*"
            f"{FOOTER}"
        )

        keyboard = [[InlineKeyboardButton("➡️ Next Question", callback_data="next")]]

        try:
            await query.edit_message_text(
                result_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        except Exception:
            await query.message.reply_text(
                result_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )


async def handle_answer(query, context, selected):
    """Handle answer selection"""
    user_id = query.from_user.id
    state = get_user_state(user_id)

    if state["answered"]:
        await query.answer("Already answered! Press Next ⏭️", show_alert=True)
        return

    state["answered"] = True

    # Cancel timer
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
            f"{compliment}\n\n"
            f"✅ *CORRECT!*\n"
            f"🎉 Answer: *{correct_letter}. {q['options'][correct]}*\n\n"
            f"📊 Score: {state['correct']}✅ | {state['wrong']}❌"
            f"{FOOTER}"
        )
    else:
        state["wrong"] += 1
        encourage = random.choice(WRONG_ENCOURAGEMENT)
        result_text = (
            f"{encourage}\n\n"
            f"❌ *Wrong!*\n"
            f"Your answer: *{selected_letter}. {q['options'][selected]}*\n"
            f"✅ Correct answer: *{correct_letter}. {q['options'][correct]}*\n\n"
            f"📊 Score: {state['correct']}✅ | {state['wrong']}❌"
            f"{FOOTER}"
        )

    keyboard = [[InlineKeyboardButton("➡️ Next Question", callback_data="next")]]

    await query.edit_message_text(
        result_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def send_next_question(query, context):
    """Move to next question"""
    user_id = query.from_user.id
    state = get_user_state(user_id)
    state["current_index"] += 1

    if state["current_index"] >= len(state["questions"]):
        await show_results(query, context)
    else:
        await send_question(query, context)


async def show_results(query, context):
    """Show final results"""
    user_id = query.from_user.id
    state = get_user_state(user_id)
    total = len(state["questions"])
    correct = state["correct"]
    wrong = state["wrong"]
    timeout = state["timeout_count"]
    percentage = round((correct / total) * 100) if total > 0 else 0

    # Determine result level
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
        f"{emoji} *QUIZ COMPLETE!*\n\n"
        f"🏆 *{title}*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *RESULTS:*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 Total Questions: *{total}*\n"
        f"✅ Correct: *{correct}*\n"
        f"❌ Wrong: *{wrong}*\n"
        f"⏰ Timeout: *{timeout}*\n"
        f"📈 Score: *{percentage}%*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎮 *Play Again:*\n"
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
        await query.edit_message_text(
            result_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception:
        await query.message.reply_text(
            result_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# ==================== MAIN ====================

def main():
    """Start the bot"""
    TOKEN = os.environ.get("BOT_TOKEN", "")

    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN not found!")
        print("Set it as environment variable: export BOT_TOKEN='your_token_here'")
        return

    print("🤖 NEET Quiz Bot starting...")
    print(f"📚 Total questions: {len(ALL_QUESTIONS)}")
    print(f"🧬 Biology: {len(BIO_QUESTIONS)}")
    print(f"⚛️ Physics: {len(PHYS_QUESTIONS)}")
    print("🫠 MADE BY SPARTA")

    # Start keep-alive system (health server + auto-ping every 5 min)
    start_keep_alive()

    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
