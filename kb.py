from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Расписание на сегодня"))
    builder.add(types.KeyboardButton(text="Расписание на завтра"))
    builder.add(types.KeyboardButton(text="Расписание на текущую неделю"))
    builder.add(types.KeyboardButton(text="Расписание на следующую неделю"))
    builder.add(types.KeyboardButton(text="Текущая группа/ФИО"))
    builder.add(types.KeyboardButton(text="Изменить группу/ФИО"))
    builder.add(types.KeyboardButton(text="Управление напоминаниями"))
    builder.adjust(2,1,1,2,1)
    return builder.as_markup(resize_keyboard=True)


def get_reminders_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Закрыть", callback_data="close_menu"))
    builder.add(types.InlineKeyboardButton(text="Добавить напоминания", callback_data="add_reminder"))
    builder.add(types.InlineKeyboardButton(text="Удалить напоминания", callback_data="remove_reminder"))
    builder.add(types.InlineKeyboardButton(text="Дни недели, для напоминаний", callback_data="days_of_week_reminder"))
    builder.adjust(1,2,1,1,2,1)
    return builder.as_markup()

def get_remove_reminders_keyboard(reminders):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Вернуться назад", callback_data="reminders_back"))
    for reminder in reminders:
        time = reminder[0]
        type_ = reminder[1]
        builder.add(types.InlineKeyboardButton(text=f"{time}{type_}", callback_data=f"reminder_rem_{time}_{type_}"))

    builder.adjust(1,2)
    return builder.as_markup()

def get_change_reminders_days():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Вернуться назад", callback_data="reminders_back"))
    builder.add(types.InlineKeyboardButton(text="День/Тип"))
    builder.add(types.InlineKeyboardButton(text="Сегодня"))
    builder.add(types.InlineKeyboardButton(text="Завтра"))
    

    builder.adjust(1,3,3,3,3,3,3,3,3)
    return builder.as_markup()