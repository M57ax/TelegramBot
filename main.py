import json
import asyncio
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from zoneinfo import ZoneInfo
now = datetime.now(ZoneInfo("Europe/Berlin"))

EVENTS_FILE = 'tasks.json'

def load_events():
    try:
        with open(EVENTS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
            return[]
    
def save_events(events):
    try:
        with open(EVENTS_FILE, 'w') as file:
            json.dump(events, file, indent=4)
    except FileNotFoundError:
            return[]
def add_events(user_id, event_name, event_datetime):
    events = load_events()
    if events:
        event_id = max(event['event_id'] for event in events) + 1
    else:
        event_id = 1
    events.append({
        "event_id": event_id,
        "user_id": user_id,
        "event": event_name,
        "datetime": event_datetime.strftime('%d-%m-%Y %H:%M')
    })
    save_events(events)
def delete_event(event_id):
    events = load_events()
    updated_events = [event for event in events if not (event['event_id'] == event_id)]
    
    if len(updated_events) == len(events):
        return False  # no event found
    else:
        save_events(updated_events)
        return True

TOKEN = '' #Add TOKEN
BOT_USERNAME: Final = '' #ADD the bot name
#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, bot started!')

    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('youse /add, /delete or /show for events')

    
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('you could add custom a custom command here')

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        event_name = context.args[0]
        event_datetime_str = context.args[1]  # Beispiel: '03-02-2025:15:00'
    except IndexError:
        await update.message.reply_text("Please enter a event name and a date. For Example:\n/add Meeting 03-02-2025:15:00")
        return

    from datetime import datetime
    try:
        event_datetime = datetime.strptime(event_datetime_str, '%d-%m-%Y:%H:%M')
    except ValueError:
        await update.message.reply_text("wrong format. use: TT-MM-JJJJ:HH:MM (e.g. 03-02-2025:15:00)")
        return

    add_events(user_id, event_name, event_datetime)
    await update.message.reply_text(f"Event '{event_name}' for {event_datetime.strftime('%d.%m.%Y %H:%M')} saved!")

#Reminder FUnktion
async def reminder(context: ContextTypes.DEFAULT_TYPE):
    events = load_events()
    now = datetime.now()

    if not events:
        return 

    today_str = now.strftime('%d-%m-%')
    
    for event in events:
        event_time_str = event["datetime"]
        event_time_obj = datetime.strptime(event_time_str, '%d-%m-%Y %H:%M')

        if event_time_obj.strftime('%d-%m-%') == today_str:
            message = f"🔔 Reminder: Youre Event **'{event['event']}'** is today!"
            await context.bot.send_message(chat_id=event["user_id"], text=message)

async def start_scheduler(application: Application):
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Berlin"))
    scheduler.add_job(reminder, 'cron', hour=7, minute=0, args=[application]) ######
    scheduler.start()

async def show_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    events = load_events()

    response = "📅 Here are your saved events:\n\n"
    for event in events:
        response += f"- {event['event']} on {event['datetime']}     ID:{event['event_id']}\n"

    await update.message.reply_text(response)
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        event_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text('This is a invalid Event-ID')
        return
    
    if delete_event(event_id):
        await update.message.reply_text(f"Event with ID {event_id} is deleted")
    else:
        await update.message.reply_text(f"No event with ID {event_id} found.")

#Resoponens
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'hey' in processed:
        return 'Hello!'

    return 'I didnt understand that'
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
    print(f'Update {update} made an error{context.error}')

if __name__ == '__main__':
    print('Startet...')
    app = Application.builder().token(TOKEN).build()
    #Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('add', add_command))
    app.add_handler(CommandHandler('show', show_command))
    app.add_handler(CommandHandler('delete', delete_command))
    
    #Start Sheduler
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(start_scheduler(app))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    #Error
    app.add_error_handler(error)

    #Updates
    print('Searching for new messages...')
    app.run_polling(poll_interval=3)
