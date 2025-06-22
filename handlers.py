import config
import db
import kb
import functions
import time

from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from functools import wraps


router = Router()

class UserStates(StatesGroup):
    choosing_group = State()
    choosing_reminders = State()
    setting_broadcast = State()
    setting_broadcast_schedule = State()


last_call = {}
def rate_limit(limit: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id
            now = time.time()
            if user_id not in last_call:
                last_call[user_id] = 0
            if now - last_call[user_id] >= limit:
                last_call[user_id] = now
                return await func(message, *args, **kwargs)
            else:
                await message.reply(f"Подождите {limit} секунды!")
        return wrapper
    return decorator


# МЕНЮ СТАРТ
@router.message(Command("start"))
@rate_limit(2)
async def cmd_start(message: types.Message, state: FSMContext):
    if db.user_group(message.from_user.id) == False:
        await state.set_state(UserStates.choosing_group)
        await message.answer("Введите вашу группу/ФИО(Для преподавателей). (Пример ввода группы: 21БТ-1 или 24ФиК-1). Если сомневаетесь, посмотрите написание на сайте расписания!")
    else:
        await message.answer("Выберите действие", reply_markup=kb.get_main_keyboard())
# МЕНЮ СТАРТ


# УДАЛАИТЬ / ЗАКРЫТЬ МЕНЮ
@router.callback_query(F.data == "close_menu")
async def remove_reminder(callback: types.CallbackQuery):
    await callback.message.delete()
# УДАЛАИТЬ / ЗАКРЫТЬ МЕНЮ


# ВЫБОР ГРУППЫ
@router.message(UserStates.choosing_group)
async def group_choosen(message: Message, state: FSMContext):
    db.change_user_group(message.from_user.id, message.text)
    await message.answer(text="Всё успешно,теперь вы можете получать расписание", reply_markup=kb.get_main_keyboard())
    await state.clear()
# ВЫБОР ГРУППЫ


# ПОЛУЧЕНИЕ РАСПИСАНИЯ
@router.message(F.text.lower() == "расписание на сегодня")
@rate_limit(2)
async def get_today_schedule_handler(message: types.Message):
    await message.reply(functions.get_today_schedule(message.from_user.id), reply_markup=kb.get_main_keyboard())

@router.message(F.text.lower() == "расписание на завтра")
@rate_limit(2)
async def get_tomorrow_schedule_handler(message: types.Message):
    await message.reply(functions.get_tomorrow_schedule(message.from_user.id), reply_markup=kb.get_main_keyboard())
    
@router.message(F.text.lower() == "расписание на текущую неделю")
@rate_limit(2)
async def get_current_week_schedule_handler(message: types.Message):
    await functions.get_current_week_schedule(message, message.from_user.id)

@router.message(F.text.lower() == "расписание на следующую неделю")
@rate_limit(2)
async def get_next_week_schedule_handler(message: types.Message):
    await functions.get_next_week_schedule(message, message.from_user.id)
# ПОЛУЧЕНИЕ РАСПИСАНИЯ


# ТЕКУЩАЯ ГРУППА/ФИО
@router.message(F.text.lower() == "текущая группа/фио")
@rate_limit(2)
async def with_puree(message: types.Message):
    if (db.user_group(message.from_user.id)) == False:
        await message.reply("У вас не указана группа")
    await message.reply(db.user_group(message.from_user.id))
# ТЕКУЩАЯ ГРУППА/ФИО


# ИЗМЕНИТЬ ГРУППУ/ФИО
@router.message(F.text.lower() == "изменить группу/фио")
@rate_limit(2)
async def with_puree(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.choosing_group)
    await message.answer("Введите вашу группу/ФИО(Для преподавателей). (Пример ввода группы: 21БТ-1 или 24ФиК-1). Если сомневаетесь, посмотрите написание на сайте расписания!")
# ИЗМЕНИТЬ ГРУППУ/ФИО


# НАПОМИНАНИЯ
@router.message(F.text.lower() == "управление напоминаниями")
@rate_limit(2)
async def reminder_menu(message: types.Message):
    #await message.answer("В разработке")
    await message.answer("Здесь вы можете настроить ваши напоминания", reply_markup=kb.get_reminders_keyboard())
    
@router.callback_query(F.data == "add_reminder")
async def add_reminder(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserStates.choosing_reminders)
    await callback.message.edit_text("Пожалуйста, введите время и тип напоминания в формате ЧЧ:ММТ, где Т - тип напоминания (с - напоминание на текущий день, з - на следующий день). Вы можете ввести несколько напоминаний, разделяя их запятыми. Например: 08:20с,12:00з,00:00с")

@router.message(UserStates.choosing_reminders)
async def choose_reminder(message: Message, state: FSMContext):
    reminders = message.text.split(',')
    user_reminders = db.get_user_reminders(message.from_user.id)
    print(user_reminders)
    successful_reminders = []
    failed_reminders = []
    print(reminders)
    for reminder in reminders:
        print(reminder)
        time, reminder_type = reminder[:-1], reminder[-1].lower()
        print((time, reminder_type))
        try:
            if reminder_type in "сcзz" and (23 >= int(time[0:2]) >= 0) and (59 >= int(time[3:5]) >= 0):
                successful_reminders.append(f"{time}{reminder_type}")
                if (time, reminder_type) not in user_reminders:
                    db.add_reminder(message.from_user.id, time, reminder_type)
        except:
            failed_reminders.append(f"{time}{reminder_type}")
            continue
    if not failed_reminders:
        reminders_text = ""
        for reminder in successful_reminders:
            reminders_text += reminder
            reminders_text += ","

        reminders_text = reminders_text[:-1]
        await message.reply(text=f"Всё успешно. Добавленные напоминания: {reminders_text}", reply_markup=kb.get_reminders_keyboard())
        await state.clear()
    elif failed_reminders and successful_reminders:
        successful_reminders_text = ""
        for reminder in successful_reminders:
            successful_reminders_text += reminder
            successful_reminders_text += ","
            
        successful_reminders_text = successful_reminders_text[:-1]
    
        failed_reminders_text = ""
        for reminder in failed_reminders:
            failed_reminders_text += reminder
            failed_reminders_text += ","
            
        failed_reminders_text = failed_reminders_text[:-1]
        await message.reply(text=f"Добавленные напоминания: {successful_reminders_text}. В этих напоминаниях ошибка: {failed_reminders_text}", reply_markup=kb.get_reminders_keyboard())
        await state.clear()
    else:
        failed_reminders_text = ""
        for reminder in failed_reminders:
            failed_reminders_text += reminder
            failed_reminders_text += ","

        failed_reminders_text = failed_reminders_text[:-1]
        await message.reply(text=f"Напоминания добавлены не были из-за ошибки в написании: {failed_reminders_text}", reply_markup=kb.get_reminders_keyboard())
        await state.clear()


@router.callback_query(F.data == "remove_reminder")
async def remove_reminders_menu(callback: types.CallbackQuery):
    reminders = db.get_user_reminders(callback.from_user.id)
    if reminders:
        await callback.message.edit_text("Нажмите на напоминание, чтобы удалить его", reply_markup=kb.get_remove_reminders_keyboard(reminders))
    else:
        await callback.message.edit_text("У вас нет напоминаний", reply_markup=kb.get_reminders_keyboard())


@router.callback_query(F.data.startswith("reminder_rem"))
async def remove_reminder(callback: types.CallbackQuery):
    data = callback.data.split('_')
    db.remove_reminder(callback.from_user.id, data[2], data[3])
    reminders = db.get_user_reminders(callback.from_user.id)
    if reminders:
        await callback.message.edit_text(f"Вы успешно удалили напоминание {data[2]}{data[3]}", reply_markup=kb.get_remove_reminders_keyboard(reminders))
    else:
        await callback.message.edit_text("У вас нет напоминаний", reply_markup=kb.get_reminders_keyboard())

@router.callback_query(F.data == "reminders_back")
async def remove_reminder(callback: types.CallbackQuery):
    await callback.message.edit_text("Здесь вы можете настроить ваши напоминания", reply_markup=kb.get_reminders_keyboard())


@router.callback_query(F.data == "days_of_week_reminder")
async def change_reminders_days(callback: types.CallbackQuery):
    await callback.message.edit_text("Выберите меню", reply_markup=kb.get_change_reminders_days())
    #db.change_notification_days(callback.from_user.id, 'с', "wed")
    #print(db.get_notification_days(callback.from_user.id))
    


# НАПОМИНАНИЯ


# ВЕЩАНИЕ
@router.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admin_id:
        await state.set_state(UserStates.setting_broadcast)
        await message.reply("Введите сообщение")

@router.message(UserStates.setting_broadcast)
async def broadcast_handler(message: Message, state: FSMContext):
    message_text = message.text
    if message_text.lower() == "отмена":
        await message.answer("Отменено")
    else:
        await message.answer("Начинаю отправлять")
        await functions.broadcast(message,  message_text)
    await state.clear()
    await message.answer("Всё отправлено")


@router.message(Command("broadcast_schedule"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admin_id:
        await state.set_state(UserStates.setting_broadcast_schedule)
        await message.reply("Подтвердите")
        
        
@router.message(UserStates.setting_broadcast_schedule)
async def broadcast_handler(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await message.answer("Отменено")
    else:
        await message.answer("Начинаю отправлять")
        await functions.broadcast_schedule_to_users(message)
    await state.clear()
    await message.answer("Всё отправлено")
# ВЕЩАНИЕ