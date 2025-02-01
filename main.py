from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7361694135:AAGkXTulNIkx7Iqwa7uJrYhwfRD85g4tfTs'
BOT_USERNAME: Final = '@roasy_bot'
#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hallo! Schön, dass du da bist <3')

    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Das kommtn noch, hier werden die commands stehen')

    
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('custom halt')

#Resoponens
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'hey' in text in processed:
        return 'Hallo!'

    if 'wie gehts' in text in processed:
        return 'super und dir?'

    return 'das habe ich nicht verstanden'
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} hat einen Fehler verursacht{context.error}')

if __name__ == '__main__':
    print('Startet...')
    app = Application.builder().token(TOKEN).build()
    #Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('start', help_command))
    app.add_handler(CommandHandler('start', custom_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Error
    app.add_error_handler(error)

    #Updates
    print('Sucht nach neuen Nachrichten')
    app.run_polling(poll_interval=3)
