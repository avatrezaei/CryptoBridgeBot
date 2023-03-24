import logging 
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


# Your Tron network functions should be imported here
from tron_utils import deposit_address, process_withdrawal, get_balances

# Replace your_bot_token with the actual bot token from BotFather
TOKEN = "TOKEN"

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(f"Welcome {user.first_name}!\nUse /deposit, /withdraw, and /balance commands to manage your assets.")

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    address = deposit_address(user_id)
    await update.message.reply_text(f"Your deposit address is: {address}")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if len(context.args) < 2:
        await update.message.reply_text("Please provide a valid withdrawal amount and currency (USDT or BUSD).")
        return
    amount = float(context.args[0])
    currency = context.args[1].upper()
    if currency not in ["USDT", "BUSD"]:
        await update.message.reply_text("Invalid currency. Please use USDT or BUSD.")
        return
    if amount <= 0.0:
        await update.message.reply_text("Please provide a valid withdrawal amount.")
        return
    if process_withdrawal(user_id, amount, currency):
        await update.message.reply_text(f"Withdrawal successful. Amount: {amount} {currency}")
    else:
        await update.message.reply_text("Withdrawal failed. Insufficient balance.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    balances = get_balances(user_id)
    await update.message.reply_text(f"Your USDT balance is: {balances['usdt']}\nYour BUSD balance is: {balances['busd']}")

 

def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("start", start))

    app.run_polling()

if __name__ == "__main__":
    main()
