# 🤖 NEET Quiz Bot - Arihant 34 Years PYQs

### 🫠 MADE BY SPARTA

Telegram bot for NEET preparation with questions from Arihant 34 Years PYQs (Biology + Physics).

---

## 📋 Features

- 🧬 **Biology**: 104 Questions
- ⚛️ **Physics**: 12 Questions  
- 📝 **Total**: 116 Questions
- ⏱️ **60 seconds timer** per question
- ✅ Compliments on correct answers
- ❌ Encouragement on wrong answers
- 🏆 Score tracking with results
- 🖼️ Image support for diagram questions
- 🔄 Play again option after each quiz

---

## 🚀 DEPLOYMENT GUIDE

### Step 1: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Give your bot a name (e.g., "NEET Quiz Bot")
4. Give your bot a username (e.g., `neet_quiz_sparta_bot`)
5. **Copy the BOT TOKEN** (looks like: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`)

---

### 🌐 Option 1: Render.com (FREE - Recommended)

1. Go to [render.com](https://render.com) → Sign up/Login
2. Click **New → Web Service**
3. Connect your GitHub repo (or upload files)
4. Set these:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
5. Add Environment Variable:
   - **Key**: `BOT_TOKEN`
   - **Value**: `your_bot_token_here`
6. Click **Deploy**
7. Your bot is LIVE! ✅

---

### 🌐 Option 2: Railway.app (FREE)

1. Go to [railway.app](https://railway.app) → Sign up/Login
2. Click **New Project → Deploy from GitHub**
3. Select your repo
4. Add Variable:
   - `BOT_TOKEN` = `your_bot_token_here`
5. It auto-deploys! ✅

---

### 🌐 Option 3: Heroku (FREE tier)

1. Go to [heroku.com](https://heroku.com) → Sign up/Login
2. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Run these commands in terminal:

```bash
cd neet_quiz_bot
heroku login
heroku create your-bot-name
heroku config:set BOT_TOKEN="your_bot_token_here"
git init
git add .
git commit -m "NEET Quiz Bot by SPARTA"
git push heroku main
```

4. Done! ✅

---

### 💻 Option 4: Run Locally (Your Computer/VPS)

```bash
# Install Python 3.8+
# Clone or download this folder

cd neet_quiz_bot

# Install dependencies
pip install -r requirements.txt

# Set your bot token
export BOT_TOKEN="your_bot_token_here"

# Run the bot
python bot.py
```

Bot is now running! Open Telegram and use `/start`

---

### 🐳 Option 5: Docker

```bash
cd neet_quiz_bot
docker build -t neet-quiz-bot .
docker run -e BOT_TOKEN="your_bot_token_here" neet-quiz-bot
```

---

## 📁 Project Structure

```
neet_quiz_bot/
├── bot.py              # Main bot code
├── questions.json      # All quiz questions
├── requirements.txt    # Python dependencies
├── Procfile           # For Heroku/Render
├── Dockerfile         # For Docker deployment
├── render.yaml        # For Render.com
└── README.md          # This file
```

---

## 🔧 Add More Questions

Open `questions.json` and add new questions in this format:

```json
{
  "id": 117,
  "question": "Your question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": 0,
  "source": "NEET 2023",
  "subject": "Biology",
  "has_image": false
}
```

- `answer`: 0=A, 1=B, 2=C, 3=D
- `has_image`: true if question needs a diagram

---

## 🫠 MADE BY SPARTA
