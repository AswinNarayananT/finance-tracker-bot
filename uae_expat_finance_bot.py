"""
Expat's Financier Bot - Enhanced UI
Beautiful dashboard with progress bars and detailed expense tracking
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Storage directory
STORAGE_DIR = Path("user_profiles")
STORAGE_DIR.mkdir(exist_ok=True)

# Onboarding states
(ONBOARDING_NAME, ONBOARDING_JOB, ONBOARDING_SALARY,
 ONBOARDING_MONTHLY_SPENDING, ONBOARDING_EMERGENCY_FUND,
 ONBOARDING_MONTHLY_SAVINGS) = range(6)

# Main states
(DASHBOARD, MAIN_MENU, UPDATE_SALARY, UPDATE_SPENDING_GOAL,
 LOG_WEEKLY_TOTAL, LOG_REMITTANCE, LOG_FOOD, LOG_OTHER,
 ADD_EMERGENCY_MONTH, EDIT_EMERGENCY_BALANCE, EDIT_EMERGENCY_GOAL,
 ADD_SHORT_TERM, ADD_LONG_TERM, ADD_OTHER_EXPENSE_NAME, 
 ADD_OTHER_EXPENSE_AMOUNT, VIEW_OTHER_EXPENSES) = range(6, 22)


class UserProfile:
    """User's financial profile"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.name = ""
        self.job_position = ""
        self.salary = 0.0
        self.monthly_spending_goal = 0.0
        self.emergency_fund_balance = 0.0
        self.emergency_fund_goal = 0.0
        self.monthly_savings_goal = 0.0
        
        # Cumulative savings (total saved so far)
        self.short_term_savings = 0.0
        self.long_term_savings = 0.0
        
        # Weekly logs - format: {"2026-W08": {"total": 1500, "remittance": 500, "food": 400, "other": 600, "locked": False}}
        self.weekly_logs = {}
        
        # Other expenses tracking (customizable categories)
        self.other_expenses = {}  # {"Rent": 4500, "Transport": 800, "Phone": 150, ...}
        
        self.onboarding_completed = False
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
    
    def get_current_week_key(self) -> str:
        """Get current week key (e.g., '2026-W08')"""
        return datetime.now().strftime("%Y-W%U")
    
    def get_current_week_log(self) -> dict:
        """Get current week's log"""
        week_key = self.get_current_week_key()
        if week_key not in self.weekly_logs:
            self.weekly_logs[week_key] = {
                'total': 0.0,
                'remittance': 0.0,
                'food': 0.0,
                'other': 0.0,
                'locked': False
            }
        return self.weekly_logs[week_key]
    
    def lock_old_weeks(self):
        """Lock all weeks except current week"""
        current_week = self.get_current_week_key()
        for week_key in self.weekly_logs:
            if week_key != current_week:
                self.weekly_logs[week_key]['locked'] = True
    
    def get_total_savings(self) -> float:
        """Get total savings (short-term + long-term)"""
        return self.short_term_savings + self.long_term_savings
    
    def get_total_other_expenses(self) -> float:
        """Get sum of all other expenses"""
        return sum(self.other_expenses.values())
    
    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'name': self.name,
            'job_position': self.job_position,
            'salary': self.salary,
            'monthly_spending_goal': self.monthly_spending_goal,
            'emergency_fund_balance': self.emergency_fund_balance,
            'emergency_fund_goal': self.emergency_fund_goal,
            'monthly_savings_goal': self.monthly_savings_goal,
            'short_term_savings': self.short_term_savings,
            'long_term_savings': self.long_term_savings,
            'weekly_logs': self.weekly_logs,
            'other_expenses': self.other_expenses,
            'onboarding_completed': self.onboarding_completed,
            'created_at': self.created_at,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        profile = cls(data['user_id'])
        profile.name = data.get('name', '')
        profile.job_position = data.get('job_position', '')
        profile.salary = data.get('salary', 0.0)
        profile.monthly_spending_goal = data.get('monthly_spending_goal', 0.0)
        profile.emergency_fund_balance = data.get('emergency_fund_balance', 0.0)
        profile.emergency_fund_goal = data.get('emergency_fund_goal', 0.0)
        profile.monthly_savings_goal = data.get('monthly_savings_goal', 0.0)
        profile.short_term_savings = data.get('short_term_savings', 0.0)
        profile.long_term_savings = data.get('long_term_savings', 0.0)
        profile.weekly_logs = data.get('weekly_logs', {})
        profile.other_expenses = data.get('other_expenses', {})
        profile.onboarding_completed = data.get('onboarding_completed', False)
        profile.created_at = data.get('created_at', datetime.now().isoformat())
        profile.last_updated = data.get('last_updated', datetime.now().isoformat())
        return profile


class ProfileManager:
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
    
    def get_profile_file(self, user_id: int) -> Path:
        return self.storage_dir / f"user_{user_id}.json"
    
    def load_profile(self, user_id: int) -> UserProfile:
        profile_file = self.get_profile_file(user_id)
        if profile_file.exists():
            try:
                with open(profile_file, 'r') as f:
                    return UserProfile.from_dict(json.load(f))
            except Exception as e:
                logger.error(f"Error loading profile: {e}")
        return UserProfile(user_id)
    
    def save_profile(self, profile: UserProfile):
        try:
            profile.lock_old_weeks()
            profile.last_updated = datetime.now().isoformat()
            with open(self.get_profile_file(profile.user_id), 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving profile: {e}")


profile_manager = ProfileManager(STORAGE_DIR)


def create_progress_bar(percentage: float, length: int = 10) -> str:
    """Create a beautiful progress bar with percentage"""
    filled = int((min(percentage, 100) / 100) * length)
    empty = length - filled
    bar = "█" * filled + "░" * empty
    
    # Add color indicators
    if percentage >= 75:
        icon = "🟢"
    elif percentage >= 50:
        icon = "🟡"
    elif percentage >= 25:
        icon = "🟠"
    else:
        icon = "🔴"
    
    return f"{icon} {bar} {percentage:.0f}%"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start bot"""
    user_id = update.effective_user.id
    profile = profile_manager.load_profile(user_id)
    context.user_data['profile'] = profile
    
    if profile.onboarding_completed:
        return await show_dashboard(update, context)
    
    await update.message.reply_text(
        "👋 *Welcome to Expat's Financier*\n\n"
        "Let's set up your profile!\n\n"
        "What's your name?",
        parse_mode='Markdown'
    )
    return ONBOARDING_NAME


async def onboarding_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    profile = context.user_data['profile']
    profile.name = update.message.text.strip()
    
    await update.message.reply_text(f"Hi {profile.name}! 👋\n\nYour job position?")
    return ONBOARDING_JOB


async def onboarding_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    profile = context.user_data['profile']
    profile.job_position = update.message.text.strip()
    
    await update.message.reply_text("💰 Monthly salary in AED?")
    return ONBOARDING_SALARY


async def onboarding_salary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        salary = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.salary = salary
        
        await update.message.reply_text(
            f"✅ Salary: AED {salary:,.0f}\n\n"
            f"📊 Monthly spending goal?"
        )
        return ONBOARDING_MONTHLY_SPENDING
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return ONBOARDING_SALARY


async def onboarding_monthly_spending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        spending = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.monthly_spending_goal = spending
        
        await update.message.reply_text(
            f"✅ Spending Goal: AED {spending:,.0f}\n\n"
            f"🚨 Emergency fund goal?\n"
            f"(Target amount you want to keep)"
        )
        return ONBOARDING_EMERGENCY_FUND
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return ONBOARDING_MONTHLY_SPENDING


async def onboarding_emergency_fund(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        emergency = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.emergency_fund_goal = emergency
        profile.emergency_fund_balance = 0.0
        
        await update.message.reply_text(
            f"✅ Emergency Goal: AED {emergency:,.0f}\n\n"
            f"💰 Monthly savings goal?"
        )
        return ONBOARDING_MONTHLY_SAVINGS
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return ONBOARDING_EMERGENCY_FUND


async def onboarding_monthly_savings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        savings = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.monthly_savings_goal = savings
        profile.onboarding_completed = True
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(
            f"🎉 *Setup Complete!*\n\n"
            f"Welcome, {profile.name}!\n\n"
            f"Loading your dashboard...",
            parse_mode='Markdown'
        )
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return ONBOARDING_MONTHLY_SAVINGS


async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show beautiful enhanced dashboard"""
    profile = context.user_data['profile']
    
    # Get current week data
    current_week = profile.get_current_week_log()
    week_spent = current_week['total']
    
    # Calculate percentages
    spending_pct = (week_spent / (profile.monthly_spending_goal / 4) * 100) if profile.monthly_spending_goal > 0 else 0
    ef_pct = (profile.emergency_fund_balance / profile.emergency_fund_goal * 100) if profile.emergency_fund_goal > 0 else 0
    
    total_savings = profile.get_total_savings()
    savings_pct = (total_savings / (profile.monthly_savings_goal * 12) * 100) if profile.monthly_savings_goal > 0 else 0
    
    text = (
        f"┏━━━━━━━━━━━━━━━━━━━━┓\n"
        f"┃  *{profile.name}'s Dashboard*  \n"
        f"┗━━━━━━━━━━━━━━━━━━━━┛\n\n"
        
        f"👤 *{profile.job_position}*\n"
        f"💵 Salary: *AED {profile.salary:,.0f}*\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *SPENDING THIS WEEK*\n"
        f"AED {week_spent:,.0f} / {(profile.monthly_spending_goal/4):,.0f}\n"
        f"{create_progress_bar(spending_pct)}\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚨 *EMERGENCY FUND*\n"
        f"AED {profile.emergency_fund_balance:,.0f} / {profile.emergency_fund_goal:,.0f}\n"
        f"{create_progress_bar(ef_pct)}\n\n"
        
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 *TOTAL SAVINGS*\n"
        f"AED {total_savings:,.0f}\n"
        f"├ Short-term: AED {profile.short_term_savings:,.0f}\n"
        f"└ Long-term: AED {profile.long_term_savings:,.0f}\n"
        f"{create_progress_bar(savings_pct)}\n\n"
        
        f"🎯 Monthly Goal: AED {profile.monthly_savings_goal:,.0f}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("📅 Log This Week", callback_data='log_week_menu')],
        [InlineKeyboardButton("⚙️ Update", callback_data='update_menu')],
        [InlineKeyboardButton("🔄 Refresh", callback_data='refresh')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    
    return DASHBOARD


async def show_log_week_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show weekly logging menu"""
    query = update.callback_query
    await query.answer()
    
    profile = context.user_data['profile']
    current_week = profile.get_current_week_log()
    
    text = (
        f"📅 *This Week's Spending*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💵 Total: *AED {current_week['total']:,.0f}*\n\n"
        f"Breakdown:\n"
        f"├ 🏠 Remittance: AED {current_week['remittance']:,.0f}\n"
        f"├ 🍽️ Food: AED {current_week['food']:,.0f}\n"
        f"└ 📦 Other: AED {current_week['other']:,.0f}\n\n"
        f"What to log?"
    )
    
    keyboard = [
        [InlineKeyboardButton("💵 Total Spending", callback_data='log_total')],
        [InlineKeyboardButton("🏠 Home Remittance", callback_data='log_remittance')],
        [InlineKeyboardButton("🍽️ Food", callback_data='log_food')],
        [InlineKeyboardButton("📦 Other Expenses", callback_data='log_other')],
        [InlineKeyboardButton("« Back", callback_data='back_dashboard')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    return DASHBOARD


async def show_update_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show update menu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💰 Edit Salary", callback_data='edit_salary')],
        [InlineKeyboardButton("📊 Edit Spending Goal", callback_data='edit_spending')],
        [InlineKeyboardButton("🚨 Emergency Fund", callback_data='emergency_menu')],
        [InlineKeyboardButton("💵 Savings", callback_data='savings_menu')],
        [InlineKeyboardButton("📋 Other Expenses", callback_data='other_expenses_menu')],
        [InlineKeyboardButton("« Back", callback_data='back_dashboard')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ *Update Menu*\n\nWhat to update?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return MAIN_MENU


async def show_emergency_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show emergency fund menu"""
    query = update.callback_query
    await query.answer()
    
    profile = context.user_data['profile']
    ef_pct = (profile.emergency_fund_balance / profile.emergency_fund_goal * 100) if profile.emergency_fund_goal > 0 else 0
    
    text = (
        f"🚨 *Emergency Fund*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Balance: *AED {profile.emergency_fund_balance:,.0f}*\n"
        f"Goal: AED {profile.emergency_fund_goal:,.0f}\n\n"
        f"{create_progress_bar(ef_pct)}\n\n"
        f"What to do?"
    )
    
    keyboard = [
        [InlineKeyboardButton("➕ Add This Month", callback_data='add_emergency_month')],
        [InlineKeyboardButton("✏️ Edit Balance", callback_data='edit_emergency_balance')],
        [InlineKeyboardButton("🎯 Edit Goal", callback_data='edit_emergency_goal')],
        [InlineKeyboardButton("« Back", callback_data='update_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    return MAIN_MENU


async def show_savings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show savings menu"""
    query = update.callback_query
    await query.answer()
    
    profile = context.user_data['profile']
    total = profile.get_total_savings()
    
    text = (
        f"💰 *Savings*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Total: *AED {total:,.0f}*\n\n"
        f"├ 💵 Short-term: AED {profile.short_term_savings:,.0f}\n"
        f"└ 💎 Long-term: AED {profile.long_term_savings:,.0f}\n\n"
        f"What to do?"
    )
    
    keyboard = [
        [InlineKeyboardButton("💵 Add to Short-term", callback_data='add_short_term')],
        [InlineKeyboardButton("💎 Add to Long-term", callback_data='add_long_term')],
        [InlineKeyboardButton("« Back", callback_data='update_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    return MAIN_MENU


async def show_other_expenses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show other expenses menu"""
    query = update.callback_query
    await query.answer()
    
    profile = context.user_data['profile']
    
    text = f"📋 *Other Expenses*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if profile.other_expenses:
        text += "Current expenses:\n"
        for name, amount in profile.other_expenses.items():
            text += f"├ {name}: AED {amount:,.0f}\n"
        text += f"\nTotal: *AED {profile.get_total_other_expenses():,.0f}*\n"
    else:
        text += "No expenses added yet.\n"
    
    text += "\nWhat to do?"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add New Expense", callback_data='add_other_expense')],
    ]
    
    if profile.other_expenses:
        keyboard.append([InlineKeyboardButton("📋 View All", callback_data='view_other_expenses')])
    
    keyboard.append([InlineKeyboardButton("« Back", callback_data='update_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    return MAIN_MENU


async def show_view_other_expenses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show detailed view of other expenses with edit options"""
    query = update.callback_query
    await query.answer()
    
    profile = context.user_data['profile']
    
    text = f"📋 *Your Other Expenses*\n━━━━━━━━━━━━━━━━━━━━\n\n"
    
    keyboard = []
    for name, amount in profile.other_expenses.items():
        text += f"• {name}: AED {amount:,.0f}\n"
        keyboard.append([InlineKeyboardButton(f"✏️ Edit {name}", callback_data=f'edit_other_{name}')])
    
    text += f"\nTotal: *AED {profile.get_total_other_expenses():,.0f}*"
    
    keyboard.append([InlineKeyboardButton("« Back", callback_data='other_expenses_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    return MAIN_MENU


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle all menu callbacks"""
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == 'refresh' or action == 'back_dashboard':
        return await show_dashboard(update, context)
    
    elif action == 'log_week_menu':
        return await show_log_week_menu(update, context)
    
    elif action == 'update_menu':
        return await show_update_menu(update, context)
    
    elif action == 'emergency_menu':
        return await show_emergency_menu(update, context)
    
    elif action == 'savings_menu':
        return await show_savings_menu(update, context)
    
    elif action == 'other_expenses_menu':
        return await show_other_expenses_menu(update, context)
    
    elif action == 'view_other_expenses':
        return await show_view_other_expenses(update, context)
    
    elif action == 'add_other_expense':
        await query.edit_message_text("Enter expense name (e.g., Rent, Transport, Phone):")
        return ADD_OTHER_EXPENSE_NAME
    
    elif action.startswith('edit_other_'):
        expense_name = action.replace('edit_other_', '')
        context.user_data['editing_expense'] = expense_name
        await query.edit_message_text(f"Enter new amount for *{expense_name}*:", parse_mode='Markdown')
        return ADD_OTHER_EXPENSE_AMOUNT
    
    # Logging callbacks
    elif action == 'log_total':
        await query.edit_message_text("💵 Enter total spending for this week:")
        return LOG_WEEKLY_TOTAL
    
    elif action == 'log_remittance':
        await query.edit_message_text("🏠 Enter home remittance amount:")
        return LOG_REMITTANCE
    
    elif action == 'log_food':
        await query.edit_message_text("🍽️ Enter food expenses:")
        return LOG_FOOD
    
    elif action == 'log_other':
        await query.edit_message_text("📦 Enter other expenses:")
        return LOG_OTHER
    
    # Update callbacks
    elif action == 'edit_salary':
        await query.edit_message_text("💰 Enter new monthly salary:")
        return UPDATE_SALARY
    
    elif action == 'edit_spending':
        await query.edit_message_text("📊 Enter new monthly spending goal:")
        return UPDATE_SPENDING_GOAL
    
    elif action == 'add_emergency_month':
        await query.edit_message_text("➕ How much to add to emergency fund?")
        return ADD_EMERGENCY_MONTH
    
    elif action == 'edit_emergency_balance':
        await query.edit_message_text("✏️ Enter new emergency fund balance:")
        return EDIT_EMERGENCY_BALANCE
    
    elif action == 'edit_emergency_goal':
        await query.edit_message_text("🎯 Enter new emergency fund goal:")
        return EDIT_EMERGENCY_GOAL
    
    elif action == 'add_short_term':
        await query.edit_message_text("💵 How much to add to short-term savings?")
        return ADD_SHORT_TERM
    
    elif action == 'add_long_term':
        await query.edit_message_text("💎 How much to add to long-term savings?")
        return ADD_LONG_TERM
    
    return DASHBOARD


# Logging handlers
async def handle_log_total(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        current_week = profile.get_current_week_log()
        current_week['total'] = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ Total logged: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return LOG_WEEKLY_TOTAL


async def handle_log_remittance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        current_week = profile.get_current_week_log()
        current_week['remittance'] = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ Remittance logged: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return LOG_REMITTANCE


async def handle_log_food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        current_week = profile.get_current_week_log()
        current_week['food'] = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ Food logged: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return LOG_FOOD


async def handle_log_other(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        current_week = profile.get_current_week_log()
        current_week['other'] = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ Other logged: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return LOG_OTHER


# Update handlers
async def handle_salary_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.salary = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ Salary updated: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return UPDATE_SALARY


async def handle_spending_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.monthly_spending_goal = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ Spending goal updated: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return UPDATE_SPENDING_GOAL


async def handle_add_emergency_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.emergency_fund_balance += amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(
            f"✅ Added AED {amount:,.0f}\n"
            f"New balance: AED {profile.emergency_fund_balance:,.0f}"
        )
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return ADD_EMERGENCY_MONTH


async def handle_edit_emergency_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.emergency_fund_balance = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ Balance set to: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return EDIT_EMERGENCY_BALANCE


async def handle_edit_emergency_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.emergency_fund_goal = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ Goal set to: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return EDIT_EMERGENCY_GOAL


async def handle_add_short_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.short_term_savings += amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(
            f"✅ Added AED {amount:,.0f}\n"
            f"Total short-term: AED {profile.short_term_savings:,.0f}"
        )
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return ADD_SHORT_TERM


async def handle_add_long_term(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        profile.long_term_savings += amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(
            f"✅ Added AED {amount:,.0f}\n"
            f"Total long-term: AED {profile.long_term_savings:,.0f}"
        )
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return ADD_LONG_TERM


async def handle_add_other_expense_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle adding new other expense - get name first"""
    expense_name = update.message.text.strip()
    context.user_data['new_expense_name'] = expense_name
    
    await update.message.reply_text(f"Enter monthly amount for *{expense_name}*:", parse_mode='Markdown')
    return ADD_OTHER_EXPENSE_AMOUNT


async def handle_add_other_expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle adding/editing other expense - get amount"""
    try:
        amount = float(update.message.text.replace(',', '').strip())
        profile = context.user_data['profile']
        
        # Check if we're adding new or editing existing
        if 'new_expense_name' in context.user_data:
            expense_name = context.user_data['new_expense_name']
            del context.user_data['new_expense_name']
        elif 'editing_expense' in context.user_data:
            expense_name = context.user_data['editing_expense']
            del context.user_data['editing_expense']
        else:
            await update.message.reply_text("❌ Error. Please try again.")
            return await show_dashboard(update, context)
        
        profile.other_expenses[expense_name] = amount
        profile_manager.save_profile(profile)
        
        await update.message.reply_text(f"✅ {expense_name}: AED {amount:,.0f}")
        return await show_dashboard(update, context)
    except ValueError:
        await update.message.reply_text("Please enter a valid number:")
        return ADD_OTHER_EXPENSE_AMOUNT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled")
    return await show_dashboard(update, context)


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")
    
    app = Application.builder().token(token).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            # Onboarding
            ONBOARDING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_name)],
            ONBOARDING_JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_job)],
            ONBOARDING_SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_salary)],
            ONBOARDING_MONTHLY_SPENDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_monthly_spending)],
            ONBOARDING_EMERGENCY_FUND: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_emergency_fund)],
            ONBOARDING_MONTHLY_SAVINGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_monthly_savings)],
            
            # Main screens
            DASHBOARD: [CallbackQueryHandler(handle_callback)],
            MAIN_MENU: [CallbackQueryHandler(handle_callback)],
            
            # Logging
            LOG_WEEKLY_TOTAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_log_total)],
            LOG_REMITTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_log_remittance)],
            LOG_FOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_log_food)],
            LOG_OTHER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_log_other)],
            
            # Updates
            UPDATE_SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_salary_update)],
            UPDATE_SPENDING_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_spending_update)],
            ADD_EMERGENCY_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_emergency_month)],
            EDIT_EMERGENCY_BALANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_emergency_balance)],
            EDIT_EMERGENCY_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_emergency_goal)],
            ADD_SHORT_TERM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_short_term)],
            ADD_LONG_TERM: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_long_term)],
            
            # Other expenses
            ADD_OTHER_EXPENSE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_other_expense_name)],
            ADD_OTHER_EXPENSE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_other_expense_amount)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(conv_handler)
    
    logger.info("Expat's Financier Bot - Enhanced UI started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
