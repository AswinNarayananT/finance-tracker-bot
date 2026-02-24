# 🧪 UAE Expat Finance Bot --- Testing Guide

Telegram Bot: @expatsfinbot\
Main File: uae_expat_finance_bot.py\
Storage: JSON-based (user_profiles folder)

------------------------------------------------------------------------

# 1️⃣ Overview

This testing guide validates the current version of the UAE Expat
Finance Bot.

The bot includes:

-   User onboarding
-   Income tracking
-   Expense tracking
-   Emergency fund tracking
-   Savings tracking
-   Weekly financial summary
-   JSON-based data persistence
-   Multi-user data isolation

The bot DOES NOT include: - AI-based financial advice - End of Service
(EOS) calculator - External API integrations - Database backend (uses
local JSON)

------------------------------------------------------------------------

# 2️⃣ Environment Setup

## Step 1 --- Create Virtual Environment

python -m venv venv venv`\Scripts`{=tex}`\activate   `{=tex}(Windows) \#
or source venv/bin/activate (Linux/Mac)

## Step 2 --- Install Dependencies

pip install -r requirements.txt

## Step 3 --- Configure .env

Add:

TELEGRAM_BOT_TOKEN=your_bot_token_here

## Step 4 --- Run the Bot

python uae_expat_finance_bot.py

Expected Output: Bot starts without errors.

------------------------------------------------------------------------

# 3️⃣ Manual Functional Testing

## ✅ Test 1 --- Bot Startup

Action: Send /start

Expected: - Welcome message - Main menu displayed - User profile created
inside user_profiles/

------------------------------------------------------------------------

## ✅ Test 2 --- Income Entry

Action: 1. Click "Set Income" 2. Enter a valid number (e.g., 5000)

Expected: - Income saved - Confirmation message shown - JSON updated
correctly

Negative Test: Enter text instead of number

Expected: - Validation error message

------------------------------------------------------------------------

## ✅ Test 3 --- Add Expense

Action: 1. Click "Add Expense" 2. Choose category 3. Enter amount

Expected: - Expense saved - Updated balance shown

Negative Test: Enter negative or invalid input

Expected: - Error handled gracefully

------------------------------------------------------------------------

## ✅ Test 4 --- Emergency Fund

Action: 1. Click "Emergency Fund" 2. Add amount

Expected: - Fund saved - JSON updated - Progress reflected in summary

------------------------------------------------------------------------

## ✅ Test 5 --- Savings Entry

Action: 1. Click "Add Savings" 2. Enter amount

Expected: - Savings updated - Reflected in weekly summary

------------------------------------------------------------------------

## ✅ Test 6 --- Weekly Summary

Action: Click "View Summary"

Expected: - Income displayed - Total expenses calculated - Savings
shown - Remaining balance accurate

Manual Verification Formula:

Remaining Balance = Income - Total Expenses - Savings

------------------------------------------------------------------------

# 4️⃣ Data Persistence Testing

## Restart Test

1.  Stop the bot
2.  Restart it
3.  Send /start

Expected: All previous data still available.

------------------------------------------------------------------------

# 5️⃣ Multi-User Isolation Test

Use two Telegram accounts.

Expected: - Separate JSON file per user - No data mixing

------------------------------------------------------------------------

# 6️⃣ File System Validation

Inside user_profiles/

Expected: - One JSON file per user - Proper structure - No corruption
after multiple updates

------------------------------------------------------------------------

# 7️⃣ Edge Case Testing

Test cases:

-   Very large numbers
-   Zero income
-   Expenses greater than income
-   Repeated updates
-   Rapid button clicking

Expected: Bot should not crash.

------------------------------------------------------------------------

# 8️⃣ Performance Testing

Simulate:

-   50+ interactions in short time
-   Multiple users interacting

Expected: - No crashes - No memory leaks - Stable response time

------------------------------------------------------------------------

# 9️⃣ Security Testing

-   Ensure .env is not exposed
-   Ensure bot token is not printed in logs
-   Ensure user data is not accessible by other users

------------------------------------------------------------------------

# 🔟 Regression Checklist

Before deployment:

-   Bot starts successfully
-   All menu buttons work
-   Income logic correct
-   Expense totals accurate
-   JSON updates correctly
-   Restart persistence verified
-   No unhandled exceptions in logs

------------------------------------------------------------------------

# 🏁 Conclusion

This testing guide validates the current stable architecture of:

-   Single-file bot logic
-   JSON-based persistence
-   Telegram handler-driven flow

If architecture changes (database, AI, financial engine abstraction),
this guide must be updated accordingly.
