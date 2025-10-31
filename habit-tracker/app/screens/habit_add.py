from kivymd.uix.screen import MDScreen
from app import db


class HabitAddScreen(MDScreen):
    def go_back(self):
        # возвращаемся на экран списка привычек
        if self.manager and "habit_list" in self.manager.screen_names:
            self.manager.current = "habit_list"

    def save_habit(self):
        # Используем правильные id из KV файла
        name = self.ids.habit_title.text if "habit_title" in self.ids else ""
        goal_value = self.ids.goal_value.text if "goal_value" in self.ids else ""
        goal_unit = self.ids.goal_unit.text if "goal_unit" in self.ids else "раз"

        # Формируем цель
        goal = None
        if goal_value and goal_value.strip():
            goal = f"{goal_value.strip()} {goal_unit.strip()}"

        # Проверяем что название не пустое
        if not name or name.strip() == "":
            print("❌ Введите название привычки")
            return

        repeat = "Ежедневно"

        habit_id = db.add_habit(name.strip(), goal, repeat)

        if habit_id is None:
            print("❌ Ошибка: не удалось сохранить привычку в БД")
            return

        print(f"✅ Привычка '{name}' сохранена в БД (id={habit_id})")

        # Очищаем поля
        if "habit_title" in self.ids:
            self.ids.habit_title.text = ""
        if "habit_description" in self.ids:
            self.ids.habit_description.text = ""
        if "goal_value" in self.ids:
            self.ids.goal_value.text = ""

        # Возвращаемся и обновляем список привычек
        self.go_back_and_refresh()

    def go_back_and_refresh(self):
        if self.manager and "habit_list" in self.manager.screen_names:
            # Получаем экран списка и обновляем его
            habit_list_screen = self.manager.get_screen("habit_list")
            self.manager.current = "habit_list"
            # Даем время на переход и затем обновляем список
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: habit_list_screen.load_habits(), 0.1)

    def select_repeat(self, option):
        print(f"Выбрано повторение: {option}")
        # Можно сохранить выбор в переменную
        self.selected_repeat = option

    def select_goal(self, option):
        print(f"Выбрана цель: {option}")
        # Меняем текст единицы измерения
        if "goal_unit" in self.ids:
            if option == "days":
                self.ids.goal_unit.text = "дней"
            elif option == "times":
                self.ids.goal_unit.text = "раз"

    def set_reminder(self):
        if self.manager and "reminders" in self.manager.screen_names:
            reminders_screen = self.manager.get_screen("reminders")

            # ПЕРЕДАЕМ ID ТОЛЬКО ЧТО СОХРАНЕННОЙ ПРИВЫЧКИ
            name = self.ids.habit_title.text if "habit_title" in self.ids else ""
            goal_value = self.ids.goal_value.text if "goal_value" in self.ids else ""
            goal_unit = self.ids.goal_unit.text if "goal_unit" in self.ids else "раз"

            # Формируем цель
            goal = None
            if goal_value and goal_value.strip():
                goal = f"{goal_value.strip()} {goal_unit.strip()}"

            # Проверяем что название не пустое
            if not name or name.strip() == "":
                print("❌ Введите название привычки")
                return

            repeat = "Ежедневно"

            # СОХРАНЯЕМ ПРИВЫЧКУ И ПОЛУЧАЕМ ЕЕ ID
            habit_id = db.add_habit(name.strip(), goal, repeat)

            if habit_id is None:
                print("❌ Ошибка: не удалось сохранить привычку в БД")
                return

            print(f"✅ Привычка '{name}' сохранена в БД (id={habit_id})")

            # ПЕРЕДАЕМ ID СОХРАНЕННОЙ ПРИВЫЧКИ НА ЭКРАН НАПОМИНАНИЙ
            reminders_screen.habit_id = habit_id
            self.manager.current = "reminders"

            # Очищаем поля после успешного сохранения
            if "habit_title" in self.ids:
                self.ids.habit_title.text = ""
            if "habit_description" in self.ids:
                self.ids.habit_description.text = ""
            if "goal_value" in self.ids:
                self.ids.goal_value.text = ""

        else:
            print("⚠ Экран reminders не найден")