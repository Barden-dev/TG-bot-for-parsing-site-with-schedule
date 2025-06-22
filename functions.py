import db
import wsite as site

from datetime import datetime, timedelta
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from contextlib import suppress
from tqdm import tqdm


days_translation = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье"
}

def get_current_date(days_to_add=0, weeks_to_add=0):
    total_days_to_add = days_to_add + weeks_to_add * 7
    target_date = datetime.now() + timedelta(days=total_days_to_add)
    current_date = target_date.date()
    weekday_name = days_translation.get(target_date.strftime("%A"), target_date.strftime("%A"))
    formatted_date = {weekday_name : current_date.strftime('%d.%m.%Y')}
    return formatted_date

def get_next_week_days():
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_monday)
    next_week = {}
    for i in range(7):
        day = next_monday + timedelta(days=i)
        weekday_name = days_translation.get(day.strftime("%A"), day.strftime("%A"))
        next_week[weekday_name] = day.strftime('%d.%m.%Y')
    return next_week

def get_current_week_days():
    today = datetime.now()
    previous_monday = today - timedelta(days=today.weekday())
    current_week = {}
    for i in range(7):
        day = previous_monday + timedelta(days=i)
        weekday_name = days_translation.get(day.strftime("%A"), day.strftime("%A"))
        current_week[weekday_name] = day.strftime('%d.%m.%Y')
    return current_week

def get_current_week():
    start_date = datetime(2024, 8, 26)
    current_date = datetime.now()
    days_difference = (current_date - start_date).days
    current_week = days_difference // 7 + 1
    return current_week - 2
def get_current_day():
    day_of_week = datetime.now().weekday()
    return day_of_week



# РАСПИСАНИЕ
def get_today_schedule(userid):
    date = get_current_date()
    if (db.user_group(userid)) == False:
        return "У вас не указана группа"
    schedule = site.get_user_schedule(db.user_group(userid), day_of_week=get_current_day())
    print(schedule)
    try:
        if list(schedule.values())[0] != '':
            return f'Расписание на <b>{list(schedule.keys())[0] + " " + list(date.values())[0]}</b>\n\n{list(schedule.values())[0]}'
        else:
            return f'Расписание на сегодня <b>{list(schedule.keys())[0] + " " + list(date.values())[0]}</b> отсутствует или же вы неправильно указали группу/ФИО'
    except:
        return f'Расписание на сегодня отсутствует или же вы неправильно указали группу/ФИО'



def get_tomorrow_schedule(userid):
    if (db.user_group(userid)) == False:
        return "У вас не указана группа"
    if (get_current_day() + 1) > 5:
        date = get_current_date(8 - (get_current_day() + 1))
        schedule = site.get_user_schedule(db.user_group(userid), True, 0)
    else:
        date = get_current_date(1)
        schedule = site.get_user_schedule(db.user_group(userid), day_of_week=get_current_day() + 1)
    
    try:
        if list(schedule.values())[0] != '':
            return f'Расписание на <b>{list(schedule.keys())[0] + " " + list(date.values())[0]}</b>\n\n{list(schedule.values())[0]}'
        else:
            return f'Расписание на завтра <b>{list(schedule.keys())[0] + " " + list(date.values())[0]}</b> отсутствует или же вы неправильно указали группу/ФИО'
    except:
        return f'Расписание на завтра отсутствует или же вы неправильно указали группу/ФИО'

async def get_current_week_schedule(message, userid):
    if (db.user_group(userid)) == False:
        return "У вас не указана группа"
    schedule = site.get_user_schedule(db.user_group(userid), day_of_week=0, days_count=6)
    if schedule:
        if all(element == '' for element in schedule.values()):
            await message.bot.send_message(chat_id=userid, text=f'Расписание на текущую неделю отсутствует или же вы неправильно указали группу/ФИО')
            return 
        for day, schedule_text in schedule.items():
            if schedule_text:
                date = get_current_week_days()[day]
                await message.bot.send_message(chat_id=userid, text=f'<b>{day + " " + date}</b>\n\n{schedule_text}')
    else:
        await message.bot.send_message(chat_id=userid, text=f'Расписание на текущую неделю отсутствует или же вы неправильно указали группу/ФИО')
        
    
async def get_next_week_schedule(message, userid):
    if (db.user_group(userid)) == False:
        return "У вас не указана группа"
    schedule = site.get_user_schedule(db.user_group(userid), True , day_of_week=0, days_count=6)
    if schedule:
        if all(element == '' for element in schedule.values()):
            await message.bot.send_message(chat_id=userid, text=f'Расписание на следующую неделю отсутствует или же вы неправильно указали группу/ФИО')
            return 
        for day, schedule_text in schedule.items():
            if schedule_text:
                date = get_next_week_days()[day]
                await message.bot.send_message(chat_id=userid, text=f'<b>{day + " " + date}</b>\n\n{schedule_text}')
# РАСПИСАНИЕ

async def broadcast(message, message_text):
    users = db.get_users_id()
    for user in users:
            with suppress(TelegramBadRequest):
                with suppress(TelegramForbiddenError):
                    await message.bot.send_message(chat_id=user[0], text=message_text)

async def broadcast_schedule_to_users(message):
    users = db.get_users_id()
    for user in tqdm(users):
        with suppress(TelegramBadRequest):
            with suppress(TelegramForbiddenError):
                date = get_current_date(1)
                schedule = site.get_user_schedule(db.user_group(user[0]), True, 0)
                try:
                    if list(schedule.values())[0] != '':
                        await message.bot.send_message(chat_id=user[0], text=f'Расписание на <b>{list(schedule.keys())[0] + " " + list(date.values())[0]}</b>\n\n{list(schedule.values())[0]}')
                except:
                    continue