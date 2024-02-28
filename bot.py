import logging
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import sqlite3

# Database creation
conn = sqlite3.connect('proverbs.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS proverbs (
        id INTEGER PRIMARY KEY,
        kazakh_text TEXT NOT NULL,
        russian_text TEXT NOT NULL,
        topic TEXT
    )
''')

conn.commit()
conn.close()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN: Final = 'Your TOKEN'
BOT_USERNAME: Final = '@qazaq_maqal_matel_bot'

TOPICS = [
    'Жизнь 🌳',
    'Здоровье ⚕️',
    'Труд 💪',
    'Родина 🇰🇿',
    'Дружба 👫',
    'Семья 👨‍👩‍👧‍👦',
    'Знание 📚',
    'Богатство 💰',
]


# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create custom keyboard buttons for topics
    keyboard = [[TOPICS[i], TOPICS[i + 1]] for i in range(0, len(TOPICS), 2)]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    # Send the message with the custom keyboard
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Я бот, который поможет Вам погрузиться в мир пословиц и поговорок 😃 \nВыберите тему, чтобы начать!",
        reply_markup=reply_markup
    )


def connect_to_database():
    conn = sqlite3.connect('proverbs.db')
    return conn


def get_proverb_by_topic(topic):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT kazakh_text, russian_text FROM proverbs WHERE topic=? ORDER BY RANDOM() LIMIT 1", (topic,))
    proverb = cursor.fetchone()
    conn.close()
    if proverb:
        kazakh_text, russian_text = proverb
        return f"🇰🇿: {kazakh_text}\n\n🇷🇺: {russian_text}"
    else:
        return None  # Return None when no proverb is found


# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Упс! Возникли проблемы, попробуйте позже!"
    )


# Responses
def handle_response(text: str) -> str:
    return 'Пожалуйста, пользуйтесь кнопками!'


# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    user_id: int = update.message.from_user.id

    print(f'User ({user_id}): "{text}"')

    if text in TOPICS:
        # If the text is one of the topics, get a proverb for that topic
        proverb = get_proverb_by_topic(text)
        if proverb is None:
            response = 'No proverb found for this topic.'
        else:
            response = proverb
    else:
        # Otherwise, use the original response
        response = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Commands
    application.add_handler(CommandHandler('start', start))

    # Messages
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    # Errors
    application.add_error_handler(error)

    # Polling
    application.run_polling(poll_interval=3)
