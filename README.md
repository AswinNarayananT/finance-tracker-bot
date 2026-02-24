# 💰 Expat's Financier Bot -- Enhanced UI

A powerful Telegram finance tracking bot designed for expats to manage
their income, spending, emergency funds, and savings with a clean
interactive dashboard and visual progress bars.

Built using **Python** and the **python-telegram-bot (async)**
framework.

------------------------------------------------------------------------

## 🔗 Telegram Bot

**Username:** @expatsfinbot

👉 **Bot Link:**\
https://t.me/expatsfinbot

------------------------------------------------------------------------

## ✨ Features

### 📊 Interactive Financial Dashboard

-   Weekly spending progress tracking
-   Emergency fund progress bar
-   Short-term & long-term savings overview
-   Clean percentage-based indicators
-   Auto-refreshable UI

### 📅 Weekly Expense Logging

-   Log total weekly spending
-   Track remittance
-   Track food expenses
-   Track other weekly expenses
-   Automatic weekly locking of past logs

### 🚨 Emergency Fund Management

-   Set emergency fund goal
-   Add monthly contributions
-   Edit balance anytime
-   Real-time progress visualization

### 💰 Savings Tracking

-   Add to short-term savings
-   Add to long-term savings
-   View total savings
-   Progress toward yearly savings goal

### 📋 Custom Monthly Expenses

-   Add custom expense categories (Rent, Transport, etc.)
-   Edit expense amounts
-   View total monthly custom expenses

### 💾 Local JSON Storage

Each user's data is stored locally in:

    user_profiles/user_<telegram_id>.json

No external database required.

------------------------------------------------------------------------

# 🛠 Tech Stack

-   Python 3.10+
-   python-telegram-bot (async version)
-   python-dotenv
-   Local JSON-based storage
-   InlineKeyboard UI

------------------------------------------------------------------------

# 🚀 Setup Guide (Local Development)

## 1️⃣ Clone the Repository

    git clone <your-repository-url>
    cd <project-folder>

------------------------------------------------------------------------

## 2️⃣ Create Virtual Environment

### Windows:

    python -m venv venv
    venv\Scripts\activate

### Linux / Mac:

    python3 -m venv venv
    source venv/bin/activate

------------------------------------------------------------------------

## 3️⃣ Install Dependencies

Make sure you have:

    requirements.txt

Then install:

    pip install -r requirements.txt

------------------------------------------------------------------------

## 4️⃣ Configure Environment Variables

Create a file named:

    .env

Add your Telegram bot token:

    TELEGRAM_BOT_TOKEN=your_bot_token_here

------------------------------------------------------------------------

## 5️⃣ Run the Bot

    python uae_expat_finance_bot.py

If successful, you should see:

    Expat's Financier Bot - Enhanced UI started!

The bot runs using long polling (no webhook required).

------------------------------------------------------------------------

# 📁 Project Structure

    .
    ├── uae_expat_finance_bot.py
    ├── requirements.txt
    ├── .env
    ├── user_profiles/
    │   ├── user_123456.json
    │   └── ...

------------------------------------------------------------------------

# 🔐 Security Best Practices

Create a .gitignore file:

    venv/
    .env
    __pycache__/
    user_profiles/

Never commit: - Bot token - Virtual environment - User data files

------------------------------------------------------------------------

# 📌 Commands

  Command   Description
  --------- --------------------------
  /start    Start bot & onboarding
  /cancel   Cancel current operation

All other interactions are handled through inline buttons.

------------------------------------------------------------------------

# 👨‍💻 Author

Developed by **Aswin Nt**\
Telegram Bot: @expatsfinbot
