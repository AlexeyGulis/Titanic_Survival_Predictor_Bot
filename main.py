import re

from get_data_and_predict import get_predict
import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

PCLASS, AGE, NAME, SEX, SIBSP, PARCH, TICKET, FARE, CABIN, EMBARKED = range(10)


def float_or_int_checker(el: str) -> bool:
    pattern = r'^[-+]?(\d+(\.\d*)?|\.\d+)$'
    if re.match(pattern, el):
        return True
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the conversation about passenger."""
    reply_keyboard = [["1", "2", "3"]]
    await update.message.reply_text(
        "Hello, feel yourself as a titanic passenger, "
        "you need to write information and i am predict if you could survive or not. Good Luck!"
        "Send /cancel to stop talking to me.\n\n"
        "Lets start from Ticket class: 1 = 1st, 2 = 2nd, 3 = 3rd. ",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Ticket class"
        ),
    )
    return PCLASS


async def pclass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores pclass and ask for age"""
    text = update.message.text
    context.user_data['Pclass'] = [text]
    await update.message.reply_text(
        "How old are you?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AGE


async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores age and ask for name"""
    text = update.message.text
    if float_or_int_checker(text) and float(text) >= 0.0:
        context.user_data['Age'] = [float(text)]
        await update.message.reply_text(
            "What is your Name?",
            reply_markup=ReplyKeyboardRemove(),
        )
        return NAME
    else:
        await update.message.reply_text(
            "Please enter correct number age",
            reply_markup=ReplyKeyboardRemove(),
        )
        return AGE


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores name and ask for sex"""
    text = update.message.text
    context.user_data['Name'] = [text]
    reply_keyboard = [["female", "male"]]
    await update.message.reply_text(
        "Choose gender",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Gender"
        ),
    )
    return SEX


async def sex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores sex and ask for sibsp"""
    text = update.message.text
    context.user_data['Sex'] = [text]
    await update.message.reply_text(
        "Write a number of your siblings / spouses aboard the Titanic.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return SIBSP


async def sibsp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores name and ask for number of siblings on the ship"""
    text = update.message.text
    if text.isdigit() and int(text) >= 0:
        context.user_data['SibSp'] = [int(text)]
        await update.message.reply_text(
            "Write a number of your parents / children aboard the Titanic.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return PARCH
    else:
        await update.message.reply_text(
            "Write a number of your siblings / spouses aboard the Titanic with correct number value.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return SIBSP


async def parch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores sibsp and ask for number of parents / children aboard the Titanic"""
    text = update.message.text
    if text.isdigit() and int(text) >= 0:
        context.user_data['Parch'] = [int(text)]
        await update.message.reply_text(
            "Write a number of your ticket.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return TICKET
    else:
        await update.message.reply_text(
            "Write a number of your parents / children aboard the Titanic with correct number value.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return PARCH


async def ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores parch and ask for ticket"""
    text = update.message.text
    context.user_data['Ticket'] = [text]
    await update.message.reply_text(
        "How much cost ticket?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return FARE


async def fare(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores fare and ask for cabin"""
    text = update.message.text
    if float_or_int_checker(text) and float(text) >= 0.0:
        context.user_data['Fare'] = [float(text)]
        await update.message.reply_text(
            "Write a cabin number",
            reply_markup=ReplyKeyboardRemove(),
        )
        return CABIN
    else:
        await update.message.reply_text(
            "Please enter correct cost of ticket.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FARE


async def cabin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores cabin and ask for embarked"""
    text = update.message.text
    context.user_data['Cabin'] = [text]
    reply_keyboard = [["C", "Q", "S"]]
    await update.message.reply_text(
        "Choose port of Embarkation\n\n"
        "C = Cherbourg, Q = Queenstown, S = Southampton",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Port"
        ),
    )
    return EMBARKED


async def embarked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """stores embarked and get predict"""
    text = update.message.text
    context.user_data['Embarked'] = [text]
    await update.message.reply_text(
        "Wait for predict....",
    )
    await predict(update, context)
    await update.message.reply_text(
        "If you want start prediction again, use command /start \n \nGood Luck.",
    )
    return ConversationHandler.END


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Try to predict"""
    logger.info("Start prediction!")
    context.user_data['PassengerId'] = [3000]
    res = get_predict(context.user_data)
    logger.info("End prediction!")
    if res[0] == 0:
        text = "Sorry, but you died in this disaster"
    else:
        text = "Congratulations. You survived"
    await update.message.reply_text(text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the prediction."""
    user = update.message.from_user
    logger.info("User %s canceled the prediction.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can play another time.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def main():
    application = ApplicationBuilder().token('TOKEN').build()

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PCLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, pclass)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            SEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, sex)],
            SIBSP: [MessageHandler(filters.TEXT & ~filters.COMMAND, sibsp)],
            PARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, parch)],
            TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ticket)],
            FARE: [MessageHandler(filters.TEXT & ~filters.COMMAND, fare)],
            CABIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, cabin)],
            EMBARKED: [MessageHandler(filters.TEXT & ~filters.COMMAND, embarked)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
