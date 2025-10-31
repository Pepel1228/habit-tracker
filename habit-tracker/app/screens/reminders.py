from kivymd.uix.screen import MDScreen
from kivy.properties import BooleanProperty, StringProperty, ListProperty, NumericProperty
from app import db
import json


class RemindersScreen(MDScreen):
    habit_id = NumericProperty(None)
    reminder_enabled = BooleanProperty(False)
    reminder_time = StringProperty("08:00")
    vibration_enabled = BooleanProperty(False)
    sound_enabled = BooleanProperty(True)
    reminder_text = StringProperty("Не забыть выполнить привычку")
    repeat_option = StringProperty("Каждый день")
    days_selected = ListProperty([])

    def on_enter(self):
        print(f"🔍 RemindersScreen: habit_id = {self.habit_id}")
        if self.habit_id:
            self.load_existing_reminder()
        else:
            print("⚠ Внимание: habit_id не установлен")

    def load_existing_reminder(self):
        print(f"🔍 Загрузка напоминания для habit_id={self.habit_id}")

        reminder_data = db.get_reminder(self.habit_id)
        if reminder_data:
            # Заполняем поля данными из БД
            self.reminder_time = reminder_data.get('time', '08:00')
            self.repeat_option = reminder_data.get('repeat', 'daily')  # исправлено на английские ключи

            # Обрабатываем дни (они могут быть в формате JSON строки)
            days = reminder_data.get('days', [])
            if isinstance(days, str):
                try:
                    days = json.loads(days)
                except:
                    days = []
            self.days_selected = days

            self.vibration_enabled = bool(reminder_data.get('vibration', False))
            self.sound_enabled = bool(reminder_data.get('sound', True))
            self.reminder_text = reminder_data.get('text', 'Не забыть выполнить привычку')
            self.reminder_enabled = True

            print(f"✅ Загружены настройки напоминания: {self.reminder_time}, {self.repeat_option}")

            # Обновляем UI
            self.update_ui_from_data()
        else:
            print("ℹ️ Напоминание не найдено, используем настройки по умолчанию")

    def update_ui_from_data(self):
        try:
            # Обновляем поле времени
            if 'reminder_time' in self.ids:
                self.ids.reminder_time.text = self.reminder_time

            # Обновляем переключатель напоминаний
            if 'reminder_enabled' in self.ids:
                self.ids.reminder_enabled.active = self.reminder_enabled

            # Обновляем переключатели вибрации и звука
            if 'vibration_switch' in self.ids:
                self.ids.vibration_switch.active = self.vibration_enabled
            if 'sound_switch' in self.ids:
                self.ids.sound_switch.active = self.sound_enabled

            # Обновляем текст напоминания
            if 'reminder_text' in self.ids:
                self.ids.reminder_text.text = self.reminder_text

            # Обновляем выбор повторения
            self.set_repeat_option(self.repeat_option)

            # Обновляем дни недели
            self.update_days_buttons()

        except Exception as e:
            print(f"⚠ Ошибка при обновлении UI: {e}")

    def update_days_buttons(self):
        day_buttons = {
            "Mon": self.ids.day_mon if 'day_mon' in self.ids else None,
            "Tue": self.ids.day_tue if 'day_tue' in self.ids else None,
            "Wed": self.ids.day_wed if 'day_wed' in self.ids else None,
            "Thu": self.ids.day_thu if 'day_thu' in self.ids else None,
            "Fri": self.ids.day_fri if 'day_fri' in self.ids else None,
            "Sat": self.ids.day_sat if 'day_sat' in self.ids else None,
            "Sun": self.ids.day_sun if 'day_sun' in self.ids else None,
        }

        for day_name, button in day_buttons.items():
            if button:
                if day_name in self.days_selected:
                    # Выделенный цвет
                    button.md_bg_color = self.theme_cls.primary_color
                else:
                    # Серый цвет для невыбранных
                    button.md_bg_color = (0.5, 0.5, 0.5, 1)

    def go_back(self):
        if self.manager and 'habit_add' in self.manager.screen_names:
            self.manager.current = 'habit_add'

    def toggle_reminder(self, active):
        self.reminder_enabled = bool(active)
        print(f"Напоминания {'включены' if self.reminder_enabled else 'выключены'}")

    def set_time(self, text):
        self.reminder_time = text
        print(f"Установлено время напоминания: {self.reminder_time}")

    def set_repeat_option(self, option):
        self.repeat_option = option
        print(f"Выбрано повторение: {option}")

        # Получаем кнопки дней недели
        days = [
            self.ids.day_mon, self.ids.day_tue, self.ids.day_wed,
            self.ids.day_thu, self.ids.day_fri, self.ids.day_sat, self.ids.day_sun
        ]

        if option == "custom":
            # Включаем выбор дней
            for btn in days:
                btn.disabled = False
        else:
            # Отключаем выбор дней
            for btn in days:
                btn.disabled = True
                btn.md_bg_color = (0.5, 0.5, 0.5, 1)  # серый цвет
            self.days_selected = []

    def toggle_day(self, day):
        btn_map = {
            "Mon": self.ids.day_mon,
            "Tue": self.ids.day_tue,
            "Wed": self.ids.day_wed,
            "Thu": self.ids.day_thu,
            "Fri": self.ids.day_fri,
            "Sat": self.ids.day_sat,
            "Sun": self.ids.day_sun,
        }
        btn = btn_map.get(day)

        if not btn:
            return

        if day in self.days_selected:
            self.days_selected.remove(day)
            btn.md_bg_color = (0.5, 0.5, 0.5, 1)  # серый
            print(f"День снят: {day}")
        else:
            self.days_selected.append(day)
            btn.md_bg_color = self.theme_cls.primary_color  # выделенный цвет
            print(f"День выбран: {day}")

    def toggle_vibration(self, active):
        self.vibration_enabled = bool(active)
        print(f"Вибрация {'включена' if self.vibration_enabled else 'выключена'}")

    def toggle_sound(self, active):
        self.sound_enabled = bool(active)
        print(f"Звук {'включен' if self.sound_enabled else 'выключен'}")

    def save_settings(self):
        if not self.habit_id:
            print("⚠ Нет habit_id, напоминание не сохранено")
            return

        # Сохраняем в БД
        db.save_reminder(
            habit_id=self.habit_id,
            time=self.reminder_time,
            repeat=self.repeat_option,
            days=self.days_selected,
            vibration=self.vibration_enabled,
            sound=self.sound_enabled,
            text=self.reminder_text
        )
        print(f"✅ Напоминание сохранено для привычки {self.habit_id}")

        # Возвращаемся на экран добавления привычки
        if self.manager and 'habit_add' in self.manager.screen_names:
            self.manager.current = 'habit_add'