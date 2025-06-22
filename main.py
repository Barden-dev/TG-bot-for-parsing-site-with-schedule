import db
import config

import asyncio
import sys
import logging
import schedule

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from datetime import datetime
from handlers import router
import functions



async def send_notification_to_user():
    current_time = datetime.now().strftime("%H:%M")
    items = db.get_current_notification(current_time)
    for item in items:
        if item[2].lower() in "сc":
            await send_message_to_user(item[0], f"<b>Напоминание!</b>\n\n{functions.get_today_schedule(item[0])}")
        elif item[2].lower() in "зz":
            await send_message_to_user(item[0], f"<b>Напоминание!</b>\n\n{functions.get_tomorrow_schedule(item[0])}")

def schedule_tasks():
    #schedule.every(60).seconds.do(lambda: asyncio.create_task(send_notification_to_user()))
    return

async def scheduler_loop():
    while True:
        schedule.run_pending()
        await asyncio.sleep(5)

async def send_message_to_user(user_id, message_text):
    await bot.send_message(chat_id=user_id, text=message_text)
        
async def main():
    global bot
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    db.init_db()
    
    schedule_tasks()
    asyncio.create_task(scheduler_loop())
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), handle_signals=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

