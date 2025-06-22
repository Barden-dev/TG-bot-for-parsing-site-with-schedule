import requests
from bs4 import BeautifulSoup

days_names = {"Понедельник": 0, "Вторник": 1, "Среда": 2, "Четверг": 3, "Пятница": 4, "Суббота": 5}
inv_days_names = {value: key for key, value in days_names.items()}

def get_user_schedule(group, next_week=False, day_of_week=0, days_count=1):
    schedule = {}
    URL = ""

    edited_group = group.replace(" ", "+")
    if "+" in edited_group:
        base_url = f"https://www.polessu.by/ruz/ng/?teacher={edited_group}"
    else:
        base_url = f"https://www.polessu.by/ruz/ng/?group={edited_group}"

    URL = f"{base_url}&day=next-week" if next_week else base_url

    try:
        response = requests.get(URL, timeout=10) # Добавлен таймаут для запроса
        response.raise_for_status() # Проверка на HTTP ошибки (4xx, 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе URL {URL}: {e}")
        return schedule # Возвращаем пустой словарь при ошибке сети/сервера

    soup = BeautifulSoup(response.text, 'html.parser')

    days_headers = soup.find_all('h3')
    daysInSchedule = {} # Словарь для хранения найденных в HTML дней и их заголовков
    for header in days_headers:
        try:
            # Извлекаем название дня (первое слово из текста заголовка)
            day_name_from_header = header.text.split()[0]
            if day_name_from_header in days_names:
                daysInSchedule[days_names[day_name_from_header]] = header
        except IndexError:
            # Если заголовок h3 пуст или не содержит текста, пропускаем
            # print(f"Предупреждение: не удалось извлечь имя дня из заголовка: '{header.text}'") # для отладки
            continue

    # current_calendar_day_index отслеживает фактический индекс дня недели (0-5), который мы пытаемся извлечь.
    current_calendar_day_index = day_of_week
    
    # Пытаемся извлечь 'days_count' количество дней.
    for _ in range(days_count):
        # Убедимся, что не выходим за пределы субботы (индекс 5)
        if current_calendar_day_index > 5: # Предполагаем рабочую неделю до субботы включительно
            break

        # Проверяем, есть ли этот календарный день в загруженном HTML (в daysInSchedule)
        if current_calendar_day_index in daysInSchedule:
            # Этот день существует в HTML, парсим его
            schedule_text_for_day = "" # Текст расписания для текущего дня
            current_day_header_tag = daysInSchedule[current_calendar_day_index]

            day_block = current_day_header_tag.find_next_sibling('div', class_='row acty-group')
            if not day_block:
                # Если нет блока с занятиями, переходим к следующему дню
                current_calendar_day_index += 1
                continue

            time_blocks = day_block.find_all('div', class_='col-md-2 acty-time')
            for time_block in time_blocks:
                time = time_block.text.strip()
                activities_list_div = time_block.find_next_sibling('div', class_='col-md-10 acty-list')
                if not activities_list_div:
                    continue

                for activity in activities_list_div.find_all('div', class_='acty-item'):
                    room = activity.find('div', class_='acty-rooms')
                    room_text = room.text.strip() if room else "Не указана"

                    tags = activity.find('span', class_='acty-tags')
                    tag_text = tags.text.strip() if tags else ""

                    subject = activity.find('span', class_='acty-subjects')
                    subject_text = subject.text.strip() if subject else "Не указано"

                    new_tag_text = f" - {tag_text}" if tag_text else ""
                    
                    if "+" in edited_group:  # Для преподавателя
                        students = activity.find('span', class_='acty-students')
                        group_text = students.text.strip() if students else "Не указана"
                        schedule_text_for_day += f"🕘{time} - {subject_text}{new_tag_text}\n📝Группа: {group_text}\n🏫Аудитория: {room_text}\n\n"
                    else:  # Для студента
                        teacher = activity.find('span', class_='acty-teachers')
                        teacher_text = teacher.text.strip() if teacher else "Не указан"
                        subgroup = activity.find('span', class_='acty-students')

                        if subgroup and subgroup.text.strip():
                            subgroup_text = subgroup.text.strip()
                            if "/" in subgroup_text:
                                schedule_text_for_day += f"🕘{time} - {subject_text}{new_tag_text}\n📝Подгруппа: {subgroup_text}\n🏫Аудитория: {room_text}\n👨‍Преподаватель: {teacher_text}\n\n"
                            else:
                                schedule_text_for_day += f"🕘{time} - {subject_text}{new_tag_text}\n📝Группа: {subgroup_text}\n🏫Аудитория: {room_text}\n👨‍Преподаватель: {teacher_text}\n\n"
                        else:
                            schedule_text_for_day += f"🕘{time} - {subject_text}{new_tag_text}\n🏫Аудитория: {room_text}\n👨‍Преподаватель: {teacher_text}\n\n"
            
            # Добавляем день в расписание, только если для него есть записи
            if schedule_text_for_day:
                day_name_to_store = inv_days_names[current_calendar_day_index]
                schedule[day_name_to_store] = schedule_text_for_day.strip()
        
        # Переходим к следующему календарному дню для следующей итерации/попытки.
        # Это происходит независимо от того, был ли день найден в HTML,
        # потому что мы итерируемся по 'days_count' последовательным календарным дням.
        current_calendar_day_index += 1

    return schedule

# Пример использования:
if __name__ == "__main__":
    # Расписание группы 24ИТ-3 на следующую неделю, начиная с понедельника, 6 дней
    print("--- Расписание для группы 24ИТ-3, следующая неделя (6 дней с ПН) ---")
    student_schedule_next_week = get_user_schedule("24ИТ-3", next_week=True, day_of_week=0, days_count=6)
    if student_schedule_next_week:
        for day, text in student_schedule_next_week.items():
            print(f"--- {day} ---")
            print(f"{text}\n")
    else:
        print("Расписание не найдено или произошла ошибка.\n")

    # Расписание группы 24ИТ-3 на текущую неделю, только Пятница
    print("--- Расписание для группы 24ИТ-3, текущая неделя (только ПТ) ---")
    student_schedule_friday = get_user_schedule("24ИТ-3", next_week=False, day_of_week=4, days_count=1) # day_of_week=4 это Пятница
    if student_schedule_friday:
        for day, text in student_schedule_friday.items():
            print(f"--- {day} ---")
            print(f"{text}\n")
    else:
        print("Расписание на пятницу не найдено или произошла ошибка.\n")

    # Пример для преподавателя, если необходимо
    # print("--- Расписание для преподавателя 'Фамилия И О', текущая неделя (Вторник) ---")
    # teacher_schedule = get_user_schedule("Фамилия И О", next_week=False, day_of_week=1, days_count=1) # day_of_week=1 это Вторник
    # if teacher_schedule:
    #     for day, text in teacher_schedule.items():
    #         print(f"--- {day} ---")
    #         print(f"{text}\n")
    # else:
    #     print("Расписание для преподавателя не найдено или произошла ошибка.\n")